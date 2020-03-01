
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
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response

from api.pb_ordered import pb_ordered
from api.model_mapping_util import import_by_model_name
from permission.models import SystemDefaultObject
from avi.rest.error_list import DataException
from avi.rest.view_utils import MultipleViewCUD
from avi.rest.db_cache import DbCache
import avi.rest.views as views
from avi.protobuf import options_pb2
from api.models import Tenant
from avi.rest.pb2model import protobuf2model
from avi.infrastructure.db_transaction import db_transaction

log = logging.getLogger(__name__)

@db_transaction
def enter_macro(tenant_name):
    tenant_obj = Tenant.objects.select_for_update().get(name=tenant_name)
    tenant_pb = tenant_obj.protobuf()
    tenant_ext_pb = tenant_obj.protobuf_extension()
    if tenant_ext_pb.tenant_force_delete_in_progress:
        raise Exception("Tenant Delete in progress!")
    else:
        tenant_ext_pb.macro_in_progress += 1
        protobuf2model(tenant_pb, tenant_ext_pb, False, skip_save_diff=True)

@db_transaction
def exit_macro(tenant_name):
    tenant_obj = Tenant.objects.select_for_update().get(name=tenant_name)
    tenant_pb = tenant_obj.protobuf()
    tenant_ext_pb = tenant_obj.protobuf_extension()
    tenant_ext_pb.macro_in_progress -= 1
    protobuf2model(tenant_pb, tenant_ext_pb, False, skip_save_diff=True)

@db_transaction
def tenant_force_delete(tenant_uuid):
    tenant_obj = Tenant.objects.select_for_update().get(uuid=tenant_uuid)
    tenant_pb = tenant_obj.protobuf()
    tenant_ext_pb = tenant_obj.protobuf_extension()
    if tenant_ext_pb.macro_in_progress > 0:
        raise Exception('Macro operation in progess!')
    else:
        tenant_ext_pb.tenant_force_delete_in_progress = True
        protobuf2model(tenant_pb, tenant_ext_pb, False, skip_save_diff=True)

def protected_tenant_access(f):
    def _tenant_delete_protect(*args, **kwargs):
        if 'macro' in args[1].path:
            tenant_name = args[0].tenant.name
            enter_macro(tenant_name)
            try:
                rsp = f(*args, **kwargs)
                #rsp = f(_obj, _req, _args, kwargs=_kwargs)
            finally:
                exit_macro(tenant_name)
        elif 'tenant' in args[1].path:
            tenant_uuid = kwargs.get('slug')
            tenant_force_delete(tenant_uuid)
            rsp = f(*args, **kwargs)
        return rsp
    return _tenant_delete_protect

def _custom_data_fix(model_name, data):
    """
    Fix input data before call the views
    Main use is to clean up UI generated fields
    """
    if not data:
        return
    if model_name == 'Pool':
        name = data.get('name', '')
        if ':' in name:
            name = name.replace(':', '')
            data['name'] = name

def _get_pb_class_from_name(pb_name):
    try:
        model = import_by_model_name(pb_name)
    except LookupError:
        raise DataException("Top-level object type %s not found" % pb_name)

    if hasattr(model, 'pb_class') and model.pb_class:
        pb_class = model.pb_class
    else:
        raise DataException('Object type %s is not supported for macro api:'
                            ' No links to protobuf class')
    return pb_class

