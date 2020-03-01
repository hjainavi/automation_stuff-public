
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

"""
=====================
Webhook Views
=====================
"""

import logging
from rest_framework.response import Response

from avi.rest.views import CreateView
from google.protobuf.service import RpcController
from avi.infrastructure.rpc_channel import RpcChannel
from avi.protobuf.cloud_connector_rpc_pb2 import (CloudConnectorService_Stub,
                  cc_webhook_mesos_req, cc_webhook_marathon_req)
from rest_framework.permissions import AllowAny
from api.views_cloud_connector_custom import _get_cloud
from avi.protobuf import common_pb2

log = logging.getLogger(__name__)

class WebhookMesosAgent(CreateView):
    permission_classes = (AllowAny,)
    def post(self, request, *args, **kwargs):
        (cc_obj, rsp_obj) = _get_cloud(request.DATA,
                                       vtype_chk=common_pb2.CLOUD_MESOS)
        if rsp_obj:
            return rsp_obj
        req = cc_webhook_mesos_req()
        req.cc_id = cc_obj.uuid
        req.response_uuid = request.DATA.get('response_uuid', '')
        if not req.response_uuid:
            raise Exception('response_uuid is required')
        req.status_code = request.DATA.get('status_code', 200)
        req.response = request.DATA.get('response', '')
        CloudConnectorService_Stub(RpcChannel()).\
            cc_webhook_mesos(RpcController(), req)
        return Response(data='Success', status=200)

class WebhookMarathon(CreateView):
    permission_classes = (AllowAny,)
    def post(self, request, *args, **kwargs):
        event_type = request.DATA.get('eventType', '')
        if not event_type:
            raise Exception('event_type is required')
        elif (event_type != 'api_post_event' and
              event_type != 'status_update_event'):
            return Response(status=200)
        (cc_obj, rsp_obj) = _get_cloud(request.DATA,
            vtype_chk=common_pb2.CLOUD_MESOS, def_cloud='Default-Cloud')
        if rsp_obj:
            return rsp_obj
        req = cc_webhook_marathon_req()
        req.cc_id = cc_obj.uuid
        req.event_type = event_type
        req.timestamp = request.DATA.get('timestamp', '')
        req.task_id = request.DATA.get('taskId', '')
        if req.event_type == 'api_post_event':
            app_defn = request.DATA.get('appDefinition', {})
            if 'id' not in app_defn:
                raise Exception('id not present in appDefinition')
            else:
                req.app_id = app_defn['id']
        elif req.event_type == 'status_update_event':
            req.app_id = request.DATA.get('appId', '')
            if not req.app_id:
                raise Exception('appId null in status_update_event')
        CloudConnectorService_Stub(RpcChannel()).\
            cc_webhook_marathon(RpcController(), req)
        return Response(status=200)

