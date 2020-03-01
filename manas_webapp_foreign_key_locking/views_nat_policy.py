
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

    
class NatPolicyList(CreateView, ListView, ):
    model = NatPolicy
    serializer_class = NatPolicySerializer
    rpc_data = {
        
        'post': {
            'class_name': 'NatPolicy',
            'method_name': 'Create',
            'field_name': 'nat_policy',
            'service_name': 'NatPolicyService_Stub',
            'module': 'avi.protobuf.nat_policy_pb2'
        },
            }
    
    
class NatPolicyDetail(UpdateView, DeleteView, RetrieveView, ):
    model = NatPolicy
    serializer_class = NatPolicySerializer
    rpc_data = {
        
        'put': {
            'class_name': 'NatPolicy',
            'method_name': 'Update',
            'field_name': 'nat_policy',
            'service_name': 'NatPolicyService_Stub',
            'module': 'avi.protobuf.nat_policy_pb2'
        },
        
        'patch': {
            'class_name': 'NatPolicy',
            'method_name': 'Update',
            'field_name': 'nat_policy',
            'service_name': 'NatPolicyService_Stub',
            'module': 'avi.protobuf.nat_policy_pb2'
        },
        
        'delete': {
            'class_name': 'NatPolicy',
            'method_name': 'Delete',
            'field_name': 'nat_policy',
            'service_name': 'NatPolicyService_Stub',
            'module': 'avi.protobuf.nat_policy_pb2'
        },
            }
            
