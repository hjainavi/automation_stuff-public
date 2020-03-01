
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

from datetime import datetime
from iptools import IpRange
import random
from copy import deepcopy
from string import ascii_lowercase

import api.models as models
from rest_framework.response import Response
from rest_framework import status
from avi.util.protobuf import protobuf2dict
from avi.rest.pb2model import protobuf2model
from avi.rest.json_db_utils import transform_json_refs_to_uuids
from avi.protobuf_json.protobuf_json import json2pb
from avi.protobuf.network_policy_pb2 import (NetworkSecurityPolicy as
                                             NetworkSecurityPolicyProto,
                                             NetworkSecurityPolicyDos as
                                             NetworkSecurityPolicyDosProto,
                                             NetworkSecurityPolicyDosUnblock as
                                             NetworkSecurityPolicyDosUnblockProto,
                                             NetworkSecurityPolicyDosInfo as
                                             NetworkSecurityPolicyDosInfoProto)
from avi.rest.views import (CreateView, UpdateView, RetrieveView)
from avi.rest.db_cache import DbCache
from avi.protobuf.vs_rpc_pb2 import VirtualServiceService_Stub
from avi.infrastructure.db_transaction import db_transaction
from google.protobuf.service import RpcController
from avi.infrastructure.rpc_channel import RpcChannel
import avi.rest.callbacks as callbacks
from avi.util.job_db import NspJobDB

import logging
log = logging.getLogger(__name__)

AVI_NSP_NAME_LEN = 6
AVI_NSP_NAME_PREFIX = "AviNetworkSecurityPolicy-"
AVI_DOS_RULE_PREFIX = "AviDosRule_"
METHOD_NOT_ALLOWED = "Method not allowed!"

