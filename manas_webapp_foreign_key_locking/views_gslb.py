
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

    
class GslbGeoDbProfileList(ListView, CreateView):
    model = GslbGeoDbProfile
    serializer_class = GslbGeoDbProfileSerializer
    rpc_data = {
        
        'post': {
            'class_name': 'GslbGeoDbProfile',
            'method_name': 'Create',
            'field_name': 'gslb_geodb',
            'service_name': 'GslbGeoDbProfileService_Stub',
            'module': 'avi.protobuf.gslb_pb2'
        },
            }
    
    
class GslbGeoDbProfileDetail(RetrieveView, UpdateView, DeleteView):
    model = GslbGeoDbProfile
    serializer_class = GslbGeoDbProfileSerializer
    rpc_data = {
        
        'put': {
            'class_name': 'GslbGeoDbProfile',
            'method_name': 'Update',
            'field_name': 'gslb_geodb',
            'service_name': 'GslbGeoDbProfileService_Stub',
            'module': 'avi.protobuf.gslb_pb2'
        },
        
        'patch': {
            'class_name': 'GslbGeoDbProfile',
            'method_name': 'Update',
            'field_name': 'gslb_geodb',
            'service_name': 'GslbGeoDbProfileService_Stub',
            'module': 'avi.protobuf.gslb_pb2'
        },
        
        'delete': {
            'class_name': 'GslbGeoDbProfile',
            'method_name': 'Delete',
            'field_name': 'gslb_geodb',
            'service_name': 'GslbGeoDbProfileService_Stub',
            'module': 'avi.protobuf.gslb_pb2'
        },
            }
            
class GslbGeoDbProfileRuntimeView(GetActionView):
    model = GslbGeoDbProfile
    serializer_class = GslbGeoDbProfileSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'GslbGeoDbProfileRuntime', 'service_name': 'GslbGeoDbProfileRuntimeService_Stub', 'default_filter': 'SUMMARY', 'method_name': 'Read', 'response_field': 'geo_summary'}}
    
