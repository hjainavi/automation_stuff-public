
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

    
class CloudPropertiesList(ListView, ):
    model = CloudProperties
    serializer_class = CloudPropertiesSerializer
    rpc_data = {
            }
    
    
class CloudPropertiesDetail(UpdateView, RetrieveView, ):
    model = CloudProperties
    serializer_class = CloudPropertiesSerializer
    rpc_data = {
        
        'put': {
            'class_name': 'CloudProperties',
            'method_name': 'Update',
            'field_name': 'cloud_props',
            'service_name': 'ControllerWorkerService_Stub',
            'module': 'avi.protobuf.cloud_properties_pb2'
        },
        
        'patch': {
            'class_name': 'CloudProperties',
            'method_name': 'Update',
            'field_name': 'cloud_props',
            'service_name': 'ControllerWorkerService_Stub',
            'module': 'avi.protobuf.cloud_properties_pb2'
        },
            }
            
