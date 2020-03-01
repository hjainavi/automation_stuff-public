
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

    
class ServiceEngineGroupList(ListView, CreateView):
    model = ServiceEngineGroup
    serializer_class = ServiceEngineGroupSerializer
    rpc_data = {
        
        'post': {
            'class_name': 'ServiceEngineGroup',
            'method_name': 'Create',
            'field_name': 'service_engine_group',
            'service_name': 'SeResMgrService_Stub',
            'module': 'avi.protobuf.se_group_pb2'
        },
            }
    
    
class ServiceEngineGroupDetail(RetrieveView, UpdateView, DeleteView):
    model = ServiceEngineGroup
    serializer_class = ServiceEngineGroupSerializer
    rpc_data = {
        
        'put': {
            'class_name': 'ServiceEngineGroup',
            'method_name': 'Update',
            'field_name': 'service_engine_group',
            'service_name': 'SeResMgrService_Stub',
            'module': 'avi.protobuf.se_group_pb2'
        },
        
        'patch': {
            'class_name': 'ServiceEngineGroup',
            'method_name': 'Update',
            'field_name': 'service_engine_group',
            'service_name': 'SeResMgrService_Stub',
            'module': 'avi.protobuf.se_group_pb2'
        },
        
        'delete': {
            'class_name': 'ServiceEngineGroup',
            'method_name': 'Delete',
            'field_name': 'service_engine_group',
            'service_name': 'SeResMgrService_Stub',
            'module': 'avi.protobuf.se_group_pb2'
        },
            }
        
class ServiceEngineGroupRedistributeView(PostActionView):
    model = ServiceEngineGroup
    serializer_class = ServiceEngineGroupSerializer
    rpc_data = {'post': {'class_name': 'ServiceEngineGroup', 'method_name': 'Redistribute', 'exclusive': False, 'service_name': 'SeResMgrService_Stub'}}
    
class ServiceEngineGroupClearView(PostActionView):
    model = ServiceEngineGroup
    serializer_class = ServiceEngineGroupSerializer
    rpc_data = {'post': {'class_name': 'ServiceEngineGroup', 'method_name': 'Clear', 'exclusive': False, 'service_name': 'SeResMgrService_Stub'}}
        
class ServiceEngineGroupRuntimeView(GetActionView):
    model = ServiceEngineGroup
    serializer_class = ServiceEngineGroupSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'ServiceEngineGroupRuntime', 'service_name': 'SeResMgrService_Stub', 'default_filter': 'SUMMARY', 'method_name': 'Read', 'response_field': 'se_group_runtime'}}
    
class ServiceEngineGroupRuntimeClearView(PostActionView):
    model = ServiceEngineGroup
    serializer_class = ServiceEngineGroupSerializer
    rpc_data = {'post': {'class_name': 'ServiceEngineGroupRuntime', 'method_name': 'Clear', 'exclusive': False, 'service_name': 'SeResMgrService_Stub'}}
    
