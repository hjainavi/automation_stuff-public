
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
Licensing Views
=====================
"""

import json
import logging
import os
import netifaces
import requests
import string
import random
from time import sleep

from rest_framework.response import Response

from avi.rest.error_list import ServerException, PermissionError
from avi.rest.file_service_utils import parse_fs_uri
from avi.rest.views import (
    CommonView, SingleObjectView, RetrieveView, UpdateView, PostActionView,
    CreateView, DeleteView
)
from google.protobuf.service import RpcController
from google.protobuf.text_format import MessageToString
from avi.infrastructure.rpc_channel import RpcChannel
from avi.protobuf import syserr_pb2
from avi.protobuf.license_rpc_pb2 import (LicenseService_Stub, LicenseCfgReq,
                                          LicenseToggleEnforcementReq, LicenseReq)
from avi.util.protobuf import protobuf2dict

log = logging.getLogger(__name__)


class Licensing(RetrieveView, UpdateView):
    def get(self, request, *args, **kwargs):
        req = LicenseReq()
        rpc_rsp = LicenseService_Stub(RpcChannel()).\
              ReadLicense(RpcController(), req)
        if rpc_rsp:
            if rpc_rsp.ret_status == syserr_pb2.SYSERR_SUCCESS:
                if rpc_rsp.HasField('controller_license'):
                    rsp = protobuf2dict(rpc_rsp.controller_license)
                else:
                    rsp = {}
                ret = 200
            else:
                log.error('rsp err %d status %s for ReadLicense' %
                          (rpc_rsp.ret_status, rpc_rsp.ret_string))
                rsp = {'result': 'failed %s' % rpc_rsp.ret_string}
                ret = 500
        else:
            log.error('null rsp for ReadLicense')
            rsp = {'result': 'timed out: unable to retrieve license'}
            ret = 503
        return Response(data=rsp, status=ret)

    def put(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        req = LicenseCfgReq()
        req.license_text = request.DATA.get('license_text', '')
        rpc_rsp = LicenseService_Stub(RpcChannel()).\
              ConfigureLicense(RpcController(), req)
        if rpc_rsp:
            if rpc_rsp.ret_status == syserr_pb2.SYSERR_SUCCESS:
                rsp = {'result': rpc_rsp.ret_string}
                ret = 200
            else:
                log.error('rsp err %d status %s for ConfigureLicense' %
                          (rpc_rsp.ret_status, rpc_rsp.ret_string))
                rsp = {'result': 'failed %s' % rpc_rsp.ret_string}
                ret = 500
        else:
            log.error('null rsp for ConfigureLicense')
            rsp = {'result': 'failed'}
            ret = 503
        return Response(data=rsp, status=ret)


class LicensingToggleEnforcement(UpdateView):
    def put(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        if 'enforce' not in request.DATA or \
                'enforce_key' not in request.DATA:
            rsp = {'result': 'failed invalid parameters'}
            return Response(data=rsp, status=422)

        req = LicenseToggleEnforcementReq()
        req.enforce_licensing = request.DATA.get('enforce')
        req.enforce_key = request.DATA.get('enforce_key')
        rpc_rsp = LicenseService_Stub(RpcChannel()). \
            ToggleLicenseEnforcement(RpcController(), req)
        if rpc_rsp:
            if rpc_rsp.ret_status == syserr_pb2.SYSERR_SUCCESS:
                rsp = {'result': rpc_rsp.ret_string}
                ret = 200
            else:
                log.error('rsp err %d status %s for LicensingToggleEnforcement' %
                          (rpc_rsp.ret_status, rpc_rsp.ret_string))
                rsp = {'result': 'failed %s' % rpc_rsp.ret_string}
                ret = 500
        else:
            log.error('null rsp for LicensingToggleEnforcement')
            rsp = {'result': 'failed'}
            ret = 503
        return Response(data=rsp, status=ret)


class LicensingDelete(DeleteView):
    def delete(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        if 'slug' not in kwargs:
            return Response(data={'result': 'invalid license id'}, status=404)
        req = LicenseReq()
        req.name = kwargs['slug']
        req.license_id = kwargs['slug']
        rpc_rsp = LicenseService_Stub(RpcChannel()).\
              DeleteLicense(RpcController(), req)
        if rpc_rsp:
            if rpc_rsp.ret_status == syserr_pb2.SYSERR_SUCCESS:
                return Response(status=200)
            else:
                log.error('rsp err %d status %s for DeleteLicense' %
                          (rpc_rsp.ret_status, rpc_rsp.ret_string))
                rsp = {'result': 'failed %s' % rpc_rsp.ret_string}
                ret = 500
        else:
            log.error('null rsp for DeleteLicense')
            rsp = {'result': 'timed out: unable to delete license'}
            ret = 503
        return Response(data=rsp, status=ret)

