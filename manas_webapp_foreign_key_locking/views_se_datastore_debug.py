
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

    
class SeDatastoreStatusList(GetActionView,):
    model = None
    rpc_data = {'get': {'exclusive': False, 'class_name': 'SeDatastoreStatus', 'service_name': 'SeDatastoreDebugService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'se_datastore_status', 'filter': ['se_datastore_debug_filter']}}
    
    
class SeDatastoreStatusDetail(GetActionView):
    model = None
    rpc_data = {'get': {'exclusive': False, 'class_name': 'SeDatastoreStatus', 'service_name': 'SeDatastoreDebugService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'se_datastore_status', 'filter': ['se_datastore_debug_filter']}}
            
    
class DiffQueueStatusList(GetActionView,):
    model = None
    rpc_data = {'get': {'exclusive': False, 'class_name': 'DiffQueueStatus', 'service_name': 'SeDatastoreDebugService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'diff_queue_status', 'filter': ['diff_queue_debug_filter']}}
    
    
class DiffQueueStatusDetail(GetActionView):
    model = None
    rpc_data = {'get': {'exclusive': False, 'class_name': 'DiffQueueStatus', 'service_name': 'SeDatastoreDebugService_Stub', 'default_filter': 'INTERNAL', 'method_name': 'Read', 'response_field': 'diff_queue_status', 'filter': ['diff_queue_debug_filter']}}
            
