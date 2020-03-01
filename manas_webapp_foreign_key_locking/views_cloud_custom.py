
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

import logging
import time
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist

from api.models import (Cloud, CloudRuntime,
                        CloudSerializer, CloudRuntimeSerializer, Tenant)
from permission.models import SystemDefaultObject

from avi.protobuf.cloud_objects_pb2 import Cloud as CloudProto
from avi.protobuf.common_pb2 import WRITE_ACCESS, READ_ACCESS
from avi.protobuf.django_internal_pb2 import PERMISSION_CLOUD
from avi.rest.callbacks_custom import CallbackCustom
from avi.rest.db_cache import DbCache
from avi.rest.views import ListView, RetrieveView, CreateView, UpdateView, DeleteView
from avi.rest.view_utils import MultipleViewCUD, create_default_objects_in_cloud_tenant
from avi.rest.url_utils import slug_from_uri
from avi.rest.error_list import DataException, ServerException
from avi.infrastructure.db_transaction import db_transaction

log = logging.getLogger(__name__)

def _has_read_or_write_access_for_cloud(user, tenant):
    if user.is_superuser:
        return True
    for role in map(lambda r: r.role_ref, user.access.filter(Q(tenant_ref=tenant) | Q(all_tenants=True))):
        if not role:
            continue
        role_pb = role.protobuf()
        for p in role_pb.privileges:
            if p.resource == PERMISSION_CLOUD:
                if p.type == WRITE_ACCESS:
                    return True
                if p.type == READ_ACCESS:
                    return True
    return False

_PUBLIC_FIELDS = ['uuid', 'url', 'name', 'vtype', 'tenant_ref', 'apic_mode']
_PUBLIC_VCENTER_FIELDS = ['vcenter_url', 'privilege', 'datacenter_ref']
def _clean_cloud_data(cloud_data):
    for f_name in cloud_data.keys():
        if f_name not in _PUBLIC_FIELDS:
            if f_name == 'vcenter_configuration':
                vcenter_data = cloud_data['vcenter_configuration']
                if not vcenter_data:
                    continue
                for sub_f_name in vcenter_data.keys():
                    if sub_f_name not in _PUBLIC_VCENTER_FIELDS:
                        vcenter_data.pop(sub_f_name)
            else:
                cloud_data.pop(f_name, None)

class CloudList(ListView, CreateView):
    model = Cloud
    serializer_class = CloudSerializer
    rpc_data = {}

    def _create_default_objects(self):
        pb = self.object.protobuf()
        if pb.name == 'Default-Cloud' and pb.tenant_uuid == 'admin':
            return
        tenants = Tenant.objects.all()
        create_default_objects_in_cloud_tenant(tenants, [self.object])

    def post(self, request, *args, **kwargs):
        rsp = self.do_post_transaction(request, *args, **kwargs)
        self.run_callback()
        self._create_default_objects()

        return rsp

    def get(self, request, *args, **kwargs):
        kwargs['permission'] = 'PERMISSION_EXEMPT'
        rsp = super(CloudList, self).do_get_list(request, *args, **kwargs)
        if not _has_read_or_write_access_for_cloud(request.user, self.tenant):
            for obj in rsp.data.get('results', []):
                _clean_cloud_data(obj)
        return rsp

