
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

    
class VIDCInfoList(ListView, ):
    model = VIDCInfo
    serializer_class = VIDCInfoSerializer
    rpc_data = {
            }
    
    
class VIDCInfoDetail(RetrieveView, ):
    model = VIDCInfo
    serializer_class = VIDCInfoSerializer
    rpc_data = {
            }
            
    
class VIMgrSEVMRuntimeList(ListView, ):
    model = VIMgrSEVMRuntime
    serializer_class = VIMgrSEVMRuntimeSerializer
    rpc_data = {
            }
    
    
class VIMgrSEVMRuntimeDetail(RetrieveView, ):
    model = VIMgrSEVMRuntime
    serializer_class = VIMgrSEVMRuntimeSerializer
    rpc_data = {
            }
            
    
class VIMgrNWRuntimeList(ListView, ):
    model = VIMgrNWRuntime
    serializer_class = VIMgrNWRuntimeSerializer
    rpc_data = {
            }
    
    
class VIMgrNWRuntimeDetail(RetrieveView, ):
    model = VIMgrNWRuntime
    serializer_class = VIMgrNWRuntimeSerializer
    rpc_data = {
            }
            
    
class VIPGNameInfoList(ListView, ):
    model = VIPGNameInfo
    serializer_class = VIPGNameInfoSerializer
    rpc_data = {
            }
    
    
class VIPGNameInfoDetail(RetrieveView, ):
    model = VIPGNameInfo
    serializer_class = VIPGNameInfoSerializer
    rpc_data = {
            }
            
    
class VIMgrClusterRuntimeList(ListView, ):
    model = VIMgrClusterRuntime
    serializer_class = VIMgrClusterRuntimeSerializer
    rpc_data = {
            }
    
    
class VIMgrClusterRuntimeDetail(RetrieveView, ):
    model = VIMgrClusterRuntime
    serializer_class = VIMgrClusterRuntimeSerializer
    rpc_data = {
            }
            
    
class VIMgrControllerRuntimeList(ListView, ):
    model = VIMgrControllerRuntime
    serializer_class = VIMgrControllerRuntimeSerializer
    rpc_data = {
            }
    
    
class VIMgrControllerRuntimeDetail(RetrieveView, ):
    model = VIMgrControllerRuntime
    serializer_class = VIMgrControllerRuntimeSerializer
    rpc_data = {
            }
            
    