class NestedObjectList(views.CreateView):
    """
    POST/PUT one object that contained other object as data in its referred fields
    """

    def _add_data_to_list(self, obj_data, model_name, obj_list):
        data = {
            'model_name' : model_name,
            'name' : obj_data['name'],
            'data': obj_data
        }
        obj_list.append(data)

    def _create_ref_link(self, obj_data, model_name):
        obj_name = obj_data.get('name')
        ref_link = '/api/%s?name=%s' % (model_name.lower(), obj_name)
        return ref_link

    def fix_related_fields(self, pb_des, data, obj_list):
        """
        Data can contained referred field data such as pool_ref_data
        If this obj_ref_data field is None, do nothing
        If obj_ref_data field has value
         Remove obj_ref_data field from data
         Recursively run this func inside obj_ref_data
         Add obj_ref_data to obj list
        """

        for field_name in pb_des.fields_by_name:
            field_desc = pb_des.fields_by_name[field_name]
            if field_desc.type == field_desc.TYPE_MESSAGE:
                if not data.get(field_name):
                    continue
                field_val = data.get(field_name)
                if field_desc.label == field_desc.LABEL_REPEATED:
                    for val in field_val:
                        self.fix_related_fields(field_desc.message_type,
                            val, obj_list)
                else:
                    self.fix_related_fields(field_desc.message_type, field_val,
                                             obj_list)

            model_name = None
            if (field_desc.GetOptions().Extensions[options_pb2.refers_to]):
                model_name = field_desc.GetOptions().Extensions[options_pb2.refers_to]
            elif (field_desc.GetOptions().Extensions[options_pb2.weak_refers_to]):
                model_name = field_desc.GetOptions().Extensions[options_pb2.weak_refers_to]
            elif (field_desc.GetOptions().Extensions[options_pb2.belongs_to]):
                model_name = field_desc.GetOptions().Extensions[options_pb2.belongs_to]
            elif (field_desc.GetOptions().Extensions[options_pb2.hyperlink_to]):
                model_name = field_desc.GetOptions().Extensions[options_pb2.hyperlink_to]
            if not model_name:
                continue

            ref_name = field_desc.name.replace('uuid', 'ref')
            ref_data_name = ref_name + "_data"

            if not data.get(ref_data_name):
                continue
            ref_data = data.pop(ref_data_name)

            ref_pb_class = _get_pb_class_from_name(model_name)
            ref_pb_des = ref_pb_class.DESCRIPTOR
            if field_desc.label == field_desc.LABEL_REPEATED:
                data[ref_name] = []
                for subobj_data in ref_data:
                    _custom_data_fix(model_name, subobj_data)
                    ref_link = self._create_ref_link(subobj_data, model_name)
                    data[ref_name].append(ref_link)
                    self.fix_related_fields(ref_pb_des, subobj_data, obj_list)
                    self._add_data_to_list(subobj_data, model_name,
                                                obj_list)
            else:
                _custom_data_fix(model_name, ref_data)
                ref_link = self._create_ref_link(ref_data, model_name)
                data[ref_name] = ref_link
                self.fix_related_fields(ref_pb_des, ref_data, obj_list)
                self._add_data_to_list(ref_data, model_name, obj_list)

    def convert_nested_to_list(self, request):
        """
        Converted nested object data that contains other objects in refer_to field,
        to a flat list of object data
        """
        obj_list = []
        data = request.DATA.copy() #need to modify

        model_name = data.get('model_name')
        if not model_name:
            if request.META.get('HTTP_X_AVI_USERAGENT') == 'UI':
                model_name = 'virtualservice'
                data['model_name'] = model_name
            else:
                raise DataException("Input object does not have model_name field")
        pb_class = _get_pb_class_from_name(model_name)
        self.fix_related_fields(pb_class.DESCRIPTOR, data.get('data', {}), obj_list)
        obj_list.append(data)
        return obj_list

    @db_transaction
    def _process_list_txn(self, request, obj_list, method):
        original_method = None
        user_agent = request.META.get('HTTP_X_AVI_USERAGENT')
        if user_agent == 'UI':
            original_method = request.method.lower()

        return self.macro_view.process_list_no_txn(method, self.tenant,
                                                   obj_list, request.user, original_method=original_method)

    @protected_tenant_access
    def _process_nested_view_tenant_scope(self, request, *args, **kwargs):
        self.macro_view = MultipleViewCUD(request)
        obj_list = self.convert_nested_to_list(request)
        rsp_data = self._process_list_txn(request, obj_list, 'post')
        self.macro_view.run_callback()
        return rsp_data

    def _process_nested_view(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        return self._process_nested_view_tenant_scope(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        rsp_data = self._process_nested_view(request, *args, **kwargs)
        return Response(rsp_data, status=201)

    def put(self, request, *args, **kwargs):
        rsp_data = self._process_nested_view(request, *args, **kwargs)
        return Response(rsp_data, status=200)

    def convert_nested_to_delete_list(self, request):
        """
        Create a list of objects to be delete
        This list has the main object and children objects that:
        . Not a system type or default object
        . Use somewhere else - has parent objects that not in this list
        . Optional: if user use created_by filter, this field in obj need to match
        """
        data = request.DATA.copy() #need to modify
        model_name = data.get('model_name', '')
        if not model_name:
            raise DataException("Input object does not have model_name field")
        try:
            model = import_by_model_name(model_name)
        except LookupError:
            raise DataException("Model name %s not found" % model_name)

        main_uuid = None
        if data.get('data', {}).get('uuid'):
            main_uuid = data['data']['uuid']
        elif data.get('data', {}).get('name'):
            uuids = model.objects.filter(tenant_ref=self.tenant,
                        name=data['data']['name']).values_list('uuid', flat=True)
            if uuids:
                main_uuid = uuids[0]
            else:
                raise DataException("Input object does not exist -- cannot delete")
        else:
            raise DataException('Need uuid or name of the main object')
        default_objs = SystemDefaultObject.objects.all()
        default_uuids = [tobj.object_uuid for tobj in default_objs if tobj.tenant_uuid == 'admin' and tobj.default]
        db_cache = DbCache()
        ref_list = db_cache.get_children(model_name, uuid=main_uuid)
        uuid_list = [ref.uuid for ref in ref_list]
        #log.error('uuid list %s ' % uuid_list)
        delete_list = []
        for subobj_ref in ref_list:
            if not subobj_ref.model_name:
                continue
            if subobj_ref.model_name in ['Tenant', 'Cloud', 'ServiceEngine',
                                          'Network', 'NetworkRuntime', 'VsVip']:
                continue
            if subobj_ref.model_name.startswith('VIMgr'):
                continue
            if subobj_ref.uuid in default_uuids:
                continue
            delete = True
            subref_list = db_cache.get_parents(subobj_ref.model_name,
                                                uuid=subobj_ref.uuid)
            #log.error('SUBREF for %s : %s' % (subobj_ref.uuid, subref_list))
            for subref in subref_list:
                if subref.uuid not in uuid_list and subref.uuid != main_uuid:
                    delete = False
                    break

            if delete and self.filter_created_by:
                try:
                    obj_pb = subobj_ref.obj_ref().protobuf()
                    created_by = getattr(obj_pb, 'created_by', '')
                    if created_by != self.filter_created_by:
                        continue
                except ObjectDoesNotExist:
                    continue

            if delete:
                delete_list.append(subobj_ref)
        obj_list = [data]
        for type_name in reversed(pb_ordered):
            sorted_list = []
            for ref in delete_list:
                if ref.model_name == type_name:
                    obj_data = {
                        'model_name' : ref.model_name,
                        'data': {'uuid' : ref.uuid}
                    }
                    sorted_list.append(obj_data)
            sorted_list.sort(key=lambda obj_data: len(db_cache.get_parents(obj_data['model_name'], slug=obj_data['data']['uuid'], model_filter=[obj_data['model_name']])))
            obj_list.extend(sorted_list)
        return obj_list

    def delete_all_objects(self, model_name):
        try:
            model = import_by_model_name(model_name)
        except LookupError:
            raise DataException("Model name %s not found" % model_name)

        objs = model.objects.filter(tenant_ref=self.tenant)
        objs.delete()

    @protected_tenant_access
    def _delete_tenant_scope(self, request, *args, **kwargs):
        model_name = request.DATA.get('model_name', '')
        self.macro_view = MultipleViewCUD(request)

        if request.QUERY_PARAMS.get('created_by'):
            self.filter_created_by = request.QUERY_PARAMS.get('created_by')
        else:
            self.filter_created_by = None

        if request.QUERY_PARAMS.get('filter', '')  == 'all':
            if model_name.lower()  == 'alert':
                self.delete_all_objects(model_name)
                return Response(status=204)
            else:
                raise DataException("Delete with filter all not supported for model_name: %s" % model_name)

        obj_list = self.convert_nested_to_delete_list(request)
        #log.error('delete list %s ' % obj_list)
        rsp_data = self._process_list_txn(request, obj_list, 'delete')
        self.macro_view.run_callback()
        return Response(rsp_data, status=204)


    def delete(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        return self._delete_tenant_scope(request, *args, **kwargs)