class CloudDetail(RetrieveView, UpdateView, DeleteView):
    model = Cloud
    serializer_class = CloudSerializer
    rpc_data = {}

    def get(self, request, *args, **kwargs):
        kwargs['permission'] = 'PERMISSION_EXEMPT'
        rsp = super(CloudDetail, self).do_get_detail(request, *args, **kwargs)
        if not _has_read_or_write_access_for_cloud(request.user, self.tenant):
            _clean_cloud_data(rsp.data)
        return rsp

    def delete_sys_objs(self, request, sys_objs, cloud):
        self.macro_view = None
        if not sys_objs:
            return
        self.macro_view = MultipleViewCUD(request)

        obj_list = []
        for obj in sys_objs:
            req_data = {
                'model_name': obj.object_model,
                'data': {'uuid': obj.object_uuid,
                         'tenant_ref': '/api/tenant/%s' % obj.tenant_uuid
                          },
                'force_delete': True
            }
            obj_list.append(req_data)
            tenants = Tenant.objects.filter(uuid= obj.tenant_uuid)
            if tenants:
                tenant = tenants[0]
            else:
                continue
        self.macro_view.process_list_no_txn('delete', tenant, obj_list, request.user, cloud=cloud.uuid)
        sys_objs.delete()

    CLOUD_CONFIG = ['VirtualService', 'Pool', 'ServiceEngine', 'ServiceEngineGroup',
                    'VrfContext']
    def _config_ref_check(self, cloud_pb, db_cache, default_uuids):
        """
        Block delete if there are config objects in this cloud, or SE Group is not empty
        """
        ref_list = db_cache.get_parents('Cloud', uuid=cloud_pb.uuid,
                                       model_filter=self.CLOUD_CONFIG, depth=1)
        name_list = []
        for ref in ref_list:
            if ref.uuid not in default_uuids:
                try:
                    name_list.append(str(ref.model_name + ' ' + ref.name()))
                except ObjectDoesNotExist:
                    log.error('%s %s in db-cache but not in db',
                              ref.model_name, ref.uuid)
        if name_list:
            msg = 'Cannot delete, object is referred by: %s' % str(name_list)
            raise DataException(msg)
        seg_refs = db_cache.get_parents('Cloud', uuid=cloud_pb.uuid,
                                       model_filter=['ServiceEngineGroup'],
                                       depth=1)
        for seg in seg_refs:
            if seg.name() == 'Default-Group':
                se_refs = db_cache.get_parents('ServiceEngineGroup', uuid=seg.uuid,
                                               model_filter=['ServiceEngine'],
                                               depth=1)
                if se_refs:
                    raise DataException('Default ServiceEngineGroup in this Cloud still has ServiceEngine')

    def _vcenter_delete(self, cloud_pb):
        new_pb = CloudProto()
        new_pb.CopyFrom(cloud_pb)
        new_pb.ClearField('vcenter_configuration')
        cloud_callback = CallbackCustom.Cloud()
        cloud_callback.validate_vcenter(new_pb, cloud_pb)
        time.sleep(10)

    def _is_runtime(self, model_name):
        if model_name == 'Network' or model_name.startswith('VIMgr'):
            return True
        else:
            return False

    def _verify_vcenter_delete(self, uuid, db_cache, runtime_only=False):
        MAX_TRIES = 15
        finished = False
        refs = []
        for i in range(0, MAX_TRIES):
            refs = db_cache.get_parents('Cloud', uuid=uuid, depth=1)
            if runtime_only:
                finished = True
                for ref in refs:
                    if self._is_runtime(ref.model_name):
                        finished = False
                        break
            elif len(refs) == 0:
                finished = True
            if finished:
                break
            time.sleep(15)

        if not finished:
            refs = [(r.uuid, r.model_name)  for r in refs]
            log.error('Remaining Cloud refs: %s' % refs)
            raise ServerException('Cloud VCenter clean up is not successful')

    @db_transaction
    def do_delete_transaction(self, request, *args, **kwargs):
        """
        Block if there is config objects in this cloud
        Delete default objs for this cloud
        """
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        cloud_uuid = kwargs.get('slug')
        cloud = Cloud.objects.get(uuid=cloud_uuid)
        cloud_pb = cloud.protobuf()
        sys_objs = SystemDefaultObject.objects.filter(cloud_uuid = cloud_uuid)
        model_list = [name.lower() for name in self.CLOUD_CONFIG]
        default_uuids = [obj.object_uuid for obj in sys_objs
                          if obj.object_model in model_list]
        db_cache = DbCache()
        self._config_ref_check(cloud_pb, db_cache, default_uuids)
        if cloud_pb.HasField('vcenter_configuration'):
            self._vcenter_delete(cloud_pb)
            self._verify_vcenter_delete(cloud_pb.uuid, db_cache, runtime_only=True)
        self.delete_sys_objs(request, sys_objs, cloud)

        if cloud_pb.HasField('vcenter_configuration'):
            self._verify_vcenter_delete(cloud_pb.uuid, db_cache)
        rsp = super(CloudDetail, self).destroy(request, *args, **kwargs)

        if self.macro_view:
            self.macro_view.run_callback()
        return rsp

class CloudRuntimeList(ListView, ):
    model = CloudRuntime
    serializer_class = CloudRuntimeSerializer
    rpc_data = {}


class CloudRuntimeDetail(RetrieveView, ):
    model = CloudRuntime
    serializer_class = CloudRuntimeSerializer
    rpc_data = {}
