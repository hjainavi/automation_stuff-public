
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

    
class IpAddrGroupList(ListView, CreateView):
    model = IpAddrGroup
    serializer_class = IpAddrGroupSerializer
    rpc_data = {
        
        'post': {
            'class_name': 'IpAddrGroup',
            'method_name': 'Create',
            'field_name': 'ip_addr_group',
            'service_name': 'IpAddrGroupService_Stub',
            'module': 'avi.protobuf.match_pb2'
        },
            }
    
    
class IpAddrGroupDetail(RetrieveView, UpdateView, DeleteView):
    model = IpAddrGroup
    serializer_class = IpAddrGroupSerializer
    rpc_data = {
        
        'put': {
            'class_name': 'IpAddrGroup',
            'method_name': 'Update',
            'field_name': 'ip_addr_group',
            'service_name': 'IpAddrGroupService_Stub',
            'module': 'avi.protobuf.match_pb2'
        },
        
        'patch': {
            'class_name': 'IpAddrGroup',
            'method_name': 'Update',
            'field_name': 'ip_addr_group',
            'service_name': 'IpAddrGroupService_Stub',
            'module': 'avi.protobuf.match_pb2'
        },
        
        'delete': {
            'class_name': 'IpAddrGroup',
            'method_name': 'Delete',
            'field_name': 'ip_addr_group',
            'service_name': 'IpAddrGroupService_Stub',
            'module': 'avi.protobuf.match_pb2'
        },
            }
            
    
class StringGroupList(ListView, CreateView):
    model = StringGroup
    serializer_class = StringGroupSerializer
    rpc_data = {
        
        'post': {
            'class_name': 'StringGroup',
            'method_name': 'Create',
            'field_name': 'string_group',
            'service_name': 'StringGroupService_Stub',
            'module': 'avi.protobuf.match_pb2'
        },
            }
    
    
class StringGroupDetail(RetrieveView, UpdateView, DeleteView):
    model = StringGroup
    serializer_class = StringGroupSerializer
    rpc_data = {
        
        'put': {
            'class_name': 'StringGroup',
            'method_name': 'Update',
            'field_name': 'string_group',
            'service_name': 'StringGroupService_Stub',
            'module': 'avi.protobuf.match_pb2'
        },
        
        'patch': {
            'class_name': 'StringGroup',
            'method_name': 'Update',
            'field_name': 'string_group',
            'service_name': 'StringGroupService_Stub',
            'module': 'avi.protobuf.match_pb2'
        },
        
        'delete': {
            'class_name': 'StringGroup',
            'method_name': 'Delete',
            'field_name': 'string_group',
            'service_name': 'StringGroupService_Stub',
            'module': 'avi.protobuf.match_pb2'
        },
            }
            
    
class MicroServiceGroupList(ListView, CreateView):
    model = MicroServiceGroup
    serializer_class = MicroServiceGroupSerializer
    rpc_data = {
        
        'post': {
            'class_name': 'MicroServiceGroup',
            'method_name': 'Create',
            'field_name': 'microservice_group',
            'service_name': 'MicroServiceGroupService_Stub',
            'module': 'avi.protobuf.match_pb2'
        },
            }
    
    
class MicroServiceGroupDetail(RetrieveView, UpdateView, DeleteView):
    model = MicroServiceGroup
    serializer_class = MicroServiceGroupSerializer
    rpc_data = {
        
        'put': {
            'class_name': 'MicroServiceGroup',
            'method_name': 'Update',
            'field_name': 'microservice_group',
            'service_name': 'MicroServiceGroupService_Stub',
            'module': 'avi.protobuf.match_pb2'
        },
        
        'patch': {
            'class_name': 'MicroServiceGroup',
            'method_name': 'Update',
            'field_name': 'microservice_group',
            'service_name': 'MicroServiceGroupService_Stub',
            'module': 'avi.protobuf.match_pb2'
        },
        
        'delete': {
            'class_name': 'MicroServiceGroup',
            'method_name': 'Delete',
            'field_name': 'microservice_group',
            'service_name': 'MicroServiceGroupService_Stub',
            'module': 'avi.protobuf.match_pb2'
        },
            }
            
class MicroServiceGroupDetailView(GetActionView):
    model = MicroServiceGroup
    serializer_class = MicroServiceGroupSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'MicroServiceGroupDetail', 'service_name': 'MicroServiceGroupService_Stub', 'default_filter': 'DETAIL', 'method_name': 'Read', 'response_field': 'msg_detail', 'filter': ['se_params_filter']}}
    
