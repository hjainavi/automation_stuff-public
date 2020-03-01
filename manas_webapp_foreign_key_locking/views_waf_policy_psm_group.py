
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

    
class WafPolicyPSMGroupList(CreateView, ListView, ):
    model = WafPolicyPSMGroup
    serializer_class = WafPolicyPSMGroupSerializer
    rpc_data = {
        
        'post': {
            'class_name': 'WafPolicyPSMGroup',
            'method_name': 'Create',
            'field_name': 'waf_policy_psm_group',
            'service_name': 'WafPolicyPSMGroupService_Stub',
            'module': 'avi.protobuf.waf_policy_psm_group_pb2'
        },
            }
    
    
class WafPolicyPSMGroupDetail(UpdateView, DeleteView, RetrieveView, ):
    model = WafPolicyPSMGroup
    serializer_class = WafPolicyPSMGroupSerializer
    rpc_data = {
        
        'put': {
            'class_name': 'WafPolicyPSMGroup',
            'method_name': 'Update',
            'field_name': 'waf_policy_psm_group',
            'service_name': 'WafPolicyPSMGroupService_Stub',
            'module': 'avi.protobuf.waf_policy_psm_group_pb2'
        },
        
        'patch': {
            'class_name': 'WafPolicyPSMGroup',
            'method_name': 'Update',
            'field_name': 'waf_policy_psm_group',
            'service_name': 'WafPolicyPSMGroupService_Stub',
            'module': 'avi.protobuf.waf_policy_psm_group_pb2'
        },
        
        'delete': {
            'class_name': 'WafPolicyPSMGroup',
            'method_name': 'Delete',
            'field_name': 'waf_policy_psm_group',
            'service_name': 'WafPolicyPSMGroupService_Stub',
            'module': 'avi.protobuf.waf_policy_psm_group_pb2'
        },
            }
            
