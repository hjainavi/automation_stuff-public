
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

    
class DebugServiceEngineList(ListView, ):
    model = DebugServiceEngine
    serializer_class = DebugServiceEngineSerializer
    rpc_data = {
            }
    
    
class DebugServiceEngineDetail(UpdateView, RetrieveView, ):
    model = DebugServiceEngine
    serializer_class = DebugServiceEngineSerializer
    rpc_data = {
        
        'put': {
            'class_name': 'DebugServiceEngine',
            'method_name': 'Update',
            'field_name': 'debug_service_engine',
            'service_name': 'SeMgrService_Stub',
            'module': 'avi.protobuf.debug_se_pb2'
        },
        
        'patch': {
            'class_name': 'DebugServiceEngine',
            'method_name': 'Update',
            'field_name': 'debug_service_engine',
            'service_name': 'SeMgrService_Stub',
            'module': 'avi.protobuf.debug_se_pb2'
        },
            }
            