class NetworkSecurityPolicyDosView(CreateView, UpdateView, RetrieveView,):
    model = models.NetworkSecurityPolicy
    serializer_class = models.NetworkSecurityPolicySerializer

    rpc_data = {
        'put': {
            'class_name': 'NetworkSecurityPolicy',
            'method_name': 'Update',
            'field_name': 'network_security_policy',
            'service_name': 'NetworkSecurityPolicyService_Stub'
        },

        'post': {
            'class_name': 'NetworkSecurityPolicy',
            'method_name': 'Create',
            'field_name': 'network_security_policy',
            'service_name': 'NetworkSecurityPolicyService_Stub'
        },
    }

    @db_transaction
    def create_block_policy(self, vs_uuid, block_pb, method):
        """
        Creates a Network Security Policy object with the input
        as NetworkSecurityPolicyDos object
        """
        vs_pb = models.VirtualService.objects.select_for_update().get(uuid=vs_uuid).protobuf()

        ns_pb = NetworkSecurityPolicyProto()
        ns_pb.uuid = ""
        ns_pb.name = AVI_NSP_NAME_PREFIX + get_nsp_name_str()
        rindex = 0
        for rule in block_pb.rules:
            r = ns_pb.rules.add()
            r.enable = rule.enable
            r.match.CopyFrom(rule.match)
            r.action = rule.action
            r.log = rule.log
            r.age = rule.age
            if rule.HasField('rl_param'):
                r.rl_param.CopyFrom(rule.rl_param)
            r.name = AVI_DOS_RULE_PREFIX + datetime.utcnow().isoformat()
            r.index = rindex
            rindex += 1

        try:
            policy_obj, is_created = protobuf2model(ns_pb, None, False)
            self.save_callback(policy_obj, method)
            self.run_callback()
            vs_pb.network_security_policy_uuid = policy_obj.uuid
            protobuf2model(vs_pb, None, True)
            req = callbacks.new_rpc_req(vs_pb, 'VirtualService', 'virtual_service', pb2_module='avi.protobuf.vs_pb2')
            VirtualServiceService_Stub(RpcChannel()).Update(RpcController(), req)
        except Exception as e:
            log.error("POST: %s block failed with %s" % (vs_uuid, e))
        return policy_obj, vs_pb

    @db_transaction
    def update_block_policy(self, policy_uuid, block_pb, method, context):
        """
        Updates Network Security Policy object with the input
        as NetworkSecurityPolicyDos object
        """
        # Get a lock on the NetworkSecurityPolicy object
        old_obj = self.model.objects.select_for_update().get(uuid=policy_uuid)
        old_obj_data = self.serializer_class(old_obj, context=context).data
        ns_pb = old_obj.protobuf()

        old_pb = deepcopy(ns_pb)
        num_erules = len(block_pb.rules)
        rindex = 0
        # Re-arrange existing rule indices, but preserve order
        for rule in ns_pb.rules:
            rule.index += num_erules

        for rule in block_pb.rules:
            r = ns_pb.rules.add()
            r.enable = rule.enable
            r.match.CopyFrom(rule.match)
            r.action = rule.action
            r.log = rule.log
            r.age = rule.age
            if rule.HasField('rl_param'):
                r.rl_param.CopyFrom(rule.rl_param)
            r.name = AVI_DOS_RULE_PREFIX + datetime.utcnow().isoformat()
            r.index = rindex
            rindex += 1

        try:
            policy_obj, is_created = protobuf2model(ns_pb, None, False)
            self.save_callback(policy_obj, method, old_pb)
            self.run_callback()
        except Exception as e:
            log.error("Policy update for %s failed with %s" % (policy_uuid, e))
        return policy_obj, old_obj_data

    @db_transaction
    def unblock_policy(self, policy_uuid, unblock_pb, method, context):
        """
        Unblocks a list of IPs (request) in the Virtualservice's network security
        policy object
        """
        old_obj = self.model.objects.select_for_update().get(uuid=policy_uuid)
        old_obj_data = self.serializer_class(old_obj, context=context).data
        ns_pb = old_obj.protobuf()
        old_pb = deepcopy(ns_pb)

        # TODO: Searching only for individual IPs or Groups. Enhance this if
        #        other search criteria needed.
        for ip in unblock_pb.ips.addrs:
            for rule in list(ns_pb.rules):
                if not rule.match.HasField('client_ip'):
                    continue
                for ipr in list(rule.match.client_ip.addrs):
                    if ip.addr != ipr.addr:
                        continue
                    rule.match.client_ip.addrs.remove(ipr)
                if rule_empty(rule.match.client_ip):
                    ns_pb.rules.remove(rule)

        try:
            policy_obj, is_created = protobuf2model(ns_pb, None, False)
        except Exception as e:
            log.error("PUT: failed with %s" % e)
        self.save_callback(policy_obj, method, old_pb)
        self.run_callback()
        return policy_obj, old_obj_data

    def do_block_transaction(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)

        #method = request.method.lower()
        context = {'request': request}
        block_pb = NetworkSecurityPolicyDosProto()
        transform_json_refs_to_uuids(request.DATA, preserve_uri=True)
        json2pb(block_pb, request.DATA, replace=True)
        vs_uuids = models.VirtualService.objects.filter(name=block_pb.vs_name,
                                                tenant_ref=self.tenant).values('uuid')
        vs_uuid = vs_uuids[0]['uuid'] if vs_uuids else ''
        if not vs_uuid and block_pb.HasField('vs_uuid'):
            vs_uuid = block_pb.vs_uuid

        policies = DbCache().get_children('VirtualService', uuid=vs_uuid,
                                model_filter=['NetworkSecurityPolicy'])
        old_obj = None
        method = ''
        if not policies:
            obj, vs_pb = self.create_block_policy(vs_uuid, block_pb, 'post')
            code = status.HTTP_201_CREATED
            method = 'POST'
        else:
            obj, old_obj = self.update_block_policy(policies[0].uuid,
                                                    block_pb, 'put',
                                                    context)
            code = status.HTTP_200_OK

        obj_data = self.serializer_class(obj, context=context).data
        self.generate_config_log(request, True, None, obj_data,
                                 old_obj_data=old_obj, override_method=method)
        return Response(obj_data, status=code)

    @db_transaction
    def do_unblock_transaction(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)

        #method = request.method.lower()
        context = {'request': request}
        unblock_pb = NetworkSecurityPolicyDosUnblockProto()
        transform_json_refs_to_uuids(request.DATA, preserve_uri=True)
        json2pb(unblock_pb, request.DATA, replace=True)
        vs_uuids = models.VirtualService.objects.filter(name=unblock_pb.vs_name,
                                                tenant_ref=self.tenant).values('uuid')
        vs_uuid = vs_uuids[0]['uuid'] if vs_uuids else ''
        if not vs_uuid and unblock_pb.HasField('vs_uuid'):
            vs_uuid = unblock_pb.vs_uuid

        policies = DbCache().get_children('VirtualService', uuid=vs_uuid,
                                model_filter=['NetworkSecurityPolicy'])
        if not policies:
            resp_data = "No Network Security Policy found for %s." % vs_uuid
            return Response(resp_data, status=status.HTTP_200_OK)

        obj, old_obj = self.unblock_policy(policies[0].uuid,
                                           unblock_pb, 'put', context)

        obj_data = self.serializer_class(obj, context=context).data
        self.generate_config_log(request, True, None, obj_data,
                                 old_obj_data=old_obj)
        ns_pb_tmp = self.model.objects.get(uuid=policies[0].uuid).protobuf()
        ns_pb = get_custom_nsp(ns_pb_tmp)
        return Response(protobuf2dict(ns_pb), status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        action_type = request.QUERY_PARAMS.get('action', None)
        if not action_type:
            log.error("No action specified in this API!")
            return Response("Unsupported API!",
                            status=status.HTTP_400_BAD_REQUEST)

        if 'block' != action_type:
            return Response("Unrecognised action: %s!" % action_type,
                            status=status.HTTP_400_BAD_REQUEST)

        rsp = self.do_block_transaction(request, *args, **kwargs)
        return rsp

    def put(self, request, *args, **kwargs):
        action_type = request.QUERY_PARAMS.get('action', None)
        if not action_type:
            log.error("No action specified in this API!")
            return Response("Unsupported API!",
                            status=status.HTTP_400_BAD_REQUEST)

        if 'block' == action_type:
            rsp = self.do_block_transaction(request, *args, **kwargs)
        elif 'unblock' == action_type:
            rsp = self.do_unblock_transaction(request, *args, **kwargs)
        else:
            rsp = Response("Unrecognised API: %s!" % action_type,
                            status=status.HTTP_400_BAD_REQUEST)
        return rsp

    def patch(self, request, *args, **kwargs):
        action_type = request.QUERY_PARAMS.get('action', None)
        if not action_type:
            log.error("No action specified in this API!")
            return Response("Unsupported API!",
                            status=status.HTTP_400_BAD_REQUEST)

        if 'block' == action_type:
            rsp = self.do_block_transaction(request, *args, **kwargs)
        elif 'unblock' == action_type:
            rsp = self.do_unblock_transaction(request, *args, **kwargs)
        else:
            rsp = Response("Unrecognised API: %s!" % action_type,
                            status=status.HTTP_400_BAD_REQUEST)
        return rsp

    def get(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)

        dos_rsp_pb = NetworkSecurityPolicyDosInfoProto()
        vs_name = request.QUERY_PARAMS.get('name', None)
        vs_uuids = models.VirtualService.objects.filter(name=vs_name,
                                                tenant_ref=self.tenant).values('uuid')
        vs_uuid = vs_uuids[0]['uuid'] if vs_uuids else ''

        nsp_uuid = DbCache().get_children('VirtualService', uuid=vs_uuid,
                            model_filter=['NetworkSecurityPolicy'])
        ip_count = 0
        if nsp_uuid:
            ns_pb_tmp = self.model.objects.get(uuid=nsp_uuid[0].uuid).protobuf()
            ns_pb = get_custom_nsp(ns_pb_tmp)
            for rule in ns_pb.rules:
                if AVI_DOS_RULE_PREFIX not in rule.name:
                    continue
                r = dos_rsp_pb.rules.add()
                r.CopyFrom(rule)
                ip_count += get_ip_count(r.match.client_ip)

        dos_rsp_pb.ip_count = ip_count
        return Response(protobuf2dict(dos_rsp_pb))


def get_custom_nsp(bef_pb):
    """
    Returns the NetworkSecurityPolicy protobuf after updating
    the current age time of all rules
    """
    pb_dict = protobuf2dict(bef_pb)
    NspJobDB().updateGetResponse(pb_dict)
    aft_pb = NetworkSecurityPolicyProto()
    transform_json_refs_to_uuids(pb_dict, preserve_uri=True)
    json2pb(aft_pb, pb_dict, replace=True)
    return aft_pb

def get_nsp_name_str():
    return ''.join(random.choice(ascii_lowercase) for _ in range(AVI_NSP_NAME_LEN))

def rule_empty(rule):
    x = len(rule.addrs) + len(rule.prefixes) + len(rule.ranges) + len(rule.group_uuids)
    return (not x)

def get_ip_count(r, grp_uuid_check=True):
    '''
    Returns total IP count from named addrs,ranges,prefixes fields if they
    exist in the arg protobuf. Supported args: IpAddrMatch, IpAddrGroup
    '''
    # Single IPs
    ip_count = len(r.addrs)
    # Range of IPs
    for rang in r.ranges:
        ip_count += len(IpRange(rang.begin.addr, rang.end.addr))
    # Prefixes
    for pref in r.prefixes:
        ip_count += len(IpRange(pref.ip_addr.addr + '/' + str(pref.mask)))
    # Group of UUIDs
    if grp_uuid_check:
        for grp_uuid in r.group_uuids:
            grp_pb = models.IpAddrMatch.objects.get(uuid=grp_uuid).protobuf()
            ip_count += get_ip_count(grp_pb, grp_uuid_check=False)

    return ip_count
