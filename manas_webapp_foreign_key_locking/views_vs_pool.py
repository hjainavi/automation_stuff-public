
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
import copy
from concurrent.futures import ThreadPoolExecutor
from rest_framework.response import Response
import api.models as models
from avi.rest.error_list import DataException
from django.db.models import Q
from django.utils.crypto import get_random_string
from views_vs import VirtualServiceList, VirtualServiceDetail
from views_pool import PoolDetail
from views_application_policy import HTTPPolicySetDetail
from views_network_policy import NetworkSecurityPolicyDetail
from views_micro_service import MicroServiceDetail
from avi.rest.views import ListView, DetailView, CreateView
from avi.rest.api_perf import api_perf
from avi.rest.url_utils import slug_for_obj_uri, uri_from_slug, slug_from_uri
from avi.rest.pb2model import protobuf2model
from avi.util.vs_vip_utils import merge_vs_vip_protobuf, vsvip_config_fields, merge_vs_vip_json
from avi.infrastructure.save_diff import save_diff
from avi.infrastructure.db_transaction import db_transaction
from avi.util.cloud_util import get_my_admin_cloud
from avi.rest.db_cache import DbCache
from avi.infrastructure.db_base_cache import DbBaseCache
from avi.rest.api_version import api_version
from avi.rest.mixins import get_patch_data
from avi.protobuf.vs_pb2 import VirtualServiceType
from avi.rest.filters import NestedFilter

log = logging.getLogger(__name__)

class VirtualServicePoolCommon(object):
    def __init__(self):
        self.view_list = []
        #list of subviews to run callbacks after commit

    def _vs_type_for_vsvip(self, data):
        VS_TYPES_FOR_VSVIP = {'VS_TYPE_NORMAL', 'VS_TYPE_VH_PARENT'}
        if ((not data.has_key('type')) or
            data['type'] in VS_TYPES_FOR_VSVIP or
            (data['type'] in VirtualServiceType.values() and
                VirtualServiceType.Name(data['type']) in VS_TYPES_FOR_VSVIP)):
            return True
        else:
            return False

    def vsvip_matches_db(self, data, vsvip_ref):
        # Returns True if ips in data match ips in vsvip_ref
        # TODO: optimize this check to do 1 db access
        data_ips = set()
        db_ips = set()
        data_ip6s = set()
        db_ip6s = set()
        cloud = self.cloud if self.cloud else models.Cloud.objects.get(uuid=get_my_admin_cloud().uuid)
        vsvip_uuid = slug_for_obj_uri(vsvip_ref, models.VsVip, tenant=self.tenant, cloud=cloud)
        old_pb = models.VsVip.objects.get(uuid=vsvip_uuid).protobuf()
        if data.get('vip', []):
            for vip in old_pb.vip:
                if vip.ip_address.addr:
                    db_ips.add(vip.ip_address.addr)
                if vip.ip6_address.addr:
                    db_ip6s.add(vip.ip6_address.addr)
            for vip in data['vip']:
                if vip.get('ip_address',{}).get('addr', None):
                    data_ips.add(vip['ip_address']['addr'])
                if vip.get('ip6_address',{}).get('addr', None):
                    data_ip6s.add(vip['ip6_address']['addr'])
            if not (data_ips == db_ips and data_ip6s == db_ip6s):
                return False
        if data.get('east_west_placement', False):
            if data['east_west_placement'] != old_pb.east_west_placement:
                return False
        if data.get('dns_info', []):
            db_fqdns = {dns.fqdn for dns in old_pb.dns_info if dns.fqdn}
            data_fqdns = {dns['fqdn'] for dns in data['dns_info'] if dns['fqdn']}
            if db_fqdns != data_fqdns:
                return False

        return True


