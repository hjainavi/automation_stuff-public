
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
OpenStack LBaaS provider plugin Views
=====================
"""

import logging

#from avi.infrastructure.db_transaction import db_transaction
from rest_framework.response import Response
from avi.rest.request_generator import RequestGenerator

from avi.rest.views import RetrieveView, CreateView
from google.protobuf.service import RpcController
from avi.infrastructure.rpc_channel import RpcChannel
from avi.protobuf import syserr_pb2
from avi.protobuf import common_pb2
from avi.util.protobuf import protobuf2dict
from api.models import V4
#from avi.rest.pb2model import protobuf2model
from avi.rest.pb2dict import protobuf2dict_withrefs
from avi.protobuf.cloud_connector_rpc_pb2 import (
    CloudConnectorService_Stub, cc_lbprov_plugin_req, cc_lbprov_plugin_status_req)
from avi.protobuf import os_lbprov_plugin_pb2
from api.views_cloud_connector_custom import _get_cloud
from api.views_cloud_connector_custom import _mask_keys
from avi.util.views_constants import ERR_RC, SVR_RC

from django.core.urlresolvers import resolve

log = logging.getLogger(__name__)

class OsLbProvPluginView(CreateView, RetrieveView):

    def update_cloud_osconfig(self, request, cc_pb, prov_name, add=True):
        upd     = False
        found   = False
        foundidx= -1
        for idx, pname in enumerate(cc_pb.openstack_configuration.prov_name):
            if pname.lower() == prov_name.lower():
                found = True
                foundidx = idx
                break
        if add and not found:
            cc_pb.openstack_configuration.prov_name.append(prov_name)
            upd = True
        elif not add and found:
            del(cc_pb.openstack_configuration.prov_name[foundidx])
            upd = True
        if upd:
            uri_path = '/api/cloud/%s' % cc_pb.uuid
            v_func, v_args, v_kwargs = resolve(uri_path)
            generator = RequestGenerator()
            obj_data = protobuf2dict_withrefs(cc_pb, request)
            sys_request = generator.create_request(uri_path, 'PUT', obj_data, request.user)
            rsp = v_func(sys_request, *v_args, **v_kwargs)  # pylint: disable=E1102
            if rsp.status_code > 300:
                log.error(rsp.data)
                return rsp
            '''
            # this doesnt update the datastore, the callbacks_custom is not invoked
                -    @db_transaction
                -    def update_cloud_osconfig(self, prov_name):
                -        sys_cfg = SystemConfiguration.objects.select_for_update().get()
                         ...
                         protobuf2model(cc_pb, None, True, run_default_function=False)
            '''
        return None

    def invoke(self, request):
        (cc_obj, rsp_obj) = _get_cloud(request.DATA, vtype_chk=common_pb2.CLOUD_OPENSTACK)
        if rsp_obj:
            return rsp_obj
        req = cc_lbprov_plugin_req()
        req.cc_id = cc_obj.uuid
        req.form.neutron_host_ip.type = V4
        req.form.neutron_host_ip.addr = request.DATA.get('neutron_host_ip', '')
        req.form.prov_host_ip.type = V4
        req.form.prov_host_ip.addr = request.DATA.get('prov_host_ip', '')
        req.form.restart_neutron = request.DATA.get('restart_neutron', True)
        tmp = request.DATA.get('op_type', os_lbprov_plugin_pb2.POT_GET)
        if isinstance(tmp, str) or isinstance(tmp, unicode):
            tmp = os_lbprov_plugin_pb2.OsLbProvOpType.Value(tmp)
        req.form.op_type = tmp
        fields = ['neutron_host_user', 'neutron_host_passwd',
            'prov_name', 'prov_svc_user', 'prov_svc_passwd']
        for f in fields:
            setattr(req.form, f, request.DATA.get(f,''))
        rpc_rsp = CloudConnectorService_Stub(RpcChannel()).\
              cc_lbprov_plugin(RpcController(), req)
        if rpc_rsp:
            rsp = protobuf2dict(rpc_rsp)
            if rpc_rsp.ret_status == syserr_pb2.SYSERR_SUCCESS:
                ret = 200
                sr  = None
                if req.form.op_type in [os_lbprov_plugin_pb2.POT_PUT, os_lbprov_plugin_pb2.POT_POST]:
                    sr = self.update_cloud_osconfig(request, cc_obj, req.form.prov_name, True)
                elif req.form.op_type == os_lbprov_plugin_pb2.POT_DELETE:
                    sr = self.update_cloud_osconfig(request, cc_obj, req.form.prov_name, False)
                if sr:
                    rsp = {'result': sr.data}
                    ret = sr.status_code
            else:
                log.error('rsp err %d status %s for cc_lbprov_plugin' %
                          (rpc_rsp.ret_status, rpc_rsp.ret_string))
                rsp = {'result': rpc_rsp.ret_string}
                ret = ERR_RC
        else:
            log.error('null rsp for cc_lbprov_plugin')
            rsp = {'result': 'failed'}
            ret = SVR_RC
        return Response(data=rsp, status=ret)

    def post(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        rsp = 'POST invoked with args request %s args %s kwargs %s' % (_mask_keys(request.DATA), args, kwargs)
        log.info(rsp)
        obj = self.invoke(request)
        return obj

    def get(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        rsp = 'GET invoked with args request %s args %s kwargs %s' % (request.QUERY_PARAMS, args, kwargs)
        log.info(rsp)
        (cc_obj, rsp_obj) = _get_cloud(request.QUERY_PARAMS, vtype_chk=common_pb2.CLOUD_OPENSTACK)
        if rsp_obj:
            return rsp_obj
        req = cc_lbprov_plugin_status_req()
        req.cc_id = cc_obj.uuid
        rpc_rsp = CloudConnectorService_Stub(RpcChannel()).\
              cc_lbprov_plugin_status(RpcController(), req)
        if rpc_rsp:
            rsp = protobuf2dict(rpc_rsp)
            if rpc_rsp.ret_status == syserr_pb2.SYSERR_SUCCESS:
                ret = 200
            else:
                log.error('rsp err %d status %s for cc_lbprov_plugin_status' %
                          (rpc_rsp.ret_status, rpc_rsp.ret_string))
                rsp = {'result': rpc_rsp.ret_string}
                ret = ERR_RC
        else:
            log.error('null rsp for cc_lbprov_plugin_status')
            rsp = {'result': 'failed'}
            ret = SVR_RC
        return Response(data=rsp, status=ret)
