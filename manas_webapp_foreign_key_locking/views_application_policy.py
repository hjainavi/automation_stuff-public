
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

    
class HTTPPolicySetList(ListView, CreateView):
    model = HTTPPolicySet
    serializer_class = HTTPPolicySetSerializer
    rpc_data = {
        
        'post': {
            'class_name': 'HTTPPolicySet',
            'method_name': 'Create',
            'field_name': 'http_policy_set',
            'service_name': 'HTTPPolicySetService_Stub',
            'module': 'avi.protobuf.application_policy_pb2'
        },
            }
    
    
class HTTPPolicySetDetail(RetrieveView, UpdateView, DeleteView):
    model = HTTPPolicySet
    serializer_class = HTTPPolicySetSerializer
    rpc_data = {
        
        'put': {
            'class_name': 'HTTPPolicySet',
            'method_name': 'Update',
            'field_name': 'http_policy_set',
            'service_name': 'HTTPPolicySetService_Stub',
            'module': 'avi.protobuf.application_policy_pb2'
        },
        
        'patch': {
            'class_name': 'HTTPPolicySet',
            'method_name': 'Update',
            'field_name': 'http_policy_set',
            'service_name': 'HTTPPolicySetService_Stub',
            'module': 'avi.protobuf.application_policy_pb2'
        },
        
        'delete': {
            'class_name': 'HTTPPolicySet',
            'method_name': 'Delete',
            'field_name': 'http_policy_set',
            'service_name': 'HTTPPolicySetService_Stub',
            'module': 'avi.protobuf.application_policy_pb2'
        },
            }
            