class VirtualServicePoolList(VirtualServiceList, VirtualServicePoolCommon):

    def run_subview_callbacks(self):
        for v in self.view_list:
            if v == self:
                super(VirtualServicePoolList, self).run_callback()
            else:
                v.run_callback()

    @api_version
    def do_post_action(self, request, *args, **kwargs):
        self.view_list = []
        vsvip_cb = None

        kwargs['skip-versioning'] = True
        data = request.DATA
        if self._vs_type_for_vsvip(data):
            vsvip_in_data = any(field in data.keys() for field in vsvip_config_fields())
            if vsvip_in_data:
                if 'vsvip_ref' in data:
                    vsvip_uuid = slug_for_obj_uri(data['vsvip_ref'], models.VsVip, tenant=self.tenant, cloud=self.cloud)
                    models.VsVip.objects.select_for_update().get(uuid=vsvip_uuid) # lock to protect must_check
                    if not self.vsvip_matches_db(data, data['vsvip_ref']):
                        raise Exception('VirtualService contents  do not match provided vsvip_ref')
                else:
                    vs_name = data.get('name', '')
                    data['name'] = 'vsvip-' + get_random_string(6)

                    vsvip_cb = VsVipList()
                    vsvip_cb.initial(request, *args, **kwargs)
                    vsvip_cb.request = request
                    vsvip_cb.args = args
                    vsvip_cb.kwargs = kwargs
                    vip_rsp = vsvip_cb.do_post_list(request, *args, **kwargs)
                    self.view_list.append(vsvip_cb)

                    data['name'] = vs_name
                    data['vsvip_ref'] = vip_rsp.data['url']

        try:
            rsp = super(VirtualServicePoolList, self).do_post_action(request, *args, **kwargs)
            self.view_list.append(self)
        except:
            #rollback db_cache if VS create fails
            if vsvip_cb:
                vsvip_uuid = vip_rsp.data['uuid']
                vsvip_db_obj = models.VsVip.objects.get(uuid=vsvip_uuid)
                vsvip_cb.db_cache_delete(vsvip_db_obj)
                vsvip_cb.custom_rollback(vsvip_cb.object.protobuf())
            raise

        if rsp.data.has_key('vsvip_ref'):
            merge_vs_vip_json(rsp.data, request=request)
        return rsp

    def run_callback(self):
        self.run_subview_callbacks()

    @api_version
    def do_get_action(self, request, *args, **kwargs):
        kwargs['skip-versioning'] = True
        rsp = super(VirtualServicePoolList, self).do_get_action(request, *args, **kwargs)
        for vs_json_obj in rsp.data['results']:
            if vs_json_obj.has_key('vsvip_ref'):
                merge_vs_vip_json(vs_json_obj, request=request)
        return rsp


