
############################################################################
#
# AVI CONFIDENTIAL
# __________________
#
# [2013] - [2018] Avi Networks Incorporated
# All Rights Reserved.
#
# NOTICE: All information contained herein is, and remains the property
# of Avi Networks Incorporated and its suppliers, if any. The intellectual
# and technical concepts contained herein are proprietary to Avi Networks
# Incorporated, and its suppliers and are covered by U.S. and Foreign
# Patents, patents in process, and are protected by trade secret or
# copyright law, and other laws. Dissemination of this information or
# reproduction of this material is strictly forbidden unless prior written
# permission is obtained from Avi Networks Incorporated.
###

"""
=====================
Cloud Connector Views
=====================
"""
import copy
import logging
import traceback
from google.protobuf.service import RpcController
from rest_framework.response import Response

from api.models import Cloud, CloudRuntime
from api.models import CloudProperties
from api.models import IpamDnsProviderProfile
from api.models import SystemConfiguration
from api.models import VIMgrHostRuntime, \
     VIMgrVcenterRuntime, VIMgrDCRuntime
from avi.protobuf.cloud_connector_rpc_pb2 import (
    CloudConnectorService_Stub, cc_flavor_req, cc_internals_req,
    cc_zone_req, cc_req, cc_gc_req, cc_health_req,
    cc_securitygroup_req)
from avi.protobuf.cloud_connector_rpc_pb2 import (
    cc_autoscale_group_info_req,
    cc_autoscale_servers_info_req)
from avi.protobuf.cloud_connector_go_rpc_pb2 import (
    CloudConnectorGoService_Stub)
from avi.protobuf import cloud_objects_pb2 as cloud_objects_pb
from avi.protobuf import vi_mgr_common_pb2
from avi.protobuf.cloud_connector_message_pb2 import CloudConnectorStatus
from avi.protobuf import common_pb2, ipam_profile_pb2
from avi.protobuf.common_pb2 import CloudType
from avi.protobuf import options_pb2
from avi.protobuf import syserr_pb2
from avi.protobuf import se_bandwidth_type_pb2
from avi.protobuf.vi_mgr_cli_rpc_pb2 import VIMgrCliService_Stub
from django.core.exceptions import ObjectDoesNotExist

from avi.infrastructure.rpc_channel import RpcChannel
from avi.infrastructure.datastore import (Datastore, db_table_name_from_pb,
    DatastoreException)
from avi.util.protobuf import protobuf2dict
from avi.rest.views import (RetrieveView, UpdateView, CreateView)
from avi.util.views_constants import ERR_RC, SVR_RC
from avi.protobuf_json.protobuf_json import pb2json
from avi.infrastructure.rpc_channel import AviRpcController
from avi.protobuf.network_rpc_pb2 import NetworkMgrService_Stub
from avi.protobuf.syserr_pb2 import Syserr
from avi.rest.cloudconnector_go_services import registered_cloudconnector_go_services as registered_cloudconnector_go_services

log = logging.getLogger(__name__)

_MASK_F = ['password', 'secret_access_key', 'token', 'passwd', 'secret_key', 'authentication_token']
AWS_IPAMDNS_TYPES = [ipam_profile_pb2.IPAMDNS_TYPE_AWS, ipam_profile_pb2.IPAMDNS_TYPE_AWS_DNS]

def _mask_keys(msg):
    s = ''
    for i in msg:
        val = ''
        if not isinstance(i, int):
            continue
        if isinstance(msg[i], dict):
            val = _mask_keys(msg[i])
        elif isinstance(msg[i], list):
            for j in msg[i]:
                log.info('check j %s', j)
                val += _mask_keys(j)
        elif isinstance(msg[i], str) or isinstance(msg[i], unicode):
            mask = False
            if i in _MASK_F:
                mask = True
            else:
                for f in _MASK_F:
                    if f in i:
                        mask = True
                        break
            if mask:
                val = '******'
            else:
                val = '%s' % (msg[i])
        else:
            val = '%s' % (msg[i])
        s += '%s: \"%s\" ' % (i, val)
    return s

def _get_cloud(req_dict, vtype_chk=None, def_cloud=None, required=True):
    cc_obj  = None
    rsp_obj = None
    try:
        uuid = req_dict.get('uuid')
        name = req_dict.get('cloud', def_cloud)
        if not uuid:
            uuid = req_dict.get('slug')
        if uuid:
            cc_obj = Cloud.objects.get(uuid=uuid)
        elif name:
            cc_obj = Cloud.objects.get(name=name, tenant_ref__name='admin')
        if cc_obj:
            cc_obj = cc_obj.protobuf(decrypt=True)
            if vtype_chk and cc_obj.vtype != vtype_chk:
                msg = 'Cloud %s %s is not an %s cloud' % (cc_obj.name, cc_obj.uuid, CloudType.Name(vtype_chk))
                raise Exception(msg)
        elif uuid or name:
            raise Exception('No cloud found with %s %s', uuid, name)
        elif required:
            raise Exception('No cloud parameter provided')
    except Exception as e:
        rsp = {'result': str(e)}
        ret = 404
        rsp_obj = Response(data=rsp, status=ret)
    return (cc_obj, rsp_obj)

