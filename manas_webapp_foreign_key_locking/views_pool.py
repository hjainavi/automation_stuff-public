
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

    
class PoolList(ListView, CreateView):
    model = Pool
    serializer_class = PoolSerializer
    rpc_data = {
        
        'post': {
            'class_name': 'Pool',
            'method_name': 'Create',
            'field_name': 'pool',
            'service_name': 'PoolService_Stub',
            'module': 'avi.protobuf.pool_pb2'
        },
            }
    
    
class PoolDetail(RetrieveView, UpdateView, DeleteView):
    model = Pool
    serializer_class = PoolSerializer
    rpc_data = {
        
        'put': {
            'class_name': 'Pool',
            'method_name': 'Update',
            'field_name': 'pool',
            'service_name': 'PoolService_Stub',
            'module': 'avi.protobuf.pool_pb2'
        },
        
        'patch': {
            'class_name': 'Pool',
            'method_name': 'Update',
            'field_name': 'pool',
            'service_name': 'PoolService_Stub',
            'module': 'avi.protobuf.pool_pb2'
        },
        
        'delete': {
            'class_name': 'Pool',
            'method_name': 'Delete',
            'field_name': 'pool',
            'service_name': 'PoolService_Stub',
            'module': 'avi.protobuf.pool_pb2'
        },
            }
        
class PoolScaleoutView(PostActionView):
    model = Pool
    serializer_class = PoolSerializer
    rpc_data = {'post': {'exclusive': False, 'class_name': 'Pool', 'service_name': 'AutoScaleService_Stub', 'module': 'avi.protobuf.server_autoscale_pb2', 'method_name': 'Scaleout', 'action_param': 'ServerScaleOutParams'}}
    
class PoolScaleinView(PostActionView):
    model = Pool
    serializer_class = PoolSerializer
    rpc_data = {'post': {'exclusive': False, 'class_name': 'Pool', 'service_name': 'AutoScaleService_Stub', 'module': 'avi.protobuf.server_autoscale_pb2', 'method_name': 'Scalein', 'action_param': 'ServerScaleInParams'}}
    
class PoolClearView(PostActionView):
    model = Pool
    serializer_class = PoolSerializer
    rpc_data = {'post': {'class_name': 'Pool', 'method_name': 'Clear', 'exclusive': False, 'service_name': 'PoolService_Stub'}}
        
class HealthMonitorRuntimeView(GetActionView):
    model = Pool
    serializer_class = PoolSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'HealthMonitorRuntime', 'service_name': 'PoolService_Stub', 'default_filter': 'DETAIL', 'method_name': 'Read', 'response_field': 'health_monitor_runtime'}}
    
class ServerRuntimeDetailView(GetActionView):
    model = Pool
    serializer_class = PoolSerializer
    rpc_data = {'get': {'exclusive': False, 'pagination': True, 'class_name': 'ServerRuntime', 'service_name': 'PoolService_Stub', 'default_filter': 'DETAIL', 'method_name': 'Read', 'response_field': 'server_runtime_detail', 'filter': ['se_params_filter', 'server_filter']}}
    
class ConnpoolStatsClearView(PostActionView):
    model = Pool
    serializer_class = PoolSerializer
    rpc_data = {'post': {'class_name': 'ConnpoolStats', 'method_name': 'Clear', 'exclusive': False, 'service_name': 'PoolService_Stub'}}
    
class PoolRuntimeDetailView(GetActionView):
    model = Pool
    serializer_class = PoolSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'PoolRuntimeDetail', 'service_name': 'PoolService_Stub', 'default_filter': 'DETAIL', 'method_name': 'Read', 'response_field': 'pool_runtime_detail', 'filter': ['se_params_filter', 'server_filter']}}
    
