
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
from avi.util.cloudstack_utils import (cs_verify_creds, cs_get_subnets)
from api.views_cloud_connector_custom import _mask_keys, _update_cloud_params
from api.models import Cloud
from avi.protobuf import common_pb2
from avi.util.views_constants import ERR_RC

log = logging.getLogger(__name__)

CLOUDSTACK_CRED = ['api_url', 'access_key', 'secret_key']
VTYPE           = common_pb2.CLOUD_CLOUDSTACK


class CloudstackVerifyCredView(CreateView):
    def post(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        rsp = 'POST invoked with args request %s args %s kwargs %s' % \
            (_mask_keys(request.DATA), args, kwargs)
        log.info(rsp)
        params = request.DATA
        _update_cloud_params(params, VTYPE)
        if not all(attr in params for attr in CLOUDSTACK_CRED):
            msg = "Requires fields: %s" % CLOUDSTACK_CRED
            return Response(data={'error': msg}, status=ERR_RC)
        ret, rsp = cs_verify_creds(params['api_url'],
                                   params['access_key'],
                                   params['secret_key'])
        log.debug(rsp) if ret == 200 else log.error(rsp)
        return Response(data=rsp, status=ret)


class CloudstackSubnetsView(CreateView):
    def post(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        rsp = 'POST invoked with args request %s args %s kwargs %s' % \
            (_mask_keys(request.DATA), args, kwargs)
        log.info(rsp)
        params = request.DATA
        _update_cloud_params(params, VTYPE)
        if not all(attr in params for attr in CLOUDSTACK_CRED):
            msg = "Requires fields: %s" % CLOUDSTACK_CRED
            return Response(data={'error': msg}, status=ERR_RC)
        ret, rsp = cs_get_subnets(params['api_url'],
                                  params['access_key'],
                                  params['secret_key'])
        log.debug(rsp) if ret == 200 else log.error(rsp)
        return Response(data=rsp, status=ret)