def _update_ipam_params(params):
    ipam_uuid = params.get('ipamdnsprovider_uuid')
    ipam_pb   = None
    if ipam_uuid:
        ipam_pb = IpamDnsProviderProfile.objects.get(uuid=ipam_uuid).protobuf(decrypt=True)
    if ipam_pb:
        if ipam_pb.type in AWS_IPAMDNS_TYPES:
            params = copy.deepcopy(params)
            _update_aws_params(params, ipam_pb.aws_profile, ipam_pb.proxy_configuration)
        elif ipam_pb.type in [ipam_profile_pb2.IPAMDNS_TYPE_AZURE, ipam_profile_pb2.IPAMDNS_TYPE_AZURE_DNS]:
            _update_azure_params(params, ipam_pb.azure_profile)
    return (ipam_pb, params)

def _update_azure_cloud_params(params, azure_cfg):
    if not azure_cfg:
        return

    params['cloud_credentials_uuid'] = azure_cfg.cloud_credentials_uuid
    if not azure_cfg.cloud_credentials_uuid:
        # Credentials not configured for Azure. Using MSI authentication
        params['is_azure_msi'] = True
    params['resource_group'] = azure_cfg.resource_group
    params['vnet_id'] = azure_cfg.network_info[0].virtual_network_id
    params['subscription_id'] = azure_cfg.subscription_id
    params['location'] = azure_cfg.location

def _update_gcp_params(params, gcp_cfg):
    if not gcp_cfg:
        return
    params['cloud_credentials_uuid'] = gcp_cfg.cloud_credentials_uuid
    params['region'] = gcp_cfg.region_name
    params['project'] = gcp_cfg.se_project_id

def _update_azure_params(params, azure_cfg):
    if not azure_cfg:
        return
    if azure_cfg.HasField('azure_userpass'):
        params['username'] = azure_cfg.azure_userpass.username
        params['tenant_name'] = azure_cfg.azure_userpass.tenant_name
        params['password'] = azure_cfg.azure_userpass.password
    elif azure_cfg.HasField('azure_serviceprincipal'):
        params['application_id'] = azure_cfg.azure_serviceprincipal.application_id
        params['authentication_token'] = azure_cfg.azure_serviceprincipal.authentication_token
        params['tenant_id'] = azure_cfg.azure_serviceprincipal.tenant_id
    params['resource_group'] = azure_cfg.resource_group
    params['vnet_id'] = azure_cfg.virtual_network_ids[0]
    params['subscription_id'] = azure_cfg.subscription_id

def _update_aws_params(params, cfg_obj, proxy_obj):
    akey = None
    skey = None
    role = None
    assume = None
    region = None
    vpc_id = None
    if cfg_obj:
        if cfg_obj.HasField('region'):
            region = cfg_obj.region
        if cfg_obj.HasField('vpc_id'):
            vpc_id = cfg_obj.vpc_id
        if cfg_obj.HasField('use_iam_roles'):
            role = cfg_obj.use_iam_roles
        if not role:
            if cfg_obj.HasField('access_key_id'):
                akey = cfg_obj.access_key_id
            if cfg_obj.HasField('secret_access_key'):
                skey = cfg_obj.secret_access_key
        if hasattr(cfg_obj, 'iam_assume_role') and cfg_obj.HasField('iam_assume_role'):
            assume = cfg_obj.iam_assume_role
    (pxhost, pxport, pxuser, pxpass) = (None, None, None, None)
    if proxy_obj and proxy_obj.HasField('host') and proxy_obj.HasField('port'):
        pxhost = proxy_obj.host
        pxport = proxy_obj.port
        pxuser = proxy_obj.username
        pxpass = proxy_obj.password

    # update params
    if 'use_iam_roles' not in params:
        params['use_iam_roles'] = role
    if not params.get('use_iam_roles'):
        if 'username' not in params and akey:
            params['username'] = akey
        if 'password' not in params and skey:
            params['password'] = skey
    else:
        params.pop('access_key_id', None)
        params.pop('secret_access_key', None)
        params.pop('username', None)
        params.pop('password', None)
    if 'proxy_host' not in params and pxhost:
        params['proxy_host'] = pxhost
    if 'proxy_port' not in params and pxport:
        params['proxy_port'] = pxport
    if 'proxy_user' not in params and pxuser:
        params['proxy_user'] = pxuser
    if 'proxy_pass' not in params and pxpass:
        params['proxy_pass'] = pxpass
    if 'iam_assume_role' not in params:
        params['iam_assume_role'] = assume
    if 'region' not in params and region:
        params['region'] = region
    if 'vpc' not in params and vpc_id:
        params['vpc'] = vpc_id
    return

