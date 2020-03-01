
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

    
class VirtualServiceList(ListView, CreateView):
    model = VirtualService
    serializer_class = VirtualServiceSerializer
    rpc_data = {
        
        'post': {
            'class_name': 'VirtualService',
            'method_name': 'Create',
            'field_name': '',
            'service_name': 'VirtualServiceService_Stub',
            'module': 'avi.protobuf.vs_pb2'
        },
            }
    
    
class VirtualServiceDetail(RetrieveView, UpdateView, DeleteView):
    model = VirtualService
    serializer_class = VirtualServiceSerializer
    rpc_data = {
        
        'put': {
            'class_name': 'VirtualService',
            'method_name': 'Update',
            'field_name': '',
            'service_name': 'VirtualServiceService_Stub',
            'module': 'avi.protobuf.vs_pb2'
        },
        
        'patch': {
            'class_name': 'VirtualService',
            'method_name': 'Update',
            'field_name': '',
            'service_name': 'VirtualServiceService_Stub',
            'module': 'avi.protobuf.vs_pb2'
        },
        
        'delete': {
            'class_name': 'VirtualService',
            'method_name': 'Delete',
            'field_name': '',
            'service_name': 'VirtualServiceService_Stub',
            'module': 'avi.protobuf.vs_pb2'
        },
            }
        
class VirtualServiceScale_OutView(PostActionView):
    model = VirtualService
    serializer_class = VirtualServiceSerializer
    rpc_data = {'post': {'exclusive': False, 'class_name': 'VirtualService', 'service_name': 'VirtualServiceService_Stub', 'module': 'avi.protobuf.vs_pb2', 'method_name': 'ScaleOut', 'action_param': 'VsScaleoutParams'}}
    
class VirtualServiceScale_InView(PostActionView):
    model = VirtualService
    serializer_class = VirtualServiceSerializer
    rpc_data = {'post': {'exclusive': False, 'class_name': 'VirtualService', 'service_name': 'VirtualServiceService_Stub', 'module': 'avi.protobuf.vs_pb2', 'method_name': 'ScaleIn', 'action_param': 'VsScaleinParams'}}
    
class VirtualServiceMigrateView(PostActionView):
    model = VirtualService
    serializer_class = VirtualServiceSerializer
    rpc_data = {'post': {'exclusive': False, 'class_name': 'VirtualService', 'service_name': 'VirtualServiceService_Stub', 'module': 'avi.protobuf.vs_pb2', 'method_name': 'Migrate', 'action_param': 'VsMigrateParams'}}
    
class VirtualServiceSwitchoverView(PostActionView):
    model = VirtualService
    serializer_class = VirtualServiceSerializer
    rpc_data = {'post': {'exclusive': False, 'class_name': 'VirtualService', 'service_name': 'VirtualServiceService_Stub', 'module': 'avi.protobuf.vs_pb2', 'method_name': 'Switchover', 'action_param': 'VsSwitchoverParams'}}
    
class VirtualServiceClearView(PostActionView):
    model = VirtualService
    serializer_class = VirtualServiceSerializer
    rpc_data = {'post': {'class_name': 'VirtualService', 'method_name': 'Clear', 'exclusive': False, 'service_name': 'VirtualServiceService_Stub'}}
    
class VirtualServiceResyncView(PostActionView):
    model = VirtualService
    serializer_class = VirtualServiceSerializer
    rpc_data = {'post': {'exclusive': False, 'class_name': 'VirtualService', 'service_name': 'VirtualServiceService_Stub', 'module': 'avi.protobuf.vs_pb2', 'method_name': 'Resync', 'action_param': 'VsResyncParams'}}
    
class VirtualServiceRotate_KeysView(PostActionView):
    model = VirtualService
    serializer_class = VirtualServiceSerializer
    rpc_data = {'post': {'class_name': 'VirtualService', 'method_name': 'RotateKeys', 'exclusive': False, 'service_name': 'VirtualServiceService_Stub'}}
    
class VirtualServiceApicplacementView(PostActionView):
    model = VirtualService
    serializer_class = VirtualServiceSerializer
    rpc_data = {'post': {'exclusive': False, 'class_name': 'VirtualService', 'service_name': 'APICAgentService_Stub', 'module': 'avi.protobuf.apic_pb2', 'method_name': 'Apicplacement', 'action_param': 'ApicVSPlacementReq'}}
    
class VirtualServiceRetryplacementView(PostActionView):
    model = VirtualService
    serializer_class = VirtualServiceSerializer
    rpc_data = {'post': {'exclusive': False, 'class_name': 'VirtualService', 'service_name': 'SeResMgrService_Stub', 'module': 'avi.protobuf.se_res_mgr_pb2', 'method_name': 'Retryplacement', 'action_param': 'RetryPlacementParams'}}
        
