
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

    
class SystemConfigurationList(ListView, ):
    model = SystemConfiguration
    serializer_class = SystemConfigurationSerializer
    rpc_data = {
            }
    
    
class SystemConfigurationDetail(UpdateView, RetrieveView, ):
    model = SystemConfiguration
    serializer_class = SystemConfigurationSerializer
    rpc_data = {
        
        'put': {
            'class_name': 'SystemConfiguration',
            'method_name': 'Update',
            'field_name': 'system_configuration',
            'service_name': 'SysConfService_Stub',
            'module': 'avi.protobuf.system_pb2'
        },
        
        'patch': {
            'class_name': 'SystemConfiguration',
            'method_name': 'Update',
            'field_name': 'system_configuration',
            'service_name': 'SysConfService_Stub',
            'module': 'avi.protobuf.system_pb2'
        },
            }
        
class SystemConfigurationSystestemailView(PostActionView):
    model = SystemConfiguration
    serializer_class = SystemConfigurationSerializer
    rpc_data = {'post': {'exclusive': False, 'class_name': 'SystemConfiguration', 'service_name': 'AlertMgrService_Stub', 'module': 'avi.protobuf.alerts_pb2', 'method_name': 'Systestemail', 'action_param': 'SysTestEmailParams'}}
        
    
class ControllerSiteList(ListView, CreateView):
    model = ControllerSite
    serializer_class = ControllerSiteSerializer
    rpc_data = {
            }
    
    
class ControllerSiteDetail(RetrieveView, UpdateView, DeleteView):
    model = ControllerSite
    serializer_class = ControllerSiteSerializer
    rpc_data = {
            }
            
