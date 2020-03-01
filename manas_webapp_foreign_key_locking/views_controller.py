
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

from models import *
from rest_framework.decorators import api_view
from avi.rest.views import CommonView
from avi.rest.callbacks import CallbackException
from avi.protobuf.controller_worker_rpc_pb2 import *
from avi.infrastructure.rpc_channel import RpcChannel
from google.protobuf.service import RpcController
from rest_framework.response import Response

@api_view(['GET'])
def enable_assert(request, *args, **kwargs):
    view = CommonView()
    view.model = None

    # check tenant and user permissions
    view.check_tenant(request, args, kwargs)
    view.check_user(request, args, kwargs)

    # invoke protobuf rpc service
    req = ControllerWorkerFlags()
    req.debugmode = True
    try:
        rsp = ControllerWorkerService_Stub(RpcChannel()).SetFlags(
            RpcController(), req)
    except:
        raise CallbackException("RPC Failed to Controller!")

    rsp = {'status': 'Asserts Enabled'}

    rsp = Response(rsp)

    return rsp


@api_view(['GET'])
def disable_assert(request, *args, **kwargs):
    view = CommonView()
    view.model = None

    # check tenant and user permissions
    view.check_tenant(request, args, kwargs)
    view.check_user(request, args, kwargs)

    # invoke protobuf rpc service
    req = ControllerWorkerFlags()
    req.debugmode = False
    try:
        rsp = ControllerWorkerService_Stub(RpcChannel()).SetFlags(
            RpcController(), req)
    except:
        raise CallbackException("RPC Failed to Controller!")

    rsp = {'status': 'Asserts Disabled'}

    rsp = Response(rsp)

    return rsp
