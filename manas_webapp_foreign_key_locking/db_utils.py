
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

from django.core.exceptions import ValidationError
from avi.rest.pb2dict import protobuf2dict_withrefs
from avi.rest.serializers import shorten_camel_case
from avi.rest.view_utils import get_model_from_name
from avi.util.protobuf import dict2protobuf
import json
from avi.util.vs_vip_utils import merge_vs_vip_protobuf

#from django bug: https://code.djangoproject.com/ticket/12030
# fixed commit: https://github.com/django/django/commit/1506c71a95cd7f58fbc6363edf2ef742c58d2487
# Integer field safe ranges by `internal_type` as documented
# in docs/ref/models/fields.txt.
_integer_field_ranges = {
 'IntegerField': (-2147483648, 2147483647),
 'BigIntegerField': (-9223372036854775808, 9223372036854775807),
 'PositiveIntegerField': (0, 2147483647),
 }

def _range_validator(value, int_type):
    min_val, max_val = _integer_field_ranges[int_type]
    if value < min_val:
        raise ValidationError('Input value is smaller than minimum value 0x%X' 
                             % min_val)
    if value > max_val:
        raise ValidationError('Input value is larger than maximum value 0x%X' 
                             % max_val)

def integer_validator(value):
    _range_validator(value, "IntegerField")

def big_integer_validator(value):
    _range_validator(value, "BigIntegerField")

def positive_integer_validator(value):
    _range_validator(value, "PositiveIntegerField")

def save_model_object(model):
    '''
    Add the config and extension as serialized protobuf blob in
    columns of the model object
    '''
    model.pb = model._protobuf()
    model.pb_data = model.pb.SerializeToString()
    if hasattr(model, '_protobuf_extension'):
        model.pb_extension = model._protobuf_extension()
        model.pb_extension_data = model.pb_extension.SerializeToString()
    elif hasattr(model, 'extension') and model.extension:
        model.pb_extension = model.extension._protobuf()
        model.pb_extension_data = model.pb_extension.SerializeToString()

def delete_model_object(model):
    references = getattr(model, 'references', {})
    if not references:
        return
    interested_refs = [ 'refers_to', 'weak_refers_to', 'belongs_to' ]
    m2m_models = []
    for ref, val in references.iteritems():
        if val[0] not in interested_refs:
            continue
        if ref.endswith('uuids'):
            if val[1] not in m2m_models:
                m2m_models.append(val[1])
    print str(m2m_models)
    s_model_name=model._meta.object_name
    for d_model_name in m2m_models:
        t_model_name = shorten_camel_case(s_model_name+d_model_name)
        kwargs={}
        kwargs[s_model_name.lower()]=model
        t_model=get_model_from_name(t_model_name)
        t_objs = t_model.objects.filter(**kwargs)
        if t_objs:
            for obj in t_objs:
                t_objs.delete()

def get_model_object(model, request, use_extension=True, merge_extension=True):
    data = {}
    if model.pb_data:
        pb = model.protobuf()
        limit_fields = []
        if request and 'fields' in request.QUERY_PARAMS:
            fields_s = request.QUERY_PARAMS['fields']
            if isinstance(fields_s, basestring):
                if ',' in fields_s:
                    limit_fields = fields_s.split(',')
                else:
                    limit_fields = [fields_s]

        data = protobuf2dict_withrefs(pb, request, limit_fields=limit_fields)
    if (use_extension and hasattr(model, 'pb_extension_data')
           and model.pb_extension_data):
        pb_extension = model.protobuf_extension()
        extension_data = protobuf2dict_withrefs(pb_extension, request)
        if extension_data:
            if merge_extension:
                data.update(extension_data)
            else:
                data['extension'] = extension_data
    return data 

def get_model_protobuf(model, decrypt=False):
    from avi.util.pb_transform import post_transform
    if not hasattr(model, 'pb'):
        if hasattr(model, 'pb_data') and model.pb_data:
            model.pb = model.pb_class()
            model.pb.ParseFromString(model.pb_data)
        else:
            model.pb = model._protobuf()

    if model.pb.DESCRIPTOR.name == 'VirtualService':
        merge_vs_vip_protobuf(model.pb)

    if decrypt:
        ret_pb = model.pb_class()
        ret_pb.CopyFrom(model.pb)
        post_transform(ret_pb, decrypt_only=True)
        return ret_pb
    return model.pb

def get_model_protobuf_extension(model):
    if not hasattr(model, 'pb_extension'):
        if hasattr(model, 'pb_extension_data') and model.pb_extension_data:
            model.pb_extension = model.pb_extension_class()
            model.pb_extension.ParseFromString(model.pb_extension_data)
        elif hasattr(model, 'extension') and model.extension:
            model.pb_extension = model.extension._protobuf()
        elif hasattr(model, '_protobuf_extension'):
            model.pb_extension = model._protobuf_extension()
    return model.pb_extension

def parse_blob_into_pb(blob_data, pb, repeated=False):
    if not blob_data:
        return
    data = json.loads(blob_data)
    if repeated:
        for msg_data in data:
            new_pb = pb.add()
            dict2protobuf(msg_data, new_pb)
    else:
        dict2protobuf(data, pb)


