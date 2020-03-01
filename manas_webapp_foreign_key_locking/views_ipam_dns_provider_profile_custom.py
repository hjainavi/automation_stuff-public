
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

#pylint:  skip-file
from google.protobuf.service import RpcController

import copy
from infoblox import Infoblox
import logging
import ipaddress

from api.models import IpamDnsProviderProfile, Cloud
from rest_framework.response import Response

from avi.rest.views import (ListView, RetrieveView)
from avi.protobuf import common_pb2, syserr_pb2
from avi.protobuf.ipam_profile_pb2 import IpamDnsSubnetDomainList
from avi.protobuf_json.protobuf_json import pb2json
from avi.protobuf.options_pb2 import V4
from avi.protobuf.ipam_profile_pb2 import (IpamDnsType, IPAMDNS_TYPE_INFOBLOX,
        IPAMDNS_TYPE_AWS, IPAMDNS_TYPE_INTERNAL, IPAMDNS_TYPE_INTERNAL_DNS,
        IPAMDNS_TYPE_INFOBLOX_DNS, IPAMDNS_TYPE_AWS_DNS, IPAMDNS_TYPE_AZURE,
        IPAMDNS_TYPE_AZURE_DNS, IPAMDNS_TYPE_CUSTOM, IPAMDNS_TYPE_CUSTOM_DNS)
from avi.ipam.ipam_utils import (
        ipamdns_get_configured_domains,
        IpamDnsCustom)
from avi.protobuf.cloud_connector_rpc_pb2 import (CloudConnectorService_Stub,
    cc_dns_domain_req, cc_nw_runtime_req)
from avi.infrastructure.rpc_channel import RpcChannel
from avi.util.views_constants import ERR_RC, SVR_RC
from api.views_cloud_connector_custom import _mask_keys, _get_proxy, _update_aws_params
from api.views_aws_custom import _params_check, _get_credentials
from avi.util.aws_utils import aws_get_vpc_subnets, aws_get_vpc_domains
from avi.util.azure_utils import azure_get_zones
from api.views_azure_custom import _update_params as azure_update_params
from api.views_azure_custom import _get_credentials as get_azure_credentials

log = logging.getLogger(__name__)

REQUEST_TYPE_IPAM = 1
REQUEST_TYPE_DNS = 2
IPAMDNSTYPE_STRINGS = [t.name for t in IpamDnsType.DESCRIPTOR.values]

def _get_ipamdnstype_enum(type_str):
    return IpamDnsType.DESCRIPTOR.values_by_name[type_str].number

def _get_ipamdnstype_str(type_enum):
    return IpamDnsType.DESCRIPTOR.values_by_number[type_enum].name

