
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

    
class ServiceEngineList(ListView, ):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {
            }
    
    
class ServiceEngineDetail(UpdateView, RetrieveView, DeleteView, ):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {
        
        'put': {
            'class_name': 'ServiceEngine',
            'method_name': 'Update',
            'field_name': 'service_engine',
            'service_name': 'SeMgrService_Stub',
            'module': 'avi.protobuf.se_pb2'
        },
        
        'patch': {
            'class_name': 'ServiceEngine',
            'method_name': 'Update',
            'field_name': 'service_engine',
            'service_name': 'SeMgrService_Stub',
            'module': 'avi.protobuf.se_pb2'
        },
        
        'delete': {
            'class_name': 'ServiceEngine',
            'method_name': 'Delete',
            'field_name': 'service_engine',
            'service_name': 'SeMgrService_Stub',
            'module': 'avi.protobuf.se_pb2'
        },
            }
        
class ServiceEngineRebootView(PostActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'post': {'class_name': 'ServiceEngine', 'method_name': 'Reboot', 'exclusive': False, 'service_name': 'SeMgrService_Stub'}}
    
class ServiceEngineForcedeleteView(PostActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'post': {'class_name': 'ServiceEngine', 'method_name': 'ForceDelete', 'exclusive': False, 'service_name': 'SeMgrService_Stub'}}
    
class ServiceEngineSwitchoverView(PostActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'post': {'class_name': 'ServiceEngine', 'method_name': 'Switchover', 'exclusive': False, 'service_name': 'SeResMgrService_Stub'}}
    
class ServiceEngineClearView(PostActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'post': {'class_name': 'ServiceEngine', 'method_name': 'Clear', 'exclusive': True, 'service_name': 'SeAgentService_Stub'}}
        
