
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

    
class NetworkProfileList(CreateView, ListView, ):
    model = NetworkProfile
    serializer_class = NetworkProfileSerializer
    rpc_data = {
        
        'post': {
            'class_name': 'NetworkProfile',
            'method_name': 'Create',
            'field_name': 'network_profile',
            'service_name': 'NetworkProfileService_Stub',
            'module': 'avi.protobuf.network_profile_pb2'
        },
            }
    
    
class NetworkProfileDetail(UpdateView, DeleteView, RetrieveView, ):
    model = NetworkProfile
    serializer_class = NetworkProfileSerializer
    rpc_data = {
        
        'put': {
            'class_name': 'NetworkProfile',
            'method_name': 'Update',
            'field_name': 'network_profile',
            'service_name': 'NetworkProfileService_Stub',
            'module': 'avi.protobuf.network_profile_pb2'
        },
        
        'patch': {
            'class_name': 'NetworkProfile',
            'method_name': 'Update',
            'field_name': 'network_profile',
            'service_name': 'NetworkProfileService_Stub',
            'module': 'avi.protobuf.network_profile_pb2'
        },
        
        'delete': {
            'class_name': 'NetworkProfile',
            'method_name': 'Delete',
            'field_name': 'network_profile',
            'service_name': 'NetworkProfileService_Stub',
            'module': 'avi.protobuf.network_profile_pb2'
        },
            }
            
class NetworkProfileInternalView(GetActionView):
    model = NetworkProfile
    serializer_class = NetworkProfileSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'NetworkProfileInternal', 'service_name': 'NetworkProfileService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'network_profile_internal'}}
    
