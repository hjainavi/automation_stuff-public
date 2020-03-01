
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
Filename: views_gslb_custom
This function address the backend functionality for the custom-urls. Please
review the notes in urls_gslb_custom.py file.
"""
#standard
import json
import logging
import hashlib
import collections

# Rest framework
from rest_framework import status
from rest_framework.response import Response

#Django interfaces
from django.core.exceptions import ObjectDoesNotExist
from django.http.response import HttpResponseForbidden

#Django DB Models
import api.models as api_models
from api.models_gslb import Gslb
from api.models_pool import Pool
from api.models_common import Tenant
from api.models_ssl import PKIProfile
from api.models_vs import VirtualService
from api.models_gslb import GslbService
from api.models_gslb import GslbGeoDbProfile
import api.all_views_for_gslb as all_views
from api.serializers_gslb import GslbSerializer
from api.models_health_monitor import HealthMonitor
from api.serializers_gslb import GslbServiceSerializer
from api.models_application_persistence_profile import ApplicationPersistenceProfile

#Avi pb <--> json
from avi.protobuf_json.protobuf_json import json2pb
from avi.protobuf_json.protobuf_json import pb2json

#Avi rest
from avi.rest.mixins import MixinBase
from avi.rest.views import ListView
from avi.rest.views import CreateView
from avi.rest.views import UpdateView
from avi.rest.views import DeleteView
from avi.rest.views import RetrieveView
from avi.rest.views import GetActionView
from avi.rest.views import PostActionView
import avi.rest.view_utils as view_utils
from avi.rest.api_version import api_version
from avi.rest.pb2model import protobuf2model
from avi.rest.url_utils import slug_for_obj_uri
from avi.rest.pb2dict import protobuf2dict_withrefs
from avi.infrastructure.datastore import db_table_name_from_pb
from avi.infrastructure.save_diff import save_diff

#Avi utilities
from avi.util.pb_resolve import GslbResolve
from avi.util.gslb_util import get_my_uuid
from avi.util.gslb_util import get_glb_cfg
from avi.util.gslb_util import get_sw_version
from avi.util.gslb_util import GslbVerifySite
from avi.util.gslb_util import GslbSiteOpsBasicApis
from avi.util.gslb_util import gslb_geo_db_cleanup
from avi.util.gslb_util import gslb_geo_db_upd_hdlr
from avi.util.gslb_util import gslb_get_site_cfg
from avi.util.gslb_util import gslb_stale_object_checks
from avi.util.gslb_util import gslb_stale_object_cleanup
from avi.util.pb_check import MessageValueError
from avi.util.pb_check import GslbMessageValueError
from avi.util.glb_mgr_sessions import get_timestamp
from avi.util.glb_mgr_sessions import SyserrHandler
from avi.util.must_check import GslbServiceGetFqdns
from avi.util.gslb_api_converter import DS_GSLB
from avi.util.gslb_api_converter import DS_GS
from avi.util.gslb_api_converter import DS_GEO
from avi.util.gslb_api_converter import DS_GHM
from avi.util.gslb_api_converter import DS_GAP
from avi.util.gslb_api_converter import DS_GPKI
from avi.util.gslb_api_converter import RPCResponse_xlate

#GSLB interfaces
from avi.protobuf import webapp_err_pb2 as weberr
from avi.protobuf.rpc_common_pb2 import RPCResponse
import avi.protobuf.syserr_pb2 as syserr
from avi.protobuf.gslb_pb2 import GslbSite
from avi.protobuf.gslb_pb2 import Gslb as GslbProto
from avi.protobuf.gslb_pb2 import GSLB_PASSIVE_MEMBER
from avi.protobuf.gslb_pb2 import GslbService as GslbServiceProto
from avi.protobuf.gslb_runtime_pb2 import GSLB_DECL
from avi.protobuf.gslb_runtime_pb2 import GSLB_CREATE
from avi.protobuf.gslb_runtime_pb2 import GSLB_DELETE
from avi.protobuf.gslb_runtime_pb2 import GSLB_UPDATE
from avi.protobuf.gslb_runtime_pb2 import GSLB_AVI_SITE
from avi.protobuf.gslb_runtime_pb2 import GSLB_PURGE
from avi.protobuf.gslb_runtime_pb2 import GSLB_SITE_CONFIG
from avi.protobuf.gslb_runtime_pb2 import GSLB_NOT_A_MEMBER
from avi.protobuf.gslb_runtime_pb2 import GslbSiteOpsResync
from avi.protobuf.gslb_runtime_pb2 import GslbSiteOpsLeaderChange
from avi.protobuf.gslb_runtime_pb2 import GslbSiteOpsMaintenanceMode
from avi.protobuf.gslb_runtime_pb2 import GslbSiteOpsStaleObjectStatus
from avi.protobuf.gslb_internal_pb2 import GslbSiteOpsVerify
from avi.protobuf.health_monitor_pb2 import HealthMonitor as HealthMonitorProto
from avi.protobuf.pool_pb2 import Server
from avi.protobuf.pool_pb2 import Pool as PoolProto

#grep in the directory to find the logs
LOG = logging.getLogger(__name__)
my_ts = 0.0
def get_ts():
    """ Provides a monotonically increasing value unlike time.time() """
    global my_ts
    my_ts += 1.0
    return my_ts
#---------------------------------------------------------------------------
# Default GHM List:
# This list is used to create the default gslb health monitor profiles.
# The template is copied from fixtures/initial_data.py. Set minimum
# required parameters and let pb_default do its magic. Please track
# with pb_delete_custom_checks.py to ensure it is in sync.
GSLB_DEFAULT_GHM_LIST = [
    {
        'path': '/api/healthmonitor',
        'method': 'post',
        'data': {
            # copied from initial_data defaults
            "name": "System-GSLB-Ping",
            "receive_timeout":4,
            "send_interval":10,
            "type": "HEALTH_MONITOR_PING",
            "is_federated": "true",
        }
    },
    {
        'path': '/api/healthmonitor',
        'method': 'post',
        'data': {
            # copied from initial_data defaults
            "name": "System-GSLB-TCP",
            "receive_timeout":4,
            "send_interval":10,
            "monitor_port": 80,
            "type": "HEALTH_MONITOR_TCP",
            "is_federated": "true",
        }
    },
    {
        'path': '/api/healthmonitor',
        'method': 'post',
        'data': {
            # copied from initial_data defaults
            "name": "System-GSLB-HTTP",
            "receive_timeout":4,
            "successful_checks":3,
            "failed_checks":3,
            "send_interval":10,
            "monitor_port": 80,
            "type": "HEALTH_MONITOR_HTTP",
            "is_federated": "true",
            "http_monitor": {
                "http_request": "HEAD / HTTP/1.0",
                "http_response_code": [
                    'HTTP_2XX',
                    'HTTP_3XX'
                ]
            }
        }
    },
    {
        'path': '/api/healthmonitor',
        'method': 'post',
        'data': {
            # copied from initial_data defaults
            "name": "System-GSLB-HTTPS",
            "receive_timeout":4,
            "successful_checks":3,
            "failed_checks":3,
            "send_interval":10,
            "monitor_port": 443,
            "type": "HEALTH_MONITOR_HTTPS",
            "is_federated": "true",
            "https_monitor": {
                "http_request": "HEAD / HTTP/1.0",
                "http_response_code": [
                    'HTTP_2XX',
                    'HTTP_3XX'
                ]
            }
        }
    },
    {
        'path': '/api/healthmonitor',
        'method': 'post',
        'data': {
            # copied from initial_data defaults
            "name": "System-GSLB-UDP",
            "receive_timeout":2,
            "send_interval":4,
            "monitor_port": 443,
            "type": "HEALTH_MONITOR_UDP",
            "is_federated": "true",
            "udp_monitor": {
                "udp_request": "EnterYourRequestDataHere"
            }
        }
    }
]

def gslb_get_default_ghms():
    """ Retrieves the list of default ghm object names """
    def_ghms = set()
    for entry in GSLB_DEFAULT_GHM_LIST:
        data = entry.get('data')
        def_ghms.add(data.get('name'))
    return def_ghms

#---------------------------------------------------------------------------
class GslbSiteOpsView(MixinBase, GslbSiteOpsBasicApis):
    """
    The following are applicable for all config events.
    01. Leader curates/validates the profile and sends it across. So,
        in this path, the traditional-must-checks etc are NOT executed.
        Instead, we will do some basic validation in these functions.
    02. UUID/Tenant values are retained as per leader values. It is NOT
        generated.
    """

    def __init__(self):
        """
        Pbs_for_backend = is a collection of PBs that need to be
        sent to the backend services such as glb_mgr or vs_mgr.
        This is organized as a list of tuples.  This collection
        of message/method will get sent to the back-end services
        in the custom-rpc-callback.

        [(ops, pb_type, new_pb, old_pb), (ops, pb_type, new_pb, old_pb)]
        """
        MixinBase.__init__(self)
        GslbSiteOpsBasicApis.__init__(self)
        self.pbs_for_backend = []
        self.gslb_delete_in_progress = False
        pki_list = PKIProfile.objects.filter(is_federated=True)
        for pki in pki_list:
            self.pki_uuid = pki.uuid
            break
        else:
            self.pki_uuid = None
        self.glb_cfg = self.get_glb_cfg()
        self.ops_mapping = {GSLB_CREATE:'create',
                            GSLB_UPDATE:'update',
                            GSLB_DELETE:'delete',
                            GSLB_PURGE:'purge'}
        self.ds_2_db_mapping = {DS_GSLB:Gslb,
                                DS_GPKI:PKIProfile,
                                DS_GS:GslbService,
                                DS_GHM: HealthMonitor,
                                DS_GEO:GslbGeoDbProfile,
                                DS_GAP:ApplicationPersistenceProfile}
        self.fqdn_dict = None
        return

    def ops_2_str(self, ops):
        """ Function that maps the enum to string """
        return self.ops_mapping.get(ops)

    def ds_name_2_db_model(self, ds_name):
        """ Function maps ds-name to db_model """
        return self.ds_2_db_mapping.get(ds_name)

#---------------------------------------------------------------------------
# Basic Create/Update/Delete
#---------------------------------------------------------------------------
    def _gslb_check_tenant(self, request, entry):
        """
        This function evaluates the tenant within the object. In the
        general framework, each message will contain ONE object that
        is configured in the tenant context.  In the GSLB framework,
        (especially on the follower), the GslbSiteOps message can
        contain GLB, multiple GS and GHM objects.  Each of these
        objects can potentially belong to different tenants. The
        'check_tenant' in the views.py cannot be used as such since
        it relies on a single value of the tenant either from the
        HTTP request or from the kwargs.  For GSLB message, we will
        extract the tenant_uuid from the leader replicated object
        and verify if the tenant exists.  If the tenant does NOT
        exist, we reject the entire transaction.

        Notes:
        01. tenant_uuid = /api/tenant/?name=tenant_name; This is a
            deviation from the norm.  Review notes in glb_mgr_atomic_ops.py
            for a justification of the deviation.  We also want to avoid
            a costly transform_refs_to_json in the webapp.  In short,
            we are using the tenant_uuid as tenant_ref between the
            back-end glb_mgr and follower portal.

            CU ops:
            -------
            input = /api/tenant/?name=app_tenant_2
            ouput = tenant-efeacdf1-7c52-48c6-a75a-b925711edffe

            Delete ops:
            -----------
            Since we use the PB present in the controller,  Input is
            already in the desired uuid format.  It is not present
            in the URI format. Therefore:
            input = tenant-efeacdf1-7c52-48c6-a75a-b925711edffe
            ouput = tenant-efeacdf1-7c52-48c6-a75a-b925711edffe
        """
        tenant_uuid = slug_for_obj_uri(entry.tenant_uuid, Tenant)
        try:
            args = {}
            kwargs = {}
            tenant = Tenant.objects.get(uuid=tenant_uuid)
            kwargs['tenant'] = tenant.uuid
            self.check_tenant(request, args, kwargs)
        except ObjectDoesNotExist:
            msg = 'Tenant:{x} does NOT exist for config object:{y}'.format(
                x=tenant_uuid, y=entry.name)
            LOG.error(msg)
            raise ObjectDoesNotExist(msg)
        return

    def _init_model_serializer(self, entry):
        """
        Helper function to initialize the model + serializer.

        Notes:
        01. Example:
            if entry.DESCRIPTOR.name == 'Gslb':
                self.model = Gslb
                self.serializer_class = GslbSerializer
            'Gslb' is used as a key to retrieve the model class.
            'GslbSerializer' is used as a key to retrieve the serializer class.
        """
        model_name = entry.DESCRIPTOR.name
        self.model = getattr(api_models, model_name)
        serializer_name = model_name + 'Serializer'
        self.serializer_class = getattr(api_models, serializer_name)
        return

    def _create(self, request, entry, **kwargs):
        """
        Base-create functionality used for GLB, GS, GHM, GAP and Geo.
        It retains the leader provided uuid and tenant. This function
        should mimic the 'create' in mixins.py as far as possible.

        01. System default objects *should* set the SystemDefaultObject.
            default field to True. So, for GsblHealthMonitors, we need
            to explicitly set this field. [ For the traditional system
            default objects, it gets set through 'initial_data' framework,
            whereas for GslbDefault objects, we need to explicitly set it.]
        """
        context = {'request':request}
        self._gslb_check_tenant(request, entry)
        self._init_model_serializer(entry)
        entry.tenant_uuid = self.tenant.uuid
        pb_default = kwargs.get('run_default_function', False)
        self.object, _ = protobuf2model(entry, None, False,
                                        context=context,
                                        skip_unfinished_pb=False,
                                        raise_serializer_error=True,
                                        run_default_function=pb_default)
        obj_data = self.serializer_class(self.object, context=context).data
        self.generate_config_log(request, True, None, obj_data,
                                 override_method='POST')
        system_default = kwargs.get('system_default', False)
        # Refer Notes 01.
        pb = self.object.protobuf()
        self._set_default_obj(pb, system_default=system_default)
        self._pbs_for_backend_ops(GSLB_CREATE, pb, None)
        return

    def _update(self, request, entry, **kwargs):
        """
        Base-update functionality used for GLB, GS, GHM, GAP and Geo.
        This function should mimic the 'update' in mixins.py.
        """
        context = {'request':request}
        self._gslb_check_tenant(request, entry)
        self._init_model_serializer(entry)
        entry.tenant_uuid = self.tenant.uuid

        # Retrieve existing pb and complete formalities
        self.kwargs['slug'] = entry.uuid
        self.object = self.model.objects.select_for_update().get(uuid=entry.uuid)
        self.old_pb = (self.object.protobuf()
                       if hasattr(self.object, 'protobuf') else None)
        old_data = protobuf2dict_withrefs(self.old_pb, request,
                                          skip_references=False,
                                          always_include_name=True)
        old_data['_last_modified'] = self.object._last_modified
        if hasattr(self.model, 'sensitive_fields'):
            view_utils.remove_sensitive_fields(self.model, old_data)

        # Now work with the new one
        pb_default = kwargs.get('run_default_function', False)
        self.object, _ = protobuf2model(entry, None, False,
                                        context=context,
                                        skip_unfinished_pb=False,
                                        raise_serializer_error=True,
                                        run_default_function=pb_default)
        obj_data = self.serializer_class(self.object, context=context).data
        self.generate_config_log(request, True, None, obj_data,
                                 old_data, override_method='PUT')
        pb = self.object.protobuf()
        self._pbs_for_backend_ops(GSLB_UPDATE, pb, self.old_pb)
        return

    def _delete(self, request, entry, **kwargs):
        """
        Base-update functionality used for Gslb objects.  This function
        should mimic the 'destroy' in mixins.py as much as possible.
        In the case of delete, we get the db-object.

        01. force_delete = True for Gslb System Default objects.  Otherwise
            we skip_pb_default_check (so that it does not fail on the follower)
            but still do the relation checks i.e. if there is any object
            dependency.
        """
        entry_pb = entry.protobuf()
        self._gslb_check_tenant(request, entry_pb)
        self._init_model_serializer(entry_pb)
        serializer = self.serializer_class(entry)
        serializer.always_include_name = True
        obj_data = serializer.to_native(entry)

        # Refer Notes 01
        force_delete = kwargs.get('force_delete', False)
        if force_delete:
            self.kwargs['force_delete'] = force_delete
        else:
            self.kwargs['skip_pb_delete_check'] = True
        self.check_delete_permission(entry, request)
        entry.delete()
        self.db_cache_delete(entry)
        self.generate_config_log(request, True, None, obj_data,
                                 override_method='DELETE')
        self._delete_default_obj(entry_pb, force_delete=force_delete)
        self._pbs_for_backend_ops(GSLB_DELETE, entry_pb, None)
        self.kwargs.pop('force_delete', None)
        self.kwargs.pop('skip_pb_delete_check', None)
        save_diff(entry_pb, None)
        return

    def _exception_hdlr(self, name, exception, rsp, obj_status):
        """ Exception handler """
        # Overall status
        rsp.rpc_status = syserr.SYSERR_GSLB_PARTIAL_SUCCESS
        trap = type(exception).__name__
        if trap == 'SyserrHandler':
            obj_status.status = exception.syserr
            obj_status.reason = exception.errmsg
        else:
            obj_status.status = syserr.SYSERR_GSLB_INVALID_OPS
            obj_status.reason = '{x}'.format(x=exception.args)
        LOG.error('Partial success %s:%s', name, obj_status.reason)
        return

#---------------------------------------------------------------------------
# Glb-ops: Create/Update/Delete
#---------------------------------------------------------------------------
    def _xlate_glb(self, glb):
        """
        01. In 17.2.5, we introduced a 'f_internal' field uuid in GslbSite
            and GslbThirdPartySites. This has to be populated if the trigger
            is a pre-17.2.5 trigger.
        02. Prior to 17.2.3, we had dns_vs_uuids within the site. These fields
            were deprecated in 17.2.3 and replaced by dns_vses in 17.2.3. This
            function translates the fields.
        """
        for site_cfg in glb.sites:
            # Refer Notes 01
            site_cfg.uuid = site_cfg.cluster_uuid
            if len(site_cfg.dns_vs_uuids):
                # Refer Notes 02
                while True:
                    try:
                        uuid = site_cfg.dns_vs_uuids.pop()
                        dns_vs = site_cfg.dns_vses.add()
                        dns_vs.dns_vs_uuid = uuid
                    except IndexError:
                        break
        # Refer Notes 01
        for site_cfg in glb.third_party_sites:
            site_cfg.uuid = site_cfg.cluster_uuid
        return

    def create_gslb(self, request, glb, rsp):
        """
        This function handles the GLB create. If GLB create fails,
        we reject the entire request.  We check with glb_mgr to see if
        there are any residual states. (Refer to Notes under GslbResolve)
        """
        self._xlate_glb(glb)
        LOG.info("Preparing Glb Create %s", glb.uuid)
        obj_status = rsp.resource.gs_ops_v2.objs.add()
        obj_status.uuid = glb.uuid
        obj_status.status = syserr.SYSERR_SUCCESS
        obj_status.ds_name = DS_GSLB
        GslbResolve(glb)
        self._create(request, glb)
        self.glb_cfg = self.object.protobuf()
        return

    def update_gslb(self, request, glb, rsp):
        """
        This function handles the glb_update.  We do a GslbResolve to
        see if there is any conflict with glb_mgr states.  The glb object
        update may result in downstream changes for GslbServices that have
        site-persistence enabled.
        """
        self._xlate_glb(glb)
        LOG.info("Preparing Glb update %s", glb.name)
        obj_status = rsp.resource.gs_ops_v2.objs.add()
        obj_status.uuid = glb.uuid
        obj_status.status = syserr.SYSERR_SUCCESS
        obj_status.ds_name = DS_GSLB
        try:
            #Pass the same protobuf twice
            GslbResolve(glb, old_pb=glb)
            self._update(request, glb)
            self.glb_cfg = self.object.protobuf()
            self.site_enable_disable_sp_ops(self.glb_cfg, self.old_pb)
        except Exception as e:
            self._exception_hdlr(glb.name, e, rsp, obj_status)
            rsp.rpc_status = syserr.SYSERR_GSLB_INVALID_OPS
        return

    def delete_gslb(self, request, glb, rsp):
        """
        This function handles the glb_delete. Force delete all the
        dependencies:(aka children GS, GHM, GAP, GEO) in the database as
        well as package it to GLB-MGR for subsequent cleanup. This
        is required as a catch-all to delete all the profiles as part
        of feature cleanup.

        Order: GS--> GHM --> GAP --> PKI --> GEO --> GLB.
        """
        LOG.info("Preparing Glb delete %s", glb.uuid)
        self.gslb_delete_in_progress = True
        self._pbs_for_backend_ops(GSLB_PURGE, glb, None)
        obj_status = rsp.resource.gs_ops_v2.objs.add()
        obj_status.uuid = glb.uuid
        obj_status.status = syserr.SYSERR_SUCCESS
        obj_status.ds_name = DS_GSLB

	# GS delete
        gs_list = GslbService.objects.all()
        for gs in gs_list:
            LOG.info("Preparing Gs delete %s", gs.name)
            self.delete_sp(gs.protobuf())
            self._delete(request, gs)

        # GHM delete: Retrieve system default HM names
        def_ghms = gslb_get_default_ghms()
        ghm_list = HealthMonitor.objects.filter(is_federated=True)
        for ghm in ghm_list:
            LOG.info("Preparing Ghm delete %s", ghm.name)
            force_delete = False
            # If system-default, then set the force_delete = True
            if ghm.name in def_ghms:
                force_delete = True
                def_ghms.remove(ghm.name)
            self._delete(request, ghm, force_delete=force_delete)

        # GAP delete
        gap_list = ApplicationPersistenceProfile.objects.filter(is_federated=True)
        for gap in gap_list:
            LOG.info("Preparing Gap delete %s", gap.name)
            self._delete(request, gap)

        # GPKI delete
        gpki_list = PKIProfile.objects.filter(is_federated=True)
        for gpki in gpki_list:
            LOG.info("Preparing GPKI delete %s", gpki.name)
            self._delete(request, gpki)

        # GEO delete
        geo_list = GslbGeoDbProfile.objects.all()
        for geo in geo_list:
            LOG.info("Preparing Geo delete %s", geo.name)
            gslb_geo_db_cleanup()
            self._delete(request, geo)

        # GLB delete
        glb_list = Gslb.objects.filter(uuid=glb.uuid)
        for glb in glb_list:
            self._delete(request, glb)
        return

#---------------------------------------------------------------------------
# GS-ops: Create/Update/Delete
#---------------------------------------------------------------------------
    def _fqdn_must_check(self, gs, fqdn_dict):
        """ toned down version of must-check for fqdn-uniqueness """
        for fqdn in gs.domain_names:
            gs_profs = GslbService.objects.filter(json_data__domain_names__icontains=fqdn)
            for gs in gs_profs:
                gs_pb = gs.protobuf()
                if fqdn in gs_pb.domain_names[:]:
                    fqdn_dict.setdefault(fqdn, []).append((gs.uuid, gs.name))

            obj_list = fqdn_dict.get(fqdn, None)
            if obj_list is not None:
                for oid, name in obj_list:
                    if gs.uuid == oid:
                        continue
                    msg = "GS:{a}:{b} with fqdn:{c} clashes with ".format(
                        a=gs.name, b=gs.uuid, c=fqdn)
                    msg = "{a} existing fqdn in profile:{b}:{c}".format(
                        a=msg, b=name, c=oid)
                    raise SyserrHandler(syserr.SYSERR_GSLB_FQDN_CONFLICT, msg)
        return

    def _gs_hdlr(self, request, rsp, obj, ops):
        """
        Base function to handle create and update of GS.
        Notes:
        01. Scalability enhancement:  We don't need to retrieve all the
            fqdns everytime we process a Gslbservice object. We retrieve it
            once and use it across all the GslbService objects in the bag.
            NOTE: In high scale setup, interating through all the GSes to form fqdn_dict 
            is very expensive. Instead, gs_check is done in _fqdn_must_check by using json_data filters.
        02. If there is a fqdn clash on the follower, send an unique syserr
            for that object back to the leader.
        03. Do not FORWARD the entry to the back-end glb_mgr.
        """
        LOG.info("Preparing obj %s", obj.name)
        obj_status = rsp.resource.gs_ops_v2.objs.add()
        obj_status.uuid = obj.uuid
        obj_status.status = syserr.SYSERR_SUCCESS
        obj_status.ds_name = db_table_name_from_pb(obj)
        if not self.fqdn_dict:
            self.fqdn_dict = GslbServiceGetFqdns(self.glb_cfg, gs_check=False)
        try:
            self._fqdn_must_check(obj, self.fqdn_dict)
            if ops == GSLB_CREATE:
                self._create(request, obj)
                new_gs_cfg = self.object.protobuf()
                self.create_sp(new_gs_cfg)
            else:
                self._update(request, obj)
                new_gs_cfg = self.object.protobuf()
                self.update_sp(new_gs_cfg, self.old_pb)
        except Exception as e:
            self._exception_hdlr(obj.name, e, rsp, obj_status)
        return

    def create_gslbservice(self, request, obj, rsp):
        """ This function handles the gs-create.  """
        self._gs_hdlr(request, rsp, obj, GSLB_CREATE)
        return

    def update_gslbservice(self, request, obj, rsp):
        """ This function handles the gs_update.  """
        self._gs_hdlr(request, rsp, obj, GSLB_UPDATE)
        return

    def delete_gslbservice(self, request, uuid, rsp):
        """ This function handles the gs_delete.  """
        # Address children objects: (SP) first
        gs_list = GslbService.objects.filter(uuid__in=[uuid])
        for gs in gs_list:
            self.delete_sp(gs.protobuf())
        self._obj_del_hdlr(request, rsp, DS_GS, uuid)
        return
#---------------------------------------------------------------------------
# Other objects: Create/Update/Delete
#---------------------------------------------------------------------------
    def _obj_hdlr(self, request, rsp, obj, ops):
        """ Base function to handle create and update for GHM, GEO, GAP """
        LOG.info("Preparing obj %s", obj.name)
        obj_status = rsp.resource.gs_ops_v2.objs.add()
        obj_status.uuid = obj.uuid
        obj_status.status = syserr.SYSERR_SUCCESS
        obj_status.ds_name = db_table_name_from_pb(obj)
        try:
            if ops == GSLB_CREATE:
                self._create(request, obj)
            else:
                self._update(request, obj)
        except Exception as e:
            self._exception_hdlr(obj.name, e, rsp, obj_status)
        return

    def _obj_del_hdlr(self, request, rsp, ds_name, uuid):
        """ Base function to handle delete ops for non-glb """
        LOG.info("Preparing obj delete %s", uuid)
        obj_status = rsp.resource.gs_ops_v2.objs.add()
        obj_status.uuid = uuid
        obj_status.ds_name = ds_name
        obj_status.status = syserr.SYSERR_SUCCESS
        db_model = self.ds_name_2_db_model(ds_name)
        obj_list = db_model.objects.filter(uuid__in=[uuid])
        for obj in obj_list:
            self._delete(request, obj)
        return

    def create_healthmonitor(self, request, obj, rsp):
        """ This function handles the GHM create.  """
        self._obj_hdlr(request, rsp, obj, GSLB_CREATE)
        return

    def update_healthmonitor(self, request, obj, rsp):
        """ This function handles the ghm_update.  """
        self._obj_hdlr(request, rsp, obj, GSLB_UPDATE)
        return

    def delete_healthmonitor(self, request, uuid, rsp):
        """ This function handles the ghm_delete.  """
        self._obj_del_hdlr(request, rsp, DS_GHM, uuid)
        return

    def create_gslbgeodbprofile(self, request, obj, rsp):
        """ This function handles the Geo create.  """
        self._obj_hdlr(request, rsp, obj, GSLB_CREATE)
        return

    def update_gslbgeodbprofile(self, request, obj, rsp):
        """ This function handles the GEO update.  """
        # Do file-cleanup as required.
        self._obj_hdlr(request, rsp, obj, GSLB_UPDATE)
        gslb_geo_db_upd_hdlr(self.object.protobuf(), self.old_pb)
        return

    def delete_gslbgeodbprofile(self, request, uuid, rsp):
        """ This function handles the GEO delete. Check and do file-cleanup  """
        gslb_geo_db_cleanup()
        self._obj_del_hdlr(request, rsp, DS_GEO, uuid)
        return

    def create_applicationpersistenceprofile(self, request, obj, rsp):
        """ This function handles the GAP create.  """
        self._obj_hdlr(request, rsp, obj, GSLB_CREATE)
        return

    def update_applicationpersistenceprofile(self, request, obj, rsp):
        """ This function handles the GAP update.  """
        self._obj_hdlr(request, rsp, obj, GSLB_UPDATE)
        return

    def delete_applicationpersistenceprofile(self, request, uuid, rsp):
        """ This function handles the GAP delete.  """
        self._obj_del_hdlr(request, rsp, DS_GAP, uuid)
        return

    def create_pkiprofile(self, request, obj, rsp):
        """ This function handles the GPKI create.  """
        self._obj_hdlr(request, rsp, obj, GSLB_CREATE)
        return

    def update_pkiprofile(self, request, obj, rsp):
        """ This function handles the GPKI update.  """
        self._obj_hdlr(request, rsp, obj, GSLB_UPDATE)
        return

    def delete_pkiprofile(self, request, uuid, rsp):
        """ This function handles the GPKI delete.  """
        self._obj_del_hdlr(request, rsp, DS_GPKI, uuid)
        return
#---------------------------------------------------------------------------
# Pre-declarative handling
#---------------------------------------------------------------------------
    def _pre_decl_hdlr(self, msg):
        """
        This function does declarative processing. It does pre-declarative
        processing of the input message.

        Declarative Model:
        ==================
        This is a declarative model in which the follower has to converge
        to the leader's dictate.

        The leader may have gone through an upgrade or a warm-start
        aka leader re-elect in a cluster, etc.  This will result in
        the runtime-info of each site getting lost. There could be
        a potential mismatch between the leader's view of the config
        sent to follower and follower's view of the config received.

        So after a warm-start, leader will *ALWAYS* send a GLOBAL-CREATE
        with all the current configuration. Follower needs to compute
        diff based on its existing snapshot and the leader provided
        view. This diff is sent to the back-end glb_mgr for subsequent
        processing/cleanup eventually synchronizing with the leader's
        view of the world.

        Notes:
        01. Get the PB name; Map it to the db_model. If the object
            already exists, then change the ops from GSLB_CREATE
            to GSLB_UPDATE.
        """
        if msg.ops == GSLB_CREATE:
            glb_list = Gslb.objects.filter(uuid=msg.hdr.glb_uuid)
            if glb_list:
                msg.ops = GSLB_UPDATE #Overwrite
                for entry in msg.objs:
                    field_name = entry.WhichOneof('obj')
                    pb = getattr(entry, field_name)
                    db_model = self.ds_name_2_db_model(entry.ds_name)
                    try:
                        LOG.info('pre-decl: obj(%s)', pb.name)
                        db_model.objects.get(uuid=pb.uuid)
                        LOG.info("pre-decl: obj(%s) add to upd", pb.name)
                        entry.ops = GSLB_UPDATE
                    except ObjectDoesNotExist:
                        pass
        return
#---------------------------------------------------------------------------
# Post-declarative handling
#---------------------------------------------------------------------------
    def _post_decl_obj_hdlr(self, request, rsp, ds_name, new_uuids):
        """"
        This function does batch processing in post-declarative path.
        """
        fn_hdlr = getattr(self, 'delete_' + ds_name)
        db_model = self.ds_name_2_db_model(ds_name)
        obj_list = db_model.objects.exclude(uuid__in=new_uuids).filter(is_federated=True)
        for obj in obj_list:
            LOG.info("post-decl obj del: %s/%s", obj.uuid, obj.name)
            fn_hdlr(request, obj.uuid, rsp)
        return

    def _post_decl_hdlr(self, request, msg, rsp):
        """
        This function does post-declarative processing of the objects.
        01. Use the leader provided final list of object uuids.
        02. Retrieve the list of objects whose uuids don't match
            with the leader list.  These objects are absent in leader,
            but present in the follower.
        03. This list of objects need to be deleted from the follower.

        Notes:
        a. Batch the pb-type to uuids.
        b. To ensure 'refers_to' dependencies are cleaned-up in the
           correct order, we have to delete 'gslbservice' objects and
           then the children objects such as healthmonitor, app, etc.
        """
        pb_uuids = {}
        msg.ops = GSLB_UPDATE
        # Refer Notes a.
        for entry in msg.objs:
            new_uuids = pb_uuids.get(entry.ds_name)
            if not new_uuids:
                new_uuids = []
                pb_uuids[entry.ds_name] = new_uuids
            new_uuids.append(entry.uuid)

        # Refer Notes b
        ds_names = [DS_GS, DS_GHM, DS_GPKI, DS_GAP, DS_GEO]
        for ds_name in ds_names:
            new_uuids = pb_uuids.pop(ds_name, [])
            self._post_decl_obj_hdlr(request, rsp, ds_name, new_uuids)
        return
#---------------------------------------------------------------------------
# Custom run_callack
#---------------------------------------------------------------------------
    def _pbs_for_backend_ops(self, ops, pb, old_pb):
        """
        This function inserts a tuple(ops, new_pb, old_pb).

        Notes:
        01. When a delege_gslb trigger is initiated, we do not place any
            of the GslbService objects in this list.

            a. Old: [GS1(D), GS2(D), GS3(D),. GS10K(D), HM1(D),.HM10K(D), Gslb(D)]
            b. New: [Gslb(purge), HM1(D),.. HM10K(D), Gslb(D)]
        """
        if self.gslb_delete_in_progress and pb.DESCRIPTOR.name == "GslbService":
            pass
        else:
            self.pbs_for_backend.append((ops, pb, old_pb))
        return

    def pbs_send_via_view_list(self, ops, pb, old_pb, view_list):
        """ Send one object at a time using the view_list.  """
        if ops == GSLB_CREATE:
            method = 'post'
            view_ref = getattr(all_views, view_list[0])
        elif ops == GSLB_UPDATE:
            method = 'put'
            view_ref = getattr(all_views, view_list[1])
        else:
            method = 'delete'
            view_ref = getattr(all_views, view_list[1])
        view_obj = view_ref()
        view_obj.request = self.request
        view_obj.old_pb = old_pb
        view_obj.callback_data = pb, method
        view_obj.run_callback()
        LOG.info("RPC: pb %s:method %s", pb.name, method)
        return

    def pbs_send_via_batched_mode(self, msg, ops, pb):
        """
        This function does a batched send to glb_mgr. The
        following are applicable:
        01. Create operations ==> send the actual PB.
        02. Update operations ==> send the actual PB.
        03. Delete operations (Gslb) ==> send the actual PB.
        04. Delete operations (Non Gslb) ==> send the uuid.
        05. Purge operations (Gslb) ==> send the uuid.
        """
        if not msg:
            msg = self.create_gsops_msg(GSLB_SITE_CONFIG, ops)
        entry = msg.objs.add()
        entry.ops = ops
        entry.ds_name = db_table_name_from_pb(pb)
        if entry.ops in {GSLB_CREATE, GSLB_UPDATE}:
            if entry.ds_name == DS_GSLB:
                to_pb = entry.glb
            elif entry.ds_name == DS_GS:
                to_pb = entry.gs
            elif entry.ds_name == DS_GEO:
                to_pb = entry.geo
            to_pb.CopyFrom(pb)
        else:
            if entry.ds_name == 'gslb':
                if entry.ops == GSLB_DELETE:
                    entry.glb.CopyFrom(pb)
                else:
                    entry.uuid = pb.uuid
            else:
                entry.uuid = pb.uuid
        LOG.info("RPC: pb %s:method %s", pb.name, self.ops_2_str(ops))
        return msg

    def run_callback(self):
        """
        View specific custom run_callback;  This is required because
        a single API may translate to multiple objects sent to the
        back-end services.  The following semantics need to be
        adhered.

        01. Gslb objects (Gslb, GslbGeoDbProfile, GslbService) need
            to be sent glb_mgr in a batched mode.
        02. Federated objects (HealthMonitor, PKIProfile, Application
            PersistenceProfile) need to be sent to vs_mgr; one object
            at a time.
        03. Gslb objects and Federated objects may be present in the
            same transaction. (ex: delete, purge)
        04. Sequencing of triggers in Create+Update and Delete must
            be maintained. [Otherwise, there will be dangling references
            or SE crashes in the downstream.]

        Notes:
        01. pb_order:
            holds an ordered collection of pb-types to view-names.
        02. Example:
            * Gslb, GslbGeoDbProfile, GslbService --> CUD: --> GslbSiteopsView
            * HealthMonitor --> CUD --> HealthMonitorList, HealthMonitorDetail
              We will use the RPC functionality in the views construct and NOT
              the fullblown views functionality.

        03. In order sequencing:
            pbs_for_backend: = [Gslb, HealthMonitor1, HealthMonitor2, GslbService1,
                                GslbService2, GslbGeoDbProfile, PKIProfile]
            RPC 1: Batched RPC (Gslb)
            RPC 2: Single RPC (HealthMonitor1)
            RPC 3: Single RPC (HealthMonitor2)
            RPC 4: Batched RPC (GslbService1, GslbService2, GslbGeoDbProfile)
            RPC 5: Single RPC (PKIProfile)
        """
        pb_order = collections.OrderedDict([
            ('Gslb', None),
            ('HealthMonitor', ('HealthMonitorList', 'HealthMonitorDetail')),
            ('ApplicationPersistenceProfile', ('ApplicationPersistenceProfileList',
                                               'ApplicationPersistenceProfileDetail')),
            ('PKIProfile', ('PKIProfileListView', 'PKIProfileDetailView')),
            ('Pool', ('PoolList', 'PoolDetail')),
            ('VirtualService', (None, 'VirtualServiceDetail')),
            ('GslbGeoDbProfile', None),
            ('GslbService', None)
            ])

        msg = None
        for ops, pb, old_pb in self.pbs_for_backend:
            pb_type = pb.DESCRIPTOR.name
            view_list = pb_order[pb_type]
            if view_list:
                if msg:
                    # Refer Notes 03: to maintain order
                    self.callback_data = msg, 'post' # save pb, method in callback_data
                    MixinBase.run_callback(self)
                    msg = None
                self.pbs_send_via_view_list(ops, pb, old_pb, view_list)
            else:
                msg = self.pbs_send_via_batched_mode(msg, ops, pb)
        if msg:
            # save pb, method in callback_data
            self.callback_data = msg, 'post'
            MixinBase.run_callback(self)
        return
#---------------------------------------------------------------------------
# Site Persistence APIs
#---------------------------------------------------------------------------
    def _pool_checks(self, uuid):
        """ Retrieves the pool """
        pool = None
        try:
            pool = Pool.objects.get(uuid=uuid)
        except ObjectDoesNotExist:
            LOG.error('SP Pool (%s) not present', uuid)
        return pool

    def _vs_checks(self, gs_cfg, member):
        """ Check if the VS is present on the controller.  """
        vs_cfg = None
        if member.HasField('vs_uuid'):
            try:
                vs = VirtualService.objects.get(uuid=member.vs_uuid)
                vs_cfg = vs.protobuf()
            except ObjectDoesNotExist:
                LOG.error('GS(%s) PoolMember vs_uuid %s absent',
                          gs_cfg.name, member.vs_uuid)
        return vs_cfg

    def _get_my_vs_list(self, gs_cfg):
        """
        Returns a list of (members, vs_cfg) belonging to this site
        only if member is enabled.
        """
        vs_list = []
        my_uuid = get_my_uuid()

        if gs_cfg.site_persistence_enabled:
            for group in gs_cfg.groups:
                for member in group.members:
                    if member.HasField('cluster_uuid'):
                        if member.cluster_uuid == my_uuid:
                            if not member.enabled:
                                continue
                            vs_cfg = self._vs_checks(gs_cfg, member)
                            vs_list.append((member, vs_cfg))
        return vs_list

    def _get_server_list(self, gs_cfg):
        """
        Create the server list associated with the sp-pool.
        This is primarily applicable for other sites.

        Notes:
        01. If gs-group is not enabled, then skip the members
            associated with this group.
        02. We can have only one VS from the same site.
            Don't include VS(es) vip from the same site into
            the server list.
        03. If member is not enabled, don't include the VIP
            in the server list.
        04. If site is not enabled, skip VS(es) from the
            server list.
        05. Create sha256 of the cookie: cluster_uuid:vs_uuid
            to ensure that it is encrypted.

        Example:
        01. GS1 = {(S1, VS11), (S2, VS21), (S3, VS31)}
            When GS1 memer = S2,VS21 is disabled, this member
            should NOT get included in the server-list of sites
            1 and site 3.
        """
        server_list = []
        my_uuid = get_my_uuid()
        for group in gs_cfg.groups:
            # Refer Notes 01
            if not group.enabled:
                continue
            for member in group.members:
                # Refer Notes 02
                if member.cluster_uuid == my_uuid:
                    continue
                # Refer Notes 03
                if not member.enabled:
                    continue
                # Refer Notes 04
                site_cfg = gslb_get_site_cfg(self.glb_cfg, member.cluster_uuid)
                if not site_cfg.enabled:
                    continue

                server = Server()
                server.ip.CopyFrom(member.ip)
                if member.HasField('fqdn'):
                    server.hostname = member.fqdn
                # Refer Notes 05:
                sp_cookie = member.cluster_uuid + ":" + member.vs_uuid
                server.prst_hdr_val = hashlib.sha256(sp_cookie).hexdigest()
                LOG.info('gs:%s member:%s sp-cookie: %s',
                         gs_cfg.name, member.ip.addr, sp_cookie)
                server.description = "VS-VIP from site:{x}".format(x=site_cfg.name)
                server_list.append(server)
        return server_list

    def _sp_pool_ops(self, gs_cfg, vs_cfg, servers, ops=GSLB_CREATE):
        """
        Create SP Pool from gs_cfg for a specific VS.

        Notes:
        01. For tracking the newly created pool, we use a canned pool-uuid.
            This is generated by replacing the object-type 'virtualservice-'
            with object-type 'pool-'.
            Mapping Example: virtualservice-<rand_str A> ==> pool-<rand_str A>
        """
        pool = PoolProto()
        pool.gslb_sp_enabled = True
        pool.use_service_port = True
        pool.tenant_uuid = vs_cfg.tenant_uuid
        pool.uuid = vs_cfg.uuid.replace('virtualservice-', 'pool-')
        pool.name = 'SP-' + gs_cfg.name + '-' +  vs_cfg.name
        pool.description = "Gslb SP Pool for VS:{x}".format(x=vs_cfg.name)
        pool.tenant_uuid = vs_cfg.tenant_uuid
        if len(vs_cfg.services):
            pool.default_server_port = vs_cfg.services[0].port

        # Map the hm_uuids from the GS healthmonitors
        for hm_uuid in gs_cfg.health_monitor_uuids:
            pool.health_monitor_uuids.append(hm_uuid)

        for server in servers:
            to_server = pool.servers.add()
            to_server.CopyFrom(server)

        # Assign the APP to proxy-pool
        pool.application_persistence_profile_uuid = (
            gs_cfg.application_persistence_profile_uuid)

        # Assign the VS's ssl_profile to the proxy-pool
        if vs_cfg.HasField('ssl_profile_uuid'):
            pool.ssl_profile_uuid = vs_cfg.ssl_profile_uuid

            # Set PKI iff ssl is set.
            pool.pki_profile_uuid = self.pki_uuid

        if ops == GSLB_CREATE:
            msg_key = 'create'
            self._create(self.request, pool, run_default_function=True)
        else:
            msg_key = 'update'
            self._update(self.request, pool, run_default_function=True)
        LOG.info('SP-pool %s %s for VS %s', msg_key, pool.name, vs_cfg.name)

        # Pool done; Stitch the proxy-pool to VS ONLY for CREATE
        if ops == GSLB_CREATE:
            for proxy in vs_cfg.sp_pool_uuids:
                if proxy == pool.uuid:
                    break
            else:
                # Not in the list
                vs_cfg.sp_pool_uuids.append(pool.uuid)

            LOG.info('Add NEW SP-pool(%s) to VS(%s)', pool.name, vs_cfg.name)
            self._update(self.request, vs_cfg)
        return

    def _create_sp_pool_and_update_vs(self, gs_cfg, vs_list):
        """
        This function creates the proxy pool as well as updates the
        VS with proxy-reference.  The vs_list is a validated list of
        vs_uuids for which we need to create a proxy-pool and update
        the proxy-pool reference.

        Notes:
        01. It is possible that the VS got deleted prior to the
            GS update.  In this scenario, we treat it as a NOP
            and move on.
        """
        servers = self._get_server_list(gs_cfg)

        # Create the proxy-pool
        for _, vs_cfg in vs_list:
            # Refer Notes 01
            if vs_cfg is None:
                continue

            self._sp_pool_ops(gs_cfg, vs_cfg, servers)
        return

    def create_sp(self, gs_cfg):
        """
        Function used for create site persistence related objects.
        If gs_cfg is disabled, then don't create SP objects.
        """
        if gs_cfg.enabled and gs_cfg.site_persistence_enabled:
            LOG.info('SP-Create objects of GS %s', gs_cfg.name)
            vs_list = self._get_my_vs_list(gs_cfg)
            self._create_sp_pool_and_update_vs(gs_cfg, vs_list)
        return

    def _delete_sp_pool_and_update_vs(self, vs_list):
        """
        Deletes the SP references and deletes the SP pool.

        Notes:
        01. It is possible that the underlying VS on a site
            could have got deleted. (=loosely coupled model.)
            In that scenario, there is no VS reference to be
            cleaned-up.
        """
        for member, vs_cfg in vs_list:
            if member.HasField('vs_uuid'):
                pool_uuid = member.vs_uuid.replace('virtualservice-', 'pool-')

                # Refer Notes 01: Remove SP reference in vs_cfg
                if vs_cfg:
                    index = 0
                    for entry in vs_cfg.sp_pool_uuids:
                        if entry == pool_uuid:
                            LOG.info('Disassociate SP-pool(%s) to VS(%s)',
                                     entry, vs_cfg.name)
                            del vs_cfg.sp_pool_uuids[index]
                            break
                        index += 1
                    self._update(self.request, vs_cfg)

                # Delete child:
                pool = self._pool_checks(pool_uuid)
                if pool:
                    self._delete(self.request, pool)
                    LOG.info('SP-pool(%s) deleted for VS %s',
                             pool_uuid, member.vs_uuid)
        return

    def delete_sp(self, gs_cfg):
        """ Used for SP cleanup related objects """
        if gs_cfg.enabled and gs_cfg.site_persistence_enabled:
            LOG.info('SP-Delete objects of GS %s', gs_cfg.name)
            vs_list = self._get_my_vs_list(gs_cfg)
            self._delete_sp_pool_and_update_vs(vs_list)
        return

    def _sp_pool_update_reqd(self, new_cfg, old_cfg):
        """
        This function checks if there is a difference between the
        old_gs_cfg and new_gs_cfg on the following fields.

        01. Has App Persistence Profile changed?
            Example: Earlier GslbService was associated with
            Profile A.  Now it is associated with Profile B.
            This would mean we would have to update the SP-pool
            and do a downstream update.
        02. Any HM references have changed.?
            Example: Earlier, GslbService had 3 HMs.  Now it
            is associated with a different set of HMs. This
            would mean we would have to update the SP-pool
            and do a downstream update.
        03. Any member list changes?
            Example:  Earlier, there were 2 groups with 2 members
            each.  This would translate to 4 server entries. With
            any membership change (add/delete), we would have to
            regenerate the server list, update the SP-pool and
            do a downstream update.
        04. Gslb PKI object only one for the entire GSLB system.
            So no checks are required.
        """
        # Refer Notes 01
        if (new_cfg.application_persistence_profile_uuid !=
                old_cfg.application_persistence_profile_uuid):
            LOG.info('SP-pool update reqd for GS(%s): GAP ref change',
                     new_cfg.name)
            return True

        # Refer Notes 02
        if (len(new_cfg.health_monitor_uuids) !=
                len(old_cfg.health_monitor_uuids)):
            LOG.info('SP-pool update reqd for GS(%s): HM-refs change',
                     new_cfg.name)
            return True
        else:
            # Any HM reference has changed?
            for new_hm in new_cfg.health_monitor_uuids:
                for old_hm in old_cfg.health_monitor_uuids:
                    if new_hm == old_hm:
                        break
                else:
                    LOG.info('SP-pool update reqd for GS(%s): HM-refs change',
                             new_cfg.name)
                    return True

        # Refer Notes 03
        old_servers = self._get_server_list(old_cfg)
        new_servers = self._get_server_list(new_cfg)
        if len(new_servers) != len(old_servers):
            LOG.info('SP-pool update reqd for GS(%s): server change',
                     new_cfg.name)
            return True
        else:
            for new_server in new_servers:
                for old_server in old_servers:
                    if new_server == old_server:
                        break
                else:
                    LOG.info('SP-pool update reqd for GS(%s): server change',
                             new_cfg.name)
                    return True
        # No change
        return False

    def  _sp_ops_due_vs_diff(self, new_cfg, old_cfg,
                             add_list, del_list, upd_list):
        """
        This function determines if any new vs is added or deleted.

        Notes:
        01. Dont use vs_cfg.uuid because vs_cfg can be None in some
            race-around scenarios.
        02. GS membership: new-vs-member added.
            If a VS has been added to GS, then a SP pool has to be created
            and vs-reference updated.  Appropriate downstream updates have
            to be done.
        03. GS membership changes: An existing vs-member has been removed.
            If a VS has been removed, then the corresponding SP-pool has
            to be removed and vs-reference updated. Appropriate downstream
            updates have to be done.
        04. GS membership: no change;
            Drill down to see if any other fields have changed and do a
            suitable update.
        """
        new_vs_uuids = dict()
        old_vs_uuids = dict()
        old_vs_list = self._get_my_vs_list(old_cfg)
        new_vs_list = self._get_my_vs_list(new_cfg)
        for member, vs_cfg in new_vs_list:
            # Refer Notes 01
            new_vs_uuids[member.vs_uuid] = (member, vs_cfg)
        for member, vs_cfg in old_vs_list:
            # Refer Notes 01
            old_vs_uuids[member.vs_uuid] = (member, vs_cfg)

        for key, new_value in new_vs_uuids.iteritems():
            try:
                old_vs_uuids.pop(key)
                upd_list.append(new_value)
            except KeyError:
                # Entry does not exist; create a SP for it
                add_list.append(new_value)

        # Delete scenario
        if len(old_vs_uuids):
            for key, old_value in old_vs_uuids.iteritems():
                del_list.append(old_value)
        return

    def _sp_enable_disable(self, new_gs_cfg, old_gs_cfg):
        """ Works on the site_persistence_enabled flag """
        if (new_gs_cfg.site_persistence_enabled ==
                old_gs_cfg.site_persistence_enabled):

            # Proceed only if the sp is enabled.
            if new_gs_cfg.site_persistence_enabled:

                #Drill down to see if there is any change
                add_list = []
                del_list = []
                upd_list = []
                self._sp_ops_due_vs_diff(new_gs_cfg, old_gs_cfg,
                                         add_list, del_list, upd_list)

                LOG.info('SP-Update objects of GS %s', new_gs_cfg.name)
                if len(add_list):
                    # new-vs added: Create sp-pool and update-vs-reference
                    self._create_sp_pool_and_update_vs(new_gs_cfg, add_list)

                if len(del_list):
                    # vs-deleted: Delete sp-pool and update-vs-reference
                    self._delete_sp_pool_and_update_vs(del_list)

                if len(upd_list):
                    # No vs-updates; Any pool updates required?
                    if self._sp_pool_update_reqd(new_gs_cfg, old_gs_cfg):
                        servers = self._get_server_list(new_gs_cfg)
                        for _, vs_cfg in upd_list:
                            self._sp_pool_ops(new_gs_cfg, vs_cfg,
                                              servers, ops=GSLB_UPDATE)
        # SP transition to enabled
        elif new_gs_cfg.site_persistence_enabled:
            LOG.info('GS %s: SP turned on', new_gs_cfg.name)
            self.create_sp(new_gs_cfg)

        # SP transition to disabled
        elif old_gs_cfg.site_persistence_enabled:
            LOG.info('GS %s: SP turned off', old_gs_cfg.name)
            self.delete_sp(old_gs_cfg)
        return

    def update_sp(self, new_gs_cfg, old_gs_cfg):
        """
        Function does a diff between new and old to take action.
        We need to address a combination of gs_cfg.enabled and
        sp_enabled flags. Outer function works on gs_cfg.enabled
        while the inner-functions work on the sp_flag.
        """
        if new_gs_cfg.enabled == old_gs_cfg.enabled:
            if new_gs_cfg.enabled:
                self._sp_enable_disable(new_gs_cfg, old_gs_cfg)

        # GS transition to enabled
        elif new_gs_cfg.enabled:
            self.create_sp(new_gs_cfg)

        # GS transition to disabled
        elif old_gs_cfg.enabled:
            self.delete_sp(old_gs_cfg)
        return

    def site_enable_disable_sp_ops(self, new_glb_cfg, old_glb_cfg):
        """
        This function address the site-persistence flows for site enable
        and disable. If there is a transition from enable to disable or
        from disable to enable, then retrieve all the GS(es) that have
        site-persistence enabled and recompute the proxy-pools.

        Notes:
        01. Sites that have been newly added or deleted are not applicable
            in this flow since NO related VS would be associated with the
            GS @ this time. In the case of a new added site, the VS would
            NOT be added yet, while in the case of a deleted site, earlier
            steps (disassociate all VS(es) of a site prior to delete) would
            ensure that no VS of the deleted site would be present in the
            GS.

        02. Each GS has to be parsed twice.  In the first pass we check
            if any GS member is in transition. While in the second pass
            we check if any GS member belongs to this site and if there
            is a member in transtion to recompute the SP-pool for the
            GS member.

            Example:
            ````````
            a. There are 3 sites: S1, S2, S3;
                -> Site S3: is undergoing enable --> disable
            b. There are 3 GS(es) = GS1, GS2, GS3.
                -> GS1 = (S1:VS11, S2:VS21, S3:VS31)
                -> GS2 = (S1:VS12, S2:VS22)
                -> GS3 = (S2:VS23, S3:VS32)

            1st Pass:
            `````````
            The 1st pass will detect that GS1 and GS3's members are in
            transition; Since GS2 has no member on site S3, it will NOT
            flag GS2.

            2nd pass:
            `````````
            In this pass, on site S1, only GS1 will be considered since
            it has a member on S1.  Whereas GS3 is not considered because
            it does NOT have any member on site S1.
        """
        # Refer Notes 01: Any existing sites in enable/disable transition.
        sites_in_transition = dict()
        for site_cfg in new_glb_cfg.sites:
            old_site_cfg = gslb_get_site_cfg(old_glb_cfg,
                                             site_cfg.cluster_uuid)
            if old_site_cfg and old_site_cfg.enabled != site_cfg.enabled:
                sites_in_transition[site_cfg.cluster_uuid] = site_cfg

        # Refer Notes 02
        if len(sites_in_transition):
            my_uuid = get_my_uuid()
            gs_list = GslbService.objects.filter(json_data__site_persistence_enabled=True)
            for gs in gs_list:
                gs_cfg = gs.protobuf()

                # 1st pass: Any GslbPoolMember is in transition?
                member_in_transition = False
                for group in gs_cfg.groups:
                    for member in group.members:
                        if member.cluster_uuid in sites_in_transition:
                            member_in_transition = True
                            break

                # 2nd pass: Any GslbPoolMember belongs to this site?
                if member_in_transition:
                    for group in gs_cfg.groups:
                        for member in group.members:
                            if (member.cluster_uuid == my_uuid
                                    and member.enabled):
                                servers = self._get_server_list(gs_cfg)
                                vs_cfg = self._vs_checks(gs_cfg, member)
                                if vs_cfg:
                                    self._sp_pool_ops(gs_cfg, vs_cfg,
                                                      servers, ops=GSLB_UPDATE)
        return
#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
class GslbSiteOpsSiteConfigView(CreateView, DeleteView, GslbSiteOpsView):
    """
    This class is used to address the siteconfig view. We override the
    CreateView's post api to provide GSLB specific operations
    """
    model = None
    rpc_data = {
        'post': {
            'class_name': 'GslbSiteOps',
            'method_name': 'SiteConfig',
            'field_name': 'gs_ops',
            'exclusive': False,
            'service_name': 'GslbSiteOpsService_Stub'
        },
    }

    def __init__(self):
        """ Initialize the pbs_to_backend structure """
        CreateView.__init__(self)
        DeleteView.__init__(self)
        GslbSiteOpsView.__init__(self)
        return

    def do_post_action(self, request, *args, **kwargs):
        """
        Over-ride and customize the CreateView's do_post_action.
        01. Execute pre_decl handling as required.
        02. Execute actual object handling as required.
        03. Execute post_decl handling as required.

        Notes:
        01. Gslb, Create ==> create_gslb
            GslbService, Update ==> update_gslbservice
            HealthMonitor, Delete ==> delete_healthmonitor
        """
        # Create response
        rsp = RPCResponse()
        rsp.rpc_status = syserr.SYSERR_SUCCESS
        initial_rsp_len = len(rsp.resource.gs_ops_v2.ListFields())

        #  Do basic request processing of the input trigger
        rsp_xlate, msg = self.basic_steps(request.DATA)
        self._pre_decl_hdlr(msg)
        if self.glb_cfg:
            Gslb.objects.select_for_update().get(uuid=self.glb_cfg.uuid)
        if msg.ops != GSLB_DECL:
            for entry in msg.objs:
                # Refer Notes 01
                fn_name = self.ops_2_str(entry.ops) + '_' + entry.ds_name
                obj_fn_hdlr = getattr(self, fn_name)
                field_name = entry.WhichOneof('obj')
                pb = getattr(entry, field_name)
                obj_fn_hdlr(request, pb, rsp)
        else:
            self._post_decl_hdlr(request, msg, rsp)

        # No change in rsp. So, request is a NOP
        final_rsp_len = len(rsp.resource.gs_ops_v2.ListFields())
        if final_rsp_len == initial_rsp_len:
            rsp.rpc_status = syserr.SYSERR_GSLB_METHOD_NOP
        rsp = RPCResponse_xlate(rsp, rsp_xlate)
        return Response(pb2json(rsp), status=status.HTTP_200_OK)
#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
class GslbSiteOpsHealthStatusView(PostActionView, GslbSiteOpsBasicApis):
    """ Health status api in web-portal """
    model = None
    rpc_data = {
        'post': {
            'class_name': 'GslbSiteOps',
            'method_name': 'Site2Site',
            'action_param': 'gs_ops',
            'exclusive': False,
            'service_name': 'GslbSiteHsService_Stub'
        },
    }

    @api_version
    def do_post_action(self, request, *args, **kwargs):
        """
        Overide the do_post_action to do GSLB validation.
        """
        self.basic_steps(request.DATA)
        return PostActionView.do_post_action(self, request, *args, **kwargs)
#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
class GslbSiteOpsValidateView(GslbSiteOpsBasicApis, PostActionView):
    """ BACK-END Interface for site verification """

    def _site_validate(self, request):
        """
        This function handles the site-validate checks;
        01. Role-based validation.
        02. If leader or follower, group-id should match. Otherwise
            flag it as error.
        """
        LOG.info('Received site-validate')

        # Extract the posted data into pb2 format
        my_uuid = get_my_uuid()
        msg = GslbSiteOpsVerify()
        json2pb(msg, request.DATA, replace=True)
        LOG.info('Rxed validate from tx %s: msg %s', msg.tx_uuid, msg)

        msg.rx_sw_version = get_sw_version()
        msg.site_role = GSLB_NOT_A_MEMBER
        msg.rx_uuid = my_uuid

        glb_cfg = self.get_glb_cfg()
        if glb_cfg:
            role = self.get_site_role(glb_cfg, my_uuid)
            msg.site_role = role
            if role != GSLB_NOT_A_MEMBER:
                if msg.glb_uuid != glb_cfg.uuid:
                    errmsg = "Site {x} is member in another Group {y}".format(
                        x=my_uuid, y=glb_cfg.name)
                    LOG.error(errmsg)
                    raise GslbMessageValueError(err=weberr.WEBERR_GSLB_GROUP_CONFLICT,
                                                params={'my_uuid':my_uuid,
                                                        'glb_uuid':glb_cfg.name})
        return pb2json(msg)

    def do_post_action(self, request, *args, **kwargs):
        """ Do GSLB validation """
        obj_data = self._site_validate(request)
        return Response(obj_data, status=status.HTTP_200_OK)
#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
class GslbSiteOpsVerifyView(PostActionView):
    """ FRONT-END exposed to users """

    def _site_verify(self, request):
        """
        This function handles the site-verify.
        01. If addressed to self/local, check and return the
            appropriate values
        02. For remote sites, it sets up a session and does a
            validation by posting a validate message.
        """
        LOG.info('Received site-verify')
        tenant = request.META.get('HTTP_X_AVI_TENANT')
        if tenant is None:
            tenant = 'admin'

        # Extract the posted data into pb2 format
        msg = GslbSiteOpsVerify()
        json2pb(msg, request.DATA, replace=True)

        # Extract and setup session parameters
        site_cfg = GslbSite()
        if msg.HasField('address'):
            site_cfg.address = msg.address
        for from_ip in msg.ip_addresses:
            to_ip = site_cfg.ip_addresses.add()
            to_ip.CopyFrom(from_ip)
        site_cfg.port = msg.port
        site_cfg.username = msg.username
        site_cfg.password = msg.password

        err_msg = None
        try:
            msg = GslbVerifySite(site_cfg, tenant)
        except SyserrHandler as e:
            err_msg = 'LOG:{x}'.format(x=e.errmsg)
        except Exception as e:
            err_msg = 'LOG:{x}'.format(x=e.args)
        finally:
            if err_msg is not None:
                rsp = {'error' : err_msg}
                return HttpResponseForbidden(json.dumps(rsp))
            else:
                return Response(msg, status=status.HTTP_200_OK)

    def do_post_action(self, request, *args, **kwargs):
        """ Do GSLB validation."""
        return self._site_verify(request)
#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
class GslbSiteOpsPurgeView(CreateView, DeleteView, GslbSiteOpsView):
    """
    This operation is a maintenance mode command.  It removes ALL the Gslb
    objects (Gslb, GslbService, GslbGeoDBProfile and other federated objects.)
    The behavior is different on Gslb-leader and Gslb-follower.

    01. Leader: it not only deletes all the configuration on leader, but
        also on all connected followers.
    02. Follower: it deletes all the configuration on member.  No impact
        on any of the connected members.

    Flow:
    =====
    user --> purge --> web-portal --> gslbsiteops --> glb_mgr
                                      rpc=(glb, ghm, gs)
    """
    model = None
    rpc_data = {
        'post': {
            'class_name': 'GslbSiteOps',
            'method_name': 'SiteConfig',
            'field_name': 'gs_ops',
            'exclusive': False,
            'service_name': 'GslbSiteOpsService_Stub'
        },
    }

    def __init__(self):
        """ Initialize the pbs_to_backend structure """
        CreateView.__init__(self)
        DeleteView.__init__(self)
        GslbSiteOpsView.__init__(self)
        return

    def destroy(self, request, *args, **kwargs):
        """
        Over-ride and customize the DeleteView's destroy.
        Do GSLB validation and invoke the Base Class post api to aid
        reusability.  We construct a global-site-ops message with
        glb-delete. No GSLB specific hdr checks are done.
        """
        # dummy rsp for delete_glb
        rsp = RPCResponse()
        rsp.rpc_status = syserr.SYSERR_SUCCESS
        if self.glb_cfg:
            Gslb.objects.select_for_update().get(uuid=self.glb_cfg.uuid)
            self.delete_gslb(request, self.glb_cfg, rsp)
        else:
            raise GslbMessageValueError(err=weberr.WEBERR_GSLB_NOT_CONFIGURED)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @api_version
    def do_post_action(self, request, *args, **kwargs):
        """
        Override the post action.
        """
        rsp = RPCResponse()
        rsp.rpc_status = syserr.SYSERR_SUCCESS
        if self.glb_cfg:
            Gslb.objects.select_for_update().get(uuid=self.glb_cfg.uuid)
            self.delete_gslb(request, self.glb_cfg, rsp)
        else:
            raise GslbMessageValueError(err=weberr.WEBERR_GSLB_NOT_CONFIGURED)
        return Response(pb2json(rsp), status=status.HTTP_200_OK)

#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
class GslbSiteOpsChangeLeaderView(CreateView, GslbSiteOpsView):
    """
    This command is used to change the leader of an existing GSLB group.
    It is used in partition scenarios where we change the leader.

    Example Scenario:
    01. Initially the group is G = {A, B, C, D} with Leader = A.
        The glb-uuid is X.
    02. A partition occurs and splits the group G as follows:
        -> G1 = {A, B} with Leader = A, glb-uuid = x
        -> G2 = {C, D} with Leader = A, glb-uuid = x (A is not reachable)
    03. Operator wants to manage the G2 group; Let us pick C as the new
        leader in the group G2 and make D follow C.
        -> On C: change leader to C (self).
        -> On D: change leader to C.
    04. There is a possibility that there may be one-way connectivity
        or full connectivity with some parts of the G2 with G1 etc.
        -> G1, G2, but may be D may be able to reach B, A while C
           cannot.
        -> It is also possible that the C may reach B, but not A
           and etc.
    05. To avoid inconsistencies between G1 and G2 groups, we use an
        internal view-id to differentiate G1 and G2.  The glb-uuid
        is not changed, but the internal view-id is changed whenever
        the leader is changed.
        -> On C, changeleader to self. This will generate a new internal
           view id.
        -> On D, changeleader to C and provide the view-id from the above
           step.
        -> No other configuration change is permitted.
    06. If the glb-uuid and view-ids don't match, the messages will get
        rejected.  This ensures each group will communicate only with the
        members who have the same glb-uuid and view-id.

    Flow:
    =====
    user --> changeleader --> web-portal --> gslbsiteops --> glb_mgr
                                             rpc=(glb-update)
    """
    model = None
    rpc_data = {
        'post': {
            'class_name': 'GslbSiteOps',
            'method_name': 'SiteConfig',
            'field_name': 'gs_ops',
            'exclusive': False,
            'service_name': 'GslbSiteOpsService_Stub'
        },
    }
    def __init__(self):
        """ Initialize the pbs_to_backend structure """
        CreateView.__init__(self)
        GslbSiteOpsView.__init__(self)
        return

    @api_version
    def do_post_action(self, request, *args, **kwargs):
        """
        Over-ride and customize the CreateView's do_post_action.
        The following steps are executed.

        01. Check if gslb is configured.
        02. Check if controller uuids are valid.
        03. Check if leader-uuid is same as existing leader and view-id
            is same as existing view-id.  If so, then treat it as
            idempotent trigger and move on.
        04. Check if the leader-uuid is same as self. Generate view-id and
            return it. Execute the change in back-end.
        05. Check if the leader-uuid is another leader-uuid.  In this case
            the view-id must be passed. If the view-uuid is not passed,
            reject it.  Otherwise, execute the change in back-end.
        06. Check if the the current site has DNS-VS; Leader change
            can take place ONLY on sites that have DNS-VS because they
            have all the configuration.
        """
        # Refer Notes 01
        glb_cfg = self.glb_cfg
        if not glb_cfg:
            raise GslbMessageValueError(err=weberr.WEBERR_GSLB_NOT_CONFIGURED)
        msg = GslbSiteOpsLeaderChange()
        json2pb(msg, request.DATA, replace=True)

        # Refer Notes 02
        site_cfg = gslb_get_site_cfg(glb_cfg, msg.new_leader, site_type=GSLB_AVI_SITE)
        if not site_cfg:
            raise GslbMessageValueError(
                err=weberr.WEBERR_GSLB_LEADER_NOT_IN_LIST,
                params={'leader': msg.new_leader,
                        'glb_name': glb_cfg.name})

        # Refer Notes 03
        if (msg.view_id == glb_cfg.view_id and
                msg.new_leader == glb_cfg.leader_cluster_uuid):
            msg.details.append("No change in leader-id/view-id")
            rsp_data = pb2json(msg)
            return Response(rsp_data, status=status.HTTP_200_OK)

        # Refer Notes 04
        my_uuid = get_my_uuid()
        if msg.new_leader == my_uuid:
            if my_uuid == glb_cfg.leader_cluster_uuid:
                msg.details.append("No change in leader-id")
                rsp_data = pb2json(msg)
                return Response(rsp_data, status=status.HTTP_200_OK)
            if msg.view_id != 0:
                raise GslbMessageValueError(
                    err=weberr.WEBERR_GSLB_INVALID_VIEW_ID_EQ_0)

            # Refer Notes 06
            if site_cfg.member_type == GSLB_PASSIVE_MEMBER:
                raise GslbMessageValueError(
                    err=weberr.WEBERR_GSLB_MODE_SWITCH_NOT_ALLOWED)
            if site_cfg.enabled is False:
                raise GslbMessageValueError(
                    err=weberr.WEBERR_GSLB_INVALID_SITE_STATE)
            msg.view_id = (int)(get_timestamp()) * (int)(get_ts())
        else:
            # Refer Notes 05
            if msg.view_id == 0:
                raise GslbMessageValueError(
                    err=weberr.WEBERR_GSLB_INVALID_VIEW_ID_NE_0)

        # Update the glb_cfg with the new view-id & owner
        glb_cfg.view_id = msg.view_id
        glb_cfg.leader_cluster_uuid = msg.new_leader

        # Plugin the response-data back
        msg.details.append("Review event-logs for additional information")
        rsp_data = pb2json(msg)

        # Spoof an internal message and throw-away placeholder
        LOG.info('ChangeLeader trigger %s for back-end glb_mgr', msg)
        tmp_rsp = RPCResponse()
        tmp_rsp.rpc_status = syserr.SYSERR_SUCCESS
        self.update_gslb(request, glb_cfg, tmp_rsp)

        return Response(rsp_data, status=status.HTTP_200_OK)
#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
class GslbSiteOpsMaintenanceModeView(CreateView, GslbSiteOpsView):
    """
    This command is used to place the leader in maintenance mode.
    Typically used in upgrade scenarios to ensure no new configuration
    is accepted at the leader when the members are getting upgraded.
    =====
    user --> maintenancemode --> web-portal --> gslbsiteops --> glb_mgr
                                                    rpc=(glb-update)
    """
    model = None
    rpc_data = {
        'post': {
            'class_name': 'GslbSiteOps',
            'method_name': 'SiteConfig',
            'field_name': 'gs_ops',
            'exclusive': False,
            'service_name': 'GslbSiteOpsService_Stub'
        },
    }
    def __init__(self):
        """ Initialize the pbs_to_backend structure """
        CreateView.__init__(self)
        GslbSiteOpsView.__init__(self)
        return

    @api_version
    def do_post_action(self, request, *args, **kwargs):
        """
        Over-ride and customize the CreateView's do_post_action.
        The following steps are executed.

        01. Check if gslb is configured.
        02. Check if cmd is executed on leader.

        Notes:
        01.  Set to the default-value; It invokes default-constructor
             via rhs: glb_cfg.send_interval and reinitializes it in
             the pb via lhs: glb_cfg.send_interval
        """
        # Refer Notes 01
        glb_cfg = self.glb_cfg
        if not glb_cfg:
            raise MessageValueError(err=weberr.WEBERR_GSLB_NOT_CONFIGURED)

        if get_my_uuid() != glb_cfg.leader_cluster_uuid:
            raise MessageValueError(
                err=weberr.WEBERR_GSLB_CMD_APPLICABLE_ON_LEADER)

        msg = GslbSiteOpsMaintenanceMode()
        json2pb(msg, request.DATA, replace=True)
        if glb_cfg.maintenance_mode == msg.enabled:
            msg.details.append('No change in maintenance mode')
        else:
            glb_cfg.maintenance_mode = msg.enabled
            if msg.enabled:
                # Save the old value
                glb_cfg.send_interval_prior_to_maintenance_mode = glb_cfg.send_interval
                glb_cfg.send_interval = msg.send_interval

                # Provide recommendations:
                leader = "Leader"
                active_members = []
                passive_members = []
                for site_cfg in glb_cfg.sites:
                    if site_cfg.member_type == GSLB_PASSIVE_MEMBER:
                        passive_members.append(site_cfg.name)
                    else:
                        if (get_my_uuid() == site_cfg.cluster_uuid and
                                site_cfg.cluster_uuid == glb_cfg.leader_cluster_uuid):
                            leader = site_cfg.name
                        else:
                            active_members.append(site_cfg.name)

                msg.details.append('=========================================================')
                msg.details.append('Maintenance mode enabled: Suggested upgrade order:')
                msg.details.append('=========================================================')
                if passive_members:
                    msg.details.append('Upgrade Avi passive members: {x}'.format(x=passive_members))
                if active_members:
                    msg.details.append('Upgrade Avi active members: {x}'.format(x=active_members))
                msg.details.append('Upgrade Avi leader: {x}'.format(x=leader))
                msg.details.append('=========================================================')
                msg.details.append('Maintenance mode enabled: Change leader candidates:')
                msg.details.append('=========================================================')
                if active_members:
                    msg.details.append('Avi active members {x}'.format(x=active_members))
                msg.details.append('=========================================================')
            else:
                # Refer Notes 01; Restore the old value
                glb_cfg.ClearField('send_interval')
                glb_cfg.send_interval = glb_cfg.send_interval_prior_to_maintenance_mode
                glb_cfg.ClearField('send_interval_prior_to_maintenance_mode')
                msg.details.append('Maintenance mode disabled')

            # Spoof an internal message and throw-away placeholder
            LOG.info('Maintenance mode trigger for back-end glb_mgr: %s:%s',
                     glb_cfg.maintenance_mode, glb_cfg.send_interval)
            tmp_rsp = RPCResponse()
            tmp_rsp.rpc_status = syserr.SYSERR_SUCCESS
            self.update_gslb(request, glb_cfg, tmp_rsp)

        obj_data = pb2json(msg)
        return Response(obj_data, status=status.HTTP_200_OK)
#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
class GslbSiteOpsResyncView(PostActionView):
    """
    This command is used to resync configuration to the Gslb Member.
    =====
    user --> resync --> web-portal --> gslbsiteopsresync --> glb_mgr
                                                    rpc=(site-sync)
    """
    model = None
    rpc_data = {
        'post': {
            'class_name': 'GslbSiteOpsResync',
            'method_name': 'Resync',
            'action_param': 'resync',
            'exclusive': False,
            'service_name': 'GslbSiteOpsService_Stub'
        },
    }
    def __init__(self):
        PostActionView.__init__(self)
        return

    @api_version
    def do_post_action(self, request, *args, **kwargs):
        """
        Over-ride and customize the do_post_action.
        The following steps are executed.
        01. Check if gslb is configured.
        02. Check if cmd is executed on leader.
        03. Check if leader is on maintenance mode.
        04. Check if site is not disabled.
        """
        glb_cfg = get_glb_cfg()
        if not glb_cfg:
            raise MessageValueError(err=weberr.WEBERR_GSLB_NOT_CONFIGURED)

        my_uuid = get_my_uuid()
        if my_uuid != glb_cfg.leader_cluster_uuid:
            raise MessageValueError(
                err=weberr.WEBERR_GSLB_CMD_APPLICABLE_ON_LEADER)

        if glb_cfg.maintenance_mode:
            raise MessageValueError(
                err=weberr.WEBERR_GSLB_IN_MAINTENANCE_MODE)

        msg = GslbSiteOpsResync()
        json2pb(msg, request.DATA, replace=True)
        if msg.cluster_uuid == my_uuid:
            raise MessageValueError(
                err=weberr.WEBERR_GSLB_RESYNC_NOT_APPLICABLE_TO_LEADER)

        for site_cfg in glb_cfg.sites:
            if site_cfg.cluster_uuid == msg.cluster_uuid:
                if not site_cfg.enabled:
                    raise MessageValueError(
                        err=weberr.WEBERR_GSLB_RESYNC_NOT_APPLICABLE_TO_DISABLED_SITE,
                        params={'site_name': site_cfg.name})
                break
        else:
            raise MessageValueError(
                err=weberr.WEBERR_GSLB_RESYNC_INVALID_SITE,
                params={'cluster_uuid': msg.cluster_uuid})

        # Spoof an internal message and throw-away placeholder
        LOG.info('resync trigger for back-end glb_mgr: member %s', msg.cluster_uuid)
        return PostActionView.do_post_action(self, request, *args, **kwargs)
#---------------------------------------------------------------------------
class GslbList(ListView, CreateView, GslbSiteOpsView):
    """
    Background:
    Requirement is to have healthmonitor templates for the GSLB
    feature.  These templates should  be created ONLY if GSLB feature
    is enabled.  Because of this requirement, we cannot use the default
    framework of defining the templates in:
    '/portal/api/fixtures/initial_data.py'

    Instead, a custom_view is used to create the gslb object as
    well as create the healthmonitor objects.

    Operations:
    ==========
    Create leg: Create Gslb as well as default HealthMonitor
                objects.
    Update leg: Update Gslb object. No impact on HealthMonitor
                objects.
    Delete leg: Delete default HealthMonitor objects and then delete
                Gslb object.

    Flow:
    =====
    user --> gslb ops --> web-portal --> gslbsiteops --> glb_mgr
                                             rpc=(glb, ghm)
    """
    model = Gslb
    serializer_class = GslbSerializer
    rpc_data = {
        'post': {
            'class_name': 'GslbSiteOps',
            'method_name': 'SiteConfig',
            'field_name': 'gs_ops',
            'exclusive': False,
            'service_name': 'GslbSiteOpsService_Stub'
        },
    }

    def __init__(self):
        """ Initialize the pbs_to_backend structure """
        ListView.__init__(self)
        CreateView.__init__(self)
        GslbSiteOpsView.__init__(self)
        return

    def create_default_ghm(self, request, tenant_uuid):
        """
        Retrieve the default ghm. Convert it to json and append it
        in request.Data to mimic as if it came from the user.

        Notes:
        01. GslbSystemDefault profiles should explicitly pass the
            system_default=True value for proper system_default
            behavior.
        """
        for entry in GSLB_DEFAULT_GHM_LIST:
            data = entry.get('data')
            ghm_pb2 = HealthMonitorProto()
            json2pb(ghm_pb2, data, replace=True)
            ghm_pb2.tenant_uuid = tenant_uuid
            self._create(request, ghm_pb2,
                         system_default=True,
                         run_default_function=True)

        # Revert it back to the original
        self._init_model_serializer(GslbProto())
        return

    @api_version
    def do_post_action(self, request, *args, **kwargs):
        """
        Override the do_post_action with custom specific changes.
        we reuse the create as much as possible. In addition, we
        create the default healthmonitor objects.
        """
        rsp = self.create(request, *args, **kwargs)
        self.glb_cfg = self.object.protobuf()
        self._pbs_for_backend_ops(GSLB_CREATE, self.glb_cfg, None)
        self.create_default_ghm(request, self.glb_cfg.tenant_uuid)
        return rsp
#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
class GslbDetail(RetrieveView, UpdateView, DeleteView, GslbSiteOpsView):
    """
    Refer to GslbList Notes.
    """
    model = Gslb
    serializer_class = GslbSerializer
    rpc_data = {

        'post': {
            'class_name': 'GslbSiteOps',
            'method_name': 'SiteConfig',
            'field_name': 'gs_ops',
            'exclusive': False,
            'service_name': 'GslbSiteOpsService_Stub'
        }
    }

    def __init__(self):
        """ Initialize the pbs_to_backend structure """
        RetrieveView.__init__(self)
        UpdateView.__init__(self)
        DeleteView.__init__(self)
        GslbSiteOpsView.__init__(self)
        return

    @api_version
    def do_put_action(self, request, *args, **kwargs):
        """
        Override the do_put_action.  Its used in both put and
        patch operations (views.py).
        """
        rsp = self.update(request, *args, **kwargs)
        self.glb_cfg = self.object.protobuf()
        self._pbs_for_backend_ops(GSLB_UPDATE, self.glb_cfg, self.old_pb)
        self.site_enable_disable_sp_ops(self.glb_cfg, self.old_pb)
        return rsp

    def delete_default_ghm(self, request):
        """
        Iterate over all the ghm objects. Check if it is a default
        GHM object and delete it.
        """
        # Extract the default ghm names
        def_ghm_list = list(gslb_get_default_ghms())
        ghm_list = HealthMonitor.objects.filter(name__in=def_ghm_list)
        for ghm in ghm_list:
            LOG.info("Preparing Default Ghm delete %s", ghm.name)
            self._delete(request, ghm, force_delete=True)

        # Revert it back to the original
        self._init_model_serializer(GslbProto())
        return

    def destroy(self, request, *args, **kwargs):
        """
        Delete the default ghm objects and then the glb object. Its
        a LIFO model. So we need to delete the default GHM objects
        and then go ahead with the delete of the GLB object
        """
        # Delete the default GHMs & then the GLB
        self.delete_default_ghm(request)
        pb = self.get_object().protobuf()
        rsp = DeleteView.destroy(self, request, *args, **kwargs)
        self._pbs_for_backend_ops(GSLB_DELETE, pb, None)
        return rsp
#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
class GslbRuntimeInternalView(GetActionView):
    """ Interface to retrieve the GslbRuntime internal status """
    model = Gslb
    serializer_class = GslbSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'GslbRuntimeInternal', 'service_name': 'GslbRpcService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'gslb_internal'}}

class GslbRuntimeDetailView(GetActionView):
    """ Interface to retrieve the GslbRuntime detail status """
    model = Gslb
    serializer_class = GslbSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'GslbRuntimeDetail', 'service_name': 'GslbRpcService_Stub', 'default_filter': 'DETAIL', 'method_name': 'Read', 'response_field': 'gslb_detail', 'filter': ['glb_params_filter']}}

class GslbRuntimeSummaryView(GetActionView):
    """ Interface to retrieve the GslbRuntime summary status """
    model = Gslb
    serializer_class = GslbSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'GslbRuntimeSummary', 'service_name': 'GslbRpcService_Stub', 'default_filter': 'SUMMARY', 'method_name': 'Read', 'response_field': 'gslb_summary'}}
#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
class GslbServiceList(ListView, CreateView, GslbSiteOpsView):
    """
    Prior to site-persistence feature, we were using auto-generated framework.
    This worked because in the traditional CRUD operations, it operated ONLY
    on a single object.  For site-persistence functionality, we will have to
    use custom-views because a single object may operate on multiple objects
    as described below.
     * Create: -> Create GslbService,
              -> Create SP-pool with appropriate associations.
                 (Stitch HM, APP, PKI, VS.SSL)
              -> Associate VS to newly created SP-pool.
                 (Stitch VS --> SP-pool)
    """
    model = GslbService
    serializer_class = GslbServiceSerializer
    rpc_data = {
        'post': {
            'class_name': 'GslbSiteOps',
            'method_name': 'SiteConfig',
            'field_name': 'gs_ops',
            'exclusive': False,
            'service_name': 'GslbSiteOpsService_Stub'
        },
    }

    def __init__(self):
        """ Initialize the pbs_to_backend structure """
        ListView.__init__(self)
        CreateView.__init__(self)
        GslbSiteOpsView.__init__(self)
        return

    @api_version
    def do_post_action(self, request, *args, **kwargs):
        """
        Override the do_post_action with custom specific changes.
        """
        rsp = self.create(request, *args, **kwargs)
        pb = self.object.protobuf()
        self._pbs_for_backend_ops(GSLB_CREATE, pb, None)
        self.create_sp(pb)
        return rsp
#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
class GslbServiceDetail(RetrieveView, UpdateView, DeleteView, GslbSiteOpsView):
    """
    Custom view for Update, Delete:
    * Update: -> Housekeep SP-pool
              -> Housekeep VS --> SP-pool
    * Delete: -> Remove VS to SP-pool association
              -> Delete proxy-pool
              -> Delete GslbService
    * Read:   -> Retrieve GslbService info
    """
    model = GslbService
    serializer_class = GslbServiceSerializer
    rpc_data = {

        'post': {
            'class_name': 'GslbSiteOps',
            'method_name': 'SiteConfig',
            'field_name': 'gs_ops',
            'exclusive': False,
            'service_name': 'GslbSiteOpsService_Stub'
        }
    }

    def __init__(self):
        """ Initialize the pbs_to_backend structure """
        RetrieveView.__init__(self)
        UpdateView.__init__(self)
        DeleteView.__init__(self)
        GslbSiteOpsView.__init__(self)
        return

    @api_version
    def do_put_action(self, request, *args, **kwargs):
        """
        Override the do_put_action.  Its used in both put and
        patch operations (views.py).
        """
        rsp = self.update(request, *args, **kwargs)
        pb = self.object.protobuf()
        self._pbs_for_backend_ops(GSLB_UPDATE, pb, self.old_pb)
        self.update_sp(pb, self.old_pb)
        return rsp

    def destroy(self, request, *args, **kwargs):
        """ Delete the GslbService Object.  """
        # Retrieve parent; initiate children cleanup
        pb = self.get_object().protobuf()
        self.delete_sp(pb)

        # Parent cleanup; Revert it back to the original
        self.kwargs['slug'] = pb.uuid
        self._init_model_serializer(GslbServiceProto())
        rsp = DeleteView.destroy(self, request, *args, **kwargs)
        self._pbs_for_backend_ops(GSLB_DELETE, pb, None)
        return rsp
#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
class GslbServiceRuntimeView(GetActionView):
    """ Retrieve runtime info """
    model = GslbService
    serializer_class = GslbServiceSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'GslbServiceRuntime', 'service_name': 'GslbServiceService_Stub', 'default_filter': 'SUMMARY', 'method_name': 'Read', 'response_field': 'gs_summary', 'filter': ['gs_params_filter']}}

#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
class GslbSiteOpsStaleObjectChecks(GetActionView):
    """
    This operation retrieves the stale objects in datastore.  No RPCs to
    the back-end are initiated.  This command has to be executed on each
    controller cluster and has a local significance.
    """
    model = None
    rpc_data = None

    def do_get_action(self, request, *args, **kwargs):
        """ Override the default do_get_action with stale-object checks. """
        rsp = GslbSiteOpsStaleObjectStatus()
        stale_objects = gslb_stale_object_checks()
        if stale_objects:
            for entry in stale_objects:
                _, key, name = entry #unpack
                rsp.details.append('Stale object {x}/{y}'.format(x=name, y=key))
        else:
            rsp.details.append('Database and Datastore are in sync.')
        return Response(pb2json(rsp), status=status.HTTP_200_OK)

#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
class GslbSiteOpsStaleObjectCleanup(PostActionView):
    """
    This operation cleansup the stale objects in datastore.  No RPCs to
    the back-end are initiated. This command has to be executed on each
    controller cluster and has a local impact.
    """
    model = None
    rpc_data = None

    def do_post_action(self, request, *args, **kwargs):
        """ Override the default do_post_action with stale-object cleanup. """
        rsp = GslbSiteOpsStaleObjectStatus()
        gslb_stale_object_cleanup()
        rsp.details.append('Command execution done; Verify with checks api.')
        return Response(pb2json(rsp), status=status.HTTP_200_OK)

#---------------------------------------------------------------------------
#End of file
