
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

from api.models import CloudConnectorUser
from avi.protobuf import common_pb2
from avi.rest.views import ListView
from avi.util import gcp_utils
from avi.util.views_constants import ERR_RC
from rest_framework.response import Response
from api.views_cloud_connector_custom import _update_cloud_params
from copy import deepcopy
import json


log = logging.getLogger(__name__)


def _validate_params(query_params, required_params):
    required_params.extend(['cloud_credentials_uuid', 'project'])
    missing_params = []
    for required_param in required_params:
        if required_param not in query_params:
            missing_params.append(required_param)

    if missing_params:
        rsp = {'error': "'%s' missing in query parameters" % ", ".join(missing_params)}
        return Response(data=rsp, status=ERR_RC)


def _get_sa_key_file_json(cloud_credentials_uuid):
    # If there is no cloudconnectoruser then use the default service account
    if not cloud_credentials_uuid:
        return {}
    cred = CloudConnectorUser.objects.get(uuid=cloud_credentials_uuid)
    if not cred:
        raise Exception("CloudConnectorUser %s not found" % cloud_credentials_uuid)
    cred_pb = cred.protobuf(decrypt=True)
    if not cred_pb.HasField('gcp_credentials'):
        raise Exception("CloudConnectorUser %s not found" % cloud_credentials_uuid)
    return json.loads(cred_pb.gcp_credentials.service_account_keyfile_data)


def get_credentials(params):
    return _get_sa_key_file_json(params.get('cloud_credentials_uuid'))


class RegionsView(ListView):
    def get(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        params = deepcopy(request.QUERY_PARAMS)
        _update_cloud_params(params, common_pb2.CLOUD_GCP)

        rsp = _validate_params(params, [])
        if rsp:
            return rsp

        try:
            key_file_json = get_credentials(params)
        except Exception as e:
            rsp = {'error': e.message}
            return Response(data=rsp, status=ERR_RC)

        ret, rsp = gcp_utils.get_regions(log, key_file_json, params['project'])
        return Response(data=rsp, status=ret)


class ZonesView(ListView):
    def get(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        params = deepcopy(request.QUERY_PARAMS)
        _update_cloud_params(params, common_pb2.CLOUD_GCP)

        required_params = ['region']
        rsp = _validate_params(params, required_params)
        if rsp:
            return rsp

        try:
            sa_key_file_json = get_credentials(params)
        except Exception as e:
            rsp = {'error': e.message}
            return Response(data=rsp, status=ERR_RC)

        ret, rsp = gcp_utils.get_zones(log, sa_key_file_json, params['project'],
                                           params['region'])
        return Response(data=rsp, status=ret)


class NetworksView(ListView):
    def get(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        params = deepcopy(request.QUERY_PARAMS)
        _update_cloud_params(params, common_pb2.CLOUD_GCP)

        rsp = _validate_params(params, [])
        if rsp:
            return rsp

        try:
            key_file_json = get_credentials(params)
        except Exception as e:
            rsp = {'error': e.message}
            return Response(data=rsp, status=ERR_RC)

        ret, rsp = gcp_utils.get_networks(log, key_file_json, params['project'])
        return Response(data=rsp, status=ret)


class SubnetsView(ListView):
    def get(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        params = deepcopy(request.QUERY_PARAMS)
        _update_cloud_params(params, common_pb2.CLOUD_GCP)

        required_params = ['region', 'network']
        rsp = _validate_params(params, required_params)
        if rsp:
            return rsp

        try:
            key_file_json = get_credentials(params)
        except Exception as e:
            rsp = {'error': e.message}
            return Response(data=rsp, status=ERR_RC)
        ret, rsp = gcp_utils.get_subnets(log, key_file_json, params['project'],
                                         params['region'], params['network'])
        return Response(data=rsp, status=ret)
