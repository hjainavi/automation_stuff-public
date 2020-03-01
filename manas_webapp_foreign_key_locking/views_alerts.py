
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

    
class AlertSyslogConfigList(ListView, CreateView):
    model = AlertSyslogConfig
    serializer_class = AlertSyslogConfigSerializer
    rpc_data = {
            }
    
    
class AlertSyslogConfigDetail(RetrieveView, UpdateView, DeleteView):
    model = AlertSyslogConfig
    serializer_class = AlertSyslogConfigSerializer
    rpc_data = {
            }
        
class AlertSyslogConfigAlerttestsyslogView(PostActionView):
    model = AlertSyslogConfig
    serializer_class = AlertSyslogConfigSerializer
    rpc_data = {'post': {'exclusive': False, 'class_name': 'AlertSyslogConfig', 'service_name': 'AlertMgrService_Stub', 'module': 'avi.protobuf.alerts_pb2', 'method_name': 'Alerttestsyslog', 'action_param': 'AlertTestSyslogSnmpParams'}}
        
    
class AlertScriptConfigList(ListView, CreateView):
    model = AlertScriptConfig
    serializer_class = AlertScriptConfigSerializer
    rpc_data = {
            }
    
    
class AlertScriptConfigDetail(RetrieveView, UpdateView, DeleteView):
    model = AlertScriptConfig
    serializer_class = AlertScriptConfigSerializer
    rpc_data = {
            }
            
    
class AlertEmailConfigList(ListView, CreateView):
    model = AlertEmailConfig
    serializer_class = AlertEmailConfigSerializer
    rpc_data = {
            }
    
    
class AlertEmailConfigDetail(RetrieveView, UpdateView, DeleteView):
    model = AlertEmailConfig
    serializer_class = AlertEmailConfigSerializer
    rpc_data = {
            }
        
class AlertEmailConfigAlerttestemailView(PostActionView):
    model = AlertEmailConfig
    serializer_class = AlertEmailConfigSerializer
    rpc_data = {'post': {'exclusive': False, 'class_name': 'AlertEmailConfig', 'service_name': 'AlertMgrService_Stub', 'module': 'avi.protobuf.alerts_pb2', 'method_name': 'Alerttestemail', 'action_param': 'AlertTestEmailParams'}}
        
    
class AlertList(ListView, ):
    model = Alert
    serializer_class = AlertSerializer
    rpc_data = {
            }
    
    
class AlertDetail(RetrieveView, DeleteView, ):
    model = Alert
    serializer_class = AlertSerializer
    rpc_data = {
            }
            
    
class AlertConfigList(ListView, CreateView):
    model = AlertConfig
    serializer_class = AlertConfigSerializer
    rpc_data = {
            }
    
    
class AlertConfigDetail(RetrieveView, UpdateView, DeleteView):
    model = AlertConfig
    serializer_class = AlertConfigSerializer
    rpc_data = {
            }
            
    
        
class AlertParamsSetView(PostActionView):
    model = None
    rpc_data = {'post': {'exclusive': False, 'class_name': 'AlertParams', 'service_name': 'AlertMgrService_Stub', 'module': 'avi.protobuf.alerts_pb2', 'method_name': 'Set', 'action_param': 'AlertMgrParams'}}
        
    
class ActionGroupConfigList(ListView, CreateView):
    model = ActionGroupConfig
    serializer_class = ActionGroupConfigSerializer
    rpc_data = {
            }
    
    
class ActionGroupConfigDetail(RetrieveView, UpdateView, DeleteView):
    model = ActionGroupConfig
    serializer_class = ActionGroupConfigSerializer
    rpc_data = {
            }
            
    
class AlertObjectListList(CreateView, ListView, ):
    model = AlertObjectList
    serializer_class = AlertObjectListSerializer
    rpc_data = {
            }
    
    
class AlertObjectListDetail(UpdateView, DeleteView, RetrieveView, ):
    model = AlertObjectList
    serializer_class = AlertObjectListSerializer
    rpc_data = {
            }
            