def get_ipamdns_config(params, cfg_type, cloud=None):
    ipam_type = params.get('type', '')
    ipamdnsprov_uuid = params.get('ipamdnsprovider_uuid', '')
    provider = params.get('provider', 'False')
    provider = False if str(provider).lower() == 'false' else True
    auto_allocate_only = params.get('auto_allocate_only', False)
    if auto_allocate_only:
        provider = False

    if (ipam_type not in IPAMDNSTYPE_STRINGS and not ipamdnsprov_uuid and not cloud):
        raise Exception("type[%s] unsupported or not set" % ipam_type)

    ipam_enum = _get_ipamdnstype_enum(ipam_type) if ipam_type else 0
    provider_pb = None
    cloud_pb = None

    if cloud:
        log.info("cloud: %s", cloud.uuid)
        cloud_pb = cloud.protobuf()
        # overwrite params
        ipam_enum = None
        ipamdnsprov_uuid = None
        if cfg_type == REQUEST_TYPE_IPAM:
            if cloud_pb.vtype != common_pb2.CLOUD_AWS:
                ipamdnsprov_uuid = cloud_pb.ipam_provider_uuid
            else:
                ipam_enum = IPAMDNS_TYPE_AWS
        else: #REQUEST_TYPE_DNS
            if cloud_pb.dns_provider_uuid:
                ipamdnsprov_uuid = cloud_pb.dns_provider_uuid
            elif (cloud_pb.vtype == common_pb2.CLOUD_AWS and
                cloud_pb.aws_configuration.route53_integration):
                ipam_enum = IPAMDNS_TYPE_AWS_DNS
            elif (cloud_pb.vtype == common_pb2.CLOUD_AZURE and
                cloud_pb.azure_configuration.use_azure_dns):
                ipam_enum = IPAMDNS_TYPE_AZURE_DNS

    if ipamdnsprov_uuid:
        provider_pb = IpamDnsProviderProfile.objects.get(
                            uuid=ipamdnsprov_uuid).protobuf(decrypt=True)
        if provider_pb:
            ipam_enum = provider_pb.type
    else:
        provider = True

    creds = None
    if ipam_enum in [IPAMDNS_TYPE_INFOBLOX, IPAMDNS_TYPE_INFOBLOX_DNS]:
        addr = None
        username = password = None
        wapi_version = network_view = dns_view = None
        if provider_pb and provider_pb.HasField('infoblox_profile'):
            iblx_prof = provider_pb.infoblox_profile
            addr = iblx_prof.ip_address.addr
            username = iblx_prof.username
            password = iblx_prof.password
            wapi_version = iblx_prof.wapi_version
            network_view = iblx_prof.network_view
            dns_view = iblx_prof.dns_view
        # override if any
        addr = params.get('ip_address', addr)
        username = params.get('username', username)
        password = params.get('password', password)
        wapi_version = params.get('wapi_version', wapi_version) or '1.6'
        network_view = params.get('network_view', network_view) or 'default'
        dns_view = params.get('dns_view', dns_view) or 'default'
        creds = (addr, username, password, wapi_version, network_view, dns_view)
    elif ipam_enum in [IPAMDNS_TYPE_AWS, IPAMDNS_TYPE_AWS_DNS]:
        cfg_obj = None
        proxy_obj = None
        if provider_pb:
            cfg_obj = provider_pb.aws_profile
            proxy_obj = provider_pb.proxy_configuration
        elif cloud_pb:
            cfg_obj = cloud_pb.aws_configuration
            proxy_obj = cloud_pb.proxy_configuration
        creds = copy.deepcopy(params)
        _update_aws_params(creds, cfg_obj, proxy_obj)
    elif ipam_enum in [IPAMDNS_TYPE_CUSTOM, IPAMDNS_TYPE_CUSTOM_DNS]:
        creds = copy.deepcopy(params)
    return ipam_enum, creds, provider_pb, cloud_pb, provider