class VsDosStatRuntimeView(GetActionView):
    model = VirtualService
    serializer_class = VirtualServiceSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'VsDosStatRuntime', 'service_name': 'VirtualServiceService_Stub', 'default_filter': 'DETAIL', 'method_name': 'Read', 'response_field': 'vs_dos_stat_runtime', 'filter': ['se_params_filter', 'cps_doser_filter']}}
    
class ClientSummaryInternalView(GetActionView):
    model = VirtualService
    serializer_class = VirtualServiceSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'ClientSummaryInternal', 'service_name': 'VirtualServiceService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'client_summary_internal', 'filter': ['se_params_filter']}}
    
class ConnectionDumpRuntimeView(GetActionView):
    model = VirtualService
    serializer_class = VirtualServiceSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'ConnectionDumpRuntime', 'service_name': 'VirtualServiceService_Stub', 'default_filter': 'DETAIL', 'method_name': 'Read', 'response_field': 'connection_dump_runtime', 'filter': ['connection_filter']}}
    
class ConnectionDumpRuntimeClearView(PostActionView):
    model = VirtualService
    serializer_class = VirtualServiceSerializer
    rpc_data = {'post': {'class_name': 'ConnectionDumpRuntime', 'method_name': 'Clear', 'action_param': 'connection_filter', 'exclusive': False, 'service_name': 'VirtualServiceService_Stub'}}
    
class GeoDbInternalView(GetActionView):
    model = VirtualService
    serializer_class = VirtualServiceSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'GeoDbInternal', 'service_name': 'VirtualServiceService_Stub', 'default_filter': 'DETAIL', 'method_name': 'Read', 'response_field': 'geo_db_internal', 'filter': ['se_params_filter']}}
    
class KeyvalInternalView(GetActionView):
    model = VirtualService
    serializer_class = VirtualServiceSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'KeyvalInternal', 'service_name': 'VirtualServiceService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'keyval_internal'}}
    
class KeyvalInternalClearView(PostActionView):
    model = VirtualService
    serializer_class = VirtualServiceSerializer
    rpc_data = {'post': {'class_name': 'KeyvalInternal', 'method_name': 'Clear', 'exclusive': False, 'service_name': 'VirtualServiceService_Stub'}}
    
class HTTPPolicySetInternalView(GetActionView):
    model = VirtualService
    serializer_class = VirtualServiceSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'HTTPPolicySetInternal', 'service_name': 'VirtualServiceService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'http_policy_set_internal', 'filter': ['se_params_filter']}}
    
class CltrackSummaryInternalView(GetActionView):
    model = VirtualService
    serializer_class = VirtualServiceSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'CltrackSummaryInternal', 'service_name': 'VirtualServiceService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'cltrack_summary_internal', 'filter': ['se_params_filter']}}
    
class VirtualServiceSeScaleoutStatusView(GetActionView):
    model = VirtualService
    serializer_class = VirtualServiceSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'VirtualServiceSeScaleoutStatus', 'service_name': 'VirtualServiceService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'virtual_service_se_scaleout_status', 'filter': ['se_params_filter']}}
    
class SeConsumerProtoView(GetActionView):
    model = VirtualService
    serializer_class = VirtualServiceSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'SeConsumerProto', 'service_name': 'ResMgrReadService_Stub', 'default_filter': 'DETAIL', 'method_name': 'Read', 'response_field': 'se_con_internal'}}
    
class UserDefinedDataScriptCountersView(GetActionView):
    model = VirtualService
    serializer_class = VirtualServiceSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'UserDefinedDataScriptCounters', 'service_name': 'VirtualServiceService_Stub', 'default_filter': 'DETAIL', 'method_name': 'Read', 'response_field': 'userdef_datascript_counters', 'filter': ['se_params_filter']}}
    
class UserDefinedDataScriptCountersClearView(PostActionView):
    model = VirtualService
    serializer_class = VirtualServiceSerializer
    rpc_data = {'post': {'class_name': 'UserDefinedDataScriptCounters', 'method_name': 'Clear', 'exclusive': False, 'service_name': 'VirtualServiceService_Stub'}}
    
class GslbServiceDetailView(GetActionView):
    model = VirtualService
    serializer_class = VirtualServiceSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'GslbServiceDetail', 'service_name': 'VirtualServiceService_Stub', 'default_filter': 'DETAIL', 'method_name': 'Read', 'response_field': 'gs_detail', 'filter': ['se_params_filter', 'gs_filter', 'server_filter']}}
    
