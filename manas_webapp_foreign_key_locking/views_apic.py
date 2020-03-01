
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

    
class ApicDevicePkgVerList(GetActionView,):
    model = None
    rpc_data = {'get': {'exclusive': False, 'class_name': 'ApicDevicePkgVer', 'service_name': 'APICAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'ApicDevPkgVer', 'response_field': 'apic_device_pkg_ver'}}
    
    
class ApicDevicePkgVerDetail(GetActionView):
    model = None
    rpc_data = {'get': {'exclusive': False, 'class_name': 'ApicDevicePkgVer', 'service_name': 'APICAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'ApicDevPkgVer', 'response_field': 'apic_device_pkg_ver'}}
            
    
class ApicAgentInternalList(GetActionView,):
    model = None
    rpc_data = {'get': {'exclusive': False, 'class_name': 'ApicAgentInternal', 'service_name': 'APICAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'apic_agent_internal'}}
    
    
class ApicAgentInternalDetail(GetActionView):
    model = None
    rpc_data = {'get': {'exclusive': False, 'class_name': 'ApicAgentInternal', 'service_name': 'APICAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'apic_agent_internal'}}
        
class ApicAgentInternalVerifyapicloginView(PostActionView):
    model = None
    rpc_data = {'post': {'exclusive': False, 'class_name': 'ApicAgentInternal', 'service_name': 'APICAgentService_Stub', 'module': 'avi.protobuf.apic_pb2', 'method_name': 'Verifyapiclogin', 'action_param': 'ApicLogin'}}
        
    
class APICTenantsList(GetActionView,):
    model = None
    rpc_data = {'get': {'exclusive': False, 'class_name': 'APICTenants', 'service_name': 'APICAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Apictenants', 'response_field': 'apic_tenants', 'filter': ['apic_cli_login']}}
    
    
class APICTenantsDetail(GetActionView):
    model = None
    rpc_data = {'get': {'exclusive': False, 'class_name': 'APICTenants', 'service_name': 'APICAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Apictenants', 'response_field': 'apic_tenants', 'filter': ['apic_cli_login']}}
            
    
class APICGraphInstancesList(GetActionView,):
    model = None
    rpc_data = {'get': {'exclusive': False, 'class_name': 'APICGraphInstances', 'service_name': 'APICAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Apicgraphinstances', 'response_field': 'apic_graph_instances'}}
    
    
class APICGraphInstancesDetail(GetActionView):
    model = None
    rpc_data = {'get': {'exclusive': False, 'class_name': 'APICGraphInstances', 'service_name': 'APICAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Apicgraphinstances', 'response_field': 'apic_graph_instances'}}
            
    
class APICEpgEpsList(GetActionView,):
    model = None
    rpc_data = {'get': {'exclusive': False, 'class_name': 'APICEpgEps', 'service_name': 'APICAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Apicepgeps', 'response_field': 'apic_epg_eps', 'filter': ['apic_epg_filter']}}
    
    
class APICEpgEpsDetail(GetActionView):
    model = None
    rpc_data = {'get': {'exclusive': False, 'class_name': 'APICEpgEps', 'service_name': 'APICAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Apicepgeps', 'response_field': 'apic_epg_eps', 'filter': ['apic_epg_filter']}}
            
    
class APICVmmDomainsList(GetActionView,):
    model = None
    rpc_data = {'get': {'exclusive': False, 'class_name': 'APICVmmDomains', 'service_name': 'APICAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Apicvmmdomains', 'response_field': 'apic_vmm_domains', 'filter': ['apic_cli_login']}}
    
    
class APICVmmDomainsDetail(GetActionView):
    model = None
    rpc_data = {'get': {'exclusive': False, 'class_name': 'APICVmmDomains', 'service_name': 'APICAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Apicvmmdomains', 'response_field': 'apic_vmm_domains', 'filter': ['apic_cli_login']}}
            
    
        
class APICTransactionFlapFlapView(PostActionView):
    model = None
    rpc_data = {'post': {'class_name': 'APICTransactionFlap', 'method_name': 'Flap', 'action_param': 'apic_txn_params', 'exclusive': False, 'service_name': 'APICAgentService_Stub'}}
        
    
class CIFTableList(GetActionView,):
    model = None
    rpc_data = {'get': {'exclusive': False, 'class_name': 'CIFTable', 'service_name': 'APICAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'cif_table'}}
    
    
class CIFTableDetail(GetActionView):
    model = None
    rpc_data = {'get': {'exclusive': False, 'class_name': 'CIFTable', 'service_name': 'APICAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'cif_table'}}
            
    
class APICEpgsList(GetActionView,):
    model = None
    rpc_data = {'get': {'exclusive': False, 'class_name': 'APICEpgs', 'service_name': 'APICAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Apicepgs', 'response_field': 'apic_epgs', 'filter': ['apic_all_tenant_filter']}}
    
    
class APICEpgsDetail(GetActionView):
    model = None
    rpc_data = {'get': {'exclusive': False, 'class_name': 'APICEpgs', 'service_name': 'APICAgentService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Apicepgs', 'response_field': 'apic_epgs', 'filter': ['apic_all_tenant_filter']}}
            
    
class APICLifsRuntimeList(ListView, ):
    model = APICLifsRuntime
    serializer_class = APICLifsRuntimeSerializer
    rpc_data = {
            }
    
    
class APICLifsRuntimeDetail(RetrieveView, ):
    model = APICLifsRuntime
    serializer_class = APICLifsRuntimeSerializer
    rpc_data = {
            }
            
