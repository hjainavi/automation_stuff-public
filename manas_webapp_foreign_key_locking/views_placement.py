
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

    
class PlacementStatsList(GetActionView,):
    model = None
    rpc_data = {'get': {'exclusive': False, 'class_name': 'PlacementStats', 'service_name': 'ResMgrReadService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'se_stats'}}
    
    
class PlacementStatsDetail(GetActionView):
    model = None
    rpc_data = {'get': {'exclusive': False, 'class_name': 'PlacementStats', 'service_name': 'ResMgrReadService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'se_stats'}}
            
    
class PlacementStatusList(GetActionView,):
    model = None
    rpc_data = {'get': {'exclusive': False, 'class_name': 'PlacementStatus', 'service_name': 'ResMgrReadService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'placement_status', 'filter': ['placement_status_filter']}}
    
    
class PlacementStatusDetail(GetActionView):
    model = None
    rpc_data = {'get': {'exclusive': False, 'class_name': 'PlacementStatus', 'service_name': 'ResMgrReadService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'placement_status', 'filter': ['placement_status_filter']}}
            
    
class SeConsumerProtoList(GetActionView,):
    model = None
    rpc_data = {'get': {'exclusive': False, 'class_name': 'SeConsumerProto', 'service_name': 'ResMgrReadService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'se_con_internal', 'filter': ['con_filter']}}
    
    
class SeConsumerProtoDetail(GetActionView):
    model = None
    rpc_data = {'get': {'exclusive': False, 'class_name': 'SeConsumerProto', 'service_name': 'ResMgrReadService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'se_con_internal', 'filter': ['con_filter']}}
            
    
class SeCreatePendingProtoList(GetActionView,):
    model = None
    rpc_data = {'get': {'exclusive': False, 'class_name': 'SeCreatePendingProto', 'service_name': 'ResMgrReadService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'se_create_pending'}}
    
    
class SeCreatePendingProtoDetail(GetActionView):
    model = None
    rpc_data = {'get': {'exclusive': False, 'class_name': 'SeCreatePendingProto', 'service_name': 'ResMgrReadService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'se_create_pending'}}
            
    
class SeVipProtoList(GetActionView,):
    model = None
    rpc_data = {'get': {'exclusive': False, 'class_name': 'SeVipProto', 'service_name': 'ResMgrReadService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'se_vip', 'filter': ['vip_filter']}}
    
    
class SeVipProtoDetail(GetActionView):
    model = None
    rpc_data = {'get': {'exclusive': False, 'class_name': 'SeVipProto', 'service_name': 'ResMgrReadService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'se_vip', 'filter': ['vip_filter']}}
            
    
class SeResourceProtoList(GetActionView,):
    model = None
    rpc_data = {'get': {'exclusive': False, 'class_name': 'SeResourceProto', 'service_name': 'ResMgrReadService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'se_res_internal', 'filter': ['res_filter']}}
    
    
class SeResourceProtoDetail(GetActionView):
    model = None
    rpc_data = {'get': {'exclusive': False, 'class_name': 'SeResourceProto', 'service_name': 'ResMgrReadService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'se_res_internal', 'filter': ['res_filter']}}
            
    
class RmVrfProtoList(GetActionView,):
    model = None
    rpc_data = {'get': {'exclusive': False, 'class_name': 'RmVrfProto', 'service_name': 'ResMgrReadService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'rmvrf', 'filter': ['vrf_filter']}}
    
    
class RmVrfProtoDetail(GetActionView):
    model = None
    rpc_data = {'get': {'exclusive': False, 'class_name': 'RmVrfProto', 'service_name': 'ResMgrReadService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'rmvrf', 'filter': ['vrf_filter']}}
            
    
class PlacementGlobalsList(GetActionView,):
    model = None
    rpc_data = {'get': {'exclusive': False, 'class_name': 'PlacementGlobals', 'service_name': 'ResMgrReadService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'placement_globals'}}
    
    
class PlacementGlobalsDetail(GetActionView):
    model = None
    rpc_data = {'get': {'exclusive': False, 'class_name': 'PlacementGlobals', 'service_name': 'ResMgrReadService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'placement_globals'}}
            
