
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
Webhook Views
=====================
"""

import json
import logging
import uuid

from google.protobuf.service import RpcController
from rest_framework.response import Response

from api.views_cloud_connector_custom import _get_cloud
from avi.infrastructure.rpc_channel import RpcChannel
from avi.protobuf import common_pb2, syserr_pb2
from avi.protobuf.cloud_connector_rpc_pb2 import (CloudConnectorService_Stub,
                                                  cc_mesos_serviceengine_req)
from avi.protobuf.rpc_common_pb2 import RPCRequest
from avi.protobuf.cloud_connector_message_pb2 import MesosLogin, OShiftK8SLogin
from avi.rest.views import CreateView, DeleteView, UpdateView
from api.views_cloud_connector_custom import _mask_keys
from avi.util.views_constants import ERR_RC, SVR_RC, AUTH_RC
from avi.rest.url_utils import slug_from_uri

log = logging.getLogger(__name__)

class MesosServiceEngine(CreateView, DeleteView, UpdateView):
    def post(self, request, *args, **kwargs):
        (cc_obj, rsp_obj) = _get_cloud(request.DATA,
                                       vtype_chk=common_pb2.CLOUD_MESOS)
        req = cc_mesos_serviceengine_req()
        req.cc_id = cc_obj.uuid
        req.action = 'start'
        req.host = request.DATA.get('host', '')
        if not req.host:
            raise Exception('host is required')
        rsp = CloudConnectorService_Stub(RpcChannel()).\
            cc_mesos_serviceengine(RpcController(), req)
        if rsp.ret_status == syserr_pb2.SYSERR_SUCCESS:
            return Response(status=200)
        else:
            return Response(data=rsp.ret_string, status=SVR_RC)

    def delete(self, request, *args, **kwargs):
        (cc_obj, rsp_obj) = _get_cloud(request.DATA,
                                       vtype_chk=common_pb2.CLOUD_MESOS)
        req = cc_mesos_serviceengine_req()
        req.cc_id = cc_obj.uuid
        req.action = 'cleanup'
        req.host = request.DATA.get('host', '')
        if not req.host:
            raise Exception('host is required')
        rsp = CloudConnectorService_Stub(RpcChannel()).\
            cc_mesos_serviceengine(RpcController(), req)
        if rsp.ret_status == syserr_pb2.SYSERR_SUCCESS:
            return Response(status=200)
        else:
            return Response(data=rsp.ret_string, status=SVR_RC)

    def put(self, request, *args, **kwargs):
        (cc_obj, rsp_obj) = _get_cloud(request.DATA,
                                       vtype_chk=common_pb2.CLOUD_MESOS)
        req = cc_mesos_serviceengine_req()
        req.cc_id = cc_obj.uuid
        req.host = request.DATA.get('host', '')
        if not req.host:
            raise Exception('host is required')
        req.action = request.DATA.get('action', '')
        if not req.action:
            raise Exception('action is required')
        elif req.action not in ['reboot']:
            raise Exception('action is not reboot')
        rsp = CloudConnectorService_Stub(RpcChannel()).\
            cc_mesos_serviceengine(RpcController(), req)
        if rsp.ret_status == syserr_pb2.SYSERR_SUCCESS:
            return Response(status=200)
        else:
            return Response(data=rsp.ret_string, status=SVR_RC)

class MesosVerifyLogin(CreateView):
    def post(self, request, *args, **kwargs):
        if (not request.DATA) or ('mesos_url' not in request.DATA):
            return Response(status=ERR_RC)
        rsp = 'POST invoked with args request %s args %s kwargs %s' % (_mask_keys(request.DATA), args, kwargs)
        log.info(rsp)
        req = MesosLogin()
        req.mesos_url = request.DATA['mesos_url']

        if (request.QUERY_PARAMS
                and 'include_mesos_hosts' in request.QUERY_PARAMS
                and str(request.QUERY_PARAMS['include_mesos_hosts']).lower() != 'false'):
            req.include_mesos_hosts = True

        for marathon_login in request.DATA['marathon_creds']:
            m_login = req.marathon_logins.add()
            m_login.marathon_url = marathon_login['marathon_url']
            if 'marathon_username' in marathon_login:
                m_login.marathon_username = marathon_login['marathon_username']
            if 'marathon_password' in marathon_login:
                m_login.marathon_password = marathon_login['marathon_password']
            if 'use_token_auth' in marathon_login:
                m_login.use_token_auth = marathon_login['use_token_auth']
        rsp = CloudConnectorService_Stub(RpcChannel()).\
            MesosVerifyLogin(RpcController(), req)
        if rsp.rpc_status == syserr_pb2.SYSERR_SUCCESS:
            return Response(data=rsp.error_message, status=200)
        else:
            return Response(data=rsp.error_message, status=AUTH_RC)

class OshiftK8SVerifyLogin(CreateView):
    def post(self, request, *args, **kwargs):
        if not request.DATA:
            return Response(status=ERR_RC)

        rsp = 'POST invoked with args request %s args %s kwargs %s' % (
                _mask_keys(request.DATA), args, kwargs)
        log.info(rsp)
        req = OShiftK8SLogin()
        # Max 5 nodes expected for login verification (of form node1, node2, .. nodeX)
        #  where each nodeT is of the form https://hostOrIP:8443
        nodes_found = False
        for node_url in request.DATA.get('nodes', []):
            if not node_url:
                continue
            nodes_found = True
            req.master_nodes.append(node_url)

        if not nodes_found:
            err_msg = "No valid Openshift/K8S master URLs provided. Pls include " \
                        "the master URLs in the request in the form of: " \
                        "nodes: [https://<master-1>:8443, https://<master-2>:8443, etc.]"
            return Response(data=err_msg, status=ERR_RC)

        ca_cert = request.DATA.get('ca_key_cert_uuid', '')
        if ca_cert:
            req.ca_tls_key_and_certificate_uuid = slug_from_uri(ca_cert)

        client_cert = request.DATA.get('client_key_cert_uuid', '')
        if client_cert:
            req.client_tls_key_and_certificate_uuid = slug_from_uri(client_cert)

        account_token = request.DATA.get('account_token', '')
        if account_token:
            req.service_account_token = account_token

        certs_bool = ca_cert and client_cert
        if not account_token and not certs_bool:
            err_msg = "Not enough credentials provided. Please provide both " \
                        "client and ca certificate UUIDs or the service " \
                        "account token for this Openshift/K8S cluster."
            return Response(data=err_msg, status=ERR_RC)

        rsp = CloudConnectorService_Stub(RpcChannel()).\
                OshiftVerifyLogin(RpcController(), req)
        if rsp.rpc_status == syserr_pb2.SYSERR_SUCCESS:
            return Response(data=json.dumps(json.loads(rsp.error_message)), status=200)
        else:
            return Response(data=json.dumps(json.loads(rsp.error_message)), status=AUTH_RC)
