
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

    
class ApplicationProfileList(ListView, CreateView):
    model = ApplicationProfile
    serializer_class = ApplicationProfileSerializer
    rpc_data = {
        
        'post': {
            'class_name': 'ApplicationProfile',
            'method_name': 'Create',
            'field_name': 'application_profile',
            'service_name': 'ApplicationProfileService_Stub',
            'module': 'avi.protobuf.application_profile_pb2'
        },
            }
    
    
class ApplicationProfileDetail(RetrieveView, UpdateView, DeleteView):
    model = ApplicationProfile
    serializer_class = ApplicationProfileSerializer
    rpc_data = {
        
        'put': {
            'class_name': 'ApplicationProfile',
            'method_name': 'Update',
            'field_name': 'application_profile',
            'service_name': 'ApplicationProfileService_Stub',
            'module': 'avi.protobuf.application_profile_pb2'
        },
        
        'patch': {
            'class_name': 'ApplicationProfile',
            'method_name': 'Update',
            'field_name': 'application_profile',
            'service_name': 'ApplicationProfileService_Stub',
            'module': 'avi.protobuf.application_profile_pb2'
        },
        
        'delete': {
            'class_name': 'ApplicationProfile',
            'method_name': 'Delete',
            'field_name': 'application_profile',
            'service_name': 'ApplicationProfileService_Stub',
            'module': 'avi.protobuf.application_profile_pb2'
        },
            }
            
class ApplicationProfileInternalView(GetActionView):
    model = ApplicationProfile
    serializer_class = ApplicationProfileSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'ApplicationProfileInternal', 'service_name': 'ApplicationProfileService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'application_profile_internal'}}
    