def _update_cloud_params(params, vtype):
    cc_obj, rsp_obj = _get_cloud(params, vtype_chk=vtype, required=False)
    if not cc_obj:
        return None
    if vtype == common_pb2.CLOUD_AWS:
        _update_aws_params(params, cc_obj.aws_configuration, cc_obj.proxy_configuration)
    elif vtype == common_pb2.CLOUD_AZURE:
        _update_azure_cloud_params(params, cc_obj.azure_configuration)
    elif vtype == common_pb2.CLOUD_GCP:
        _update_gcp_params(params, cc_obj.gcp_configuration)
    elif vtype == common_pb2.CLOUD_OPENSTACK:
        os_cfg = cc_obj.openstack_configuration
        user   = None
        passwd = None
        kshost = None
        ksurl  = None
        tname  = None
        use_int_ep = False
        vsd_user   = None
        vsd_passwd = None
        if os_cfg.HasField('username'):
            user   = os_cfg.username
        if os_cfg.HasField('password'):
            passwd = os_cfg.password
        if os_cfg.HasField('keystone_host'):
            kshost = os_cfg.keystone_host
        if os_cfg.HasField('auth_url'):
            ksurl  = os_cfg.auth_url
        if os_cfg.HasField('admin_tenant'):
            tname  = os_cfg.admin_tenant
        if os_cfg.HasField('use_internal_endpoints'):
            use_int_ep = os_cfg.use_internal_endpoints
        if os_cfg.HasField('nuage_vsd_host'):
            if os_cfg.HasField('nuage_password'):
                vsd_passwd = os_cfg.nuage_password
            if os_cfg.HasField('nuage_username'):
                vsd_user = os_cfg.nuage_username
        # update params
        if 'username' not in params and user:
            params['username'] = user
        if 'password' not in params and passwd:
            params['password'] = passwd
        if 'keystone_host' not in params and kshost:
            params['keystone_host'] = kshost
        if 'auth_url' not in params and ksurl:
            params['auth_url'] = ksurl
        if 'tenant_uuid' not in params and tname:
            params['tenant_name'] = tname
        if 'use_internal_endpoints' not in params:
            params['use_internal_endpoints'] = use_int_ep
        # update nuage params
        if 'vsd_host' in params:
            if 'vsd_password' not in params:
                params['vsd_password'] = vsd_passwd
            if 'vsd_username' not in params:
                params['vsd_username'] = vsd_user
    elif vtype == common_pb2.CLOUD_CLOUDSTACK:
        cs_cfg = cc_obj.cloudstack_configuration
        akey   = None
        skey   = None
        apiurl = None
        if cs_cfg.HasField('access_key_id'):
            akey = cs_cfg.access_key_id
        if cs_cfg.HasField('secret_access_key'):
            skey = cs_cfg.secret_access_key
        if cs_cfg.HasField('api_url'):
            apiurl = cs_cfg.api_url
        # update params
        if 'access_key' not in params and akey:
            params['access_key'] = akey
        if 'secret_key' not in params and skey:
            params['secret_key'] = skey
        if 'api_url' not in params and apiurl:
            params['api_url'] = apiurl
    elif vtype == common_pb2.CLOUD_VCA:
        vca_cfg = cc_obj.vca_configuration
        user    = None
        passwd  = None
        inst    = None
        vdc     = None
        if vca_cfg.HasField('vca_username'):
            user   = vca_cfg.vca_username
        if vca_cfg.HasField('vca_password'):
            passwd = vca_cfg.vca_password
        if vca_cfg.HasField('vca_instance'):
            inst   = vca_cfg.vca_instance
        if vca_cfg.HasField('vca_vdc'):
            vdc    = vca_cfg.vca_vdc
        # update params
        if 'instance' not in params and inst:
            params['instance'] = inst
        if 'username' not in params and user:
            params['username'] = user
        if 'password' not in params and passwd:
            params['password'] = passwd
        if 'vdc' not in params and vdc:
            params['vdc'] = vdc
    return cc_obj

def _get_proxy(params):
    (pxhost, pxport, pxuser, pxpass) = (None, None, None, None)
    if 'proxy_host' in params and 'proxy_port' in params:
        pxhost = params.get('proxy_host')
        pxport = params.get('proxy_port')
        pxuser = params.get('proxy_user')
        pxpass = params.get('proxy_pass')
    if not pxhost:
        proxy = SystemConfiguration.objects.get().protobuf().proxy_configuration
        if proxy.host and proxy.port:
            pxhost = proxy.host
            pxport = proxy.port
            pxuser = proxy.username
            pxpass = proxy.password
    return (pxhost, pxport, pxuser, pxpass)

