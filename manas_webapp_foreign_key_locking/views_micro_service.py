
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

#GENERATED FILE
#pylint:  skip-file
from api.models import *
from avi.rest.views import *

    
class MicroServiceList(ListView, CreateView):
    model = MicroService
    serializer_class = MicroServiceSerializer
    rpc_data = {
        
        'post': {
            'class_name': 'MicroService',
            'method_name': 'Create',
            'field_name': 'microservice',
            'service_name': 'MicroServiceService_Stub',
            'module': 'avi.protobuf.micro_service_pb2'
        },
            }
    
    
class MicroServiceDetail(RetrieveView, UpdateView, DeleteView):
    model = MicroService
    serializer_class = MicroServiceSerializer
    rpc_data = {
        
        'put': {
            'class_name': 'MicroService',
            'method_name': 'Update',
            'field_name': 'microservice',
            'service_name': 'MicroServiceService_Stub',
            'module': 'avi.protobuf.micro_service_pb2'
        },
        
        'patch': {
            'class_name': 'MicroService',
            'method_name': 'Update',
            'field_name': 'microservice',
            'service_name': 'MicroServiceService_Stub',
            'module': 'avi.protobuf.micro_service_pb2'
        },
        
        'delete': {
            'class_name': 'MicroService',
            'method_name': 'Delete',
            'field_name': 'microservice',
            'service_name': 'MicroServiceService_Stub',
            'module': 'avi.protobuf.micro_service_pb2'
        },
            }
            
class MicroServiceDetailView(GetActionView):
    model = MicroService
    serializer_class = MicroServiceSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'MicroServiceDetail', 'service_name': 'MicroServiceService_Stub', 'default_filter': 'DETAIL', 'method_name': 'Read', 'response_field': 'ms_detail', 'filter': ['se_params_filter']}}
    
class MicroServiceInternalView(GetActionView):
    model = MicroService
    serializer_class = MicroServiceSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'MicroServiceInternal', 'service_name': 'MicroServiceService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'ms_internal', 'filter': ['se_params_filter']}}
    
