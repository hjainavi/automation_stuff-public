
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
Treeview for all inventory objects
"""

import logging

import gevent

from django.db.models import ObjectDoesNotExist
from rest_framework.response import Response

from avi.protobuf.common_pb2 import READ_ACCESS 
from avi.protobuf.django_internal_pb2 import PERMISSION_SERVICEENGINE

from api.views_inventory import (VirtualServiceSummaryInventoryView,
                                  PoolInventoryServerView, DEFAULT_HS_DATA)
from api.models import (Pool, ServiceEngine, Network,
                            ServiceEngineSerializer, PoolGroupSerializer)
from avi.rest.error_list import PermissionError
from avi.infrastructure.db_base_cache import DbBaseCache
from avi.rest.api_perf import api_perf
from avi.rest.url_utils import uri_from_slug

log = logging.getLogger(__name__)


class InventoryMapView(VirtualServiceSummaryInventoryView):
    def parse_config_data(self, config):
        data = {}
        config.pop('app_profile_type', None)
        data['name'] = config.pop('name', None)
        data['uuid'] = config.pop('uuid', None)
        data['url'] = config.pop('url', None)
        data['vip'] = config.pop('vip', None)
        data['floating_ip'] = config.pop('floating_ip', None)
        data['fqdn'] = config.pop('fqdn', '')
        data['cloud_ref'] = config.pop('cloud_ref', None)
        data['se_group_ref'] = config.pop('se_group_ref', None)
        data['east_west_placement'] = config.pop('east_west_placement', False)
        data['waf_policy_ref'] = config.pop('waf_policy_ref', None)
        return data

    def check_se_access(self, request):
        se_access = True
        try:
            self.check_user_tenant_resource(request.user, self.tenant,
                            PERMISSION_SERVICEENGINE, READ_ACCESS, 'ServiceEngine')
        except PermissionError:
            se_access = False
        return se_access
        
    @api_perf
    def get(self, request, *args, **kwargs):
        rsp = super(InventoryMapView, self).get(request, *args, **kwargs)
        
        if request.QUERY_PARAMS.get('skip_se', False):
            se_access = False
        else:
            se_access = self.check_se_access(request)
        data = rsp.data

        obj_list = data['results']

        pool_set = set()
        se_set = set()
        for vs_data in obj_list:
            vs_uuid = vs_data['uuid']
            
            oper_status =  vs_data.pop('oper_status', {})
            if oper_status:
                vs_data['runtime'] = {'oper_status': oper_status}

            # get SE
            if se_access and not vs_data.get('east_west_placement'):
                se_refs = self.db_cache.get_children('VirtualService', uuid=vs_uuid,
                                                 model_filter=['ServiceEngine'],
                                                 depth=1)
            else:
                se_refs = []
            for ref in se_refs:
                se_set.add(ref.uuid)
            vs_data['serviceengines'] = [ref.uuid for ref in se_refs]
        
            # get Pool
            pool_refs = self.db_cache.get_children('VirtualService', uuid=vs_uuid, 
                                                   model_filter=['Pool'])
            for ref in pool_refs:
                pool_set.add(ref.uuid)

            vs_data['pool_refs'] = pool_refs
            vs_data['config'] = self.parse_config_data(vs_data)

            # get PoolGroup
            poolgroup_refs = self.db_cache.get_children('VirtualService', uuid=vs_uuid, model_filter=['PoolGroup'])
            poolgroup_serializer = PoolGroupSerializer(context={'request': request})
            pg_objs = [poolgroup_serializer.to_native(x.obj_ref()) for x in poolgroup_refs]
            pg_refs = []
            for obj in pg_objs:
                pg_refs.append({"uuid": obj.get('uuid'),
                                "url": obj.get('url'),
                                "name": obj.get('name', ''),
                                "members": obj.get('members', [])})
            vs_data['poolgroup_refs'] = pg_refs

        pool_list = list(pool_set)
        self.server_view = self.initialize_view(PoolInventoryServerView, request,
                                                args, kwargs)

        if 'health_score' in self.resource_list:
            self.pool_srvr_healthscores = self.server_view.\
                get_server_health_score_data(','.join(pool_list),
                                             request)
            self.pool_heathscores = self.get_collection_healthscore(request,
                                                                    'Pool',
                                                                    pool_list)
            self.se_healthscores = self.get_collection_healthscore(request,
                                                                   'ServiceEngine',
                                                                   list(se_set))
        else:
            self.pool_srvr_healthscores = {}
            self.pool_heathscores = {}
            self.se_healthscores = {}

        for vs_data in obj_list:
            pools = []
            threads = []
            for pool_ref in vs_data.pop('pool_refs'):
                threads.append(gevent.spawn(self.get_pool_data, request,
                                            pool_ref))
            gevent.joinall(threads)
            pools = [thread.value for thread in threads]

            vs_data['pools'] = pools

            poolgroup_refs = []
            for poolgroup_ref in vs_data.pop('poolgroup_refs'):
                members = poolgroup_ref.pop('members', [])
                for member in members:
                    threads = []
                    pool_data = {}
                    if member.get('pool_ref', None):
                        pool_data = self.get_pool_data(request, pool_uuid=(member.get('pool_ref').split('/')[-1].split('#')[0]))

                    member['pool_ref_data'] = pool_data
                poolgroup_ref['members'] = members
                poolgroup_refs.append(poolgroup_ref)

            vs_data['poolgroup_refs'] = poolgroup_refs

        data['serviceengines'] = self.get_se_data(request, se_set)

        return Response(data)

    def _get_nw_name_from_uuid(self, nw_uuid):
        name = DbBaseCache.uuid2name(nw_uuid)
        if not name:
            nw_names = Network.objects.filter(uuid=nw_uuid).values('name')
            if nw_names:
                return nw_names[0]['name']
            else:
                return None
        return name

    def _get_server_key(self, server_pb, default_port):
        s_port = server_pb.port
        if not s_port:
            s_port = default_port
        s_ip = server_pb.ip.addr
        server_key = "%s:%s" % (s_ip, s_port)
        return server_key

    def _get_network_data(self, pool_pb, default_port):
        # check network
        network_dict = {}
        for server_pb in pool_pb.servers:
            server_key = self._get_server_key(server_pb, default_port)
            if server_pb.discovered_networks:
                for discovered_nw in server_pb.discovered_networks:
                    nw_uuid = discovered_nw.network_uuid
                    nw_name = self._get_nw_name_from_uuid(nw_uuid)
                    if nw_name:
                        if nw_name not in network_dict:
                            network_dict[nw_name] = []
                        network_dict[nw_name].append(server_key)
        return network_dict

    def _get_server_data(self, uuid, pool_pb, default_port, request, pool_runtime):
        server_data = {}
        server_hs = None
        if self.pool_srvr_healthscores:
            server_hs = self.pool_srvr_healthscores.get(uuid, None)
        # TODO: gevent here
        if 'runtime' in self.resource_list:
            server_runtimes = self.server_view.get_server_runtime(uuid,
                                                        default_port, request)
        else:
            server_runtimes = {}
        for server_pb in pool_pb.servers:
            server_key = self._get_server_key(server_pb, default_port)
            s_data = dict()
            s_data['config'] = {}
            s_data['config']['hostname'] = server_pb.hostname
            if 'runtime' in self.resource_list:
                if server_key in server_runtimes:
                    s_data['runtime'] = {}
                    s_data['runtime'].update(server_runtimes[server_key])
                else:
                    s_data['runtime'] = pool_runtime
            if 'health_score' in self.resource_list:
                if server_hs:
                    s_data['health_score'] = server_hs.get(server_key, '')
                if not s_data.get('health_score'):
                    s_data['health_score'] = DEFAULT_HS_DATA.copy()

            server_data[server_key] = s_data
        return server_data
    
    @api_perf
    def _get_pool_data(self, request, pool_uuid):
        pool_data = {}
        if pool_uuid in self.pool_heathscores:
            pool_data['health_score'] = self.pool_heathscores[pool_uuid]
        if 'runtime' in self.resource_list:
            pool_data['runtime'] = self.get_runtime_data(pool_uuid, request)
        if 'alert' in self.resource_list:
            pool_data['alert'] = self.get_alert_data(pool_uuid, request)
        pool_obj = Pool.objects.get(uuid=pool_uuid)
        pool_pb = pool_obj.protobuf()
        default_server_port = pool_pb.default_server_port
        if not default_server_port:
            default_server_port = 80
        pool_data['networks'] = self._get_network_data(pool_pb, default_server_port)
        pool_data['servers'] = self._get_server_data(pool_uuid, pool_pb, default_server_port, request, pool_data.get('runtime'))
        pool_data['config'] = {}
        pool_data['config']['url'] = uri_from_slug("pool", pool_uuid, host=request.get_host())
        pool_data['config']['uuid'] = pool_uuid
        pool_data['config']['name'] = pool_pb.name
        return pool_data

    @api_perf
    def get_pool_data(self, request, pool_ref=None, pool_uuid=None):
        data = {}
        uuid = pool_ref.uuid if pool_ref else pool_uuid
        try:
            pool_obj = Pool.objects.get(uuid=uuid)
        except ObjectDoesNotExist:
            log.error('Error in getting pool data for map api:'
                      'Cannot find pool with uuid %s' % uuid)
            return {}

        data.update(self._get_pool_data(request, uuid))

        return data

    @api_perf
    def get_se_data(self, request, uuids):
        data = []
        if not uuids:
            return data
        se_list = ServiceEngine.objects.filter(uuid__in=uuids)
        se_serializer = ServiceEngineSerializer(context={'request': request})

        threads = []
        for se in se_list:
            threads.append(gevent.spawn(self.get_each_se_data,
                                        se_serializer, se, request))
        gevent.joinall(threads)
        data = [thread.value for thread in threads]

        return data

    def get_each_se_data(self, se_serializer, se, request):
        se_config = se_serializer.to_native(se)
        uuid = se.uuid
        se_config =  se_serializer.to_native(se)
        se_data = dict()
        se_data['config'] = {}
        se_data['config']['uuid'] = uuid
        se_data['config']['name'] = se_config.get('name')
        se_data['config']['url'] = se_config.get('url')
        se_data['config']['cloud_ref'] = se_config.get('cloud_ref')
        if uuid in self.se_healthscores:
            se_data['health_score'] = self.se_healthscores[uuid]
        se_data['runtime'] = self.get_runtime_data(uuid, request)
        se_data['alert'] = self.get_alert_data(uuid, request)

        return se_data
