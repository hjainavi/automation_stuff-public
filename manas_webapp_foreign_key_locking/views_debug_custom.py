
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

from rest_framework.response import Response

from api.models_debug_se import DebugVirtualService
from api.serializers_debug_se import DebugVirtualServiceSerializer
from avi.rest.views import ListView, RetrieveView, UpdateView
from avi.util.protobuf import protobuf2dict
from avi.rest.debug_se_utils import get_debug_vs_capture_progress

class DebugVirtualServiceProgressView(RetrieveView):
    def get(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        vs_uuid = kwargs.get('slug')
        progress_pb = get_debug_vs_capture_progress(vs_uuid)
        data = protobuf2dict(progress_pb)
        rsp = Response(data=data, status=200)
        return rsp


class DebugVirtualServiceList(ListView, ):
    model = DebugVirtualService
    serializer_class = DebugVirtualServiceSerializer
    rpc_data = {}


class DebugVirtualServiceDetail(UpdateView, RetrieveView, ):
    model = DebugVirtualService
    serializer_class = DebugVirtualServiceSerializer
    rpc_data = {
        'put': {
            'class_name': 'DebugVirtualService',
            'method_name': 'UpdateDebugVS',
            'field_name': '',
            'service_name': 'VirtualServiceService_Stub',
            'module': 'avi.protobuf.debug_se_pb2'
        },
        'patch': {
            'class_name': 'DebugVirtualService',
            'method_name': 'UpdateDebugVS',
            'field_name': '',
            'service_name': 'VirtualServiceService_Stub',
            'module': 'avi.protobuf.debug_se_pb2'
        }
    }