class VirtualServiceRuntimeDetailView(GetActionView):
    model = VirtualService
    serializer_class = VirtualServiceSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'VirtualServiceRuntimeDetail', 'service_name': 'VirtualServiceService_Stub', 'default_filter': 'DETAIL', 'method_name': 'Read', 'response_field': 'virtual_service_runtime_detail', 'filter': ['se_params_filter', 'tcp_stat_filter', 'vstype_filter']}}
    
class VirtualServiceRuntimeDetailClearView(PostActionView):
    model = VirtualService
    serializer_class = VirtualServiceSerializer
    rpc_data = {'post': {'class_name': 'VirtualServiceRuntimeDetail', 'method_name': 'Clear', 'exclusive': False, 'service_name': 'VirtualServiceService_Stub'}}
    
class NetworkSecurityPolicyDetailView(GetActionView):
    model = VirtualService
    serializer_class = VirtualServiceSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'NetworkSecurityPolicyDetail', 'service_name': 'VirtualServiceService_Stub', 'default_filter': 'DETAIL', 'method_name': 'Read', 'response_field': 'network_security_policy_detail'}}
    
class GslbServiceInternalView(GetActionView):
    model = VirtualService
    serializer_class = VirtualServiceSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'GslbServiceInternal', 'service_name': 'VirtualServiceService_Stub', 'default_filter': 'DETAIL', 'method_name': 'Read', 'response_field': 'gs_internal', 'filter': ['se_params_filter', 'gs_filter', 'server_filter']}}
    
class GslbServiceHmonStatView(GetActionView):
    model = VirtualService
    serializer_class = VirtualServiceSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'GslbServiceHmonStat', 'service_name': 'VirtualServiceService_Stub', 'default_filter': 'DETAIL', 'method_name': 'Read', 'response_field': 'gs_hmonstat', 'filter': ['se_params_filter', 'gs_filter', 'server_filter']}}
    
class KeyvalSummaryInternalView(GetActionView):
    model = VirtualService
    serializer_class = VirtualServiceSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'KeyvalSummaryInternal', 'service_name': 'VirtualServiceService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'keyval_summary_internal'}}
    
class TrafficCloneRuntimeView(GetActionView):
    model = VirtualService
    serializer_class = VirtualServiceSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'TrafficCloneRuntime', 'service_name': 'VirtualServiceService_Stub', 'default_filter': 'DETAIL', 'method_name': 'Read', 'response_field': 'traffic_clone_stats', 'filter': ['se_params_filter']}}
    
class HTTPPolicySetStatsView(GetActionView):
    model = VirtualService
    serializer_class = VirtualServiceSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'HTTPPolicySetStats', 'service_name': 'VirtualServiceService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'http_policy_set_stats', 'filter': ['se_params_filter']}}
    
class HTTPPolicySetStatsClearView(PostActionView):
    model = VirtualService
    serializer_class = VirtualServiceSerializer
    rpc_data = {'post': {'class_name': 'HTTPPolicySetStats', 'method_name': 'Clear', 'exclusive': False, 'service_name': 'VirtualServiceService_Stub'}}
    
class VirtualServiceRuntimeSummaryView(GetActionView):
    model = VirtualService
    serializer_class = VirtualServiceSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'VirtualServiceRuntimeSummary', 'service_name': 'VirtualServiceService_Stub', 'default_filter': 'SUMMARY', 'method_name': 'Read', 'response_field': 'virtual_service_runtime_summary'}}
    
class ClientInternalView(GetActionView):
    model = VirtualService
    serializer_class = VirtualServiceSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'ClientInternal', 'service_name': 'VirtualServiceService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'client_internal', 'filter': ['se_params_filter']}}
    
class ClientInternalClearView(PostActionView):
    model = VirtualService
    serializer_class = VirtualServiceSerializer
    rpc_data = {'post': {'class_name': 'ClientInternal', 'method_name': 'Clear', 'exclusive': False, 'service_name': 'VirtualServiceService_Stub'}}
    
class VsCandidateSeHostListView(GetActionView):
    model = VirtualService
    serializer_class = VirtualServiceSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'VsCandidateSeHostList', 'service_name': 'ResMgrReadService_Stub', 'default_filter': 'DETAIL', 'method_name': 'Read', 'response_field': 'vs_candidate_se_host_list', 'filter': ['candidate_se_host_filter']}}
    
class DnsTableView(GetActionView):
    model = VirtualService
    serializer_class = VirtualServiceSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'DnsTable', 'service_name': 'VirtualServiceService_Stub', 'default_filter': 'DETAIL', 'method_name': 'Read', 'response_field': 'dns_table', 'filter': ['se_params_filter']}}
    