class ServerInternalView(GetActionView):
    model = Pool
    serializer_class = PoolSerializer
    rpc_data = {'get': {'exclusive': False, 'pagination': True, 'class_name': 'ServerRuntime', 'service_name': 'PoolService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'server_internal', 'filter': ['se_params_filter', 'server_filter']}}
    
class PersistenceInternalView(GetActionView):
    model = Pool
    serializer_class = PoolSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'PersistenceInternal', 'service_name': 'PoolService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'persistence_internal', 'filter': ['persistence_filter', 'se_params_filter']}}
    
class PersistenceInternalClearView(PostActionView):
    model = Pool
    serializer_class = PoolSerializer
    rpc_data = {'post': {'class_name': 'PersistenceInternal', 'method_name': 'Clear', 'action_param': 'persistence_filter', 'exclusive': False, 'service_name': 'PoolService_Stub'}}
    
class RequestQueueRuntimeClearView(PostActionView):
    model = Pool
    serializer_class = PoolSerializer
    rpc_data = {'post': {'class_name': 'RequestQueueRuntime', 'method_name': 'Clear', 'exclusive': False, 'service_name': 'PoolService_Stub'}}
    
class HttpCacheStatsView(GetActionView):
    model = Pool
    serializer_class = PoolSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'HttpCacheStats', 'service_name': 'PoolService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'httpcache_stats', 'filter': ['se_params_filter']}}
    
class HttpCacheStatsClearView(PostActionView):
    model = Pool
    serializer_class = PoolSerializer
    rpc_data = {'post': {'class_name': 'HttpCacheStats', 'method_name': 'Clear', 'exclusive': False, 'service_name': 'PoolService_Stub'}}
    
class PoolStatsClearView(PostActionView):
    model = Pool
    serializer_class = PoolSerializer
    rpc_data = {'post': {'class_name': 'PoolStats', 'method_name': 'Clear', 'exclusive': False, 'service_name': 'PoolService_Stub'}}
    
class ConnpoolInternalView(GetActionView):
    model = Pool
    serializer_class = PoolSerializer
    rpc_data = {'get': {'exclusive': False, 'pagination': True, 'class_name': 'ConnpoolInternal', 'service_name': 'PoolService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'connpool_internal', 'filter': ['connpool_filter', 'se_params_filter']}}
    
class ConnpoolInternalClearView(PostActionView):
    model = Pool
    serializer_class = PoolSerializer
    rpc_data = {'post': {'class_name': 'ConnpoolInternal', 'method_name': 'Clear', 'action_param': 'connpool_filter', 'exclusive': False, 'service_name': 'PoolService_Stub'}}
    
class VsesSharingPoolView(GetActionView):
    model = Pool
    serializer_class = PoolSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'VsesSharingPool', 'service_name': 'PoolService_Stub', 'default_filter': 'DETAIL', 'method_name': 'Read', 'response_field': 'vses_sharing_pool'}}
    
class HttpCacheView(GetActionView):
    model = Pool
    serializer_class = PoolSerializer
    rpc_data = {'get': {'exclusive': False, 'pagination': True, 'class_name': 'HttpCache', 'service_name': 'PoolService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'httpcache', 'filter': ['httpcache_obj_filter', 'se_params_filter']}}
    
class HttpCacheClearView(PostActionView):
    model = Pool
    serializer_class = PoolSerializer
    rpc_data = {'post': {'exclusive': False, 'class_name': 'HttpCache', 'service_name': 'PoolService_Stub', 'method_name': 'Clear', 'action_param': 'httpcache_obj_filter', 'filter': ['httpcache_obj_filter']}}
    
class HttpCacheView(GetActionView):
    model = Pool
    serializer_class = PoolSerializer
    rpc_data = {'get': {'exclusive': False, 'pagination': True, 'class_name': 'HttpCache', 'service_name': 'PoolService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'httpcache', 'filter': ['httpcache_obj_filter', 'se_params_filter']}}
    
class PoolDebugView(GetActionView):
    model = Pool
    serializer_class = PoolSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'PoolDebug', 'service_name': 'PoolService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'pool_debug'}}
    
class HttpCacheStatsDetailView(GetActionView):
    model = Pool
    serializer_class = PoolSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'HttpCacheStats', 'service_name': 'PoolService_Stub', 'default_filter': 'DETAIL', 'method_name': 'Read', 'response_field': 'httpcache_stats_detail', 'filter': ['se_params_filter']}}
    
class ServerRuntimeSummaryView(GetActionView):
    model = Pool
    serializer_class = PoolSerializer
    rpc_data = {'get': {'exclusive': False, 'pagination': True, 'class_name': 'ServerRuntime', 'service_name': 'PoolService_Stub', 'default_filter': 'SUMMARY', 'method_name': 'Read', 'response_field': 'server_runtime_summary', 'filter': ['server_filter']}}
    
class PoolRuntimeSummaryView(GetActionView):
    model = Pool
    serializer_class = PoolSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'PoolRuntimeSummary', 'service_name': 'PoolService_Stub', 'default_filter': 'SUMMARY', 'method_name': 'Read', 'response_field': 'pool_runtime_summary'}}
    
class AlgoStatRuntimeView(GetActionView):
    model = Pool
    serializer_class = PoolSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'AlgoStatRuntime', 'service_name': 'PoolService_Stub', 'default_filter': 'DETAIL', 'method_name': 'Read', 'response_field': 'algo_stat_runtime'}}
    
class PoolInternalView(GetActionView):
    model = Pool
    serializer_class = PoolSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'PoolInternal', 'service_name': 'PoolService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'pool_internal', 'filter': ['se_params_filter', 'server_filter']}}
    
class HealthMonitorStatRuntimeView(GetActionView):
    model = Pool
    serializer_class = PoolSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'HealthMonitorStatRuntime', 'service_name': 'PoolService_Stub', 'default_filter': 'DETAIL', 'method_name': 'Read', 'response_field': 'health_monitor_stat_runtime', 'filter': ['se_params_filter', 'server_filter']}}
    
