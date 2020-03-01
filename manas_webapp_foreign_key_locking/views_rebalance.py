
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

import logging

from google.protobuf.service import RpcController
from rest_framework.response import Response

from avi.rest.error_list import ServerException
from avi.rest.views import (
    CommonView, SingleObjectView
)
from avi.protobuf.res_monitor_rpc_pb2 import ResMonService_Stub
from avi.protobuf.rebalance_pb2 import RebalanceParams
from avi.infrastructure.rpc_channel import RpcChannel
from avi.rest.url_utils import slug_from_uri

LOG = logging.getLogger(__name__)
HTTP_RPC_TIMEOUT = 3.0

class RebalanceView (CommonView, SingleObjectView):
    def post(self, request, *args, **kwargs):
        rsp = {}
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)

        LOG.info('Start Rebalance.')
        rsp = {'status': 'rebalance in progress...'}
        req = RebalanceParams()
        req.se_group_uuid = slug_from_uri(request.DATA.get('se_group_ref', ''))
        req.one_time = request.DATA.get('one_time', False)
        try:
            # send rpc to Res Monitor
            stub = ResMonService_Stub(RpcChannel())
            stub.SeRebalanceRpc(RpcController(), req)
        except Exception as err:
            msg = 'Rebalance Error:' + str(err)
            raise ServerException(msg)
        return Response(data=rsp, status=200)
