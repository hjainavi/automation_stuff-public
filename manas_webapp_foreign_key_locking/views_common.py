
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


from api.models import (Tenant, TenantSerializer, Alert, Cloud,
                         DebugVirtualService, SCPoolServerStateInfo,
                         SCVsStateInfo)
import api.models as api_models
from permission.models import User, SystemDefaultObject
from avi.rest.views import ListView, CreateView, DetailView
from avi.rest.db_cache import DbCache
from avi.rest.view_utils import MultipleViewCUD, create_default_objects_in_cloud_tenant
from avi.rest.error_list import DataException
from avi.rest.session_utils import invalidate_user_sessions
from avi.infrastructure.db_transaction import db_transaction
import os, sys
import logging
from api.views_macro import protected_tenant_access
from django.db.models import Q

log = logging.getLogger(__name__)

sys.path.append(os.path.dirname(__file__) + '/../../fixtures')



IGNORED_OBJECT_PATHS = [
   '/api/debugcontroller'
]

IGNORED_OBJECT_NAMES = [
    "System-Admin",
    "System-Default-Portal-Cert",
    "Default-Cloud"
]

class TenantList(ListView, CreateView):
    model = Tenant
    serializer_class = TenantSerializer

    def copy_initial_data(self, user):
        tenant_pb = self.object.protobuf()
        if (not (tenant_pb.config_settings.tenant_vrf or
                not tenant_pb.config_settings.se_in_provider_context)):
            return

        clouds = Cloud.objects.all()
        create_default_objects_in_cloud_tenant([self.object], clouds)


    def post(self, request, *args, **kwargs):
        rsp = self.do_post_transaction(request, *args, **kwargs)
        self.run_callback()
        self.copy_initial_data(request.user)
        try:
            admin = User.objects.get(id=1)
            tenant_pb = self.object.protobuf()
            if tenant_pb.local:
                invalidate_user_sessions(admin)
        except:
            log.exception('Add admin role to tenant error:')
        return rsp


