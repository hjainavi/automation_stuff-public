
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

    
class ProtocolParserList(ListView, CreateView):
    model = ProtocolParser
    serializer_class = ProtocolParserSerializer
    rpc_data = {
        
        'post': {
            'class_name': 'ProtocolParser',
            'method_name': 'Create',
            'field_name': 'protocol_parser',
            'service_name': 'ProtocolParserService_Stub',
            'module': 'avi.protobuf.protocol_parser_pb2'
        },
            }
    
    
class ProtocolParserDetail(RetrieveView, UpdateView, DeleteView):
    model = ProtocolParser
    serializer_class = ProtocolParserSerializer
    rpc_data = {
        
        'put': {
            'class_name': 'ProtocolParser',
            'method_name': 'Update',
            'field_name': 'protocol_parser',
            'service_name': 'ProtocolParserService_Stub',
            'module': 'avi.protobuf.protocol_parser_pb2'
        },
        
        'patch': {
            'class_name': 'ProtocolParser',
            'method_name': 'Update',
            'field_name': 'protocol_parser',
            'service_name': 'ProtocolParserService_Stub',
            'module': 'avi.protobuf.protocol_parser_pb2'
        },
        
        'delete': {
            'class_name': 'ProtocolParser',
            'method_name': 'Delete',
            'field_name': 'protocol_parser',
            'service_name': 'ProtocolParserService_Stub',
            'module': 'avi.protobuf.protocol_parser_pb2'
        },
            }
            
