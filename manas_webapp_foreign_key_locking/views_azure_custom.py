
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
import os
from copy import deepcopy
import requests
from api.models import CloudConnectorUser
from avi.protobuf import common_pb2, ipam_profile_pb2
from avi.rest.views import CreateView
from rest_framework.response import Response
from api.views_cloud_connector_custom import (_mask_keys, _update_ipam_params, _update_cloud_params)
from avi.util.azure_utils import (azure_try_access, azure_get_resource_groups,
            azure_get_virtual_networks, azure_get_subnets, get_resource_group_from_id, 
            azure_get_albs, azure_get_locations, azure_all_resources, get_kwargs_azure, get_rate_card)
from avi.util.views_constants import ERR_RC
from avi.protobuf import common_pb2, ipam_profile_pb2
from api.models import SystemConfiguration

log = logging.getLogger(__name__)

AZURE_DNS_TYPES = [ipam_profile_pb2.IPAMDNS_TYPE_AZURE, ipam_profile_pb2.IPAMDNS_TYPE_AZURE_DNS]

def _get_credentials(params):
    try:
        config = SystemConfiguration.objects.get().protobuf(decrypt=True)
        az_proxy = get_kwargs_azure(config.proxy_configuration)
        if az_proxy and az_proxy['host'] and az_proxy['port']:
            if az_proxy['username'] and az_proxy['password']:
                url_http = 'http://%s:%s@%s:%s' % (az_proxy['username'], az_proxy['password'], az_proxy['host'], az_proxy['port'])
            else:
                url_http = 'http://%s:%s' % (az_proxy['host'], az_proxy['port'])
            return azure_try_access(params, url_http), None
        else:
            return azure_try_access(params), None

    except Exception as e:
        return None, 'Failed to validate Azure credentials: %s'%str(e)

def _params_check(params):
    msg = None
    if (params.get('username') and params.get('application_id')):
        msg = 'Both username and application_id cannot be specified'
    if not params.get('subscription_id'):
        msg = 'Subscription_id not provided'

    return msg

def _update_cloud_credentials(params):
    credentials = CloudConnectorUser.objects.get(uuid=params['cloud_credentials_uuid'])
    cred_pb = credentials.protobuf(decrypt=True)
    if cred_pb.HasField('azure_userpass'):
        params['username'] = cred_pb.azure_userpass.username
        params['tenant_name'] = cred_pb.azure_userpass.tenant_name
        params['password'] = cred_pb.azure_userpass.password
    elif cred_pb.HasField('azure_serviceprincipal'):
        params['application_id'] = cred_pb.azure_serviceprincipal.application_id
        params['authentication_token'] = cred_pb.azure_serviceprincipal.authentication_token
        params['tenant_id'] = cred_pb.azure_serviceprincipal.tenant_id

def _update_params(params):
    cc_obj = _update_cloud_params(params, common_pb2.CLOUD_AZURE)
    if not cc_obj and 'ipamdnsprovider_uuid' in params:
        ipam_pb, params = _update_ipam_params(params)
        if not ipam_pb or ipam_pb.type not in AZURE_DNS_TYPES:
            rsp = {'error': 'Unsupported IPAM type'}
            ret = ERR_RC
            return Response(data=rsp, status=ret)
    if 'cloud_credentials_uuid' in params:
        _update_cloud_credentials(params)

    if not cc_obj and not 'cloud_credentials_uuid' in params:
        # Setting is_azure_msi parameter for new cloud creation if cloud_credentials_uuid is not present
        params['is_azure_msi'] = True

    return None