class CCFlavorsView(RetrieveView):
    def get(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        rsp  = 'GET invoked with args request %s args %s kwargs %s' % (request.QUERY_PARAMS, args, kwargs)
        log.info(rsp)
        (cc_obj, rsp_obj) = _get_cloud(kwargs)
        if rsp_obj:
            return rsp_obj
        req = cc_flavor_req()
        req.cc_id = cc_obj.uuid
        params = request.QUERY_PARAMS
        if 'search' in params:
            req.search = params['search']
        else:
            cc_props = CloudProperties.objects.get().protobuf()
            for cc in cc_props.info:
                if cc.vtype == cc_obj.vtype and cc.HasField('flavor_regex_filter'):
                    req.search = cc.flavor_regex_filter
        if 'tenant_uuid' in params:
            req.tenant_uuid = params['tenant_uuid']
        else:
            req.tenant_uuid = self.tenant.uuid
        if 'show_only_recommended' in params and params['show_only_recommended'].lower() == 'true':
            req.show_only_recommended = True
        elif 'show_only_recommended' in params and params['show_only_recommended'].lower() == 'false':
            req.show_only_recommended = False
        if 'se_usage_type' in params and 'license_type' in params:
            if params['license_type'] == 'LIC_BACKEND_SERVERS':
                req.license_type = options_pb2.LIC_BACKEND_SERVERS
            elif params['license_type'] == 'LIC_SOCKETS':
                req.license_type = options_pb2.LIC_SOCKETS
            elif params['license_type'] == 'LIC_CORES':
                req.license_type = options_pb2.LIC_CORES
            elif params['license_type'] == 'LIC_HOSTS':
                req.license_type = options_pb2.LIC_HOSTS
            elif params['license_type'] == 'LIC_SE_BANDWIDTH':
                req.license_type = options_pb2.LIC_SE_BANDWIDTH
            elif params['license_type'] == 'LIC_METERED_SE_BANDWIDTH':
                req.license_type = options_pb2.LIC_METERED_SE_BANDWIDTH

            if params['se_usage_type'] == "SE_BANDWIDTH_UNLIMITED":
                req.se_usage_type = se_bandwidth_type_pb2.SE_BANDWIDTH_UNLIMITED
            elif params['se_usage_type'] == "SE_BANDWIDTH_25M":
                req.se_usage_type = se_bandwidth_type_pb2.SE_BANDWIDTH_25M
            elif params['se_usage_type'] == "SE_BANDWIDTH_200M":
                req.se_usage_type = se_bandwidth_type_pb2.SE_BANDWIDTH_200M
            elif params['se_usage_type'] == "SE_BANDWIDTH_1000M":
                req.se_usage_type = se_bandwidth_type_pb2.SE_BANDWIDTH_1000M
            elif params['se_usage_type'] == "SE_BANDWIDTH_10000M":
                req.se_usage_type = se_bandwidth_type_pb2.SE_BANDWIDTH_10000M
        if 'private' in params:
            req.private = True if params['private'].lower() == 'true' else False
        if cc_obj.vtype in registered_cloudconnector_go_services:
            rpc_rsp = CloudConnectorGoService_Stub(RpcChannel()).\
                  cc_get_flavors(RpcController(), req)
        else:
            rpc_rsp = CloudConnectorService_Stub(RpcChannel()).\
                  cc_get_flavors(RpcController(), req)
        if rpc_rsp:
            if rpc_rsp.ret_status == syserr_pb2.SYSERR_SUCCESS:
                ret = 200
                rsp = protobuf2dict(rpc_rsp)
                rsp_obj = {'count':len(rsp.get('flavors')), 'results':rsp.get('flavors')}
                rsp = rsp_obj
            else:
                log.error('rsp err %d status %s for cc_get_flavors',
                          rpc_rsp.ret_status, rpc_rsp.ret_string)
                rsp = {'result': rpc_rsp.ret_string}
                ret = ERR_RC
        else:
            log.error('null rsp for cc_get_flavors')
            rsp = {'result': 'failed'}
            ret = SVR_RC
        return Response(data=rsp, status=ret)


class CCInternalsView(RetrieveView):
    def get(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)

        rsp  = 'GET invoked with args request %s args %s kwargs %s' % (request.QUERY_PARAMS, args, kwargs)
        log.info(rsp)
        (cc_obj, rsp_obj) = _get_cloud(kwargs, required=False)
        if rsp_obj:
            return rsp_obj
        req = cc_internals_req()
        if cc_obj:
            # Restrict non cloud-connector cloud to get cloud nternals
            if cc_obj.vtype in [common_pb2.CLOUD_NONE, common_pb2.CLOUD_VCENTER]:
                ret = ERR_RC
                rsp = {'result' : 'Not supported for Vcenter and no access clouds'}
                return Response(data=rsp, status=ret)
            req.cc_id = cc_obj.uuid
        rpc_rsp = CloudConnectorService_Stub(RpcChannel()).\
              cc_get_internals(RpcController(), req)
        if rpc_rsp:
            if rpc_rsp.ret_status == syserr_pb2.SYSERR_SUCCESS:
                ret = 200
                rsp = protobuf2dict(rpc_rsp)
            else:
                log.error('rsp err %d status %s for cc_get_internals',
                          rpc_rsp.ret_status, rpc_rsp.ret_string)
                rsp = {'result': rpc_rsp.ret_string}
                ret = ERR_RC
        else:
            log.error('null rsp for cc_get_internals')
            rsp = {'result': 'failed'}
            ret = SVR_RC

        return Response(data=rsp, status=ret)


class CCAvailabilityZonesView(RetrieveView):
    def _aws_revalidate_zones(self, cc_obj, zones):
        cc_zones = cc_obj.aws_configuration.zones
        cfg_zones = [z.availability_zone for z in cc_zones if z.mgmt_network_name]
        for z in zones:
            if z.name not in cfg_zones:
                z.available = False
        return

    def get(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)

        rsp  = 'GET invoked with args request %s args %s kwargs %s' % (request.QUERY_PARAMS, args, kwargs)
        log.info(rsp)
        params = request.QUERY_PARAMS
        (cc_obj, rsp_obj) = _get_cloud(kwargs)
        if rsp_obj:
            return rsp_obj
        req = cc_zone_req()
        req.cc_id = cc_obj.uuid
        if params:
            if cc_obj.vtype == common_pb2.CLOUD_OPENSTACK:
                req.search  = params.get('search', 'nova-compute')
                tmp = params.get('unavail')
                req.unavail = True if (tmp and tmp.lower() == 'true') else False
                tmp = params.get('detail')
                req.detail  = True if (tmp and tmp.lower() == 'true') else False
        if cc_obj.vtype == common_pb2.CLOUD_AWS:
            rpc_rsp = CloudConnectorGoService_Stub(RpcChannel()).\
                  cc_get_zones(RpcController(), req)
        else:
            rpc_rsp = CloudConnectorService_Stub(RpcChannel()).\
                  cc_get_zones(RpcController(), req)
        if rpc_rsp:
            if cc_obj.vtype == common_pb2.CLOUD_AWS:
                self._aws_revalidate_zones(cc_obj, rpc_rsp.zones)
            if rpc_rsp.ret_status == syserr_pb2.SYSERR_SUCCESS:
                ret = 200
                rsp = protobuf2dict(rpc_rsp)
            else:
                log.error('rsp err %d status %s for cc_get_zones',
                          rpc_rsp.ret_status, rpc_rsp.ret_string)
                rsp = {'result': rpc_rsp.ret_string}
                ret = ERR_RC
        else:
            log.error('null rsp for cc_get_zones')
            rsp = {'result': 'failed'}
            ret = SVR_RC
        return Response(data=rsp, status=ret)


class CCGarbageCollView(CreateView, UpdateView):
    def put(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)

        rsp  = 'PUT invoked with args request %s args %s kwargs %s' % (request.QUERY_PARAMS, args, kwargs)
        log.info(rsp)
        params = request.QUERY_PARAMS
        if not params:
            params = request.DATA
        (cc_obj, rsp_obj) = _get_cloud(kwargs)
        if rsp_obj:
            return rsp_obj
        req = cc_gc_req()
        req.cc_id = cc_obj.uuid
        if params:
            req.force = (str(params.get('force','False')).lower() == 'true')
            req.cleanup = (str(params.get('cleanup','False')).lower() == 'true')
        rpc_rsp = CloudConnectorService_Stub(RpcChannel()).\
              cc_garbage_collect(RpcController(), req)
        if rpc_rsp:
            if rpc_rsp.ret_status == syserr_pb2.SYSERR_SUCCESS:
                ret = 200
                rsp = protobuf2dict(rpc_rsp)
            else:
                log.error('rsp err %d status %s for cc_garbage_collect' %
                          (rpc_rsp.ret_status, rpc_rsp.ret_string))
                rsp = {'result': rpc_rsp.ret_string}
                ret = ERR_RC
        else:
            log.error('null rsp for cc_garbage_collect')
            rsp = {'result': 'failed'}
            ret = SVR_RC
        return Response(data=rsp, status=ret)

    def post(self, request, *args, **kwargs):
        return self.put(request, *args, **kwargs)


class CloudStatusView(RetrieveView):
    datastore = None

    def _get_vcenter_status(self, cloud_uuid):
        req = vi_mgr_common_pb2.VcenterCloudStatusReq()
        req.cloud_uuid = cloud_uuid
        rsp = VIMgrCliService_Stub(RpcChannel()).\
                Vcenterstatus(RpcController(), req)
        return rsp.resource.vcenter_cloud_status_rsp

    def _get_cc_status(self, cloud_uuid):
        req = cc_req()
        req.quiet = True
        if cloud_uuid:
            req.cc_id = cloud_uuid
        rpc_rsp = CloudConnectorService_Stub(RpcChannel()).\
                    cc_get_status(RpcController(), req)
        return rpc_rsp

    def _parse_cc_status(self, rsp_pb):
        state = None
        reason = ''
        if not rsp_pb.agents:
            log.error('Cloud connector RPC returns empty "agents" list: %s',
                rsp_pb.ret_string)
            state = cloud_objects_pb.CLOUD_STATE_UNKNOWN
            reason = 'Cannot connect to Cloud Connector: %s' % rsp_pb.ret_string
            return state, reason
        agent_pb = rsp_pb.agents[0]
        state = agent_pb.state
        reason = agent_pb.reason
        return state, reason

    def _get_ds_status(self, uuid):
        if not self.datastore:
            self.datastore = Datastore()
        pb_name = db_table_name_from_pb(CloudConnectorStatus())
        try:
            ds_data = self.datastore.get(pb_name, uuid)
        except DatastoreException as e:
            return cloud_objects_pb.CLOUD_STATE_UNKNOWN, "%s" % e

        cc_status = ds_data.get('config')

        return cc_status.detail.state, cc_status.detail.reason

    def get(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        uuid = kwargs.get('slug')
        cloud_pb = Cloud.objects.get(uuid=uuid).protobuf()

        status_pb = cloud_objects_pb.CloudStatus()
        if not self.datastore:
            self.datastore = Datastore()
        sys_conf_ds = self.datastore.get('systemconfiguration', 'default')
        sys_conf_runtime = sys_conf_ds['runtime']

        if sys_conf_runtime and sys_conf_runtime.sys_config_in_progress:
            status_pb.state = cloud_objects_pb.CLOUD_STATE_IN_PROGRESS
            status_pb.reason = 'System Configuration in progress'
        elif cloud_pb.vtype == common_pb2.CLOUD_NONE:
            status_pb.state = cloud_objects_pb.CLOUD_STATE_PLACEMENT_READY

        elif cloud_pb.vtype == common_pb2.CLOUD_VCENTER:
            rpc_rsp = self._get_vcenter_status(uuid)
            status_pb.state = rpc_rsp.state
            status_pb.reason = rpc_rsp.reason
            if status_pb.state == cloud_objects_pb.CLOUD_STATE_PLACEMENT_READY:
                try:
                    cc_runtime_pb = CloudRuntime.objects.get(uuid=uuid).protobuf()
                    if not cc_runtime_pb.network_sync_complete:
                        status_pb.state = cloud_objects_pb.CLOUD_STATE_IN_PROGRESS
                        status_pb.reason = 'Network Sync in progress'
                except ObjectDoesNotExist:
                    pass

        else:
            current = kwargs.get('current') or 'current' in request.QUERY_PARAMS
            if current:
                cc_pb = self._get_cc_status(uuid)
                status_pb.state, status_pb.reason = self._parse_cc_status(cc_pb)
            else:
                status_pb.state, status_pb.reason = self._get_ds_status(uuid)

        data = protobuf2dict(status_pb)
        return Response(data=data)


class CCHealthCheckView(RetrieveView, CreateView, UpdateView):
    def get(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)

        rsp  = 'GET invoked with args request %s args %s kwargs %s' % (request.QUERY_PARAMS, args, kwargs)
        log.info(rsp)
        (cc_obj, rsp_obj) = _get_cloud(kwargs)
        if rsp_obj:
            return rsp_obj
        req = cc_internals_req()
        req.cc_id = cc_obj.uuid
        req.quiet = True
        rpc_rsp = CloudConnectorService_Stub(RpcChannel()).\
              cc_get_internals(RpcController(), req)
        if rpc_rsp:
            if rpc_rsp.ret_status == syserr_pb2.SYSERR_SUCCESS:
                ret = 200
                rsp = None
                if rpc_rsp.agents and rpc_rsp.agents[0].HasField('health'):
                    rsp = protobuf2dict(rpc_rsp.agents[0].health)
            else:
                log.error('rsp err %d status %s for cc_get_internals',
                          rpc_rsp.ret_status, rpc_rsp.ret_string)
                rsp = {'result': rpc_rsp.ret_string}
                ret = ERR_RC
        else:
            log.error('null rsp for cc_get_internals')
            rsp = {'result': 'failed'}
            ret = SVR_RC

        return Response(data=rsp, status=ret)

    def put(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)

        rsp  = 'PUT invoked with args request %s args %s kwargs %s' % (request.QUERY_PARAMS, args, kwargs)
        log.info(rsp)
        params = request.QUERY_PARAMS
        if not params:
            params = request.DATA
        (cc_obj, rsp_obj) = _get_cloud(kwargs)
        if rsp_obj:
            return rsp_obj
        req = cc_health_req()
        req.cc_id = cc_obj.uuid
        if params:
            req.extensions = (str(params.get('extensions','False')).lower() == 'true')
            req.ssh_checks = (str(params.get('ssh_checks','False')).lower() == 'true')
        rpc_rsp = CloudConnectorService_Stub(RpcChannel()).\
              cc_health_check(RpcController(), req)
        if rpc_rsp:
            if rpc_rsp.ret_status == syserr_pb2.SYSERR_SUCCESS:
                ret = 200
                rsp = protobuf2dict(rpc_rsp)
            else:
                log.error('rsp err %d status %s for cc_garbage_collect' %
                          (rpc_rsp.ret_status, rpc_rsp.ret_string))
                rsp = {'result': rpc_rsp.ret_string}
                ret = ERR_RC
        else:
            log.error('null rsp for cc_health_check')
            rsp = {'result': 'failed'}
            ret = SVR_RC
        return Response(data=rsp, status=ret)

    def post(self, request, *args, **kwargs):
        return self.put(request, *args, **kwargs)

class CCSecurityGroupsView(RetrieveView):
    def get(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        rsp  = 'GET invoked with args request %s args %s kwargs %s' % (request.QUERY_PARAMS, args, kwargs)
        log.info(rsp)
        (cc_obj, rsp_obj) = _get_cloud(kwargs)
        if rsp_obj:
            return rsp_obj
        req = cc_securitygroup_req()
        req.cc_id = cc_obj.uuid
        params = request.QUERY_PARAMS
        if 'search' in params:
            req.search = params['search']
        if 'tenant_uuid' in params:
            req.tenant_uuid = params['tenant_uuid']
        else:
            req.tenant_uuid = self.tenant.uuid
        if cc_obj.vtype == common_pb2.CLOUD_AWS:
            rpc_rsp = CloudConnectorGoService_Stub(RpcChannel()).\
                  cc_get_securitygroups(RpcController(), req)
        else:
            rpc_rsp = CloudConnectorService_Stub(RpcChannel()).\
                  cc_get_securitygroups(RpcController(), req)
        if rpc_rsp:
            if rpc_rsp.ret_status == syserr_pb2.SYSERR_SUCCESS:
                ret = 200
                rsp = protobuf2dict(rpc_rsp)
            else:
                log.error('rsp err %d status %s for cc_get_securitygroups',
                          rpc_rsp.ret_status, rpc_rsp.ret_string)
                rsp = {'result': rpc_rsp.ret_string}
                ret = ERR_RC
        else:
            log.error('null rsp for cc_get_securitygroups')
            rsp = {'result': 'failed'}
            ret = SVR_RC
        return Response(data=rsp, status=ret)



class CCAutoscaleGroupListView(RetrieveView):
    """
    This view returns the list of autoscale groups that it learned in the
    cloud.
    """
    def get(self, request, *args, **kwargs):
        """
        :param request: django request object
        :param args: from the views urls
        :param kwargs:
        :return: List of autoscale group info
        """
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)

        log.info('GET invoked with args request %s args %s kwargs %s',
                 request.QUERY_PARAMS, args, kwargs)
        try:
            req = cc_autoscale_group_info_req()
            (cc_obj, rsp_obj) = _get_cloud(kwargs)
            req.cc_id = cc_obj.uuid

            group_name = request.QUERY_PARAMS.get('group_name', '').strip()
            if group_name:
                req.group_name = group_name
            include_servers = str(request.QUERY_PARAMS.get(
                    'include_servers', 'false')).strip().lower()
            req.include_servers = include_servers == 'true'
            if req.include_servers and not group_name:
                rsp = {'rc: include servers not allowed without group name'}
                ret = SVR_RC
                return Response(data=rsp, status=ret)

            rpc_rsp = CloudConnectorService_Stub(RpcChannel()).\
                cc_get_autoscale_group_info(RpcController(), req)

            if rpc_rsp and rpc_rsp.ret_status == syserr_pb2.SYSERR_SUCCESS:
                rsp = {'count': len(rpc_rsp.group_info),
                       'results': []}
                for group_info in rpc_rsp.group_info:
                    json_group_info = protobuf2dict(group_info)
                    json_group_info['name'] = json_group_info['group_name']
                    rsp['results'].append(json_group_info)
                ret = 200
            else:
                log.error('req %s rsp %s', req, rpc_rsp)
                rsp = {'rc: %s %s' % (Syserr.DESCRIPTOR.values_by_number[
                        rpc_rsp.ret_status].name, rpc_rsp.ret_string)}
                ret = SVR_RC
        except:
            log.error('%s', traceback.format_exc())
            raise
        return Response(data=rsp, status=ret)


class CCAutoscaleGroupView(RetrieveView):
    """
    This view returns a single autoscale group information
    cloud.
    """
    def get(self, request, *args, **kwargs):
        """
        :param request: django request object
        :param args: from the views urls
        :param kwargs:
        :return: List of autoscale group info
        """
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)

        log.info('GET invoked with args request %s args %s kwargs %s',
                 request.QUERY_PARAMS, args, kwargs)
        try:
            req = cc_autoscale_group_info_req()
            (cc_obj, rsp_obj) = _get_cloud(kwargs)
            req.cc_id = cc_obj.uuid

            group_name = kwargs['group_name']
            if group_name:
                req.group_name = group_name
            include_servers = str(request.QUERY_PARAMS.get(
                    'include_servers', 'false')).strip().lower()
            req.include_servers = include_servers == 'true'
            if req.include_servers and not group_name:
                rsp = {'rc: include servers not allowed without group name'}
                ret = SVR_RC
                return Response(data=rsp, status=ret)

            rpc_rsp = CloudConnectorService_Stub(RpcChannel()).\
                cc_get_autoscale_group_info(RpcController(), req)

            if (rpc_rsp and rpc_rsp.ret_status == syserr_pb2.SYSERR_SUCCESS and
                    rpc_rsp.group_info):
                group_info = rpc_rsp.group_info[0]
                rsp = protobuf2dict(group_info)
                ret = 200
            else:
                log.error('req %s rsp %s', req, rpc_rsp)
                rsp = {'rc: %s %s' % (Syserr.DESCRIPTOR.values_by_number[
                        rpc_rsp.ret_status].name, rpc_rsp.ret_string)}
                ret = SVR_RC
        except:
            log.error('%s', traceback.format_exc())
            raise
        return Response(data=rsp, status=ret)


class CCAutoscaleGroupServersListView(RetrieveView):
    """
    This view returns the list of servers in a autoscale groups within a
    cloud.
    """
    def get(self, request, *args, **kwargs):
        """
        :param request: django request object
        :param args: from the views urls
        :param kwargs:
        :return: List of autoscale group info
        """
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)

        log.info('GET invoked with args request %s args %s kwargs %s',
                 request.QUERY_PARAMS, args, kwargs)
        try:
            req = cc_autoscale_servers_info_req()
            (cc_obj, rsp_obj) = _get_cloud(kwargs)
            req.cc_id = cc_obj.uuid
            req.group_names.append(kwargs['group_name'])
            rpc_rsp = CloudConnectorService_Stub(RpcChannel()).\
                cc_get_autoscale_servers_info(RpcController(), req)
            if rpc_rsp and rpc_rsp.ret_status == syserr_pb2.SYSERR_SUCCESS:
                rsp = {'count': len(rpc_rsp.servers),
                       'results': []}
                for server in rpc_rsp.servers:
                    json_server = protobuf2dict(server)
                    json_server['name'] = json_server['hostname']
                    rsp['results'].append(json_server)
                ret = 200
            else:
                log.error('req %s rsp %s', req, rpc_rsp)
                rsp = {'rc: %s %s' % (Syserr.DESCRIPTOR.values_by_number[
                        rpc_rsp.ret_status].name, rpc_rsp.ret_string)}
                ret = SVR_RC
        except:
            log.error('%s', traceback.format_exc())
            raise
        return Response(data=rsp, status=ret)