class InterestedVMsList(GetActionView,):
    model = None
    rpc_data = {'get': {'exclusive': False, 'class_name': 'InterestedVMs', 'service_name': 'VIMgrCliService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'interested_vms'}}
    
    
class InterestedVMsDetail(GetActionView):
    model = None
    rpc_data = {'get': {'exclusive': False, 'class_name': 'InterestedVMs', 'service_name': 'VIMgrCliService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'interested_vms'}}
            
    
class VIMgrDCRuntimeList(ListView, ):
    model = VIMgrDCRuntime
    serializer_class = VIMgrDCRuntimeSerializer
    rpc_data = {
            }
    
    
class VIMgrDCRuntimeDetail(RetrieveView, ):
    model = VIMgrDCRuntime
    serializer_class = VIMgrDCRuntimeSerializer
    rpc_data = {
            }
            
    
class InterestedHostsList(GetActionView,):
    model = None
    rpc_data = {'get': {'exclusive': False, 'class_name': 'InterestedHosts', 'service_name': 'VIMgrCliService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'interested_hosts'}}
    
    
class InterestedHostsDetail(GetActionView):
    model = None
    rpc_data = {'get': {'exclusive': False, 'class_name': 'InterestedHosts', 'service_name': 'VIMgrCliService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'interested_hosts'}}
            
    
class VIMgrVMRuntimeList(ListView, ):
    model = VIMgrVMRuntime
    serializer_class = VIMgrVMRuntimeSerializer
    rpc_data = {
            }
    
    
class VIMgrVMRuntimeDetail(RetrieveView, ):
    model = VIMgrVMRuntime
    serializer_class = VIMgrVMRuntimeSerializer
    rpc_data = {
            }
            
    
class VIMgrVcenterRuntimeList(ListView, ):
    model = VIMgrVcenterRuntime
    serializer_class = VIMgrVcenterRuntimeSerializer
    rpc_data = {
            }
    
    
class VIMgrVcenterRuntimeDetail(RetrieveView, ):
    model = VIMgrVcenterRuntime
    serializer_class = VIMgrVcenterRuntimeSerializer
    rpc_data = {
            }
        
class VIMgrVcenterRuntimeSpawnView(PostActionView):
    model = VIMgrVcenterRuntime
    serializer_class = VIMgrVcenterRuntimeSerializer
    rpc_data = {'post': {'exclusive': False, 'class_name': 'VIMgrVcenterRuntime', 'service_name': 'VIMgrCliService_Stub', 'module': 'avi.protobuf.vi_mgr_common_pb2', 'method_name': 'Spawn', 'action_param': 'VICreateSEReq'}}
    
class VIMgrVcenterRuntimeRemoveView(PostActionView):
    model = VIMgrVcenterRuntime
    serializer_class = VIMgrVcenterRuntimeSerializer
    rpc_data = {'post': {'exclusive': False, 'class_name': 'VIMgrVcenterRuntime', 'service_name': 'VIMgrCliService_Stub', 'module': 'avi.protobuf.vi_mgr_common_pb2', 'method_name': 'Remove', 'action_param': 'VIDeleteSEReq'}}
    
class VIMgrVcenterRuntimeSetmgmtipView(PostActionView):
    model = VIMgrVcenterRuntime
    serializer_class = VIMgrVcenterRuntimeSerializer
    rpc_data = {'post': {'exclusive': False, 'class_name': 'VIMgrVcenterRuntime', 'service_name': 'VIMgrCliService_Stub', 'module': 'avi.protobuf.vi_mgr_common_pb2', 'method_name': 'Setmgmtip', 'action_param': 'VISetMgmtIpSEReq'}}
    
class VIMgrVcenterRuntimeModifymgmtipView(PostActionView):
    model = VIMgrVcenterRuntime
    serializer_class = VIMgrVcenterRuntimeSerializer
    rpc_data = {'post': {'exclusive': False, 'class_name': 'VIMgrVcenterRuntime', 'service_name': 'VIMgrCliService_Stub', 'module': 'avi.protobuf.vi_mgr_common_pb2', 'method_name': 'Modifymgmtip', 'action_param': 'VISetMgmtIpSEReq'}}
    
class VIMgrVcenterRuntimeSetvnicView(PostActionView):
    model = VIMgrVcenterRuntime
    serializer_class = VIMgrVcenterRuntimeSerializer
    rpc_data = {'post': {'exclusive': False, 'class_name': 'VIMgrVcenterRuntime', 'service_name': 'VIMgrCliService_Stub', 'module': 'avi.protobuf.vi_mgr_common_pb2', 'method_name': 'Setvnic', 'action_param': 'VISetvNicNwReq'}}
    
class VIMgrVcenterRuntimeModifyvnicView(PostActionView):
    model = VIMgrVcenterRuntime
    serializer_class = VIMgrVcenterRuntimeSerializer
    rpc_data = {'post': {'exclusive': False, 'class_name': 'VIMgrVcenterRuntime', 'service_name': 'VIMgrCliService_Stub', 'module': 'avi.protobuf.vi_mgr_common_pb2', 'method_name': 'Modifyvnic', 'action_param': 'VISetvNicNwReq'}}
    
class VIMgrVcenterRuntimeRetrievevcenterdcnwsView(PostActionView):
    model = VIMgrVcenterRuntime
    serializer_class = VIMgrVcenterRuntimeSerializer
    rpc_data = {'post': {'class_name': 'VIMgrVcenterRuntime', 'method_name': 'Retrievevcenterdcnws', 'action_param': 'vi_retrieve_pg_names', 'exclusive': False, 'service_name': 'VIMgrCliService_Stub'}}
    
class VIMgrVcenterRuntimeRediscoverView(PostActionView):
    model = VIMgrVcenterRuntime
    serializer_class = VIMgrVcenterRuntimeSerializer
    rpc_data = {'post': {'class_name': 'VIMgrVcenterRuntime', 'method_name': 'Rediscover', 'action_param': 'rediscover_vcenter_param', 'exclusive': False, 'service_name': 'VIMgrCliService_Stub'}}
    
class VIMgrVcenterRuntimeGetnetworksView(PostActionView):
    model = VIMgrVcenterRuntime
    serializer_class = VIMgrVcenterRuntimeSerializer
    rpc_data = {'post': {'class_name': 'VIMgrVcenterRuntime', 'method_name': 'Getnetworks', 'exclusive': False, 'service_name': 'VIMgrCliService_Stub'}}
    
class VIMgrVcenterRuntimeVerifyloginView(PostActionView):
    model = VIMgrVcenterRuntime
    serializer_class = VIMgrVcenterRuntimeSerializer
    rpc_data = {'post': {'class_name': 'VIMgrVcenterRuntime', 'method_name': 'Verifylogin', 'action_param': 'vcenter_login', 'exclusive': False, 'service_name': 'VIMgrCliService_Stub'}}
    
class VIMgrVcenterRuntimeOs_Verify_LoginView(PostActionView):
    model = VIMgrVcenterRuntime
    serializer_class = VIMgrVcenterRuntimeSerializer
    rpc_data = {'post': {'exclusive': False, 'class_name': 'VIMgrVcenterRuntime', 'service_name': 'CloudConnectorService_Stub', 'module': 'avi.protobuf.cloud_connector_message_pb2', 'method_name': 'OsVerifyLogin', 'action_param': 'OpenstackLogin'}}
    
class VIMgrVcenterRuntimeAws_Verify_LoginView(PostActionView):
    model = VIMgrVcenterRuntime
    serializer_class = VIMgrVcenterRuntimeSerializer
    rpc_data = {'post': {'exclusive': False, 'class_name': 'VIMgrVcenterRuntime', 'service_name': 'CloudConnectorService_Stub', 'module': 'avi.protobuf.cloud_connector_message_pb2', 'method_name': 'AwsVerifyLogin', 'action_param': 'AWSLogin'}}
    
class VIMgrVcenterRuntimeFaultinjectView(PostActionView):
    model = VIMgrVcenterRuntime
    serializer_class = VIMgrVcenterRuntimeSerializer
    rpc_data = {'post': {'exclusive': False, 'class_name': 'VIMgrVcenterRuntime', 'service_name': 'VIMgrCliService_Stub', 'module': 'avi.protobuf.vi_mgr_common_pb2', 'method_name': 'Faultinject', 'action_param': 'VIFaultInjection'}}
    
class VIMgrVcenterRuntimeDeletenetworkView(PostActionView):
    model = VIMgrVcenterRuntime
    serializer_class = VIMgrVcenterRuntimeSerializer
    rpc_data = {'post': {'class_name': 'VIMgrVcenterRuntime', 'method_name': 'Deletenetwork', 'action_param': 'vi_delete_network_filter', 'exclusive': False, 'service_name': 'VIMgrCliService_Stub'}}
    
class VIMgrVcenterRuntimeVcenterstatusView(PostActionView):
    model = VIMgrVcenterRuntime
    serializer_class = VIMgrVcenterRuntimeSerializer
    rpc_data = {'post': {'exclusive': False, 'class_name': 'VIMgrVcenterRuntime', 'service_name': 'VIMgrCliService_Stub', 'module': 'avi.protobuf.vi_mgr_common_pb2', 'method_name': 'Vcenterstatus', 'action_param': 'VcenterCloudStatusReq'}}
    
class VIMgrVcenterRuntimeVcenterdiagView(PostActionView):
    model = VIMgrVcenterRuntime
    serializer_class = VIMgrVcenterRuntimeSerializer
    rpc_data = {'post': {'exclusive': False, 'class_name': 'VIMgrVcenterRuntime', 'service_name': 'FiltersService_Stub', 'module': 'avi.protobuf.vi_mgr_common_pb2', 'method_name': 'Vcenterdiag', 'action_param': 'VcenterInventoryDiagReq'}}
    
class VIMgrVcenterRuntimeControlleripsubnetsView(PostActionView):
    model = VIMgrVcenterRuntime
    serializer_class = VIMgrVcenterRuntimeSerializer
    rpc_data = {'post': {'class_name': 'VIMgrVcenterRuntime', 'method_name': 'Controlleripsubnets', 'exclusive': False, 'service_name': 'NetworkMgrService_Stub'}}
    
class VIMgrVcenterRuntimeGeneventView(PostActionView):
    model = VIMgrVcenterRuntime
    serializer_class = VIMgrVcenterRuntimeSerializer
    rpc_data = {'post': {'class_name': 'VIMgrVcenterRuntime', 'method_name': 'Genevent', 'action_param': 'event_gen_params', 'exclusive': False, 'service_name': 'FiltersService_Stub'}}
        
class VINetworkSubnetVMsView(GetActionView):
    model = VIMgrVcenterRuntime
    serializer_class = VIMgrVcenterRuntimeSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'VINetworkSubnetVMs', 'service_name': 'VIMgrCliService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'vi_network_subnet_vms', 'filter': ['vi_network_subnet_filter']}}
    
class VIDatastoreContentsView(GetActionView):
    model = VIMgrVcenterRuntime
    serializer_class = VIMgrVcenterRuntimeSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'VIDatastoreContents', 'service_name': 'VIMgrCliService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'datastore_contents', 'filter': ['vi_redis_datastore_filter']}}
    
class VIDatastoreView(GetActionView):
    model = VIMgrVcenterRuntime
    serializer_class = VIMgrVcenterRuntimeSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'VIDatastore', 'service_name': 'VIMgrCliService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'vi_datastores', 'filter': ['vi_datastore_filtler']}}
    
class VISubfoldersView(GetActionView):
    model = VIMgrVcenterRuntime
    serializer_class = VIMgrVcenterRuntimeSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'VISubfolders', 'service_name': 'VIMgrCliService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'vi_subfolders', 'filter': ['vi_subfolder_filtler']}}
    
class VIHostResourcesView(GetActionView):
    model = VIMgrVcenterRuntime
    serializer_class = VIMgrVcenterRuntimeSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'VIHostResources', 'service_name': 'VIMgrCliService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'vi_hostresources', 'filter': ['vi_host_resource_filter']}}
    
    
class SEVMCreateProgressList(GetActionView,):
    model = None
    rpc_data = {'get': {'exclusive': False, 'class_name': 'SEVMCreateProgress', 'service_name': 'VIMgrCliService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'sevm_create_progress'}}
    
    
class SEVMCreateProgressDetail(GetActionView):
    model = None
    rpc_data = {'get': {'exclusive': False, 'class_name': 'SEVMCreateProgress', 'service_name': 'VIMgrCliService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'sevm_create_progress'}}
            
    
class VIMgrHostRuntimeList(ListView, ):
    model = VIMgrHostRuntime
    serializer_class = VIMgrHostRuntimeSerializer
    rpc_data = {
            }
    
    
class VIMgrHostRuntimeDetail(RetrieveView, ):
    model = VIMgrHostRuntime
    serializer_class = VIMgrHostRuntimeSerializer
    rpc_data = {
            }
        
class VIMgrHostRuntimeMakeaccessibleView(PostActionView):
    model = VIMgrHostRuntime
    serializer_class = VIMgrHostRuntimeSerializer
    rpc_data = {'post': {'class_name': 'VIMgrHostRuntime', 'method_name': 'Makeaccessible', 'exclusive': False, 'service_name': 'VIMgrCliService_Stub'}}
        
