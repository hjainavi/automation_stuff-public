
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
import os, json
import requests
from rest_framework.response import Response
from avi.rest.views import CreateView
from rest_framework.decorators import api_view
from permission.keystone_auth import cleanup_users_tenants
from avi.util.nuage_utils import vsd_verify_creds
from avi.util.openstack_utils import os_get_tenants
from avi.util.openstack_utils import os_get_tenant_networks
from avi.util.jvnc_utils import vnc_verify_creds
from api.views_cloud_connector_custom import _mask_keys, _update_cloud_params
from avi.util.views_constants import ERR_RC
from django.http.response import HttpResponse
from avi.protobuf import common_pb2
from avi.infrastructure.db_transaction import db_transaction

log = logging.getLogger(__name__)

VSD_ARGS    = ['vsd_host', 'vsd_port', 'vsd_username', 'vsd_password', 'organization']
VNC_ARGS    = ['username', 'password', 'tenant_name', 'contrail_endpoint']
VTYPE       = common_pb2.CLOUD_OPENSTACK

class OsVerifyCredView(CreateView):
    def post(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        rsp = 'POST invoked with args request %s args %s kwargs %s' % (_mask_keys(request.DATA), args, kwargs)
        log.info(rsp)
        msg = None
        ret = 200
        params = request.DATA
        _update_cloud_params(params, VTYPE)
        emsg = "Required fields: keystone_host or auth_url, username," \
               " and password"
        for rfield in ['username', 'password']:
            if not params or rfield not in params:
                msg = emsg
                break
        if (not params or
           ("keystone_host" not in params and "auth_url" not in params)):
            msg = emsg
        if msg:
            rsp = {'error': msg}
            ret = ERR_RC
        else:
            ret, rsp = os_get_tenants(params.get('keystone_host'),
                          params['username'], params['password'],
                          auth_url=params.get('auth_url'))
        log.debug(rsp) if ret == 200 else log.error(rsp)
        return Response(data=rsp, status=ret)


class OsNetworksView(CreateView):
    def post(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        rsp = 'POST invoked with args request %s args %s kwargs %s' % (_mask_keys(request.DATA), args, kwargs)
        log.info(rsp)
        msg = None
        ret = 200
        params = request.DATA
        _update_cloud_params(params, VTYPE)
        emsg = "Required fields: keystone_host or auth_url, username," \
               " password, and tenant_uuid"
        for rfield in ['username', 'password', 'tenant_uuid']:
            if not params or rfield not in params:
                msg = emsg
                break
        if(not params or
           ("keystone_host" not in params and "auth_url" not in params)):
            msg = emsg
        if msg:
            rsp = {'result': msg}
            ret = ERR_RC
        else:
            ret, rsp = os_get_tenant_networks(params.get('keystone_host'),
                        params['username'], params['password'],
                        pd_uuid=params['tenant_uuid'], pd_name=params.get('tenant_name'),
                        region=params.get('region'), auth_url=params.get('auth_url'),
                        use_int_ep=params.get('use_internal_endpoints', False))
        log.debug(rsp) if ret == 200 else log.error(rsp)
        return Response(data=rsp, status=ret)


class NuageVerifyCredView(CreateView):
    def post(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        rsp = 'POST invoked with args request %s args %s kwargs %s' % (_mask_keys(request.DATA), args, kwargs)
        log.info(rsp)
        msg = None
        ret = 200
        params = request.DATA
        _update_cloud_params(params, VTYPE)
        for rfield in VSD_ARGS:
            if not params or rfield not in params:
                msg = "All fields are required: %s" % VSD_ARGS
                break
        if msg:
            rsp = {'error': msg}
            ret = ERR_RC
        else:
            ret, rsp = vsd_verify_creds(params['vsd_host'], params['vsd_port'],
                        params['vsd_username'], params['vsd_password'], params['organization'])
        log.debug(rsp) if ret == 200 else log.error(rsp)
        return Response(data=rsp, status=ret)

class ContrailVerifyCredView(CreateView):
    def post(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        rsp = 'POST invoked with args request %s args %s kwargs %s' % (_mask_keys(request.DATA), args, kwargs)
        log.info(rsp)
        msg = None
        ret = 200
        params = request.DATA
        _update_cloud_params(params, VTYPE)
        for rfield in VNC_ARGS:
            if not params or rfield not in params:
                msg = "All fields are required: %s" % VNC_ARGS
                break
        if msg:
            rsp = {'error': msg}
            ret = ERR_RC
        else:
            ret, rsp = vnc_verify_creds(params.get('keystone_host'), params['username'], params['password'],
                params['tenant_name'], params['contrail_endpoint'], auth_url=params.get('auth_url'))
        log.debug(rsp) if ret == 200 else log.error(rsp)
        return Response(data=rsp, status=ret)

@api_view(['GET'])
@db_transaction
def os_cleanup(request, *args, **kwargs):
    resp = cleanup_users_tenants()
    return Response(data={'resp': resp}, status=200)