class GeoLocationInfoView(GetActionView):
    model = VirtualService
    serializer_class = VirtualServiceSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'GeoLocationInfo', 'service_name': 'VirtualServiceService_Stub', 'default_filter': 'DETAIL', 'method_name': 'Read', 'response_field': 'geo_location', 'filter': ['se_params_filter', 'geo_location_filter']}}
    
class GslbSiteInternalView(GetActionView):
    model = VirtualService
    serializer_class = VirtualServiceSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'GslbSiteInternal', 'service_name': 'VirtualServiceService_Stub', 'default_filter': 'DETAIL', 'method_name': 'Read', 'response_field': 'gslb_site_internal', 'filter': ['se_params_filter']}}
    
class VirtualServiceInternalView(GetActionView):
    model = VirtualService
    serializer_class = VirtualServiceSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'VirtualServiceInternal', 'service_name': 'VirtualServiceService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'virtual_service_internal', 'filter': ['se_params_filter']}}
    
class CltrackInternalView(GetActionView):
    model = VirtualService
    serializer_class = VirtualServiceSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'CltrackInternal', 'service_name': 'VirtualServiceService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'cltrack_internal', 'filter': ['se_params_filter']}}
    
class CltrackInternalClearView(PostActionView):
    model = VirtualService
    serializer_class = VirtualServiceSerializer
    rpc_data = {'post': {'class_name': 'CltrackInternal', 'method_name': 'Clear', 'exclusive': False, 'service_name': 'VirtualServiceService_Stub'}}
    
class NetworkSecurityPolicyStatsView(GetActionView):
    model = VirtualService
    serializer_class = VirtualServiceSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'NetworkSecurityPolicyStats', 'service_name': 'VirtualServiceService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'network_security_policy_stats', 'filter': ['se_params_filter']}}
    
class VirtualServiceAuthStatsView(GetActionView):
    model = VirtualService
    serializer_class = VirtualServiceSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'VirtualServiceAuthStats', 'service_name': 'VirtualServiceService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'virtual_service_auth_stats', 'filter': ['se_params_filter']}}
    
class VirtualServiceAuthStatsClearView(PostActionView):
    model = VirtualService
    serializer_class = VirtualServiceSerializer
    rpc_data = {'post': {'class_name': 'VirtualServiceAuthStats', 'method_name': 'Clear', 'exclusive': False, 'service_name': 'VirtualServiceService_Stub'}}
    
class UdpStatRuntimeView(GetActionView):
    model = VirtualService
    serializer_class = VirtualServiceSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'UdpStatRuntime', 'service_name': 'VirtualServiceService_Stub', 'default_filter': 'DETAIL', 'method_name': 'Read', 'response_field': 'udp_stat_runtime', 'filter': ['udp_stat_filter', 'se_params_filter']}}
    
class L4PolicySetStatsView(GetActionView):
    model = VirtualService
    serializer_class = VirtualServiceSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'L4PolicySetStats', 'service_name': 'VirtualServiceService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'l4_policy_set_stats', 'filter': ['se_params_filter']}}
    
class L4PolicySetStatsClearView(PostActionView):
    model = VirtualService
    serializer_class = VirtualServiceSerializer
    rpc_data = {'post': {'class_name': 'L4PolicySetStats', 'method_name': 'Clear', 'exclusive': False, 'service_name': 'VirtualServiceService_Stub'}}
    
class L7VirtualServiceStatsRuntimeView(GetActionView):
    model = VirtualService
    serializer_class = VirtualServiceSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'L7VirtualServiceStatsRuntime', 'service_name': 'VirtualServiceService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'l7_virtual_service_stats_runtime', 'filter': ['se_params_filter']}}
    
class DnsPolicyStatsView(GetActionView):
    model = VirtualService
    serializer_class = VirtualServiceSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'DnsPolicyStats', 'service_name': 'VirtualServiceService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'dns_policy_stats', 'filter': ['se_params_filter']}}
    
class DnsPolicyStatsClearView(PostActionView):
    model = VirtualService
    serializer_class = VirtualServiceSerializer
    rpc_data = {'post': {'class_name': 'DnsPolicyStats', 'method_name': 'Clear', 'exclusive': False, 'service_name': 'VirtualServiceService_Stub'}}
    
class TcpStatRuntimeView(GetActionView):
    model = VirtualService
    serializer_class = VirtualServiceSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'TcpStatRuntime', 'service_name': 'VirtualServiceService_Stub', 'default_filter': 'DETAIL', 'method_name': 'Read', 'response_field': 'tcp_stat_runtime', 'filter': ['tcp_stat_filter', 'se_params_filter']}}
    