class CCCloudDiagViews(RetrieveView):
    def retrieveVcenterCloudState(self, vcenter_pb):
        state = vcenter_pb.inventory_state
        #log.info("state ->" + str(state))
        if (state == vi_mgr_common_pb2.VCENTER_DISCOVERY_RETRIEVING_DC or \
            state == vi_mgr_common_pb2.VCENTER_DISCOVERY_WAITING_DC or \
            state == vi_mgr_common_pb2.VCENTER_DISCOVERY_ONGOING or
            state == vi_mgr_common_pb2.VCENTER_DISCOVERY_DELETING_VCENTER or
            state == vi_mgr_common_pb2.VCENTER_DISCOVERY_RETRIEVING_NW or
            state == vi_mgr_common_pb2.VCENTER_DISCOVERY_RESYNCING):
            return cloud_objects_pb.CLOUD_STATE_IN_PROGRESS
        if state == vi_mgr_common_pb2.VCENTER_DISCOVERY_COMPLETE_NO_MGMT_NW:
            return cloud_objects_pb.CLOUD_STATE_IN_PROGRESS
        if state == vi_mgr_common_pb2.VCENTER_DISCOVERY_COMPLETE:
            return cloud_objects_pb.CLOUD_STATE_PLACEMENT_READY
        return cloud_objects_pb.CLOUD_STATE_FAILED

    def fillVcenterHostDiagInfo(self, diag_resp):

        hosts_poweredDown = \
            VIMgrHostRuntime.objects.filter(json_data__powerstate='poweredDown')
        for host in hosts_poweredDown:
            diag_host = diag_resp.hosts.add()
            diag_host.name = host.name
            diag_host.powerstate = False

        hosts_maintenance_mode = \
            VIMgrHostRuntime.objects.filter(json_data__maintenance_mode=True)
        for host in hosts_maintenance_mode:
            diag_host = next((h for h in diag_resp.hosts if h.name==host.name), None)
            if not diag_host:
                diag_host = diag_resp.hosts.add()
                diag_host.name = host.name
            diag_host.maintenance_mode = True

        hosts_connection_state = \
            VIMgrHostRuntime.objects.filter(json_data__connection_state='disconnected')
        for host in hosts_connection_state:
            diag_host = next((h for h in diag_resp.hosts if h.name==host.name), None)
            if not diag_host:
                diag_host = diag_resp.hosts.add()
                diag_host.name = host.name
            diag_host.connection_state = False

        hosts_cntlr_accessible = \
            VIMgrHostRuntime.objects.filter(json_data__cntlr_accessible=False)
        for host in hosts_cntlr_accessible:
            diag_host = next((h for h in diag_resp.hosts if h.name==host.name), None)
            if not diag_host:
                diag_host = diag_resp.hosts.add()
                diag_host.name = host.name
            diag_host.cntlr_accessible = False

        hosts_quarantined = \
            VIMgrHostRuntime.objects.filter(json_data__quarantined=True)
        for host in hosts_quarantined:
            diag_host = next((h for h in diag_resp.hosts if h.name==host.name), None)
            if not diag_host:
                diag_host = diag_resp.hosts.add()
                diag_host.name = host.name
            diag_host.quarantined = True

        diag_resp.total_hosts = VIMgrHostRuntime.objects.count()
        diag_resp.errored_hosts = len(diag_resp.hosts)
        return

    def retrieveNetworkDiag(self, cloud_uuid):
        nw_diag_req = vi_mgr_common_pb2.NetworkManagerDiagReq()
        nw_diag_req.cloud_uuid = cloud_uuid
        nw_diag_req.summary = False
        #log.info(str(nw_diag_req))
        try:
            nw_diag_rsp = NetworkMgrService_Stub(RpcChannel()).NetworkDiag(\
                          AviRpcController(timeout=20), nw_diag_req)
        except Exception as e:
            log.error('Exception %s in retrieving network diag from network_mgr' % (e.args))
            return False, None
        #log.info(str(nw_diag_rsp))
        return nw_diag_rsp.success, nw_diag_rsp.networks


    def get(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        rsp  = 'GET invoked with args request %s args %s kwargs %s' % (request.QUERY_PARAMS, args, kwargs)
        #log.info(rsp)
        (cc_obj, rsp_obj) = _get_cloud(kwargs)
        if rsp_obj:
            return rsp_obj
        if cc_obj.vtype != common_pb2.CLOUD_VCENTER:
            rsp = {'result': 'Cloud not find vCenter Cloud'}
            ret = 404
            return Response(data=rsp, status=ret)

        cloud_uuid = cc_obj.uuid
        diag_resp = vi_mgr_common_pb2.VcenterInventoryDiagRsp()
        vcenters = VIMgrVcenterRuntime.objects.filter(cloud_ref__uuid=cloud_uuid)
        if len(vcenters):
            vc = vcenters[0]
        else:
            rsp = {'result': 'Cloud not found'}
            ret = 404
            return Response(data=rsp, status=ret)

        vc_pb = vc.protobuf()
        diag_resp.vcenter_url = vc_pb.vcenter_url
        if len(vc_pb.discovered_datacenter) == 1:
            dc_uuid = vc_pb.discovered_datacenter[0]
            try:
                dc = VIMgrDCRuntime.objects.get(uuid=dc_uuid)
            except Exception:
                log.error('Could not retrieve DC object for %s' \
                         %(dc_uuid))
                diag_resp.datacenter = dc_uuid
            else:
                diag_resp.datacenter = dc.protobuf().name
        diag_resp.state = self.retrieveVcenterCloudState(vc_pb)
        self.fillVcenterHostDiagInfo(diag_resp)
        success, networks = self.retrieveNetworkDiag(cloud_uuid)
        if success is True:
            rsp = pb2json(diag_resp)
            #log.info(str(rsp))
            ret = 200
            return Response(data=rsp, status=ret)

        if success is False and networks is None:
            rsp = pb2json(diag_resp)
            #log.info(str(rsp))
            ret = 200
            return Response(data=rsp, status=ret)

        diag_resp.networks.CopyFrom(networks)

        rsp = pb2json(diag_resp)
        #log.info(str(rsp))
        ret = 200
        return Response(data=rsp, status=ret)