class  TenantDetail(DetailView):
    model = Tenant
    serializer_class = TenantSerializer

    def _delete_role(self, request, tenant):
        roles = api_models.Role.objects.filter(tenant_ref=tenant).values('uuid')
        if not roles:
            return
        role_view = MultipleViewCUD(request)
        obj_list = []
        for role in roles:
            req_data = {
                'model_name': 'Role',
                'data': {'uuid': role['uuid']},
                'force_delete': True
            }
            obj_list.append(req_data)
            role_view.process_list_no_txn('delete', tenant, obj_list, request.user)

    def _delete_sys_objs(self, request, tenant, sys_objs):
        if not sys_objs:
            return
        self.macro_view = MultipleViewCUD(request)

        obj_list = []
        for obj in sys_objs:
            req_data = {
                'model_name': obj.object_model,
                'data': {'uuid': obj.object_uuid},
                'force_delete': True
            }
            obj_list.append(req_data)
        self.macro_view.process_list_no_txn('delete', tenant, obj_list, request.user)
        sys_objs.delete()

    def fix_user_default_tenant_ref(self, tenant):
        users = User.objects.filter(default_tenant_ref=tenant)
        if not users:
            return
        for user in users:
            default_ref = None
            user_roles = user.access.exclude(tenant_ref=tenant)
            if user_roles:
                default_ref = user_roles[0].tenant_ref
            user.default_tenant_ref = default_ref
            user.save()

    def do_delete_detail(self, request, *args, **kwargs):
        """
        Also delete Alert objs for this tenant
        """
        tenant_uuid = kwargs.get('slug')
        tenant = Tenant.objects.get(uuid=tenant_uuid)
        alert_objs = Alert.objects.filter(tenant_ref__uuid=tenant_uuid)
        alert_objs.delete()

        sys_objs = SystemDefaultObject.objects.filter(tenant_uuid = tenant_uuid
                                                      ).order_by('-id')
        if kwargs.get('force_delete') or request.QUERY_PARAMS.get('force_delete'):
            sys_objs.delete()
            DebugVirtualService.objects.filter(tenant_ref=tenant).delete()
        else:
            self._delete_sys_objs(request, tenant, sys_objs)

        if kwargs.get('delete_role') or request.QUERY_PARAMS.get('delete_role'):
            self._delete_role(request, tenant)

        self.fix_user_default_tenant_ref(tenant)

        user_list = User.objects.filter(Q(access__tenant_ref__uuid=tenant_uuid) | Q(access__all_tenants=True))
        for user in user_list:
            invalidate_user_sessions(user)

        return super(TenantDetail, self).do_delete_detail(request, *args,
                                                                **kwargs)

    def _delete_all(self, request, args, kwargs):
        @db_transaction
        def _delete_all_alerts(tenant_uuid):
            alert_objs = Alert.objects.filter(tenant_ref__uuid=tenant_uuid)
            alert_objs.delete()

        def _delete_SCStateInfo_objects(tenant_uuid, vs_delete_only=False):
            sc_vs_objs = SCVsStateInfo.objects.filter(tenant_ref__uuid=tenant_uuid)
            sc_vs_objs.delete()
            if not vs_delete_only:
                sc_pool_objs = SCPoolServerStateInfo.objects.filter(tenant_ref__uuid=tenant_uuid)
                sc_pool_objs.delete()

        def _is_internal_object(model_name):
            if (model_name.startswith('debug') or
                model_name in [SCVsStateInfo.__name__.lower(), SCPoolServerStateInfo.__name__.lower()]):
                return True
            return False

        tenant_uuid = kwargs.get('slug')
        tenant = Tenant.objects.get(uuid=tenant_uuid)
        vs_delete_only = False
        db_cache = DbCache()
        _delete_all_alerts(tenant_uuid)
        #block delete if there are SEs, only delete VS
        if api_models.ServiceEngine.objects.filter(tenant_ref=tenant).count()>0:
            vs_delete_only = True
            ref_list = db_cache.get_parents('Tenant', uuid=tenant_uuid,
                                             depth=1,
                                              model_filter=['VirtualService'])
        else:
            ref_list = db_cache.get_parents('Tenant', uuid=tenant_uuid, depth=1)

        macro_view = MultipleViewCUD(None)
        obj_list = []
        for model_name in reversed(api_models.pb_ordered):
            for ref in ref_list:
                if ref.model_name == model_name and not _is_internal_object(model_name.lower()):
                    req_data = {
                    'model_name': ref.model_name,
                    'data': {'uuid': ref.uuid},
                    'force_delete': True
                    }
                    obj_list.append(req_data)
        error_list = macro_view.delete_list(tenant_uuid, obj_list, request.user)
        _delete_SCStateInfo_objects(tenant_uuid, vs_delete_only)
        if error_list:
            log.error('Error when deleting objs in tenant: \n %s' % error_list)
        return vs_delete_only

    @protected_tenant_access
    def delete_tenant_scope(self, request, *args, **kwargs):
        if kwargs.get('force_delete') or request.QUERY_PARAMS.get('force_delete'):
            vs_delete_only = self._delete_all(request, args, kwargs)
            if vs_delete_only:
                raise DataException('There are ServiceEngine in Tenants. Only delete VirtualService')
        rsp = self.do_delete_transaction(request, *args, **kwargs)

        if self.macro_view:
            self.macro_view.run_callback()
        self.run_callback()

        return rsp

    def delete(self, request, *args, **kwargs):
        self.macro_view = None
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        return self.delete_tenant_scope(request, *args, **kwargs)

class TenantInventory(TenantList):
    def get(self, request, *args, **kwargs):
        rsp = super(TenantInventory, self).get(request, *args, **kwargs)
        if rsp.status_code != 200:
            return rsp

        for tenant in rsp.data['results']:
            uuid = tenant.get('uuid')
            query = User.objects.filter(access__tenant_ref__uuid=uuid).exclude(uuid='user-system')
            tenant['users'] = query.count()

            tenant['tenant-admin'] = []
            admin_query = query.filter(access__tenant_ref__uuid=uuid,
                                       access__role_ref__name__in=
                                       ['Tenant-Admin', 'System-Admin']).distinct().values('username')
            for user in admin_query:
                tenant['tenant-admin'].append(user.get('username', ''))
            tenant['non-admin'] = []
            non_admin_query = query.filter(access__tenant_ref__uuid=uuid).exclude(username__in=tenant['tenant-admin']).values('username')
            for user in non_admin_query:
                tenant['non-admin'].append(user.get('username', ''))

        return rsp
