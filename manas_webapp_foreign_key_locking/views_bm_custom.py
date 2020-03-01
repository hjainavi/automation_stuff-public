
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

from avi.rest.view_utils import process_view_request
from avi.rest.views import RetrieveView, CreateView
from api.views_cloud_connector_custom import _mask_keys, _get_cloud
from avi.protobuf import common_pb2
from avi.protobuf.cloud_connector_rpc_pb2 import (cc_internals_req,
    CloudConnectorService_Stub)
from avi.protobuf import syserr_pb2
from avi.infrastructure.rpc_channel import RpcChannel
from avi.util.protobuf import protobuf2dict
from avi.util.views_constants import ERR_RC, SVR_RC
from avi.util.cluster_info import get_controller_version

log = logging.getLogger(__name__)
VTYPE = common_pb2.CLOUD_LINUXSERVER

class BmVerifyCredView(CreateView):
    def post(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        rsp = 'POST invoked with args request %s args %s kwargs %s' % (_mask_keys(request.DATA), args, kwargs)
        log.info(rsp)
        ret = 200
        return Response(data=rsp, status=ret)

class BmHostsView(RetrieveView):
    def get(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)

        rsp  = 'GET invoked with args request %s args %s kwargs %s' % (request.QUERY_PARAMS, args, kwargs)
        log.info(rsp)
        (cc_obj, rsp_obj) = _get_cloud(kwargs, required=False, vtype_chk=VTYPE)
        if rsp_obj:
            return rsp_obj
        req = cc_internals_req()
        req.cc_id = cc_obj.uuid
        req.quiet = True
        rpc_rsp = CloudConnectorService_Stub(RpcChannel()).\
              cc_get_internals(RpcController(), req)
        if rpc_rsp:
            if rpc_rsp.ret_status == syserr_pb2.SYSERR_SUCCESS:
                ret = 200
                rsp = protobuf2dict(rpc_rsp.agents[0].linuxserver)
                for i in rsp.keys():
                    if i not in ['hosts', 'uninited_hosts', 'inited_hosts']:
                        del rsp[i]
                for i in list(rsp.get('hosts', [])):
                    if i['state'] == 'CC_HOST_STOPPED':
                        rsp['hosts'].remove(i)
                        continue
                    i['host_state']  = i['state']
                    i['host_reason'] = i['reason']
                    del i['state']
                    del i['reason']
                    try:
                        api = '/api/tenant/'+cc_obj.tenant_uuid+'/serviceengine/se-'+i['host']+'-avitag-1/runtime'
                        custom_view_kwargs = {'version': get_controller_version()}
                        resp = process_view_request(api, 'GET', None, request.user, custom_view_kwargs=custom_view_kwargs)
                        if resp.status_code >= 300:
                            log.error('%s Bad response status %d: %s' % (api, resp.status_code, resp.data))
                        else:
                            i['se_state'] = resp.data['oper_status']['state']
                            i['se_reason'] = resp.data['oper_status']['reason']
                    except Exception as e:
                        log.error('Fail to get serviceengine API %s, error %s', api, e)
                        pass
            else:
                log.error('rsp err %d status %s for cc_get_internals',
                          rpc_rsp.ret_status, rpc_rsp.ret_string)
                rsp = {'result': rpc_rsp.ret_string}
                ret = ERR_RC
        else:
            log.error('null rsp for cc_get_internals')
            rsp = {'result': 'failed'}
            ret = SVR_RC

        return Response(data=rsp, status=ret)

