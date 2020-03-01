
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

    
class ServerAutoScalePolicyList(ListView, CreateView):
    model = ServerAutoScalePolicy
    serializer_class = ServerAutoScalePolicySerializer
    rpc_data = {
        
        'post': {
            'class_name': 'ServerAutoScalePolicy',
            'method_name': 'Create',
            'field_name': 'server_auto_scale_policy',
            'service_name': 'ServerAutoScalePolicyService_Stub',
            'module': 'avi.protobuf.server_autoscale_pb2'
        },
            }
    
    
class ServerAutoScalePolicyDetail(RetrieveView, UpdateView, DeleteView):
    model = ServerAutoScalePolicy
    serializer_class = ServerAutoScalePolicySerializer
    rpc_data = {
        
        'put': {
            'class_name': 'ServerAutoScalePolicy',
            'method_name': 'Update',
            'field_name': 'server_auto_scale_policy',
            'service_name': 'ServerAutoScalePolicyService_Stub',
            'module': 'avi.protobuf.server_autoscale_pb2'
        },
        
        'patch': {
            'class_name': 'ServerAutoScalePolicy',
            'method_name': 'Update',
            'field_name': 'server_auto_scale_policy',
            'service_name': 'ServerAutoScalePolicyService_Stub',
            'module': 'avi.protobuf.server_autoscale_pb2'
        },
        
        'delete': {
            'class_name': 'ServerAutoScalePolicy',
            'method_name': 'Delete',
            'field_name': 'server_auto_scale_policy',
            'service_name': 'ServerAutoScalePolicyService_Stub',
            'module': 'avi.protobuf.server_autoscale_pb2'
        },
            }
            
    
class AutoScaleLaunchConfigList(ListView, CreateView):
    model = AutoScaleLaunchConfig
    serializer_class = AutoScaleLaunchConfigSerializer
    rpc_data = {
        
        'post': {
            'class_name': 'AutoScaleLaunchConfig',
            'method_name': 'Create',
            'field_name': 'auto_scale_launch_config',
            'service_name': 'AutoScaleLaunchConfigService_Stub',
            'module': 'avi.protobuf.server_autoscale_pb2'
        },
            }
    
    
class AutoScaleLaunchConfigDetail(RetrieveView, UpdateView, DeleteView):
    model = AutoScaleLaunchConfig
    serializer_class = AutoScaleLaunchConfigSerializer
    rpc_data = {
        
        'put': {
            'class_name': 'AutoScaleLaunchConfig',
            'method_name': 'Update',
            'field_name': 'auto_scale_launch_config',
            'service_name': 'AutoScaleLaunchConfigService_Stub',
            'module': 'avi.protobuf.server_autoscale_pb2'
        },
        
        'patch': {
            'class_name': 'AutoScaleLaunchConfig',
            'method_name': 'Update',
            'field_name': 'auto_scale_launch_config',
            'service_name': 'AutoScaleLaunchConfigService_Stub',
            'module': 'avi.protobuf.server_autoscale_pb2'
        },
        
        'delete': {
            'class_name': 'AutoScaleLaunchConfig',
            'method_name': 'Delete',
            'field_name': 'auto_scale_launch_config',
            'service_name': 'AutoScaleLaunchConfigService_Stub',
            'module': 'avi.protobuf.server_autoscale_pb2'
        },
            }
            