class IpamDnsProviderProfileNetworkList(ListView, RetrieveView):
    def _handle(self, request, params):
        ret = 200
        ipam_type, creds, ipam_pb, cloud_pb, provider = get_ipamdns_config(params,
            cfg_type=REQUEST_TYPE_IPAM, cloud=self.cloud)

        if not ipam_type:
            msg = "Ipam Type invalid or configuration not found in Avi"
            rsp = {'error': msg}
            return Response(rsp, status=ERR_RC)

        search = params.get('search', None)
        tenant = params.get('tenant', params.get('admin')) or self.tenant.uuid
        preferred_nw_type = params.get('preferred_nw_type', None)

        if ipam_type == IPAMDNS_TYPE_INFOBLOX:
            rsp = IpamDnsSubnetDomainList()
            ib_ip, user, pwd, wapi_v, nw_view, _ = creds
            log.info("Infoblox: get networks creds: %s", creds)
            if (ipam_pb and ipam_pb.HasField('infoblox_profile') and
                not ipam_pb.infoblox_profile.usable_subnets):
                provider = True
            if provider:
                try:
                    infoblox_nws = Infoblox.get_networks_in_view(ib_ip,
                                    user, pwd, wapi_v, nw_view)
                    infoblox_nws.sort()
                    for nw in infoblox_nws:
                        if search and search not in nw:
                            continue
                        nw_ip = str(ipaddress.ip_network(nw).network_address)
                        nw_prefix = ipaddress.ip_network(nw).prefixlen
                        nw_subnet = rsp.subnets.add()
                        nw_subnet.ip_addr.addr = nw_ip
                        nw_subnet.ip_addr.type = V4
                        nw_subnet.mask = nw_prefix
                except Exception as e:
                    err_str = str(e).lower()
                    rsp.error = err_str
                    if 'timed out' in err_str:
                        rsp.error = "Connection timedout to Infoblox at %s!"%ib_ip
                    elif 'refused' in err_str:
                        rsp.error = "Connection refused to Infoblox at %s!"%ib_ip
                    elif 'no route to host' in err_str:
                        rsp.error = "No route to Infoblox at %s!"%ib_ip
                    ret = SVR_RC
            elif ipam_pb and ipam_pb.HasField('infoblox_profile'):
                profile_snws = ipam_pb.infoblox_profile.usable_subnets
                rsp.subnets.extend([subnet for subnet in profile_snws
                    if not search or (search in subnet)])
            rsp = pb2json(rsp)
        elif ipam_type == IPAMDNS_TYPE_INTERNAL:
            # @todo
            pass
        elif ipam_type == IPAMDNS_TYPE_CUSTOM:
            log.info("CustomIPAM: get subnets => %s", creds)
            rsp = IpamDnsSubnetDomainList()
            if (ipam_pb and ipam_pb.HasField('custom_profile') and
                not ipam_pb.custom_profile.usable_subnets):
                provider = True
            if provider:
                cprof_uuid = creds.pop('customdnsprovider_uuid', None)
                if cprof_uuid:
                    cprof_params, cprof_ipam_mod = \
                            IpamDnsCustom.get_custom_profile(cprof_uuid)
                    cprof_params.update(creds)
                    try:
                        subnets = cprof_ipam_mod.GetSubnets(cprof_params)
                        subnets.sort()
                        for sn in subnets:
                            if search and search not in sn:
                                continue
                            sn_ip = str(ipaddress.ip_network(sn).network_address)
                            sn_prefix = ipaddress.ip_network(sn).prefixlen
                            sn = rsp.subnets.add()
                            sn.ip_addr.addr = sn_ip
                            sn.ip_addr.type = V4
                            sn.mask = sn_prefix
                    except Exception as e:
                        err_str = str(e).lower()
                        rsp.error = err_str
                        ret = SVR_RC
                else:
                    err_str = "Request has 'provider' mode set but "\
                            "no valid 'customdnsprovider_uuid' provided!"
                    rsp.error = err_str
                    ret = SVR_RC
            elif ipam_pb:
                profile_snws = ipam_pb.custom_profile.usable_subnets
                rsp.subnets.extend([subnet for subnet in profile_snws
                    if not search or (search in subnet)])
            else:
                ret = ERR_RC
                rsp.error = "Bad request, valid customdnsprovider_uuid "\
                        "or cloud_uuid required in request PARAMS."
            rsp = pb2json(rsp)
        elif ipam_type == IPAMDNS_TYPE_AWS:
            if (cloud_pb and cloud_pb.vtype == common_pb2.CLOUD_AWS):
                req = cc_nw_runtime_req()
                req.cc_id  = cloud_pb.uuid
                req.search = search if search else ''
                req.tenant_uuid = tenant
                if preferred_nw_type:
                    req.preferred_nw_type = preferred_nw_type
                rpc_rsp = CloudConnectorService_Stub(RpcChannel()).cc_nw_runtime(RpcController(), req)
                log.info('rpc_rsp: %s', rpc_rsp)
                if rpc_rsp.ret_status == syserr_pb2.SYSERR_SUCCESS:
                    nws = list()
                    for obj in rpc_rsp.nwruntime:
                        pfx = obj.ip_subnet[0].prefix
                        snw = {'mask': pfx.mask, 'name': obj.name, 'id': obj.uuid,
                               'ip_addr': {'addr': pfx.ip_addr.addr, 'type': pfx.ip_addr.type}}
                        nws.append(snw)
                    rsp = {'subnets': nws}
                else:
                    rsp = {'error': rpc_rsp.ret_string}
                    ret = ERR_RC
            else:
                msg = _params_check(creds)
                pxhost = None
                pxport = None
                if not msg:
                    (pxhost, pxport, pxuser, pxpass) = _get_proxy(creds)
                    (akey, skey, tkey, exp, msg) = _get_credentials(creds,
                        pxhost=pxhost, pxport=pxport, pxuser=pxuser, pxpass=pxpass)
                if msg:
                    rsp = {'error': msg}
                    ret = ERR_RC
                else:
                    rsp = dict()
                    filter_snws = list()
                    if not provider and ipam_pb:
                        zones = ipam_pb.aws_profile.zones
                        for z in zones:
                            filter_snws.extend(z.usable_network_uuids)
                        if not zones:
                            filter_snws.extend(ipam_pb.aws_profile.usable_network_uuids)
                    if not filter_snws:
                        provider = True
                    if provider or filter_snws:
                        ret, rsp = aws_get_vpc_subnets(creds['region'], akey, skey, creds['vpc'], stoken=tkey,
                            pxhost=pxhost, pxport=pxport, pxuser=pxuser, pxpass=pxpass)
                    if ret == 200:
                        nws = list()
                        for aznws in rsp.get('networks', []):
                            # ignore AZ for now
                            for i in aznws['subnets']:
                                if filter_snws and i['id'] not in filter_snws:
                                    continue
                                if (search and search not in i['cidr'] and
                                    search not in i['name'] and search not in i['id']):
                                    continue
                                tmp = i['cidr'].split('/')
                                snw = {'mask': tmp[1], 'ip_addr': {'addr': tmp[0], 'type': 'V4'}}
                                snw.update(i)
                                nws.append(snw)
                        rsp = {'subnets': nws}
                    elif rsp:
                        rsp = {'error': rsp}
        else:
            msg = "API unsupported for IpamDns type -> %s" % (_get_ipamdnstype_str(ipam_type))
            rsp = {'error': msg}
            ret = SVR_RC

        log.debug(rsp) if ret == 200 else log.error(rsp)
        return Response(data=rsp, status=ret)

    def get(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        params = request.QUERY_PARAMS
        rsp = 'GET invoked with args request %s args %s kwargs %s' % (_mask_keys(params), args, kwargs)
        log.info(rsp)
        #if not (self.cloud or params.get('ipamdnsprovider_uuid')):
        #    raise Exception('Only cloud or ipamdnsprovider_uuid based get supported')
        rsp = self._handle(request, params)
        return rsp


class IpamDnsProviderProfileDomainList(ListView, RetrieveView):
    def _handle(self, request, params):
        ret = 200
        dns_type, creds, dns_pb, cloud_pb, provider = get_ipamdns_config(params,
            cfg_type=REQUEST_TYPE_DNS, cloud=self.cloud)

        if not dns_type:
            msg = "Ipam Type invalid or configuration not found in Avi"
            rsp = {'error': msg}
            return Response(rsp, status=ERR_RC)

        search = params.get('search', None)

        rsp = IpamDnsSubnetDomainList()
        domains = list()

        if dns_type == IPAMDNS_TYPE_INFOBLOX_DNS:
            ib_ip, user, pwd, wapi_v, _, dns_view = creds
            log.info("Infoblox: get domains creds: %s", creds)
            if (dns_pb and dns_pb.HasField('infoblox_profile') and
                not dns_pb.infoblox_profile.usable_domains):
                provider = True
            if provider:
                try:
                    infoblox_ds = Infoblox.get_domains_in_view(ib_ip,
                                    user, pwd, wapi_v, dns_view)
                    domains = [domain for domain in infoblox_ds
                         if not search or search in domain]
                except Exception as e:
                    err_str = str(e).lower()
                    rsp.error = err_str
                    if 'timed out' in err_str:
                        rsp.error = "Connection timedout to Infoblox at %s!"%ib_ip
                    elif 'refused' in err_str:
                        rsp.error = "Connection refused to Infoblox at %s!"%ib_ip
                    elif 'no route to host' in err_str:
                        rsp.error = "No route to Infoblox at %s!"%ib_ip
                    ret = SVR_RC
            elif dns_pb and dns_pb.HasField('infoblox_profile'):
                profile_ds = dns_pb.infoblox_profile.usable_domains
                domains = [domain for domain in profile_ds
                    if not search or search in domain]
        elif dns_type == IPAMDNS_TYPE_INTERNAL_DNS:
            if dns_pb:
                available_domains = ipamdns_get_configured_domains(dns_pb)
                domains = [domain for domain, _ in available_domains
                    if not search or search in domain]
            else:
                ret = ERR_RC
                rsp.error = "Bad Request, valid cloud or "\
                        "ipamdnsprovider_uuid required in request PARAMS."
        elif dns_type == IPAMDNS_TYPE_CUSTOM_DNS:
            log.info("CustomDNS: get domains => %s", creds)
            if (dns_pb and dns_pb.HasField('custom_profile') and
                not dns_pb.custom_profile.usable_domains):
                provider = True
            if provider:
                cprof_uuid = creds.pop('customdnsprovider_uuid', None)
                if cprof_uuid:
                    cprof_params, cprof_dns_mod = \
                            IpamDnsCustom.get_custom_profile(cprof_uuid)
                    cprof_params.update(creds)
                    try:
                        domains = cprof_dns_mod.GetDomains(cprof_params)
                        domains = [d for d in domains if not search or search in d]
                    except Exception as e:
                        err_str = str(e).lower()
                        rsp.error = err_str
                        ret = SVR_RC
                else:
                    err_str = "Request has 'provider' mode set but "\
                            "no valid 'customdnsprovider_uuid' provided!"
                    rsp.error = err_str
                    ret = SVR_RC
            elif dns_pb:
                profile_ds = dns_pb.custom_profile.usable_domains
                domains = [d for d in profile_ds if not search or search in d]
            else:
                ret = ERR_RC
                rsp.error = "Bad request, valid customdnsprovider_uuid "\
                        "or cloud_uuid required in request PARAMS."
        elif dns_type == IPAMDNS_TYPE_AWS_DNS:
            if (cloud_pb and cloud_pb.vtype == common_pb2.CLOUD_AWS and
                cloud_pb.aws_configuration.route53_integration):
                req = cc_dns_domain_req()
                req.cc_id = cloud_pb.uuid
                req.inc_public = True
                rpc_rsp = CloudConnectorService_Stub(RpcChannel()).cc_get_domains(RpcController(), req)
                log.info('rpc_rsp: %s', rpc_rsp)
                if rpc_rsp.ret_status == syserr_pb2.SYSERR_SUCCESS and rpc_rsp.zdomains:
                    rsp.zdomains.extend(rpc_rsp.zdomains)
                    domains = [i.domain_name for i in rsp.zdomains
                        if not search or search in i.domain_name]
            else:
                msg = _params_check(creds)
                pxhost = None
                pxport = None
                if not msg:
                    (pxhost, pxport, pxuser, pxpass) = _get_proxy(creds)
                    (akey, skey, tkey, exp, msg) = _get_credentials(creds,
                        pxhost=pxhost, pxport=pxport, pxuser=pxuser, pxpass=pxpass)
                if msg:
                    rsp = {'error': msg}
                    ret = ERR_RC
                else:
                    resp = dict()
                    filter_ds = list()
                    if not provider and dns_pb:
                        filter_ds = dns_pb.aws_profile.usable_domains
                    if not filter_ds:
                        provider = True
                    if provider or filter_ds:
                        ret, resp = aws_get_vpc_domains(creds['region'], akey, skey, creds['vpc'], stoken=tkey,
                            pxhost=pxhost, pxport=pxport, pxuser=pxuser, pxpass=pxpass)
                    if ret == 200:
                        for d in resp.get('domains', []):
                            dname = d['domain_name']
                            if filter_ds and dname not in filter_ds:
                                continue
                            if search and search not in dname:
                                continue
                            domains.append(dname)
                    elif resp:
                        rsp.error = str(resp)
        elif dns_type in [IPAMDNS_TYPE_AZURE, IPAMDNS_TYPE_AZURE_DNS]:
            if cloud_pb:
                req = cc_dns_domain_req()
                req.cc_id = cloud_pb.uuid
                rpc_rsp = CloudConnectorService_Stub(RpcChannel()).cc_get_domains(RpcController(), req)
                log.info('rpc_rsp: %s', rpc_rsp)
                if rpc_rsp.ret_status == syserr_pb2.SYSERR_SUCCESS and rpc_rsp.zdomains:
                    domains = [i.domain_name for i in rpc_rsp.zdomains]
                else:
                    ret = rpc_rsp.ret_status
                    rsp.error = rpc_rsp.ret_string
            else:
                params = copy.deepcopy(params)
                azure_update_params(params)
                credentials, msg = get_azure_credentials(params)
                if msg:
                    ret = ERR_RC
                    rsp.error = msg
                    return Response(data=pb2json(rsp), status=ret)

                ret, resp = azure_get_zones(credentials, str(params['subscription_id']))
                if ret == 200:
                    for domain in resp.get('zdomains', []):
                        domain_name = domain['domain_name']
                        domains.append(domain_name)
                else:
                    rsp.error = str(resp)
        else:
            msg = "API unsupported for IpamDns type -> %s" % (_get_ipamdnstype_str(dns_type))
            rsp.error = msg
            ret = SVR_RC

        if ret == 200:
            if domains:
                rsp.domains.extend(domains)
                rsp = pb2json(rsp)
            else:
                rsp = {'domains': []}
        else:
            rsp = pb2json(rsp)

        log.debug(rsp) if ret == 200 else log.error(rsp)
        return Response(data=rsp, status=ret)

    def get(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        params = request.QUERY_PARAMS
        rsp = 'GET invoked with args request %s args %s kwargs %s' % (_mask_keys(params), args, kwargs)
        log.info(rsp)
        #if not (self.cloud or params.get('ipamdnsprovider_uuid')):
        #    raise Exception('Only cloud or ipamdnsprovider_uuid based get supported')
        rsp = self._handle(request, params)
        return rsp

class IpamDnsProviderProfileLogin(ListView, RetrieveView):
    def get(self, request, *args, **kwargs):
        """
        @get: Login with the given credentials and throw an exception if it fails
        """
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        params = request.QUERY_PARAMS
        log.info('GET invoked with args request %s args %s kwargs %s' % (_mask_keys(params), args, kwargs))
        ret = 200
        ipam_type, creds, ipam_pb, cloud_pb, provider = get_ipamdns_config(params,
            cfg_type=REQUEST_TYPE_IPAM, cloud=self.cloud)

        if not ipam_type:
            rsp = {'error': "Ipam Type[%s] invalid or configuration not found in Avi" % ipam_type}
            return Response(rsp, status=ERR_RC)

        if ipam_type in [IPAMDNS_TYPE_INFOBLOX, IPAMDNS_TYPE_INFOBLOX_DNS]:
            ib_ip, user, pwd, wapi_v, nw_view, dns_view = creds
            log.info("Infoblox: test login creds: %s", creds)
            try:
                rsp = Infoblox.test_login(ib_ip, user, pwd, wapi_v, nw_view, dns_view, False)
            except Exception as e:
                err_str = str(e).lower()
                log.error(str(e))
                if 'timed out' in err_str:
                    err_str = "Connection timedout to Infoblox at %s"%ib_ip
                elif 'refused' in err_str:
                    err_str = "Connection refused to Infoblox at %s"%ib_ip
                elif 'no route to host' in err_str:
                    err_str = "No route to Infoblox at %s"%ib_ip
                elif 'authorization required' in err_str:
                    err_str = "Invalid username or password to Infoblox at %s"%ib_ip
                rsp = {'error': err_str}
                ret = SVR_RC
            log.info("login success: %s" % rsp) if ret == 200 else log.error("login error: %s" % rsp)
        else:
            rsp = {'error': 'IpamDnsProviderProfileLogin not supported for Ipam Type %s' % ipam_type}
            ret = SVR_RC
        return Response(rsp, status=ret)