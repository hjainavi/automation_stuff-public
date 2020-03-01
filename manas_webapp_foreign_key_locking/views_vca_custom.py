
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
from rest_framework.response import Response
from avi.rest.views import CreateView
from avi.util.vca_utils import (
    vca_get_vpc, vca_get_vpc_instances, vca_get_vpc_vdcs, vca_get_vpc_subnets
)
from api.views_cloud_connector_custom import _mask_keys, _update_cloud_params
from avi.util.views_constants import ERR_RC
from avi.protobuf import common_pb2

log = logging.getLogger(__name__)

VCA_CRED_1 = ['username', 'password']
VCA_CRED_2 = ['instance', 'username', 'password']
VCA_CRED_3 = ['instance', 'username', 'password', 'vdc']
VTYPE      = common_pb2.CLOUD_VCA

# TODO: Functions to be implemented:
#       -- vca_get_vpc_subnets
#       -- vca_get_vpc_instances
#       -- vca_get_vpc
#       -- vca_get_vpc_vdcs
#       Should be implemented in avi.util.vca_utils


class VcaVerifyCredView(CreateView):
    def post(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        rsp = 'POST invoked with args request %s args %s kwargs %s' % \
            (_mask_keys(request.DATA), args, kwargs)
        log.info(rsp)
        msg = None
        ret = 200
        params = request.DATA
        _update_cloud_params(params, VTYPE)
        for rfield in VCA_CRED_1:
            if not params or rfield not in params:
                msg = "All fields are required: %s" % VCA_CRED_1
                break
        if msg:
            rsp = {'error': msg}
            ret = ERR_RC
        else:
            ret, rsp = vca_get_vpc(params['username'],
                                   params['password'])
        log.debug(rsp) if ret == 200 else log.error(rsp)
        return Response(data=rsp, status=ret)


class VcaInstancesView(CreateView):
    def post(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        rsp = 'POST invoked with args request %s args %s kwargs %s' % \
            (_mask_keys(request.DATA), args, kwargs)
        log.info(rsp)
        msg = None
        ret = 200
        params = request.DATA
        _update_cloud_params(params, VTYPE)
        for rfield in VCA_CRED_1:
            if not params or rfield not in params:
                msg = "All fields are required: %s" % VCA_CRED_1
                break
        if msg:
            rsp = {'result': msg}
            ret = ERR_RC
        else:
            ret, rsp = vca_get_vpc_instances(params['username'],
                                             params['password'])
        log.debug(rsp) if ret == 200 else log.error(rsp)
        return Response(data=rsp, status=ret)


class VcaVdcsView(CreateView):
    def post(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        rsp = 'POST invoked with args request %s args %s kwargs %s' % \
            (_mask_keys(request.DATA), args, kwargs)
        log.info(rsp)
        msg = None
        ret = 200
        params = request.DATA
        _update_cloud_params(params, VTYPE)
        for rfield in VCA_CRED_2:
            if not params or rfield not in params:
                msg = "All fields are required: %s" % VCA_CRED_2
                break
        if msg:
            rsp = {'result': msg}
            ret = ERR_RC
        else:
            ret, rsp = vca_get_vpc_vdcs(params['instance'],
                                        params['username'],
                                        params['password'])
        log.debug(rsp) if ret == 200 else log.error(rsp)
        return Response(data=rsp, status=ret)


class VcaSubnetsView(CreateView):
    def post(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        rsp = 'POST invoked with args request %s args %s kwargs %s' % \
            (_mask_keys(request.DATA), args, kwargs)
        log.info(rsp)
        msg = None
        ret = 200
        params = request.DATA
        _update_cloud_params(params, VTYPE)
        for rfield in VCA_CRED_3:
            if not params or rfield not in params:
                msg = "All fields are required: %s" % VCA_CRED_3
                break
        if msg:
            rsp = {'result': msg}
            ret = ERR_RC
        else:
            ret, rsp = vca_get_vpc_subnets(params['instance'],
                                           params['username'],
                                           params['password'],
                                           params['vdc'])
        log.debug(rsp) if ret == 200 else log.error(rsp)
        return Response(data=rsp, status=ret)
