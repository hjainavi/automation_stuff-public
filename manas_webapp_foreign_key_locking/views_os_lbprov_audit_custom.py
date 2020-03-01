
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
OpenStack LBaaS provider audit Views
=====================
"""

import logging

from rest_framework.response import Response
from avi.rest.views import (RetrieveView, CreateView)
from google.protobuf.service import RpcController
from avi.infrastructure.rpc_channel import RpcChannel
from avi.protobuf import syserr_pb2
from avi.util.protobuf import protobuf2dict
from avi.protobuf.cloud_connector_rpc_pb2 import (
    CloudConnectorService_Stub, cc_lbprov_audit_req)
from avi.protobuf import common_pb2
from api.views_cloud_connector_custom import _get_cloud
from api.views_cloud_connector_custom import _mask_keys
from avi.util.views_constants import ERR_RC, SVR_RC

log = logging.getLogger(__name__)

class OsLbProvAuditView(CreateView, RetrieveView):

    def post(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        rsp = 'POST invoked with args request %s args %s kwargs %s' % (_mask_keys(request.DATA), args, kwargs)
        log.info(rsp)
        (cc_obj, rsp_obj) = _get_cloud(request.DATA, vtype_chk=common_pb2.CLOUD_OPENSTACK)
        if rsp_obj:
            return rsp_obj
        req = cc_lbprov_audit_req()
        req.cc_id       = cc_obj.uuid
        req.form.user   = request.DATA.get('user', '')
        req.form.tenant = request.DATA.get('tenant', '')
        req.form.passwd = request.DATA.get('passwd', '')
        req.form.token  = request.DATA.get('token', '')
        provs           = request.DATA.get('prov_name', list())
        req.form.prov_name.extend(provs)
        rpc_rsp = CloudConnectorService_Stub(RpcChannel()).\
              cc_lbprov_audit(RpcController(), req)
        if rpc_rsp:
            rsp = protobuf2dict(rpc_rsp)
            if rpc_rsp.ret_status == syserr_pb2.SYSERR_SUCCESS:
                ret = 200
            else:
                log.error('rsp err %d status %s for cc_lbprov_audit' %
                          (rpc_rsp.ret_status, rpc_rsp.ret_string))
                rsp = {'result': rpc_rsp.ret_string}
                ret = ERR_RC
        else:
            log.error('null rsp for cc_lbprov_audit')
            rsp = {'result': 'failed'}
            ret = SVR_RC
        return Response(data=rsp, status=ret)

    def get(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        rsp = 'GET invoked with args request %s args %s kwargs %s' % (request.QUERY_PARAMS, args, kwargs)
        log.info(rsp)
        (cc_obj, rsp_obj) = _get_cloud(request.QUERY_PARAMS, vtype_chk=common_pb2.CLOUD_OPENSTACK)
        if rsp_obj:
            return rsp_obj
        req = cc_lbprov_audit_req()
        req.cc_id       = cc_obj.uuid
        req.form.user   = request.QUERY_PARAMS.get('user', '')
        req.form.tenant = request.QUERY_PARAMS.get('tenant', '')
        rpc_rsp = CloudConnectorService_Stub(RpcChannel()).\
              cc_lbprov_audit_status(RpcController(), req)
        if rpc_rsp:
            rsp = protobuf2dict(rpc_rsp)
            if rpc_rsp.ret_status == syserr_pb2.SYSERR_SUCCESS:
                ret = 200
            else:
                log.error('rsp err %d status %s for cc_lbprov_audit_status' %
                          (rpc_rsp.ret_status, rpc_rsp.ret_string))
                rsp = {'result': rpc_rsp.ret_string}
                ret = ERR_RC
        else:
            log.error('null rsp for cc_lbprov_audit_status')
            rsp = {'result': 'failed'}
            ret = SVR_RC
        return Response(data=rsp, status=ret)