class VirtualServicePoolDetail(VirtualServiceDetail, VirtualServicePoolCommon):

    def run_subview_callbacks(self):
        for v in self.view_list:
            if v == self:
                super(VirtualServicePoolDetail, self).run_callback()
            else:
                v.run_callback()

    def is_shared_vip(self, vsvip_slug):
        # Check db_cache if has more than 1 reference
        db_cache = DbCache()
        vs_list = db_cache.get_parents('VsVip', slug=vsvip_slug,
                                       model_filter=['VirtualService'])
        if len(vs_list) > 1:
            return True
        else:
            return False

    @api_version
    def do_put_action(self, request, *args, **kwargs):

        self.view_list = []
        kwargs['skip-versioning'] = True
        partial = kwargs.get('partial', False)
        data = request.DATA
        vsvip_cb = None
        vs_obj = None
        old_vs_data = None
        vs_obj = models.VirtualService.objects.get(uuid=kwargs['slug'])
        vsvip_uuid = vs_obj.vsvip_ref
        if vsvip_uuid:
            vsvip_obj = models.VsVip.objects.select_for_update().get(uuid=vsvip_uuid)

        if partial:
            data, add, replace, delete, update = get_patch_data(data)

            if vsvip_uuid:
                shared_vip = self.is_shared_vip(vsvip_obj.uuid)
                vsvip_in_data = any(field in data.keys() for field in vsvip_config_fields())
                if shared_vip:
                    # Cant updated any vsvip updates using PATCH on shared vip VS
                    if vsvip_in_data:
                        raise Exception('Cannot change VsVip fields for shared VirtualService.')
                else:
                    #Non Shared VIP
                    if vsvip_in_data:
                        old_vs_data = self.serializer_class().to_native(vs_obj, use_extension=False)
                        vsvip_cb = VsVipDetail()
                        vsvip_kwargs = copy.copy(kwargs)
                        vsvip_kwargs['slug'] = vsvip_obj.uuid
                        vsvip_cb.initial(request, *args, **vsvip_kwargs)
                        vsvip_cb.request = request
                        vsvip_cb.args = args
                        vsvip_cb.kwargs = vsvip_kwargs
                        vsvip_cb.do_put_detail(request, *args, **vsvip_kwargs)
                        self.view_list.append(vsvip_cb)
        else:
            # must do explicit string match as the data
            if self._vs_type_for_vsvip(data):
                shared_vip = self.is_shared_vip(vsvip_obj.uuid)
                vsvip_in_data = any(field in data.keys() for field in vsvip_config_fields())
                if shared_vip:
                    if 'vip' in data and 'vsvip_ref' in data:
                        if not self.vsvip_matches_db(data, data['vsvip_ref']):
                            raise Exception('Cannot change VsVip fields for shared VirtualService.')
                else:
                    if vsvip_in_data and 'vsvip_ref' not in data:
                        #copy vsvip_ref into data
                        # for non-shared vs allow PUT w/ vip and no vip_ref
                        if 'vsvip_ref' not in data:
                            data['vsvip_ref'] = uri_from_slug('VsVip', vsvip_obj.uuid)

                    if vsvip_in_data:
                        # PUT to VsVip if unshared
                        old_vs_data = self.serializer_class().to_native(vs_obj, use_extension=False)
                        vs_name = data.get('name', '')
                        data['name'] = vsvip_obj.name
                        vsvip_cb = VsVipDetail()
                        vsvip_kwargs = copy.copy(kwargs)
                        vsvip_kwargs['slug'] = vsvip_obj.uuid
                        vsvip_cb.initial(request, *args, **vsvip_kwargs)
                        vsvip_cb.request = request
                        vsvip_cb.args = args
                        vsvip_cb.kwargs = vsvip_kwargs
                        vsvip_cb.do_put_detail(request, *args, **vsvip_kwargs)
                        self.view_list.append(vsvip_cb)
                        data['name'] = vs_name

        try:
            rsp = super(VirtualServicePoolDetail, self).do_put_action(request, *args, **kwargs)
            self.view_list.append(self)
        except Exception as e:
            log.exception(e)
            # rollback db_cache for VsVip if VS update fails
            if vsvip_cb:
                old_data = models.VsVipSerializer().to_native(vsvip_obj, use_extension=False)
                vsvip_cb.db_cache_save(vsvip_obj, old_data)
                vsvip_cb.custom_rollback(vsvip_cb.object.protobuf(), old_pb=vsvip_cb.old_pb)
                # If VsVip successful will update db_cache for VS.
                # Reset VS for VsVip success and VS failure
                if vs_obj and old_vs_data:
                    self.db_cache_save(vs_obj, old_vs_data)
            raise
        if rsp.data.has_key('vsvip_ref'):
            merge_vs_vip_json(rsp.data, request=request)
        return rsp


    def _delete_policy(self, request, vs_uuid, p_uuid, db_cache, model_name, view_class,
                       *args, **kwargs):
        model_class = getattr(models, model_name)
        query = model_class.objects.filter(uuid=p_uuid)
        if query.count() == 0:
            # Object does not exist/has already been deleted.
            return

        policy_view = view_class()
        policy_view.initial(request, *args, **kwargs)
        policy_view.request = request
        policy_view.args = args
        kwargs['slug'] = p_uuid
        policy_view.kwargs = kwargs
        try:
            policy_view.do_delete_detail(request, *args, **kwargs)
            self.view_list.append(policy_view)
        except Exception as e:
            log.error('Delete %s:%s in virtual service failed with error: %s\nIgnoring delete of referenced object.'
                      % (model_name, p_uuid, str(e)  ))


    def delete_vsvip(self, vsvip_slug, request, *args, **kwargs):
        if not vsvip_slug:
            return
        db_cache = DbCache()
        vs_list = db_cache.get_parents('VsVip', slug=vsvip_slug, model_filter=['VirtualService'])
        if not vs_list:
            vsvip_view = VsVipDetail()
            vsvip_view.initial(request, *args, **kwargs)
            vsvip_view.request = request
            vsvip_view.args = args
            vsvip_view.kwargs = kwargs
            kwargs['slug'] = vsvip_slug
            vsvip_view.do_delete_detail(request, *args, **kwargs)
            self.view_list.append(vsvip_view)

    def do_delete_detail(self, request, *args, **kwargs):
        self.view_list = []
        # Only called during macro
        # API workflow will call VirtualServiceDetail().do_delete_detail()

        #must lock VsVip before VS to avoid deadlocks
        vsvip_slug = slug_from_uri(models.VirtualService.objects.get(uuid=kwargs['slug']).vsvip_ref)
        if vsvip_slug:
            models.VsVip.objects.select_for_update().get(uuid=vsvip_slug)

        rsp = super(VirtualServicePoolDetail, self).do_delete_detail(request, *args, **kwargs)
        self.view_list.append(self)
        self.delete_vsvip(vsvip_slug, request, *args, **kwargs)
        return rsp


    @db_transaction
    def delete_transaction(self, request, *args, **kwargs):
        self.view_list = []

        #must lock VsVip before Vs to avoid deadlocks
        vsvip_slug = slug_from_uri(models.VirtualService.objects.get(uuid=kwargs['slug']).vsvip_ref)
        if vsvip_slug:
            models.VsVip.objects.select_for_update().get(uuid=vsvip_slug)

        vs_view = VirtualServiceDetail()
        vs_view.initial(request, *args, **kwargs)
        vs_view.request = request
        vs_view.args = args
        vs_view.kwargs = kwargs
        self.view_list.append(vs_view)
        rsp = vs_view.do_delete_detail(request, *args, **kwargs)

        self.delete_vsvip(vsvip_slug, request, *args, **kwargs)

        if ('force_delete' not in request.QUERY_PARAMS and
            request.META.get('HTTP_X_AVI_USERAGENT','') != 'UI'):
            return rsp

        if not vs_view.callback_data:
            log.error('Callback data for vs view not found')
            return rsp

        vs_pb, method_name = vs_view.callback_data
        vs_uuid = vs_pb.uuid
        db_cache = DbCache()
        for policy_index in vs_pb.http_policies:
            self._delete_policy(request, vs_uuid, policy_index.http_policy_set_uuid,
                        db_cache, 'HTTPPolicySet', HTTPPolicySetDetail,
                        *args, **kwargs)

        if vs_pb.network_security_policy_uuid:
            self._delete_policy(request, vs_uuid, vs_pb.network_security_policy_uuid,
                        db_cache,'NetworkSecurityPolicy', NetworkSecurityPolicyDetail,
                        *args, **kwargs)

        if vs_pb.microservice_uuid:
            self._delete_policy(request, vs_uuid, vs_pb.microservice_uuid,
                        db_cache, 'MicroService', MicroServiceDetail,
                        *args, **kwargs)
        return rsp

    def delete(self, request, *args, **kwargs):
        """
        Also delete all connected policies of vs,
        if request has parameter force_delete
        """
        rsp = self.delete_transaction(request, *args, **kwargs)
        self.run_subview_callbacks()
        return rsp

    def run_callback(self):
        self.run_subview_callbacks()

    def populate_shared_vs_refs(self, request, rsp, kwargs):
        include_name =  ('include_name' in request.QUERY_PARAMS)
        db_cache = DbCache()
        vs_list = db_cache.get_parents('VsVip', slug=slug_from_uri(rsp.data['vsvip_ref']),
                model_filter=['VirtualService'])
        vs_uuids = [vs.uuid for vs in vs_list]
        vs_uuids.remove(kwargs['slug'])
        rsp.data.setdefault('shared_vs_refs', []).extend(
                [uri_from_slug('VirtualService', vs_uuid, host=request.get_host(),
                include_name=include_name, name=DbBaseCache.uuid2name(vs_uuid))
                for vs_uuid in vs_uuids])

    @api_version
    def do_get_action(self, request, *args, **kwargs):
        kwargs['skip-versioning'] = True
        rsp = super(VirtualServicePoolDetail, self).do_get_action(request, *args, **kwargs)
        if rsp.data.has_key('vsvip_ref'):
            self.populate_shared_vs_refs(request, rsp, kwargs)
            merge_vs_vip_json(rsp.data, request=request)
        return rsp