class LldpRuntimeView(GetActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'get': {'exclusive': True, 'class_name': 'LldpRuntime', 'service_name': 'SeAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'lldp_runtime', 'filter': ['flowtable_intf_filter']}}
    
class ServiceEngineRuntimeSummaryView(GetActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'ServiceEngineRuntimeSummary', 'service_name': 'SeMgrService_Stub', 'default_filter': 'SUMMARY', 'method_name': 'Read', 'response_field': 'service_engine_runtime_summary'}}
    
class TcpConnRuntimeDetailView(GetActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'get': {'exclusive': True, 'pagination': True, 'class_name': 'TcpConnRuntimeDetail', 'service_name': 'SeAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'tcp_conn_runtime_detail', 'filter': ['connection_filter', 'listeningsock_filter', 'corenum_filter']}}
    
class InterfaceSummaryRuntimeView(GetActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'get': {'exclusive': True, 'class_name': 'InterfaceSummaryRuntime', 'service_name': 'SeAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'interface_summary_runtime'}}
    
class InterfaceRuntimeView(GetActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'get': {'exclusive': True, 'class_name': 'InterfaceRuntime', 'service_name': 'SeAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'interface_runtime', 'filter': ['flowtable_intf_filter']}}
    
class InterfaceRuntimeClearView(PostActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'post': {'class_name': 'InterfaceRuntime', 'method_name': 'Clear', 'exclusive': True, 'service_name': 'SeAgentService_Stub'}}
    
class ArptableRuntimeView(GetActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'get': {'exclusive': True, 'class_name': 'ArptableRuntime', 'service_name': 'SeAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'arptable_runtime', 'filter': ['arp_table_filter', 'se_params_filter']}}
    
class ArptableRuntimeClearView(PostActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'post': {'class_name': 'ArptableRuntime', 'method_name': 'Clear', 'action_param': 'arp_table_filter', 'exclusive': True, 'service_name': 'SeAgentService_Stub'}}
    
class ServiceEngineRuntimeDetailView(GetActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'ServiceEngineRuntimeDetail', 'service_name': 'SeMgrService_Stub', 'default_filter': 'DETAIL', 'method_name': 'Read', 'response_field': 'service_engine_runtime_detail'}}
    
class Icmp6StatRuntimeView(GetActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'get': {'exclusive': True, 'class_name': 'Icmp6StatRuntime', 'service_name': 'SeAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'icmp6_stat_runtime', 'filter': ['se_params_filter']}}
    
class Icmp6StatRuntimeClearView(PostActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'post': {'class_name': 'Icmp6StatRuntime', 'method_name': 'Clear', 'exclusive': True, 'service_name': 'SeAgentService_Stub'}}
    
class SeAgentGraphDBRuntimeView(GetActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'get': {'exclusive': True, 'class_name': 'SeAgentGraphDBRuntime', 'service_name': 'SeAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'se_agent_graphdb_runtime', 'filter': ['se_agent_filter']}}
    
class L4PolicySetStatsView(GetActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'get': {'exclusive': True, 'class_name': 'L4PolicySetStats', 'service_name': 'SeAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'l4_policy_set_stats', 'filter': ['se_params_filter']}}
    
class L4PolicySetStatsClearView(PostActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'post': {'class_name': 'L4PolicySetStats', 'method_name': 'Clear', 'exclusive': True, 'service_name': 'SeAgentService_Stub'}}
    
class SeRumInsertionStatsView(GetActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'get': {'exclusive': True, 'class_name': 'SeRumInsertionStats', 'service_name': 'SeAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'se_rum_insertion_stats'}}
    
class SeRumInsertionStatsClearView(PostActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'post': {'class_name': 'SeRumInsertionStats', 'method_name': 'Clear', 'exclusive': True, 'service_name': 'SeAgentService_Stub'}}
    
class InterfaceLacpRuntimeView(GetActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'get': {'exclusive': True, 'class_name': 'InterfaceLacpRuntime', 'service_name': 'SeAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'interface_lacp_runtime', 'filter': ['flowtable_intf_filter']}}
    
class MeminfoRuntimeView(GetActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'get': {'exclusive': True, 'class_name': 'MeminfoRuntime', 'service_name': 'SeAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'meminfo_runtime', 'filter': ['se_params_filter']}}
    
class SeLogStatsRuntimeView(GetActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'get': {'exclusive': True, 'class_name': 'SeLogStatsRuntime', 'service_name': 'SeAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'se_log_stats_runtime'}}
    
class SeLogStatsRuntimeClearView(PostActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'post': {'class_name': 'SeLogStatsRuntime', 'method_name': 'Clear', 'exclusive': True, 'service_name': 'SeAgentService_Stub'}}
    
class SeFaultInjectExhaustConnClearView(PostActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'post': {'class_name': 'SeFaultInjectExhaustConn', 'method_name': 'Clear', 'action_param': 'se_fault_inject_exhaust_param', 'exclusive': True, 'service_name': 'SeAgentService_Stub'}}
    
class SeAgentConsistentHashView(GetActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'get': {'exclusive': True, 'class_name': 'SeAgentConsistentHash', 'service_name': 'SeAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'consistent_hash_details'}}
    
class TcpConnRuntimeView(GetActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'get': {'exclusive': True, 'pagination': True, 'class_name': 'TcpConnRuntime', 'service_name': 'SeAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'tcp_conn_runtime', 'filter': ['connection_filter', 'listeningsock_filter', 'corenum_filter']}}
    
class SeAgentShardClientResourceMapView(GetActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'get': {'exclusive': True, 'class_name': 'SeAgentShardClientResourceMap', 'service_name': 'SeAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'shard_client_domain_entry'}}
    
class IpStatRuntimeView(GetActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'get': {'exclusive': True, 'class_name': 'IpStatRuntime', 'service_name': 'SeAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'ip_stat_runtime', 'filter': ['se_params_filter']}}
    
class IpStatRuntimeClearView(PostActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'post': {'class_name': 'IpStatRuntime', 'method_name': 'Clear', 'exclusive': True, 'service_name': 'SeAgentService_Stub'}}
    
class ShMallocStatRuntimeView(GetActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'get': {'exclusive': True, 'class_name': 'ShMallocStatRuntime', 'service_name': 'SeAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'sh_malloc_stat_runtime'}}
    
class SeAuthStatsRuntimeView(GetActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'get': {'exclusive': True, 'class_name': 'SeAuthStatsRuntime', 'service_name': 'SeAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'se_auth_stats_runtime'}}
    
class SeAuthStatsRuntimeClearView(PostActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'post': {'class_name': 'SeAuthStatsRuntime', 'method_name': 'Clear', 'exclusive': True, 'service_name': 'SeAgentService_Stub'}}
    
class ArpStatRuntimeView(GetActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'get': {'exclusive': True, 'class_name': 'ArpStatRuntime', 'service_name': 'SeAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'arp_stat_runtime', 'filter': ['se_params_filter']}}
    
class ArpStatRuntimeClearView(PostActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'post': {'class_name': 'ArpStatRuntime', 'method_name': 'Clear', 'exclusive': True, 'service_name': 'SeAgentService_Stub'}}
    
class CpuStatRuntimeDetailView(GetActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'get': {'exclusive': True, 'class_name': 'CpuStatRuntimeDetail', 'service_name': 'SeAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'cpu_stat_runtime_detail', 'filter': ['se_cpu_stat_filter']}}
    
class SeAgentShardClientAppMapView(GetActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'get': {'exclusive': True, 'class_name': 'SeAgentShardClientAppMap', 'service_name': 'SeAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'domain_vs_map'}}
    
class SeMicroServiceView(GetActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'get': {'exclusive': True, 'class_name': 'SeMicroService', 'service_name': 'SeAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'se_microservice', 'filter': ['ms_filter']}}
    
class MetricsRuntimeDetailView(GetActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'get': {'exclusive': True, 'class_name': 'MetricsRuntimeDetail', 'service_name': 'SeAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'metrics_runtime_detail', 'filter': ['se_metrics_filter', 'vs_metrics_filter', 'pool_metrics_filter']}}
    
class SeAgentVnicDBRuntimeView(GetActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'get': {'exclusive': True, 'class_name': 'SeAgentVnicDBRuntime', 'service_name': 'SeAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'se_agent_vnicdb_runtime'}}
    
class NdtableRuntimeView(GetActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'get': {'exclusive': True, 'class_name': 'NdtableRuntime', 'service_name': 'SeAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'ndtable_runtime', 'filter': ['nd_table_filter', 'se_params_filter']}}
    
class NdtableRuntimeClearView(PostActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'post': {'class_name': 'NdtableRuntime', 'method_name': 'Clear', 'exclusive': True, 'filter': ['nd_table_filter'], 'service_name': 'SeAgentService_Stub'}}
    
class SeReservedVsView(GetActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'get': {'exclusive': True, 'class_name': 'SeReservedVs', 'service_name': 'SeAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'se_reserved_vs'}}
    
class SeReservedVsClearView(PostActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'post': {'class_name': 'SeReservedVs', 'method_name': 'Clear', 'exclusive': True, 'service_name': 'SeAgentService_Stub'}}
    
class SeVssPlacementView(GetActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'get': {'exclusive': True, 'class_name': 'SeVssPlacement', 'service_name': 'SeAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'se_vss_placement'}}
    
class SeFaultInjectInfraClearView(PostActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'post': {'class_name': 'SeFaultInjectInfra', 'method_name': 'Clear', 'action_param': 'se_fault', 'exclusive': True, 'service_name': 'SeAgentService_Stub'}}
    
class CpuStatRuntimeView(GetActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'get': {'exclusive': True, 'class_name': 'CpuStatRuntime', 'service_name': 'SeAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'cpu_stat_runtime'}}
    
class SeNatFlowRuntimeView(GetActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'get': {'exclusive': True, 'pagination': True, 'class_name': 'SeNatFlowRuntime', 'service_name': 'SeAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'senat_flow_runtime', 'filter': ['connection_clear_filter', 'core_filter']}}
    
class SeNatFlowRuntimeClearView(PostActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'post': {'class_name': 'SeNatFlowRuntime', 'method_name': 'Clear', 'exclusive': True, 'filter': ['connection_clear_filter'], 'service_name': 'SeAgentService_Stub'}}
    
class SeAgentStateRuntimeView(GetActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'get': {'exclusive': True, 'class_name': 'SeAgentStateRuntime', 'service_name': 'SeAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'se_agent_state_runtime'}}
    
class VshashshowRuntimeView(GetActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'get': {'exclusive': True, 'class_name': 'VshashshowRuntime', 'service_name': 'SeAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'vshashshow_runtime'}}
    
class ServiceEngineInternalView(GetActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'ServiceEngineInternal', 'service_name': 'SeMgrService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'service_engine_internal'}}
    
class DispatcherRemoteTimerListDumpRuntimeView(GetActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'get': {'exclusive': True, 'class_name': 'DispatcherRemoteTimerListDumpRuntime', 'service_name': 'SeAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'dispatcher_remote_timer_list_dump_runtime'}}
    
class SeNatStatRuntimeView(GetActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'get': {'exclusive': True, 'class_name': 'SeNatStatRuntime', 'service_name': 'SeAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'senat_stat_runtime', 'filter': ['core_filter']}}
    
class SeNatStatRuntimeClearView(PostActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'post': {'class_name': 'SeNatStatRuntime', 'method_name': 'Clear', 'exclusive': True, 'service_name': 'SeAgentService_Stub'}}
    
class SeVsHbStatRuntimeView(GetActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'get': {'exclusive': True, 'class_name': 'SeVsHbStatRuntime', 'service_name': 'SeAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'se_vs_hb_stat_runtime'}}
    
class SeVsHbStatRuntimeClearView(PostActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'post': {'class_name': 'SeVsHbStatRuntime', 'method_name': 'Clear', 'exclusive': True, 'service_name': 'SeAgentService_Stub'}}
    
class MallocStatRuntimeView(GetActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'get': {'exclusive': True, 'class_name': 'MallocStatRuntime', 'service_name': 'SeAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'malloc_stat_runtime', 'filter': ['se_params_filter']}}
    
class BgpRuntimeView(GetActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'get': {'exclusive': True, 'class_name': 'BgpRuntime', 'service_name': 'SeAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'bgp_runtime'}}
    
class SeFaultInjectExhaustMclClearView(PostActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'post': {'class_name': 'SeFaultInjectExhaustMcl', 'method_name': 'Clear', 'action_param': 'se_fault_inject_exhaust_param', 'exclusive': True, 'service_name': 'SeAgentService_Stub'}}
    
class L7GlobalStatsRuntimeView(GetActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'get': {'exclusive': True, 'class_name': 'L7GlobalStatsRuntime', 'service_name': 'SeAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'l7_global_stats_runtime', 'filter': ['se_params_filter']}}
    
class L7GlobalStatsRuntimeClearView(PostActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'post': {'class_name': 'L7GlobalStatsRuntime', 'method_name': 'Clear', 'exclusive': True, 'service_name': 'SeAgentService_Stub'}}
    
class SeFaultInjectExhaustMclSmallClearView(PostActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'post': {'class_name': 'SeFaultInjectExhaustMclSmall', 'method_name': 'Clear', 'action_param': 'se_fault_inject_exhaust_param', 'exclusive': True, 'service_name': 'SeAgentService_Stub'}}
    
class DispatcherTableDumpRuntimeView(GetActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'get': {'exclusive': True, 'pagination': True, 'class_name': 'DispatcherTableDumpRuntime', 'service_name': 'SeAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'dispatcher_table_dump_runtime', 'filter': ['flowtable_entry_filter']}}
    
class DispatcherTableDumpRuntimeClearView(PostActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'post': {'exclusive': True, 'class_name': 'DispatcherTableDumpRuntime', 'service_name': 'SeAgentService_Stub', 'method_name': 'Clear', 'action_param': 'dispatcher_table_dump_clear', 'filter': ['flowtable_entry_filter']}}
    
class SeAssertStatRuntimeView(GetActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'get': {'exclusive': True, 'class_name': 'SeAssertStatRuntime', 'service_name': 'SeAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'seassert_stat_runtime', 'filter': ['se_params_filter']}}
    
class SeAssertStatRuntimeClearView(PostActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'post': {'class_name': 'SeAssertStatRuntime', 'method_name': 'Clear', 'exclusive': True, 'service_name': 'SeAgentService_Stub'}}
    
class MetricsRuntimeSummaryView(GetActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'get': {'exclusive': True, 'class_name': 'MetricsRuntimeSummary', 'service_name': 'SeAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'metrics_runtime_summary', 'filter': ['se_metrics_filter', 'vs_metrics_filter', 'pool_metrics_filter']}}
    
class SeAgentVnicDBHistoryView(GetActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'get': {'exclusive': True, 'class_name': 'SeAgentVnicDBHistory', 'service_name': 'SeAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'se_agent_vnicdb_history', 'filter': ['vnicdb_history_filter']}}
    
class MbStatRuntimeView(GetActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'get': {'exclusive': True, 'class_name': 'MbStatRuntime', 'service_name': 'SeAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'mb_stat_runtime', 'filter': ['se_params_filter']}}
    
class MbStatRuntimeClearView(PostActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'post': {'class_name': 'MbStatRuntime', 'method_name': 'Clear', 'exclusive': True, 'service_name': 'SeAgentService_Stub'}}
    
class SeMemDistRuntimeView(GetActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'get': {'exclusive': True, 'class_name': 'SeMemDistRuntime', 'service_name': 'SeAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'se_mem_dist_runtime'}}
    
class DispatcherStatRuntimeView(GetActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'get': {'exclusive': True, 'class_name': 'DispatcherStatRuntime', 'service_name': 'SeAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'dispatcher_stat_runtime', 'filter': ['flowtable_intf_filter']}}
    
class DispatcherStatRuntimeClearView(PostActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'post': {'class_name': 'DispatcherStatRuntime', 'method_name': 'Clear', 'exclusive': True, 'service_name': 'SeAgentService_Stub'}}
    
class DispatcherSehmprobetempdisableRuntimeView(GetActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'get': {'exclusive': True, 'class_name': 'DispatcherSehmprobetempdisableRuntime', 'service_name': 'SeAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'dispatcher_sehmprobetempdisable_runtime'}}
    
class DispatcherSehmprobetempdisableRuntimeClearView(PostActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'post': {'class_name': 'DispatcherSehmprobetempdisableRuntime', 'method_name': 'Clear', 'exclusive': True, 'service_name': 'SeAgentService_Stub'}}
    
class RteringStatRuntimeView(GetActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'get': {'exclusive': True, 'class_name': 'RteringStatRuntime', 'service_name': 'SeAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'rtering_stat_runtime'}}
    
class SeDosStatRuntimeView(GetActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'get': {'exclusive': True, 'class_name': 'SeDosStatRuntime', 'service_name': 'SeAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'se_dos_stat_runtime', 'filter': ['se_params_filter']}}
    
class SeDosStatRuntimeClearView(PostActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'post': {'class_name': 'SeDosStatRuntime', 'method_name': 'Clear', 'exclusive': True, 'service_name': 'SeAgentService_Stub'}}
    
class RouteTableRuntimeView(GetActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'get': {'exclusive': True, 'class_name': 'RouteTableRuntime', 'service_name': 'SeAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'route_table_runtime', 'filter': ['se_params_filter']}}
    
class SeAgentAssertStatRuntimeView(GetActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'get': {'exclusive': True, 'class_name': 'SeAgentAssertStatRuntime', 'service_name': 'SeAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'seagentassert_stat_runtime', 'filter': ['se_params_filter']}}
    
class SeAgentAssertStatRuntimeClearView(PostActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'post': {'class_name': 'SeAgentAssertStatRuntime', 'method_name': 'Clear', 'exclusive': True, 'service_name': 'SeAgentService_Stub'}}
    
class SeFaultInjectExhaustMClearView(PostActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'post': {'class_name': 'SeFaultInjectExhaustM', 'method_name': 'Clear', 'action_param': 'se_fault_inject_exhaust_param', 'exclusive': True, 'service_name': 'SeAgentService_Stub'}}
    
class SeAgentShardClientEventHistoryView(GetActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'get': {'exclusive': True, 'class_name': 'SeAgentShardClientEventHistory', 'service_name': 'SeAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'shard_client_events'}}
    
class IcmpStatRuntimeView(GetActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'get': {'exclusive': True, 'class_name': 'IcmpStatRuntime', 'service_name': 'SeAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'icmp_stat_runtime', 'filter': ['se_params_filter']}}
    
class IcmpStatRuntimeClearView(PostActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'post': {'class_name': 'IcmpStatRuntime', 'method_name': 'Clear', 'exclusive': True, 'service_name': 'SeAgentService_Stub'}}
    
class SeResourceProtoView(GetActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'SeResourceProto', 'service_name': 'ResMgrReadService_Stub', 'default_filter': 'DETAIL', 'method_name': 'Read', 'response_field': 'se_res_internal'}}
    
class BgpDebugInfoView(GetActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'get': {'exclusive': True, 'class_name': 'BgpDebugInfo', 'service_name': 'SeAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'bgp_debuginfo'}}
    
class Ip6RouteTableRuntimeView(GetActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'get': {'exclusive': True, 'class_name': 'Ip6RouteTableRuntime', 'service_name': 'SeAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'ip6_route_table_runtime', 'filter': ['se_params_filter']}}
    
class Ip6StatRuntimeView(GetActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'get': {'exclusive': True, 'class_name': 'Ip6StatRuntime', 'service_name': 'SeAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'ip6_stat_runtime', 'filter': ['se_params_filter']}}
    
class Ip6StatRuntimeClearView(PostActionView):
    model = ServiceEngine
    serializer_class = ServiceEngineSerializer
    rpc_data = {'post': {'class_name': 'Ip6StatRuntime', 'method_name': 'Clear', 'exclusive': True, 'service_name': 'SeAgentService_Stub'}}
    
