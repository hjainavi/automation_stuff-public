
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

import importlib
from api.model_mapping import mmap
from api.pb_file_mapping import pbmap

def import_by_model_name(model_name):
    return _import_model_or_serializer_by_name(model_name)

def _import_model_or_serializer_by_name(name):
    if name.lower() in mmap:
        name, module_path = mmap[name.lower()]
        module = importlib.import_module(module_path)
        model_or_ser = getattr(module, name)
        return model_or_ser
    else:
        raise LookupError

def import_model_and_serializer(model_name):
    model = import_by_model_name(model_name)
    serializer = _import_model_or_serializer_by_name(model_name+'serializer')
    return model, serializer

def import_by_pb_name(pb_name):
    module = importlib.import_module(pbmap[pb_name])
    pbclass = getattr(module, pb_name, None)
    return pbclass