class VsVipList(ListView, CreateView):
    model = models.VsVip
    serializer_class = models.VsVipSerializer
    rpc_data = {

    }


class VsVipDetail(DetailView):
    model = models.VsVip
    serializer_class = models.VsVipSerializer
    rpc_data = {

    }

    def do_put_action(self, request, *args, **kwargs):
        old_vss = models.VirtualService.objects.filter(vsvip_ref__contains=kwargs['slug'])
        old_vs_map = {}
        for old_vs in old_vss:
            old_vs_map[old_vs.uuid] = old_vs.protobuf()
        rsp = super(VsVipDetail, self).do_put_action(request, *args, **kwargs)
        if old_vss:
            new_vss = models.VirtualService.objects.filter(vsvip_ref__contains=kwargs['slug'])
            for new_vs in new_vss:
                new_vs_pb = new_vs.protobuf()
                if new_vs_pb.uuid in old_vs_map:
                    save_diff(old_vs_map[new_vs_pb.uuid], new_vs_pb)
        return rsp

    def do_get_detail(self, request, *args, **kwargs):
        rsp = super(VsVipDetail, self).do_get_detail(
                request, *args, **kwargs)
        include_name =  ('include_name' in request.QUERY_PARAMS)
        db_cache = DbCache()
        vs_list = db_cache.get_parents('VsVip', slug=rsp.data['uuid'],
                model_filter=['VirtualService'])
        rsp.data.setdefault('vs_refs', []).extend(
                [uri_from_slug('VirtualService', vs.uuid, host=request.get_host(),
                include_name=include_name, name=DbBaseCache.uuid2name(vs.uuid))
                for vs in vs_list])
        return rsp

    def run_callback(self):
        if self.callback_data and not self.initial_data and self.request.method in ['PUT', 'PATCH']:
            vs_view = VirtualServiceDetail()
            vs_view.request = self.request
            pb, method_name = self.callback_data

            db_cache = DbCache()
            vs_list = db_cache.get_parents('VsVip', slug=pb.uuid,
                                           model_filter=['VirtualService'])
            for vs in vs_list:
                vs_obj = models.VirtualService.objects.get(uuid=vs.uuid)
                if self.old_pb:
                    old_vs_pb = models.VirtualServiceProto()
                    old_vs_pb.CopyFrom(vs_obj.protobuf())
                    merge_vs_vip_protobuf(old_vs_pb, vsvip_pb=self.old_pb)
                # TODO: might be able to remove this if/else condition.
                # Need to ensure codepath won't hit the else
                else:
                    old_vs_pb = None
                vs_view.save_callback(vs_obj, method_name, old_pb=old_vs_pb)
                vs_view.run_callback()
        super(VsVipDetail, self).run_callback()


