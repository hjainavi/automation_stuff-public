
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
from avi.rest.views import RetrieveView, CreateView
from avi.util.aws_utils import (aws_get_regions, aws_get_vpcs,
                                aws_get_vpc_subnets, aws_verify_r53_creds)
from avi.util.aws_utils import aws_get_assume_roles
from avi.util.aws_utils import aws_get_kms_cmks
from avi.util.aws_iam_utils import get_iam_keys
from api.views_cloud_connector_custom import (_mask_keys, _get_proxy,
    _update_cloud_params, _update_ipam_params)
from api.views_cloud_connector_custom import AWS_IPAMDNS_TYPES
from avi.util.views_constants import ERR_RC
from avi.protobuf import common_pb2

log = logging.getLogger(__name__)

AWS_CRED    = ['username', 'password']
AWS_NW_ARGS = ['region', 'vpc']
VTYPE       = common_pb2.CLOUD_AWS

def _get_credentials(params, pxhost=None, pxport=None, pxuser=None, pxpass=None):
    akey = skey = tkey = exp = msg = None
    region   = params.get('region')
    username = params.get('username')
    password = params.get('password')
    xrole    = params.get('iam_assume_role')
    use_iam  = params.get('use_iam_roles')
    if not use_iam or xrole:
        (akey, skey, tkey, exp, msg) = get_iam_keys(region, username, password, xrole,
            pxhost=pxhost, pxport=pxport, pxuser=pxuser, pxpass=pxpass)
    return (akey, skey, tkey, exp, msg)

def _params_check(params):
    msg = None
    rfields = ['region']
    if not params.get('use_iam_roles'):
        rfields.extend(AWS_CRED)
    for f in rfields:
        if not params or f not in params:
            msg = "All fields are required: %s" % rfields
            break
    return msg

class AwsRegionsView(RetrieveView):
    def get(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        rsp  = 'GET invoked with args request %s args %s kwargs %s' % (request.QUERY_PARAMS, args, kwargs)
        log.info(rsp)
        ret, rsp = aws_get_regions()
        log.debug(rsp) if ret == 200 else log.error(rsp)
        return Response(data=rsp, status=ret)


class AwsVerifyCredView(CreateView):
    def post(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        params = request.DATA
        rsp = 'POST invoked with args request %s args %s kwargs %s' % (_mask_keys(params), args, kwargs)
        log.info(rsp)
        msg = None
        ret = 200
        cc_obj = _update_cloud_params(params, VTYPE)
        if not cc_obj and 'ipamdnsprovider_uuid' in params:
            ipam_pb, params = _update_ipam_params(params)
            if not ipam_pb or ipam_pb.type not in AWS_IPAMDNS_TYPES:
                rsp = {'error': 'Unsupported IPAM/DNS type'}
                ret = ERR_RC
                return Response(data=rsp, status=ret)
        msg = _params_check(params)
        verify_r53 = params.get('verify_r53', '')
        pxhost = None
        pxport = None
        pxuser = None
        pxpass = None
        if not msg:
            (pxhost, pxport, pxuser, pxpass) = _get_proxy(params)
            (akey, skey, tkey, exp, msg) = _get_credentials(params,
                pxhost=pxhost, pxport=pxport, pxuser=pxuser, pxpass=pxpass)
        if msg:
            rsp = {'error': msg}
            ret = ERR_RC
        elif verify_r53.lower() == 'true':
            ret, rsp = aws_verify_r53_creds(params['region'], akey, skey, stoken=tkey,
                pxhost=pxhost, pxport=pxport, pxuser=pxuser, pxpass=pxpass)
        else:
            ret, rsp = aws_get_vpcs(params['region'], akey, skey, stoken=tkey,
                pxhost=pxhost, pxport=pxport, pxuser=pxuser, pxpass=pxpass)
        log.debug(rsp) if ret == 200 else log.error(rsp)
        return Response(data=rsp, status=ret)


class AwsSubnetsView(CreateView):
    def post(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        params = request.DATA
        rsp = 'POST invoked with args request %s args %s kwargs %s' % (_mask_keys(params), args, kwargs)
        log.info(rsp)
        msg = None
        ret = 200
        cc_obj = _update_cloud_params(params, VTYPE)
        if not cc_obj and 'ipamdnsprovider_uuid' in params:
            ipam_pb, params = _update_ipam_params(params)
            if not ipam_pb or ipam_pb.type not in AWS_IPAMDNS_TYPES:
                rsp = {'error': 'Unsupported IPAM/DNS type'}
                ret = ERR_RC
                return Response(data=rsp, status=ret)
        msg = _params_check(params)
        pxhost = None
        pxport = None
        pxuser = None
        pxpass = None
        if not msg:
            (pxhost, pxport, pxuser, pxpass) = _get_proxy(params)
            (akey, skey, tkey, exp, msg) = _get_credentials(params,
                pxhost=pxhost, pxport=pxport, pxuser=pxuser, pxpass=pxpass)
        if msg:
            rsp = {'error': msg}
            ret = ERR_RC
        else:
            ret, rsp = aws_get_vpc_subnets(params['region'], akey, skey, params['vpc'], stoken=tkey,
                        pxhost=pxhost, pxport=pxport, pxuser=pxuser, pxpass=pxpass)
        log.debug(rsp) if ret == 200 else log.error(rsp)
        return Response(data=rsp, status=ret)

class AwsAssumeRolesView(CreateView):
    def post(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        params = request.DATA
        rsp = 'POST invoked with args request %s args %s kwargs %s' % (_mask_keys(params), args, kwargs)
        log.info(rsp)
        msg = None
        ret = 200
        cc_obj = _update_cloud_params(params, VTYPE)
        if not cc_obj and 'ipamdnsprovider_uuid' in params:
            ipam_pb, params = _update_ipam_params(params)
            if not ipam_pb or ipam_pb.type not in AWS_IPAMDNS_TYPES:
                rsp = {'error': 'Unsupported IPAM/DNS type'}
                ret = ERR_RC
                return Response(data=rsp, status=ret)
        msg = _params_check(params)
        if msg:
            rsp = {'error': msg}
            ret = ERR_RC
        else:
            (pxhost, pxport, pxuser, pxpass) = _get_proxy(params)
            ret, rsp = aws_get_assume_roles(params['region'], params.get('username'), params.get('password'),
                pxhost=pxhost, pxport=pxport, pxuser=pxuser, pxpass=pxpass)
        log.debug(rsp) if ret == 200 else log.error(rsp)
        return Response(data=rsp, status=ret)

class AwsKmsCmksView(CreateView):
    def post(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        params = request.DATA
        rsp = 'POST invoked with args request: %s args: %s kwargs: %s' % (_mask_keys(params), args, kwargs)
        log.info(rsp)
        msg = None
        ret = 200
        _update_cloud_params(params, VTYPE)
        msg = _params_check(params)
        pxhost = None
        pxport = None
        pxuser = None
        pxpass = None
        if not msg:
            (pxhost, pxport, pxuser, pxpass) = _get_proxy(params)
            (akey, skey, tkey, exp, msg) = _get_credentials(params,
                pxhost=pxhost, pxport=pxport, pxuser=pxuser, pxpass=pxpass)
        if msg:
            rsp = {'error': msg}
            ret = ERR_RC
        else:
            ret, rsp = aws_get_kms_cmks(params['region'], akey, skey, params['vpc'], stoken=tkey,
                                        pxhost=pxhost, pxport=pxport, pxuser=pxuser, pxpass=pxpass,
                                        service=params.get('service', None))
        log.debug(rsp) if ret == 200 else log.error(rsp)
        return Response(data=rsp, status=ret)
