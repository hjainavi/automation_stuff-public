
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
Network Custom Views
=====================
"""

import logging
from netaddr import IPNetwork
import iptools
import traceback
import json

from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator

from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.templatetags.rest_framework import replace_query_param

from avi.infrastructure.db_transaction import db_transaction
from avi.infrastructure.rpc_channel import RpcChannel, AviRpcController
from avi.util.views_constants import CLOUD_AGENT_TYPES
from avi.util.protobuf import protobuf2dict
from avi.util.cloud_util import get_my_admin_cloud
from avi.util.cluster_info import get_controller_version

from models_network import Network, NetworkRuntime
from models_vi_mgr_runtime import VIMgrNWRuntime
from models_ipam_profile import IpamDnsProviderProfile
from api.serializers_network import NetworkSerializer

from avi.rest.views import (
    CommonView, SingleObjectView, UpdateView,
    ListView, CreateView, DetailView)
from avi.rest.pb_utils import get_pb_if_exists
from avi.rest.error_list import DataException, WebappException, ServerException
from avi.rest.pb2model import protobuf2model
from avi.rest.pb2dict import protobuf2dict_withrefs
from avi.rest.view_utils import process_view_request
from avi.rest.url_utils import uri_from_slug
from avi.rest.json_io import JSONRenderer
from avi.rest.queryset_custom import QuerysetCustom

from avi.protobuf import common_pb2, network_pb2
from avi.protobuf.options_pb2 import V4, V6, V4_ONLY, V6_ONLY, V4_V6
from avi.protobuf.network_rpc_pb2 import NetworkService_Stub
from avi.protobuf.rpc_common_pb2 import RPCRequest
from avi.protobuf import ipam_profile_pb2 as ipam_pb2
from avi.protobuf.ipam_profile_pb2 import IpamDnsSubnetDomainList
from avi.protobuf_json.protobuf_json import json2pb

log = logging.getLogger(__name__)


class NetworkRetrieveIps(UpdateView):

    @db_transaction
    def retrieveIPs(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        uuid = None
        if 'key' in kwargs:
            uuid = kwargs['key']
        elif 'slug' in kwargs:
            uuid = kwargs['slug']

        try:
            obj = Network.objects.select_for_update().get(uuid=uuid)
        except ObjectDoesNotExist:
            raise ObjectDoesNotExist("Network not found for uuid: %s"
                                     % uuid)

        try:
            obj_runtime = NetworkRuntime.objects.select_for_update().get(uuid=uuid)
        except ObjectDoesNotExist:
            raise ObjectDoesNotExist("Network Runtime not found for uuid: %s"
                                     % uuid)

        log.error(request.DATA)
        req = network_pb2.RetrieveIps()
        json2pb(req, request.DATA)
        if not req.HasField('count'):
            raise DataException('Field "count" not provided')
        if not req.HasField('subnet'):
            raise DataException('Field "subnet" not provided')

        cidr_pfx = IPNetwork(req.subnet.ip_addr.addr +
                             '/' + str(req.subnet.mask))
        req.subnet.ip_addr.addr = str(cidr_pfx.network)

        nw_runtime_pb = obj_runtime.protobuf()
        subnet_runtime_found = None
        for subnet_runtime in nw_runtime_pb.subnet_runtime:
            if (subnet_runtime.prefix.ip_addr.addr
                    != req.subnet.ip_addr.addr):
                continue
            if subnet_runtime.prefix.mask != req.subnet.mask:
                continue
            subnet_runtime_found = subnet_runtime
            break

        nw_pb = obj.protobuf()
        subnet_found = None
        for subnet in nw_pb.configured_subnets:
            if (subnet.prefix.ip_addr.addr
                    != req.subnet.ip_addr.addr):
                continue
            if subnet.prefix.mask != req.subnet.mask:
                continue
            subnet_found = subnet
            break

        if not subnet_runtime_found or not subnet_found:
            raise WebappException('Subnet %s not found' % cidr_pfx)
        if not subnet_runtime_found.HasField('free_ip_count'):
            raise WebappException('No free IPs in subnet %s' % cidr_pfx)
        if subnet_runtime_found.free_ip_count < req.count:
            raise WebappException('Insufficient free IPs in subnet %s' % cidr_pfx)

        # Create pool of static IP's, ranges
        ips = []
        for ip in subnet_found.static_ips:
            ips.append(ip.addr)
        ip_ranges = []
        for ip_range in subnet_found.static_ranges:
            ip_ranges.append(iptools.IpRange(
                ip_range.begin.addr, ip_range.end.addr))
        ip_pool = iptools.IpRangeList(*(ips+ip_ranges))

        # Convert IP pool to IP set
        ip_set = set()
        ip_iter = ip_pool.__iter__()
        while 1:
            try:
                ip = next(ip_iter)
                ip_set.add(ip)
            except Exception as e:
                break
        total_ip_count = len(ip_set)

        # Remove already allocated IP's
        for ip_alloc in subnet_runtime.ip_alloced:
            ip_set.remove(ip_alloc.ip.addr)

        # Find free IP's in pool
        ip_list = list(ip_set)
        ip_list.sort()
        ips_removed = ip_list[0:req.count]
        #log.error('Num IPs removed %d' % len(ips_removed))

        # Reset Total and free IP counts
        subnet_runtime_found.total_ip_count = \
            total_ip_count - req.count
        subnet_runtime_found.free_ip_count = \
            (subnet_runtime_found.total_ip_count -
             subnet_runtime_found.used_ip_count)

        # Update the network object with updated list of
        # static IP's and ranges
        new_nw_pb = network_pb2.Network()
        new_nw_pb.CopyFrom(nw_pb)
        new_subnet_found = None
        for subnet in new_nw_pb.configured_subnets:
            if (subnet.prefix.ip_addr.addr
                    != req.subnet.ip_addr.addr):
                continue
            if subnet.prefix.mask != req.subnet.mask:
                continue
            new_subnet_found = subnet
            break
        new_subnet_found.ClearField('static_ips')
        new_subnet_found.ClearField('static_ranges')
        for subnet_ip in subnet_found.static_ips:
            if subnet_ip.addr in ips_removed:
                continue
            new_subnet_found.static_ips.add().CopyFrpm(subnet_ip)
        ip_ranges = []
        for ip_range in subnet_found.static_ranges:
            ip_ranges.append(iptools.IpRange(
                ip_range.begin.addr, ip_range.end.addr))
        for ip in ips_removed:
            split_ip_ranges = []
            for i in range(len(ip_ranges)-1, -1, -1):
                ip_range = ip_ranges[i]
                if ip not in ip_range:
                    continue
                index = ip_range.index(ip)
                if index == 0:
                    try:
                        split_ip_range = ip_range[1:]
                        split_ip_ranges.append(split_ip_range)
                    except IndexError:
                        pass
                    #log.error('%s' % split_ip_range)
                elif index == len(ip_range) - 1:
                    try:
                        split_ip_range = ip_range[:-1]
                        split_ip_ranges.append(split_ip_range)
                    except IndexError:
                        pass
                    #log.error('%s' % split_ip_range)
                else:
                    split_ip_range = ip_range[:index]
                    split_ip_ranges.append(split_ip_range)
                    #log.error('%s' % split_ip_range)
                    split_ip_range = ip_range[index + 1:]
                    split_ip_ranges.append(split_ip_range)
                    #log.error('%s' % split_ip_range)

                del ip_ranges[i]
            ip_ranges += split_ip_ranges
        for ip_range in ip_ranges:
            range_pb = new_subnet_found.static_ranges.add()
            range_pb.begin.addr = ip_range[0]
            range_pb.begin.type = 0
            range_pb.end.addr = ip_range[-1]
            range_pb.end.type = 0

        # Save updated info in network runtime
        protobuf2model(nw_runtime_pb, None, True)
        # Save updated info in network
        protobuf2model(new_nw_pb, None, True)

        rsp = network_pb2.RetrieveIpsRsp()
        for ip in ips_removed:
            ip_pb = rsp.ips.add()
            ip_pb.addr = ip
            ip_pb.type = 0

        rpcReq = RPCRequest()
        rpcReq.uuid = uuid
        rpcReq.obj_type = common_pb2.NETWORK
        rpcReq.resource.network.CopyFrom(new_nw_pb)
        stub = NetworkService_Stub(RpcChannel(uuid=uuid, skip_rsp=True))

        return (stub, rpcReq, Response(protobuf2dict(rsp)))

    def post(self, request, *args, **kwargs):
        stub, rpcReq, rsp = self.retrieveIPs(request, *args, **kwargs)
        stub.Update(AviRpcController(), rpcReq)
        return rsp


class NetworkSubnetListView(CommonView, SingleObjectView):
    renderer_classes = (JSONRenderer,)

    def send_paginated_response(self, request, rsp_pb):
        try:
            page_size = request.QUERY_PARAMS.get('page_size',
                                                 api_settings.PAGINATE_BY)
            paginator = Paginator(rsp_pb.results, page_size)
            data = {'count': paginator.count}
            page_index = request.QUERY_PARAMS.get('page', 1)
            page = paginator.page(page_index)
            if page.has_next():
                full_uri = request.build_absolute_uri()
                data['next'] = replace_query_param(full_uri, 'page',
                                                   page.next_page_number())

            data['results'] = []
            for obj in page.object_list:
                data['results'].append(protobuf2dict_withrefs(
                    obj, request, always_include_name=True))

            return Response(data)
        except Exception as err:
            s = traceback.format_exc()
            msg = 'Get NetworkSubnetList Error:' + str(err) + 'trace:' + str(s)
            raise ServerException(msg)

    def get(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)

        if not self.cloud:
            log.warning("self.cloud is not set, using admin default cloud")
            self.cloud = get_my_admin_cloud(pb=False)
        cloud_pb = self.cloud.protobuf()

        auto_allocate_only = request.QUERY_PARAMS.get('auto_allocate_only', None)
        search = request.QUERY_PARAMS.get('search', None)
        if not search:
            search = kwargs.get('slug', None)
        vrf_context_uuid = request.QUERY_PARAMS.get('vrf_context_uuid', None)
        preferred_nw_type = request.QUERY_PARAMS.get('preferred_nw_type', None)
        discovered_only = request.QUERY_PARAMS.get('discovered_only', None)
        configured_only = request.QUERY_PARAMS.get('configured_only', None)
        name = request.QUERY_PARAMS.get('name', None)
        uuid = request.QUERY_PARAMS.get('uuid', None)
        log.info(request.QUERY_PARAMS)

        nw_dict = {}
        custom_view_kwargs = {'version': get_controller_version()}
        try:
            rsp_pb = network_pb2.NetworkSubnetList()
            ipam_provider_pb = None

            if auto_allocate_only and cloud_pb.HasField('ipam_provider_uuid'):
                ipam_provider_pb = IpamDnsProviderProfile.objects.get(
                    uuid=cloud_pb.ipam_provider_uuid).protobuf(decrypt=True)

            if ipam_provider_pb:
                log.info("allocate_ip_in_vrf:%s" % ipam_provider_pb.allocate_ip_in_vrf)

            if ipam_provider_pb and (ipam_provider_pb.type == ipam_pb2.IPAMDNS_TYPE_INFOBLOX):
                # get all networks from infoblox
                api = '/api/ipamdnsproviderprofilenetworklist'
                ipam_rsp = process_view_request(api, 'GET',
                                                request.QUERY_PARAMS,
                                                request.user,
                                                custom_view_kwargs=
                                                custom_view_kwargs)
                if ipam_rsp.status_code != 200:
                    log.error('%s Bad response status %d: %s' %
                              (api, ipam_rsp.status_code, ipam_rsp.data))
                    return Response(data=ipam_rsp, status=200)
                ipam_rsp_networks = IpamDnsSubnetDomainList()
                json2pb(ipam_rsp_networks, ipam_rsp.data)
                for network in ipam_rsp_networks.subnets:
                    # NOTE: dummy values for uuid, name & url
                    nw_view = ipam_provider_pb.infoblox_profile.network_view \
                        if ipam_provider_pb.HasField('infoblox_profile') else "unknown"
                    ib_nw_uuid = "infoblox--" + nw_view + "--"
                    ib_nw_uuid += network.ip_addr.addr + "-" + str(network.mask)
                    log.info("uuid:%s ib_nw_uuid:%s", uuid, ib_nw_uuid)
                    if name and name != nw_view:
                        continue
                    if uuid and uuid != ib_nw_uuid:
                        continue
                    nw_pb = rsp_pb.results.add()
                    nw_pb.uuid = ib_nw_uuid
                    nw_pb.name = nw_view
                    nw_pb.url = ib_nw_uuid
                    nw_pb.cloud_uuid = cloud_pb.uuid
                    subnet_pb = nw_pb.subnet.add()
                    subnet_pb.prefix.CopyFrom(network)
                return self.send_paginated_response(request, rsp_pb)
            elif (ipam_provider_pb and (ipam_provider_pb.type == ipam_pb2.IPAMDNS_TYPE_INTERNAL) and
                    ipam_provider_pb.internal_profile.usable_network_uuids):
                q = Q()
                q.add(Q(uuid__in=ipam_provider_pb.internal_profile.usable_network_uuids), Q.AND)
                if ipam_provider_pb.allocate_ip_in_vrf and vrf_context_uuid:
                    q.add(Q(vrf_context_ref__uuid=vrf_context_uuid), Q.AND)
                if search:
                    q.add(Q(name__contains=search), Q.AND)
                if preferred_nw_type in ['V4_ONLY', 'V4_V6']:
                    q.add(Q(json_data__configured_subnets__contains=json.dumps({'type': 'V4'})[1:-1]), Q.AND)
                if preferred_nw_type in ['V6_ONLY', 'V4_V6']:
                    q.add(Q(json_data__configured_subnets__contains=json.dumps({'type': 'V6'})[1:-1]), Q.AND)
                if name:
                    q.add(Q(name=name), Q.AND)
                if uuid:
                    q.add(Q(uuid=uuid), Q.AND)

                int_nws = Network.objects.filter(q).order_by('name')
                if int_nws:
                    for inw in int_nws:
                        inw_pb = inw.protobuf()
                        nw_pb = rsp_pb.results.add()
                        nw_dict[inw_pb.uuid] = nw_pb
                        nw_pb.uuid = inw_pb.uuid
                        nw_pb.name = inw_pb.name
                        nw_pb.cloud_uuid = inw_pb.cloud_uuid
                        nw_pb.tenant_uuid = inw_pb.tenant_uuid
                        if inw_pb.HasField('vrf_context_uuid'):
                            nw_pb.vrf_context_uuid = inw_pb.vrf_context_uuid
                        nw_pb.url = uri_from_slug('Network', nw_pb.uuid,
                                                  host=request.get_host(),
                                                  name=nw_pb.name,
                                                  include_name=True)
                        for subnet in inw_pb.configured_subnets:
                            subnet_pb = nw_pb.subnet.add()
                            subnet_pb.prefix.CopyFrom(subnet.prefix)
                return self.send_paginated_response(request, rsp_pb)
            elif ipam_provider_pb and (ipam_provider_pb.type == ipam_pb2.IPAMDNS_TYPE_AWS):
                # get all networks from infoblox
                api = '/api/ipamdnsproviderprofilenetworklist'
                ipam_rsp = process_view_request(api, 'GET',
                                                request.QUERY_PARAMS,
                                                request.user,
                                                custom_view_kwargs=
                                                custom_view_kwargs)
                if ipam_rsp.status_code != 200:
                    log.error('%s Bad response status %d: %s' %
                              (api, ipam_rsp.status_code, ipam_rsp.data))
                    return Response(data=ipam_rsp, status=200)
                for snw in ipam_rsp.data.get('subnets', []):
                    nw_pb = rsp_pb.results.add()
                    nw_pb.uuid = snw['id']
                    nw_pb.name = snw['name']
                    nw_pb.url = snw['id']
                    nw_pb.cloud_uuid = cloud_pb.uuid
                    subnet_pb = nw_pb.subnet.add()
                    subnet_pb.prefix.ip_addr.addr = snw['ip_addr']['addr']
                    if snw['ip_addr']['type'] == 'V4':
                        subnet_pb.prefix.ip_addr.type = V4
                    else:
                        subnet_pb.prefix.ip_addr.type = V6
                    subnet_pb.prefix.mask = int(snw['mask'])
                return self.send_paginated_response(request, rsp_pb)

            # 2) Get all configured subnets stored in DB
            q = Q()
            if self.cloud:
                q.add(Q(cloud_ref=self.cloud), Q.AND)
            if name:
                q.add(Q(name=name), Q.AND)
            if uuid:
                q.add(Q(uuid=uuid), Q.AND)
            if search:
                q.add(Q(json_data__name__contains=search), Q.AND)
            if preferred_nw_type in ['V4_ONLY', 'V4_V6']:
                q.add(Q(json_data__configured_subnets__contains=json.dumps({'type': 'V4'})[1:-1]), Q.AND)
            if preferred_nw_type in ['V6_ONLY', 'V4_V6']:
                q.add(Q(json_data__configured_subnets__contains=json.dumps({'type': 'V6'})[1:-1]), Q.AND)
            log.info("%s" % q)

            networks = []
            if not discovered_only:
                networks = Network.objects.filter(q).order_by('name')
            for network in networks:
                network_pb = network.protobuf()
                nw_pb = rsp_pb.results.add()
                nw_dict[network_pb.uuid] = nw_pb
                nw_pb.uuid = network_pb.uuid
                nw_pb.name = network_pb.name
                nw_pb.cloud_uuid = network_pb.cloud_uuid
                nw_pb.tenant_uuid = network_pb.tenant_uuid
                if network_pb.HasField('vrf_context_uuid'):
                    nw_pb.vrf_context_uuid = network_pb.vrf_context_uuid
                nw_pb.url = uri_from_slug('Network', nw_pb.uuid,
                                          host=request.get_host(),
                                          name=nw_pb.name, include_name=True)
                for subnet in network_pb.configured_subnets:
                    subnet_pb = nw_pb.subnet.add()
                    subnet_pb.prefix.CopyFrom(subnet.prefix)

            # 3) Get the discovered subnets stored in DB
            vimgr_networks = []
            if not configured_only:
                vimgr_networks = VIMgrNWRuntime.objects.filter(q).order_by('name')
            for vinw in vimgr_networks:
                vinw_pb = vinw.protobuf()
                if vinw_pb.uuid in nw_dict:
                    nw_pb = nw_dict[vinw_pb.uuid]
                else:
                    nw_pb = rsp_pb.results.add()
                    nw_dict[vinw_pb.uuid] = nw_pb
                    nw_pb.uuid = vinw_pb.uuid
                    nw_pb.name = vinw_pb.name
                    nw_pb.tenant_uuid = vinw_pb.tenant_uuid
                    if vinw_pb.HasField('vrf_context_uuid'):
                        nw_pb.vrf_context_uuid = vinw_pb.vrf_context_uuid
                    nw_pb.url = uri_from_slug('Network', nw_pb.uuid,
                                              host=request.get_host(),
                                              name=nw_pb.name,
                                              include_name=True)
                for subnet in vinw_pb.ip_subnet:
                    subnet_pb = nw_pb.subnet.add()
                    subnet_pb.prefix.CopyFrom(subnet.prefix)
                    if subnet.HasField('uuid'):
                        subnet_pb.uuid = subnet.uuid
                    if subnet.HasField('name'):
                        subnet_pb.name = subnet.name
                    if subnet.HasField('fip_available'):
                        subnet_pb.fip_available = subnet.fip_available
                    for fsnw in subnet.floatingip_subnets:
                        f = subnet_pb.floatingip_subnets.add()
                        f.CopyFrom(fsnw)

            # 4) Get the subnets by querying cloud connector API
            cc_vimgr_networks = []
            if not configured_only:
                cc_vimgr_networks = QuerysetCustom.get_object_list('VIMgrNWRuntime', request, self)
                if not cc_vimgr_networks:
                    cc_vimgr_networks = []
            for vinw_pb in cc_vimgr_networks:
                if vinw_pb.uuid in nw_dict:
                    nw_pb = nw_dict[vinw_pb.uuid]
                else:
                    nw_pb = rsp_pb.results.add()
                    nw_dict[vinw_pb.uuid] = nw_pb
                    nw_pb.uuid = vinw_pb.uuid
                    nw_pb.name = vinw_pb.name
                    nw_pb.tenant_uuid = vinw_pb.tenant_uuid
                    if vinw_pb.HasField('vrf_context_uuid'):
                        nw_pb.vrf_context_uuid = vinw_pb.vrf_context_uuid
                    nw_pb.url = uri_from_slug('Network', nw_pb.uuid,
                                              host=request.get_host(),
                                              name=nw_pb.name,
                                              include_name=True)
                for subnet in vinw_pb.ip_subnet:
                    subnet_pb = nw_pb.subnet.add()
                    subnet_pb.prefix.CopyFrom(subnet.prefix)
                    if subnet.HasField('uuid'):
                        subnet_pb.uuid = subnet.uuid
                    if subnet.HasField('name'):
                        subnet_pb.name = subnet.name
                    if subnet.HasField('fip_available'):
                        subnet_pb.fip_available = subnet.fip_available
                    for fsnw in subnet.floatingip_subnets:
                        f = subnet_pb.floatingip_subnets.add()
                        f.CopyFrom(fsnw)
        except Exception as err:
            s = traceback.format_exc()
            msg = 'Get NetworkSubnetList Error:' + str(err) + 'trace:' + str(s)
            raise ServerException(msg)
        return self.send_paginated_response(request, rsp_pb)


class NetworkList(ListView, CreateView):
    model = Network
    serializer_class = NetworkSerializer
    rpc_data = {

        'post': {
            'class_name': 'Network',
            'method_name': 'Create',
            'field_name': 'network',
            'service_name': 'NetworkService_Stub'
        },

    }

class NetworkDetail(DetailView):
    model = Network
    serializer_class = NetworkSerializer
    rpc_data = {

        'put': {
            'class_name': 'Network',
            'method_name': 'Update',
            'field_name': 'network',
            'service_name': 'NetworkService_Stub'
        },

        'patch': {
            'class_name': 'Network',
            'method_name': 'Update',
            'field_name': 'network',
            'service_name': 'NetworkService_Stub'
        },

        'delete': {
            'class_name': 'Network',
            'method_name': 'Delete',
            'field_name': 'network',
            'service_name': 'NetworkService_Stub'
        }
    }

    def get(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        rsp = None
        if not self.cloud:
            self.cloud = get_my_admin_cloud(pb=False)
        cloud_pb = self.cloud.protobuf()
        if cloud_pb.vtype in CLOUD_AGENT_TYPES:
            subnet_view = NetworkSubnetListView()
            r = subnet_view.get(request, *args, **kwargs)
            rsp_data = r.data
            if len(rsp_data.get('results', [])) == 1:
                data = rsp_data['results'][0]
                rsp = Response(data=data, status=200)
        if not rsp:
            rsp = super(NetworkDetail, self).get(request, *args, **kwargs)
        return rsp