def _execute_server_op(servers, index, op):
    if op == 'enable':
        servers[index].enabled = True
    elif op == 'disable':
        servers[index].enabled = False
    elif op == 'remove':
        del servers[index]


def _matched_server(server_pb, server_list):
    for server in server_list:
        found = True
        for field in server.keys():
            if field == 'ip':
                if server_pb.ip.addr != server['ip']['addr']:
                    found = False
                    break
            elif getattr(server_pb, field) != server[field]:
                found = False
                break
        if found:
            return True

class BatchPoolServerView(CreateView, NestedFilter):
    model = models.Pool

    @api_perf
    def _update_pools(self, pools, servers, op):
        for pool in pools:
            pb = pool.protobuf()
            old_pb = models.Pool.pb_class()
            old_pb.MergeFrom(pb)
            server_matched = False
            for i in range(len(pb.servers)-1, -1, -1):
                if _matched_server(pb.servers[i], servers):
                    server_matched = True
                    _execute_server_op(pb.servers, i, op)
            if server_matched:
                new_obj, _ = protobuf2model(pb, None, True,
                                            run_default_function=False)
                new_pb = new_obj.protobuf()
                self.callback_list.append((old_pb, new_pb))

    @api_version
    @api_perf
    def do_post_action(self, request, *args, **kwargs):
        POOL_BATCH_MAX = 100
        self.callback_list = []
        query_kwargs = {}
        op = kwargs['action']
        if self.cloud:
            query_kwargs['cloud_ref'] = self.cloud
        if not self.all_tenants and self.tenant:
            query_kwargs['tenant_ref'] = self.tenant
        servers = request.DATA.get('servers', [])
        if not servers:
            raise DataException('Specify servers to be %sd' % op)

        q_list = []
        for server in servers:
            query = ''
            for key in server:
                query_key = key
                query_value = server[key]
                if key == 'ip' and server[key].get('addr'):
                    query_key = 'addr'
                    query_value = server[key]['addr']
                query += '(%s,%s)' % (query_key, query_value)
            if query:
                q_list.append(self.translate_tuple(query))
        query_args = Q()
        for q_val in q_list:
            query_args = query_args | q_val
        pools = models.Pool.objects.select_for_update().filter(query_args)
        count = pools.count()
        if count > POOL_BATCH_MAX:
            raise DataException('Servers matching definition are present in '
                                '%s pools. Query exceeded maximum of %s.'
                                % (count, POOL_BATCH_MAX))
        self._update_pools(pools, servers, op)

        return Response(status=200)

    @api_perf
    def run_callback(self):
        futures = []
        with ThreadPoolExecutor(max_workers=2) as executor:
            for old_pb, new_pb in self.callback_list:
                future = executor.submit(self._run_callback, old_pb, new_pb)
                futures.append(future)
        for future in futures:
            future.result(timeout=60)

    def _run_callback(self, old_pb, new_pb):
        method = 'put'
        pool_view = PoolDetail()
        pool_view.request = self.request
        pool_view.old_pb = old_pb
        pool_view.callback_data = new_pb, method
        pool_view.run_callback()