class AzureVnetsView(CreateView):
    def post(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        params = deepcopy(request.DATA)
        rsp = 'POST invoked with args request %s args %s kwargs %s' % (_mask_keys(params), args, kwargs)
        log.info(rsp)
        msg = None
        ret = 200
        result = _update_params(params)
        if result:
            return result
        params.update(request.DATA)
        msg = _params_check(params)
        if not msg:
            creds, msg = _get_credentials(params)
        if msg:
            rsp = {'error': msg}
            ret = ERR_RC
        else:
            ret, rsp = azure_get_virtual_networks(creds, params['subscription_id'], location=params.get('location'))
        log.debug(rsp) if ret == 200 else log.error(rsp)
        return Response(data=rsp, status=ret)


class AzureSubnetsView(CreateView):
    def post(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        params = deepcopy(request.DATA)
        rsp = 'POST invoked with args request %s args %s kwargs %s' % (_mask_keys(params), args, kwargs)
        log.info(rsp)
        msg = None
        ret = 200
        result = _update_params(params)
        if result:
            return result
        params.update(request.DATA)
        msg = _params_check(params)
        if not msg:
            credentials, msg = _get_credentials(params)
        if msg:
            rsp = {'error': msg}
            ret = ERR_RC
        else:
            ret, rsp = azure_get_subnets(credentials, params['subscription_id'], params['vnet_id'])
        log.debug(rsp) if ret == 200 else log.error(rsp)
        return Response(data=rsp, status=ret)

class AzureResourceGroupsView(CreateView):
    def post(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        params = deepcopy(request.DATA)
        rsp = 'POST invoked with args request %s args %s kwargs %s' % (_mask_keys(params), args, kwargs)
        log.info(rsp)
        msg = None
        ret = 200
        result = _update_params(params)
        if result:
            return result
        params.update(request.DATA)
        msg = _params_check(params)
        if not msg:
            credentials, msg = _get_credentials(params)
        if msg:
            rsp = {'error': msg}
            ret = ERR_RC
        else:
            ret, rsp = azure_get_resource_groups(credentials, params['subscription_id'], location=params.get('location'))
        log.debug(rsp) if ret == 200 else log.error(rsp)
        return Response(data=rsp, status=ret)

class AzureAlbsView(CreateView):
    def post(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        params = deepcopy(request.DATA)
        rsp = 'POST invoked with args request %s args %s kwargs %s' % (_mask_keys(params), args, kwargs)
        log.info(rsp)
        msg = None
        ret = 200
        result = _update_params(params)
        if result:
            return result
        params.update(request.DATA)
        if not msg:
            credentials, msg = _get_credentials(params)
        if msg:
            rsp = {'error': msg}
            ret = ERR_RC
        else:
            ret, rsp = azure_get_albs(credentials, params['subscription_id'], params['resource_group'])
        log.debug(rsp) if ret == 200 else log.error(rsp)
        return Response(data=rsp, status=ret)

class AzureLocationsView(CreateView):
    def post(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        params = deepcopy(request.DATA)
        rsp = 'POST invoked with args request %s args %s kwargs %s' % (_mask_keys(params), args, kwargs)
        log.info(rsp)
        msg = None
        ret = 200
        result = _update_params(params)
        if result:
            return result
        params.update(request.DATA)
        msg = _params_check(params)
        if not msg:
            credentials, msg = _get_credentials(params)
        if msg:
            rsp = {'error': msg}
            ret = ERR_RC
        else:
            ret, rsp = azure_get_locations(credentials, params['subscription_id'])
        log.debug(rsp) if ret == 200 else log.error(rsp)
        return Response(data=rsp, status=ret)

class AzureAllResourcesView(CreateView):
    
    def _handle(self, request, args, kwargs, params):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        msg = None
        result = _update_params(params)
        if result:
            return result
        if not msg:
            credentials, msg = _get_credentials(params)
        if msg:
            rsp = {'error': msg}
            ret = ERR_RC
        else:
            ret, rsp = azure_all_resources(credentials, params['subscription_id'], params['resource_group'])
        rsp = Response(data=rsp, status=ret)
        return rsp
        
    def post(self, request, *args, **kwargs):
        params = deepcopy(request.DATA)
        rsp = 'POST invoked with args request %s args %s kwargs %s' % (_mask_keys(params), args, kwargs)
        if not (params.get('uuid') or params.get('ipamdnsprovider_uuid')):
            raise Exception('Only Cloud \'uuid\' or ipamdnsprovider_uuid based get supported')
        rsp = self._handle(request, args, kwargs, params)
        return rsp
    
    def get(self, request, *args, **kwargs):
        params = deepcopy(request.QUERY_PARAMS)
        rsp = 'GET invoked with args request %s args %s kwargs %s' % (_mask_keys(params), args, kwargs)
        if not (params.get('uuid') or params.get('ipamdnsprovider_uuid')):
            raise Exception('Only Cloud \'uuid\' or ipamdnsprovider_uuid based get supported')
        rsp = self._handle(request, args, kwargs, params)
        return rsp


class AzureRateCard(CreateView):
    def _handle(self, request, args, kwargs, params):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        msg = None
        result = _update_params(params)
        if result:
            return result
        ret, rsp = get_rate_card()
        rsp = Response(data=rsp, status=ret)
        return rsp

    def get(self, request, *args, **kwargs):
        params = deepcopy(request.QUERY_PARAMS)
        rsp = 'GET invoked with args request %s args %s kwargs %s' % (_mask_keys(params), args, kwargs)
        rsp = self._handle(request, args, kwargs, params)
        return rsp
