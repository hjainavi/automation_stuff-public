
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

    
class NsxSgIpsList(GetActionView,):
    model = None
    rpc_data = {'get': {'exclusive': False, 'class_name': 'NsxSgIps', 'service_name': 'NSXAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Nsxsgips', 'response_field': 'nsx_sg_ips', 'filter': ['nsx_sg_filter']}}
    
    
class NsxSgIpsDetail(GetActionView):
    model = None
    rpc_data = {'get': {'exclusive': False, 'class_name': 'NsxSgIps', 'service_name': 'NSXAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Nsxsgips', 'response_field': 'nsx_sg_ips', 'filter': ['nsx_sg_filter']}}
            
    
class NsxAgentInternalCliList(GetActionView,):
    model = None
    rpc_data = {'get': {'exclusive': False, 'class_name': 'NsxAgentInternalCli', 'service_name': 'NSXAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Nsxagentinternalcli', 'response_field': 'nsx_agent_internal_cli', 'filter': ['nsx_internal_params']}}
    
    
class NsxAgentInternalCliDetail(GetActionView):
    model = None
    rpc_data = {'get': {'exclusive': False, 'class_name': 'NsxAgentInternalCli', 'service_name': 'NSXAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Nsxagentinternalcli', 'response_field': 'nsx_agent_internal_cli', 'filter': ['nsx_internal_params']}}
            
    
        
class NsxSgInfoNsxsecuritygroupsView(PostActionView):
    model = None
    rpc_data = {'post': {'exclusive': False, 'class_name': 'NsxSgInfo', 'service_name': 'NSXAgentService_Stub', 'module': 'avi.protobuf.nsx_pb2', 'method_name': 'Nsxsecuritygroups', 'action_param': 'NsxSgParams'}}
        
    
        
class NsxAgentInternalVerifynsxloginView(PostActionView):
    model = None
    rpc_data = {'post': {'exclusive': False, 'class_name': 'NsxAgentInternal', 'service_name': 'NSXAgentService_Stub', 'module': 'avi.protobuf.nsx_pb2', 'method_name': 'Verifynsxlogin', 'action_param': 'NsxLogin'}}
    
class NsxAgentInternalClearnsxdbobjectsView(PostActionView):
    model = None
    rpc_data = {'post': {'exclusive': False, 'class_name': 'NsxAgentInternal', 'service_name': 'NSXAgentService_Stub', 'module': 'avi.protobuf.nsx_pb2', 'method_name': 'Clearnsxdbobjects', 'action_param': 'NsxSgParams'}}
    
class NsxAgentInternalInitiatensxresyncView(PostActionView):
    model = None
    rpc_data = {'post': {'exclusive': False, 'class_name': 'NsxAgentInternal', 'service_name': 'NSXAgentService_Stub', 'module': 'avi.protobuf.nsx_pb2', 'method_name': 'Initiatensxresync', 'action_param': 'NsxSgParams'}}
    
class NsxAgentInternalReprogramavinsxobjectsView(PostActionView):
    model = None
    rpc_data = {'post': {'exclusive': False, 'class_name': 'NsxAgentInternal', 'service_name': 'NSXAgentService_Stub', 'module': 'avi.protobuf.nsx_pb2', 'method_name': 'Reprogramavinsxobjects', 'action_param': 'NsxSgParams'}}
    
class NsxAgentInternalNsxfaultinjectView(PostActionView):
    model = None
    rpc_data = {'post': {'exclusive': False, 'class_name': 'NsxAgentInternal', 'service_name': 'NSXAgentService_Stub', 'module': 'avi.protobuf.nsx_pb2', 'method_name': 'Nsxfaultinject', 'action_param': 'nsx_fault_params'}}
        
