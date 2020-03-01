
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

#pylint: disable=no-member
import os
import logging
import traceback
import string
import urlparse
import urllib
import copy
from collections import defaultdict
from datetime import datetime, timedelta
import gevent
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db.models import Count, Q
from rest_framework.response import Response
from rest_framework.settings import api_settings
from portal.settings_common import REST_FRAMEWORK as common_api_settings
from rest_framework.templatetags.rest_framework import replace_query_param
import ujson
from analytics.views import MetricsQueryView, PoolMetricsView, mglobals
from analytics.views_health_score import HealthScoreView, PoolHealthScoreView, \
                                    PoolHSListSortByView
from api.models_alerts import Alert, ALERT_LOW, ALERT_MEDIUM, ALERT_HIGH
from api.models_pool import Pool, PoolGroup
from api.models_vrf import VrfContext
from api.models_ipam_profile import IpamDnsProviderProfile
from api.models import ApplicationProfile, VirtualService, ServiceEngine, VsVip, VsVipSerializer
from api.models_ssl import SSLKeyAndCertificate
from api.serializers_vrf import VrfContextSerializer
from avi.protobuf.ssl_pb2 import (SSLCertificateExpiryStatus, SSL_CERTIFICATE_EXPIRY_WARNING, SSL_CERTIFICATE_EXPIRED)
from avi.infrastructure.db_base_cache import DbBaseCache
from avi.infrastructure.state_cache import (VirtualServiceStateDBCache, PoolStateDBCache, ServerStateDBCache, StateDBCacheApi)
from avi.infrastructure.datastore import Datastore, db_table_name_from_pb
from avi.infrastructure.rpc_channel import RpcChannel,AviRpcController
from avi.infrastructure.state_cache import ServiceEngineStateDBCache
from avi.protobuf_json.protobuf_json import pb2json
from avi.protobuf.common_pb2 import OPER_UP, OPER_DOWN, OPER_INITIALIZING
from avi.protobuf.health_score_pb2 import HealthScoreQueryResponse
from avi.protobuf.gslb_rpc_pb2 import GslbServiceService_Stub
from avi.protobuf.vs_pb2 import VirtualService as VirtualServiceProto
import avi.protobuf.syserr_pb2 as syserr
from avi.rest.api_perf import api_perf
from avi.rest.db_cache import DbCache
from avi.rest.callbacks import get_obj_type_enum, get_info_type_from_filter, set_rpc_filter, set_rpc_request_meta_data
from avi.rest.error_list import DataException
from avi.rest.pb2dict import protobuf2dict_withrefs
from avi.rest.url_utils import slug_from_uri, get_obj_type_name_from_uuid, uri_from_slug, get_scheme
import avi.rest.views as views
from avi.util.time_utils import duration_to_start_stop
import views_cloud_connector_custom
import views_cloud_custom
import views_network
import views_network_custom
import views_pool
import views_pool_group
import views_se
import views_se_group
import views_vi_mgr
import views_vs_pool
import views_gslb_custom
from avi.protobuf.rpc_common_pb2 import RPCRequest
from avi.infrastructure.taskqueue import TaskQueueException
log = logging.getLogger(__name__)

GSLB_MAX_NUM_OF_OBJS_IN_MSG = 50

AVERAGE_HS_PARAMS = {'limit': 72,
                      'step': 300,
                      'summary': 'True',
                      'dimension_aggregation': 'avg',
                      'pad_missing_data': 'False',
                      'result_format': 'METRICS_FORMAT_PROTOBUF'}

REALTIME_HS_PARAMS = {'limit': 1,
                      'step': 300,
                      #'summary': 'True',
                      'pad_missing_data': 'False',
                      'result_format': 'METRICS_FORMAT_PROTOBUF'}

# SERVER_METRICS = ("l4_server.avg_bandwidth,l4_server.avg_new_established_conns,"
#  "l7_server.avg_complete_responses,l4_server.max_open_conns,"
#  "l4_server.avg_total_rtt,l7_server.avg_application_response_time")

# DEFAULT_VS_METRICS = ("l4_server.avg_bandwidth,l4_server.avg_new_established_conns,"
#  "l7_server.avg_complete_responses,l4_server.max_open_conns")


SERVER_METRICS = ''

DEFAULT_VS_METRICS = ''

DEFAULT_SE_METRICS = 'se_if.avg_bandwidth,se_stats.avg_cpu_usage'

DEFAULT_METRIC_DATA = {
          "header": {
                     "statistics": {
                    "max": 0,
                    "min": 0,
                    "mean": 0,
                    "num_samples": 0
                }
            },
           "data": {"value": 0}
        }

DEFAULT_HS_DATA = {
    'health_score': 100,
    'anomaly_penalty': 0,
    'resources_penalty': 0,
    'performance_score': 100,
    'security_penalty': 0
}

DEFAULT_DOWN_STATE = {
    'oper_status': {
        'state': 'OPER_INACTIVE'
    }
}

DEFAULT_NULL_SERVER = '0.0.0.0'
DEFAULT_NULL_SERVER_STATE = {
    'oper_status': {
        'state': 'OPER_UNAVAIL',
        'reason': ["Server resolution is incomplete"]
    }
}

DEFAULT_RESOURCE_LIST = ['alert', 'runtime', 'metrics', 'health_score']

def get_server_pool_info(pool_uuids=[]):
    ''' 
    pool_uuids = list of pool uuids
    server_count = total count of servers in all pool_uuids
    uuid_server_count_dict = dict {pool_uuid : server_count of the pool,...}
    '''

    server_count = 0
    uuid_server_count_dict = {}
    pool_uuids = tuple(map(str,pool_uuids))
    if not pool_uuids:return server_count,uuid_server_count_dict
    # in case of len(pool_uuids) == 1 ; pool_uuids equals ("pool-uuid",) , which throws an error in postgres in raw query
    # when len(pool_uuids) >1 ; pool_uuids = ("uuid-1","uuid-2","uuid-3") which is acceptable in a raw query
    if len(pool_uuids)>1:
        query = "select id,uuid,coalesce(json_array_length(json_data->'servers'),0) as servers from api_pool where uuid in {};".format(pool_uuids)
    else:
        query = "select id,uuid,coalesce(json_array_length(json_data->'servers'),0) as servers from api_pool where uuid = '{}';".format(pool_uuids[0])
    servers = Pool.objects.raw(query)
    for rec in servers:
        server_count += rec.servers
        uuid_server_count_dict[rec.uuid]=rec.servers
    return server_count,uuid_server_count_dict

class InventoryCommonView(views.CommonView):
    def __init__(self, model_details, *args, **kwargs):
        """
        skip_hs: Some inventory APIs do not have health-score. These
        apis will set the skip_hs to True in their derived classes.
        """
        super(InventoryCommonView, self).__init__(*args, **kwargs)
        self.has_metrics = False
        for view_name in model_details:
            setattr(self, view_name, model_details.get(view_name))

        self.db_cache = None
        self.vs_state_db_cache = None
        self.server_state_db_cache = None
        self.healthscore_view = None
        self.m_view = None
        self.resource_list = DEFAULT_RESOURCE_LIST
        self.hs_data = {}
        self.single_view = False
        self.skip_hs = False

    def _db_cache(self):
        if not self.db_cache:
            self.db_cache = DbCache()
        return self.db_cache

    @api_perf
    def _vs_state_db_cache(self):
        if not self.vs_state_db_cache:
            self.vs_state_db_cache = VirtualServiceStateDBCache()
        return self.vs_state_db_cache

    @api_perf
    def _server_state_db_cache(self):
        if not self.server_state_db_cache:
            self.server_state_db_cache = ServerStateDBCache()
        return self.server_state_db_cache

    def _need_realtime_hs(self, query_params):
        step = query_params.get('step', 300)
        if int(step) <= 5:
            return True
        else:
            return False

    def initialize_view(self, view_class, request, view_args, view_kargs):
        """
        Initialize a view object
        """
        view_obj = view_class()
        view_obj.initial(request, *view_args, **view_kargs)
        view_obj.request = request
        view_obj.args = view_args
        view_obj.kwargs = view_kargs
        return view_obj

    def get_view_data(self, view_class, request, *args, **kwargs):
        """
        Initialize the object GET view and return response
        """
        view_obj = self.initialize_view(view_class, request, args, kwargs)
        return view_obj.get(request, *args, **kwargs)

    def clean_config_view_params(self, request, kwargs):
        """
        Remove non-db request parameters in config view
         . Remove 'duration', it's for metrics & alert data
        """
        kwargs['skip_query_params'] = True
        if 'custom_params' not in kwargs:
            custom_params = request.QUERY_PARAMS.dict().copy()
            kwargs['custom_params'] = custom_params
        else:
            custom_params = kwargs['custom_params']
        custom_params.pop('duration', None)
        custom_params.pop('include', None)
        custom_params.pop('skip_se', None)
        return

    def get_resource_list(self, request):
        """
        This function uses the request.query and extracts the
        parameters to be queried. Typically it will be config,
        runtime and health_score.  This retrieval over-rides
        the base class resource-list.  If skip_hs is set to
        True, then we remove the health_score related attributes
        from the resource-list.

        From a typical URL:
        GET /api/gslbservice-inventory/?include_name&step=300&
        limit=72&sort=name&page_size=30&page=1&include=config
        %2Cruntime%2Chealth_score&
        """
        s = request.QUERY_PARAMS.get('include')
        if s:
            self.resource_list = s.split(',')
            if self.skip_hs:
                for key in ['health_score', '-health_score']:
                    try:
                        self.resource_list.remove(key)
                    except ValueError:
                        pass
        return

    def get_health_score_data(self, obj_uuid, request, custom_params=None,
                              use_model_type=None):
        if use_model_type:
            model_type = use_model_type.lower()
        else:
            model_type = self.model_type.lower()
        hs_kwargs = {'slug': obj_uuid,
                     'metrics_entity_type': model_type,
                     'skip_references':True,
                     'permission': "PERMISSION_VIRTUALSERVICE"
                     }
        hs_args = []

        if model_type == 'pool':
            hs_view = PoolHealthScoreView()
        else:
            hs_view = HealthScoreView()
        hs_view.initial(request, *hs_args, **hs_kwargs)

        if custom_params:
            params = custom_params
        else:
            params = request.QUERY_PARAMS
        try:
            #view return json, need to call internal methods
            hs_view.tenant = self.tenant
            hs_view.allowed_tenants = self.allowed_tenants
            hs_view.tenant_uuids = self.tenant_uuids
            entity_type = model_type.lower()
            result_pb, rc, format_type, cache_expiry = hs_view.get_entity_analytics(
                                            params, entity_type, obj_uuid,
                                             request, *hs_args, **hs_kwargs)

            return result_pb
        except Exception as e:
            log.exception(e)
            log.exception('Fail to get health score of %s uuid=%s',
                          model_type, obj_uuid)
            return None

    @api_perf
    def get_collection_healthscore(self, request, obj_type, uuids):
        """
        Get average or realtime score of a list of uuids
        """
        if not uuids:
            return {}
        realtime = self._need_realtime_hs(request.QUERY_PARAMS)

        if realtime:
            custom_params = REALTIME_HS_PARAMS
        else:
            custom_params = AVERAGE_HS_PARAMS

        obj_uuid = ','.join(uuids)

        hs_pb = self.get_health_score_data(obj_uuid, request,
                                           custom_params,
                                           use_model_type=obj_type)
        data = {}
        if not hs_pb:
            log.error('Empty group healthscores for %s %s' % (obj_type, uuids))
            return {}

        for pb in hs_pb.series:
            if obj_type.lower() == 'pool':
                uuid = pb.header.pool_uuid
            else:
                uuid = pb.header.entity_uuid

            if not uuid:
                log.error('entity uuid not found in healthscore pb')
                log.error(pb)
            if realtime:
                hs_data = self.parse_health_scores(pb, None,
                                                   include_series=False)
            else:
                hs_data = self.parse_health_scores(None, pb,
                                                   include_series=False)
            data[uuid] = hs_data

        for uuid in uuids:
            if uuid not in data:
                log.warning('Health score not found for %s, use default' % uuid)
                data[uuid] = DEFAULT_HS_DATA.copy()

        return data

    def get_health_score_list(self, request, sort_field):
        if sort_field not in ['health_score', '-health_score']:
            raise DataException('Invalid sort field %s,'
                                  ' supported healthscore sort field '
                                  'are health_score and -health_score'
                                   % sort_field)
        model_type = self.model_type.lower()

        if self._need_realtime_hs(request.QUERY_PARAMS):
            hs_params = REALTIME_HS_PARAMS.copy()
            if sort_field=='health_score':
                hs_params['order_series_by'] = 'last_sample'
            else:
                hs_params['order_series_by'] = '-last_sample'
        else:
            hs_params = AVERAGE_HS_PARAMS.copy()
            if sort_field=='health_score':
                hs_params['order_series_by'] = 'mean'
            else:
                hs_params['order_series_by'] = '-mean'

        hs_kwargs = {'slug': '*',
                     'metrics_entity_type': model_type,
                     'skip_references':True,
                     'permission': "PERMISSION_VIRTUALSERVICE",
                     }
        hs_args = []
        if model_type == 'pool':
            hs_view = PoolHSListSortByView()
        else:
            hs_view = HealthScoreView()
        hs_view.initial(request, *hs_args, **hs_kwargs)

        try:
            hs_view.tenant = self.tenant
            hs_view.allowed_tenants = self.allowed_tenants
            hs_view.tenant_uuids = self.tenant_uuids
            entity_type = model_type
            hs_pb, rc, format_type, cache_expiry = hs_view.get_entity_analytics(
                                            hs_params, entity_type, "*",
                                             request, *hs_args, **hs_kwargs)
            return hs_pb
        except Exception:
            log.exception('Fail to get health score list of %s' %
                      self.model_type)
            return None

    def parse_health_scores(self, rt_hs, avg_hs, include_series=True):
        if isinstance(rt_hs, dict):
            return rt_hs
        if isinstance(avg_hs, dict):
            return avg_hs
        data = DEFAULT_HS_DATA.copy()
        if rt_hs:
            if include_series and (not rt_hs.series):
                #log.info('Realtime healthscore pb has no series data')
                return data
            if include_series:
                data_points = rt_hs.series[0].data
            else:
                data_points = rt_hs.data
            if not data_points:
                log.error('Empty data: '+str(rt_hs))
                return data
            last_data = data_points[-1]
            data['health_score'] = last_data.value
            data['anomaly_penalty'] =  last_data.anomaly_penalty
            data['resources_penalty'] = \
                last_data.resources_penalty
            data['performance_score'] = \
                            last_data.performance_value
            data['security_penalty'] =  last_data.security_penalty
        elif avg_hs:
            if include_series:
                if not avg_hs.series:
                    log.error('Healthscore has no series ')
                    return data
                header = avg_hs.series[0].header
            else:
                header = avg_hs.header
            data['health_score'] = \
                        header.statistics.mean
            if header.anomaly_penalty_statistics:
                data['anomaly_penalty'] = \
                        header.anomaly_penalty_statistics.mean
            if header.resources_penalty_statistics:
                data['resources_penalty'] = \
                        header.resources_penalty_statistics.mean
            if header.performance_score_statistics:
                data['performance_score'] = \
                        header.performance_score_statistics.mean
            if header.security_penalty_statistics:
                data['security_penalty'] =  header.security_penalty_statistics.mean

        return data

    def parse_config_data(self, config_data):
        return config_data

    def get_agg_metric_data(self, request, entity_uuid, m_kwargs,
                            query_params):
        '''
        @param request: request object from django
        @param entity_uuid: it is set to the particular entity or * depending
            on the sort criteria from UI caller.
        @param m_kwargs: kwargs args that needs to be passed to metrics apis
        @param query_params: query parameters parsed from the request and
            modified for fetching metrics.
        '''
        model_type = self.model_type.lower()
        #query_params['dimension_aggregation'] = 'all'
        query_params['detailed_header'] = "True"
        m_args = []
        result_dict = {}
        try:
            result_dict, _, _, _ = \
                self.m_view.get_entity_analytics(
                    query_params, model_type, entity_uuid, request, *m_args,
                    **m_kwargs)
        except:
            log.exception('Fail to get metric of %s uuid=%s',
                          model_type, entity_uuid)
            log.error('%s', traceback.format_exc())
            return {}

        if not result_dict.get('series'):
            log.warning("Aggregation metrics data has no series data q %s",
                        query_params)
            # TODO: return rightaway?
            return {}
        series_data = result_dict.pop('series')
        result = {}
        for s in series_data:
            header = s.get('header')
            if not header:
                continue
            obj_uuid = header.get('entity_uuid')
            if not obj_uuid:
                log.error('entity_uuid not found in metrics data header: %s',
                          header)
                continue
            if obj_uuid not in result:
                result[obj_uuid] = {}
            name = header.get('name')
            data = s.get('data', [{'value': None}])[-1]
            value = data['value']
            result[obj_uuid][name] = {}
            result[obj_uuid][name]['value'] = value
            if 'timestamp' in data:
                result[obj_uuid][name]['timestamp'] = data['timestamp']
        return result

    def get_curr_metric_data(self, request, entity_uuid, m_kwargs,
                             query_params):
        '''
        @param request: request object from django
        @param entity_uuid: it is set to the particular entity or * depending
            on the sort criteria from UI caller.
        @param m_kwargs: kwargs args that needs to be passed to metrics apis
        @param query_params: query parameters parsed from the request and
            modified for fetching metrics.
        '''
        model_type = self.model_type.lower()
        if 'dimension_aggregation' in query_params:
            query_params.pop('dimension_aggregation')
        if 'page' in query_params:
            query_params.pop('page')
        if 'page_size' in query_params:
            query_params.pop('page_size')
        query_params['limit'] = '1'
        result = {}
        # limit & step are passed from request
        m_args = []
        try:
            sample_dict, _, _, _ = \
                self.m_view.get_entity_analytics(
                    query_params, model_type, entity_uuid, request,
                    *m_args, **m_kwargs)
        except Exception:
            log.exception('Fail to last sample of of entity %s',
                          entity_uuid)
            return result
        if not sample_dict or not sample_dict.get('series'):
            log.warning("metrics last sample data has no 'series' data %s",
                        sample_dict)
            return result

        series_data = sample_dict.pop('series')
        for s in series_data:
            header = s.get('header')
            if not header:
                continue
            obj_uuid = header.get('entity_uuid')
            if obj_uuid not in result:
                result[obj_uuid] = {}

            name = header.get('name')
            result[obj_uuid][name] = {}
            data = s.get('data')
            if not data:
                result[obj_uuid][name] = {'value': None, 'is_null': True,
                         'timestamp:': None}
            else:
                result[obj_uuid][name]['value'] = data[-1]['value']
                result[obj_uuid][name]['timestamp'] = data[-1]['timestamp']
        return result

    @api_perf
    def get_metric_data(self, request, obj_uuid=None):
        """
        This is bulk metrics calls to get the metrics for all the entities
        or single one to populate values in the inventory call.
        Get a map of obj uuid to stats & last sample metrics
        @param: request: django request object.
        """
        if not self.has_metrics:
            return {}
        if obj_uuid:
            entity_uuid = obj_uuid
        else:
            entity_uuid = '*'
        model_type = self.model_type.lower()
        m_kwargs = {'slug': entity_uuid,
                    'metrics_entity_type': model_type,
                    'skip_references': True,
                    'permisison': "PERMISSION_VIRTUALSERVICE"
                    }
        if model_type == 'pool':
            m_view = PoolMetricsView()
            m_kwargs['pool_uuid'] = '*'
        else:
            m_view = MetricsQueryView()
        m_args = []
        m_view.initial(request, *m_args, **m_kwargs)
        m_view.tenant = self.tenant
        m_view.allowed_tenants = self.allowed_tenants
        m_view.tenant_uuids = self.tenant_uuids
        self.m_view = m_view
        query_params = request.QUERY_PARAMS.dict()
        if 'metric_id' not in query_params:
            if model_type in ('pool', 'virtualservice'):
                query_params['metric_id'] = DEFAULT_VS_METRICS
            elif model_type in ('serviceengine'):
                query_params['metric_id'] = DEFAULT_SE_METRICS

        if 'dimension_aggregation' in request.QUERY_PARAMS:
            dim = request.QUERY_PARAMS['dimension_aggregation']
            if dim.lower().strip().endswith('all'):
                raise Exception('Metrics dimension aggregation all not '
                                'supported in inventory API call %s', dim)
            if dim.find('sum') != -1:
                metric_ids = query_params['metric_id'].split(',')
                metric_ids = \
                    [m for m in metric_ids
                        if not mglobals().pb_utils.is_metric_sum_agg_invalid(m)]
                query_params['metric_id'] = string.join(metric_ids, sep=',')
            result = self.get_agg_metric_data(request, entity_uuid, m_kwargs,
                                              query_params)
        else:
            result = self.get_curr_metric_data(request, entity_uuid, m_kwargs,
                                               query_params)

        return result

    def get_missing_metric_data(self, request, uuid, obj_data):
        # will call a function to return default structure
        metrics_id_s = request.QUERY_PARAMS.get('metric_id')
        if not metrics_id_s:
            if self.model_type.lower() in ('pool', 'virtualservice'):
                metrics_id_s = DEFAULT_VS_METRICS
            elif self.model_type.lower() in ('serviceengine'):
                metrics_id_s = DEFAULT_SE_METRICS
        metric_ids = metrics_id_s.split(',')
        data = obj_data['metrics']
        for metric_id in metric_ids:
            if not metric_id:
                continue
            if metric_id in data:
                continue
            data[metric_id] = {}
            data[metric_id]['value'] = 0
            data[metric_id]['is_null'] = True
            if not request.QUERY_PARAMS.get('dimension_aggregation'):
                data[metric_id]['timestamp'] = None
        return data

    def get_runtime_data(self, obj_uuid, request):
        if not obj_uuid:
            return
        if obj_uuid.startswith('virtualservice'):
            cache =  VirtualServiceStateDBCache()
        elif obj_uuid.startswith('pool'):
            cache =  PoolStateDBCache()
        elif obj_uuid.startswith('se'):
            cache = ServiceEngineStateDBCache()
        else:
            cache = self.runtime_cache()

        #Force to use RPC for inventory data of one object
        state_pb = cache.getState(obj_uuid)
        if state_pb:
            summary_pb = state_pb.summary
            return protobuf2dict_withrefs(summary_pb, request)
        else:
            return None

    def get_runtime_data_json(self, obj_uuids, request):
        if not obj_uuids:
            return []
        def _table_name(uuid):
            if uuid.startswith('virtualservice'):
                return 'virtualservice'
            elif uuid.startswith('pool'):
                return 'pool'
            elif uuid.startswith('se'):
                return 'serviceengine'
            else:
                return None

        sdb_cache = StateDBCacheApi()
        table = _table_name(obj_uuids[0])
        if table:
            objs = sdb_cache.getStates(obj_uuids, pb_name=table)
            if objs:
                return [protobuf2dict_withrefs(obj.summary, request) for obj in objs]

        return []

    def add_extra_data(self, result, obj_data, request, *args, **kwargs):
        pass

    def add_metric_data(self, request, uuid, obj_data):
        obj_data['metrics'] = {}
        if hasattr(self, 'metric_data') and self.metric_data:
            if uuid in self.metric_data:
                obj_data['metrics'] = self.metric_data[uuid]

        self.get_missing_metric_data(request, uuid, obj_data)

    def get_data_for_one_object(self, config_data, request, runtime_data,
                                *args, **kwargs):
        obj_data = dict()
        obj_data['config'] = self.parse_config_data(config_data)
        if runtime_data is not None:
            # For cloud-inventory, runtime_data is None
            obj_data['runtime'] = runtime_data
        uuid = config_data['uuid']
        obj_data['uuid'] = uuid
        if 'health_score' in self.resource_list:
            if self.hs_data and uuid in self.hs_data:
                obj_data['health_score'] = self.hs_data[uuid]
            else:
                if self._need_realtime_hs(request.QUERY_PARAMS):
                    rt_hs_pb = self.get_health_score_data(uuid, request,
                                                            REALTIME_HS_PARAMS)
                    obj_hs = self.parse_health_scores(rt_hs_pb, None)
                else:
                    avg_hs_pb = self.get_health_score_data(uuid, request,
                                                            AVERAGE_HS_PARAMS)
                    obj_hs = self.parse_health_scores(None, avg_hs_pb)
                obj_data['health_score'] = obj_hs

        self.add_extra_data(obj_data, config_data, request, *args, **kwargs)

        if self.has_metrics and 'metrics' in self.resource_list:
            self.add_metric_data(request, uuid, obj_data)
        return obj_data

    @api_perf
    def get_alert_data(self, object_uuid, request, *args, **kwargs):
        data = {'low':0, 'medium':0, 'high':0}
        contain_uuid = "%s," % object_uuid
        p = {'related_refs__contains': contain_uuid}
        model_name = get_obj_type_name_from_uuid(contain_uuid)
        if model_name == 'serviceengine':
            p['event_pages__contains'] = 'EVENT_PAGE_SE'
        if model_name == 'virtualservice':
            p['event_pages__contains'] = 'EVENT_PAGE_VS'
        if model_name == 'pool':
            p['event_pages__contains'] = 'EVENT_PAGE_POOL'
        duration = None
        if 'duration' in request.QUERY_PARAMS:
            duration = int(request.QUERY_PARAMS['duration'])
        elif 'limit' in request.QUERY_PARAMS and 'step' in request.QUERY_PARAMS:
            duration = (int(request.QUERY_PARAMS['limit']) *
                        int(request.QUERY_PARAMS['step']))

        if duration:
            start, stop = duration_to_start_stop(duration)
            p['timestamp__gte'] = start
            p['timestamp__lte'] = stop

        query = Alert.objects.filter(**p).values('level').annotate(
            count=Count('level')).order_by()

        for alert_count in query:
            a_type = alert_count.get('level', -1)
            if a_type == ALERT_LOW:
                data['low'] = alert_count.get('count', 0)
            elif a_type == ALERT_MEDIUM:
                data['medium'] = alert_count.get('count', 0)
            elif a_type == ALERT_HIGH:
                data['high'] = alert_count.get('count', 0)

        return data

class InventoryListView(InventoryCommonView, views.ListView):
    def __init__(self, model_details, *args, **kwargs):
        super(InventoryListView, self).__init__(model_details, *args, **kwargs)
        self.list_view  = model_details['list_view']

    def get_with_sorted_health_score(self, request, sort_field,
                                        *args, **kwargs):
        model_type = self.model_type.lower()
        #get all objects, no pagination
        list_kwargs = kwargs.copy()

        self.clean_config_view_params(request, list_kwargs)
        list_kwargs['custom_params']['page_size']= -1
        list_kwargs['custom_params']['page'] = 1

        rsp = self.get_view_data(self.list_view, request, *args, **list_kwargs)
        if rsp.status_code != 200:
            return rsp
        config_list = rsp.data['results']
        if not rsp.data.get('count'): #count==0
            return rsp

        #get all hs entries with sorted score
        params = request.QUERY_PARAMS
        hs_list_pb = self.get_health_score_list(request, sort_field)
        if not hs_list_pb:
            return

        obj_full_list = []

        for hs in hs_list_pb.series:
            for config in config_list:
                if model_type == 'pool':
                    hs_uuid = hs.header.pool_uuid
                else:
                    hs_uuid = hs.header.entity_uuid
                if config['uuid'] == hs_uuid:
                    obj_data = {'config_data': config}
                    obj_data['hs'] = hs

                    obj_full_list.append(obj_data)
                    config['has_health_score'] = True
                    break
        #call single heathscore query for the rest config objects,
        #to get default healthscore
        for config in config_list:
            if 'has_health_score' not in config:
                uuid = config['uuid']
                if self._need_realtime_hs(request.QUERY_PARAMS):
                    hs_params = REALTIME_HS_PARAMS.copy()
                else:
                    hs_params = AVERAGE_HS_PARAMS.copy()
                hs_pb = self.get_health_score_data(uuid, request, hs_params)
                obj_data = {'config_data': config}
                if hs_pb.series:
                    obj_data['hs'] = hs_pb.series[0]
                if sort_field.startswith('-'):
                    obj_full_list.insert(0, obj_data)
                else:
                    obj_full_list.append(obj_data)
            else:
                config.pop('has_health_score')
        if 'metrics' in self.resource_list:
            self.metric_data = self.get_metric_data(request)
        page_size = params.get('page_size', api_settings.PAGINATE_BY)

        paginator = Paginator(obj_full_list, page_size)
        data = {'count': paginator.count}
        page_index = params.get('page', 1)
        page = paginator.page(page_index)
        if page.has_next():
            full_uri = request.build_absolute_uri()
            data['next'] = replace_query_param(full_uri, 'page',
                                           page.next_page_number())

        data['results'] = []
        for obj_input in page.object_list:
            obj_data = {}
            if 'config_data' not in obj_input:
                log.error('element in object list has no config data')
                continue
            config_data = obj_input.pop('config_data')
            obj_data['config'] = self.parse_config_data(config_data)
            uuid = config_data['uuid']
            obj_data['uuid'] = uuid
            hs_pb = obj_input.get('hs', None)
            if self._need_realtime_hs(request.QUERY_PARAMS):
                obj_data['health_score'] = self.parse_health_scores(hs_pb, None,
                                                        include_series=False)
            else:
                obj_data['health_score'] = self.parse_health_scores(None, hs_pb,
                                                        include_series=False)
            if 'runtime' in self.resource_list:
                try:
                    obj_data['runtime'] = self.get_runtime_data(uuid, request)
                except Exception as e:
                    log.exception('Runtime view exception: ')
                    obj_data['runtime'] = {'error': str(e)}

            if self.has_metrics and 'metrics' in self.resource_list:
                self.add_metric_data(request, uuid, obj_data)

            self.add_extra_data(obj_data, config_data, request, *args, **kwargs)
            data['results'].append(obj_data)

        rsp = Response(data)
        return rsp

    @api_perf
    def get(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        if self.model_type.lower() != 'cloud':
            self.check_user(request, args, kwargs)

        self.get_resource_list(request)
        sort_field = request.QUERY_PARAMS.get('sort')
        if sort_field and (sort_field.startswith('health_score') or
                           sort_field.startswith('-health_score')):
            #get all health score first & do manual pagination
            return self.get_with_sorted_health_score(request, sort_field,
                                                      *args, **kwargs)
        l_kwargs = kwargs.copy()
        l_kwargs['skip_update_realtime_fields'] = True
        self.clean_config_view_params(request, l_kwargs)
        rsp = self.get_view_data(self.list_view, request, *args, **l_kwargs)
        if rsp.status_code != 200:
            return rsp
        list_data = rsp.data
        data = {'count': list_data['count']}
        if 'next' in list_data:
            data['next'] = list_data['next']

        uuids = []
        for config_data in list_data['results']:
            uuids.append(config_data['uuid'])

        runtime_data = []
        if 'runtime' in self.resource_list:
            runtime_data = self.get_runtime_data_json(uuids, request)
 
        if 'metrics' in self.resource_list:
            obj_uuid = ','.join(uuids)
            self.metric_data = self.get_metric_data(request, obj_uuid=obj_uuid)

        if 'health_score' in self.resource_list:
            self.hs_data = self.get_collection_healthscore(request,
                                                       self.model_type, uuids)

        threads = []
        for (index, config_data) in enumerate(list_data['results']):
            try:
                runtime_data_obj = runtime_data[index]
            except IndexError:
                runtime_data_obj = None
            threads.append(gevent.spawn(self.get_data_for_one_object,
                                        config_data, request,
                                        runtime_data_obj, *args, **kwargs))
        gevent.joinall(threads)
        data['results'] = [thread.value for thread in threads]

        rsp = Response(data)

        return rsp

class InventoryDetailView(InventoryCommonView, views.RetrieveView):
    def __init__(self, model_details, *args, **kwargs):
        super(InventoryDetailView, self).__init__(model_details, *args, **kwargs)
        self.detail_view  = model_details['detail_view']
        self.single_view = True

    def get(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        self.get_resource_list(request)
        rsp = self.get_view_data(self.detail_view, request, *args, **kwargs)
        if rsp.status_code != 200:
            return rsp
        config_data = rsp.data
        uuid = config_data['uuid']

        runtime_data = None
        if 'runtime' in self.resource_list:
            try:
                runtime_data = self.get_runtime_data(uuid, request)
            except Exception as e:
                log.exception('Runtime exception: ')
                runtime_data = {'error': str(e)}

        if 'metrics' in self.resource_list:
            self.metric_data = self.get_metric_data(request,
                                                    obj_uuid=uuid)

        #get healthscore for uuids in this page
        if 'health_score' in self.resource_list:
            self.hs_data = self.get_collection_healthscore(request,
                                                       self.model_type, [uuid])
        obj_data = self.get_data_for_one_object(config_data, request,
                                                runtime_data, *args, **kwargs)
        rsp = Response(obj_data)
        return rsp

class InventorySummaryView(InventoryCommonView, views.ListView):
    def __init__(self, model_details, *args, **kwargs):
        super(InventorySummaryView, self).__init__(model_details, *args, **kwargs)
        self.list_view = model_details['list_view']

    def get(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.get_resource_list(request)
        l_kwargs = kwargs.copy()
        self.clean_config_view_params(request, l_kwargs)
        rsp = self.get_view_data(self.list_view, request, *args, **l_kwargs)
        if rsp.status_code != 200:
            return rsp
        list_data = rsp.data
        data = {'count': list_data['count']}
        if 'next' in list_data:
            data['next'] = list_data['next']
        obj_results = []

        #get healthscore for uuids in this page
        uuids = []
        for config_data in list_data['results']:
            uuids.append(config_data['uuid'])
        self.hs_data = None
        if 'health_score' in self.resource_list:
            self.hs_data = self.get_collection_healthscore(request,
                                                       self.model_type, uuids)

        for config_data in list_data['results']:
            obj_data = dict()
            obj_data['name'] = config_data['name']
            obj_data['uuid'] = config_data['uuid']
            obj_data['url'] = config_data['url']

            if 'health_score' in self.resource_list:
                if self.hs_data and obj_data['uuid'] in self.hs_data:
                    obj_data['health_score'] = self.hs_data[obj_data['uuid']]
                else:
                    if self._need_realtime_hs(request.QUERY_PARAMS):
                        rt_hs_pb = self.get_health_score_data(config_data['uuid'],
                                                    request, REALTIME_HS_PARAMS)
                        avg_hs_pb = None
                    else:
                        avg_hs_pb = self.get_health_score_data(config_data['uuid'],
                                                    request, AVERAGE_HS_PARAMS)
                        rt_hs_pb = None
                    obj_data['health_score'] = self.parse_health_scores(rt_hs_pb,
                                                                        avg_hs_pb)

            if 'runtime' in self.resource_list:
                try:
                    runtime = self.get_runtime_data(config_data['uuid'], request)
                    if not runtime or ('oper_status' not in runtime):
                        raise Exception('Empty runtime data for %s' %
                                        config_data['uuid'])
                    obj_data['oper_status'] = runtime['oper_status']
                except Exception as e:
                    log.exception('Runtime view exception: ')
                    obj_data['oper_status'] = {'error': str(e)}

            self.add_extra_data(obj_data, config_data, request, *args, **kwargs)
            obj_results.append(obj_data)

        data['results'] = obj_results
        rsp = Response(data)

        return rsp

class VirtualServiceInventoryCommon(InventoryCommonView):

    @api_perf
    def get_ssl_cert_data(self, request):
        def _ssl_uri(ssl_uuid, include_name, request):
            return uri_from_slug("SSLKeyAndCertificate",
                                 ssl_uuid,
                                 host=request.get_host(),
                                 include_name=include_name,
                                 name=DbBaseCache.uuid2name(ssl_uuid))
        data = dict()
        now = datetime.utcnow()
        expires_in_one_day = now + timedelta(days=1)
        try:
            ssl_objs = SSLKeyAndCertificate.objects.filter(
                         Q(json_data__certificate__not_after__lt=expires_in_one_day) &
                         Q(json_data__certificate__not_after__gt=now))
        except Exception as e:
            log.error(e)
            return data

        include_name =  ('include_name' in request.QUERY_PARAMS)
        for obj in ssl_objs:
            try:
                ssl_pb = obj.protobuf()
            except:
                continue
            if not ssl_pb.HasField('certificate'):
                continue
            cert = ssl_pb.certificate
            if not cert.HasField("not_after"):
                continue
            ssl_uri = _ssl_uri(ssl_pb.uuid,
                               include_name,
                               request)
            ssl_info = dict()
            ssl_info['uuid'] = ssl_pb.uuid
            ssl_info['uri'] = ssl_uri
            ssl_info['time'] = cert.not_after
            data[ssl_pb.uuid] = ssl_info
        return data

    def parse_config_data(self, config):
        data = {}
        data['name'] = config['name']
        data['uuid'] = config['uuid']
        data['url'] = config['url']
        data['services'] = config.get('services', [])
        data['vip'] = config.get('vip', [])
        data['floating_ip'] = config.get('floating_ip')
        data['pool_ref'] = config.get('pool_ref', '')
        data['pool_group_ref'] = config.get('pool_group_ref')
        data['fqdn'] = config.get('fqdn', '')
        data['dns_info'] = config.get('dns_info', [])
        data['type'] = config.get('type', '')
        data['vh_domain_name'] = config.get('vh_domain_name', '')
        data['tenant_ref'] = config.get('tenant_ref', '')
        data['cloud_ref'] = config.get('cloud_ref')
        data['se_group_ref'] = config.get('se_group_ref')
        data['east_west_placement'] = config.get('east_west_placement', False)
        data['vrf_context_ref'] = config.get('vrf_context_ref', '')
        data['enabled'] = config.get('enabled', '')
        data['waf_policy_ref'] = config.get('waf_policy_ref')
        return data

    @api_perf
    def get_server_faults(self, uuid, vs_sdb_obj, request, *args, **kwargs):
        include_name =  ('include_name' in request.QUERY_PARAMS)
        pool_uuids = [ u for u in vs_sdb_obj.pool_uuids]

        server_cache = self._server_state_db_cache()
        try:
            server_sdb_objs = server_cache.getStates(pool_uuids)
        except:
            log.error('Could not get server states for VS %s, Pools %s', \
                      uuid, pool_uuids)
            return {}

        pool_dict = dict()
        for pool in server_sdb_objs:
            pool_uri = uri_from_slug("pool",
                                     pool.pool_uuid,
                                     host=request.get_host(),
                                     include_name=include_name,
                                     name=DbBaseCache.uuid2name(pool.pool_uuid))
            if pool_uri not in pool_dict:
                pool_dict[pool_uri] = []
            srvr_list = pool_dict[pool_uri]

            # aggregated state of the servers for the pool
            srvrs_dn = []
            for srvr_cfg in pool.config:
                srvr_name = '%s:%d' % \
                            (srvr_cfg.ip_addr.addr,
                             srvr_cfg.port)
                if srvr_cfg.oper_status.state == OPER_DOWN or \
                   not srvr_cfg.is_enabled:
                    srvrs_dn.append(srvr_name)
            #log.info('srvrs_dn : %s' % (srvrs_dn))

            # per SE state of the servers for the pool
            for server in pool.summary:
                srvr_name = '%s:%d' % \
                            (server.ip_addr.addr,
                             server.port)
                if srvr_name in srvrs_dn:
                    #log.info('Server : %s down from all SEs' %
                    #         (srvr_name))
                    continue
                if server.HasField('hostname'):
                    srvr_name = server.hostname
                if (server.oper_status.state != OPER_UP or
                    self.get_test_server_fault_config()):
                    se_uri = uri_from_slug('serviceengine',
                                 server.se_uuid,
                                 host=request.get_host(),
                                 include_name=include_name,
                                 name=DbBaseCache.uuid2name(server.se_uuid))
                    srvr_info = {}
                    for srvr in srvr_list:
                        if srvr['server'] == srvr_name:
                            srvr_info = srvr
                            break
                    if not srvr_info:
                        srvr_info['server'] = srvr_name
                        srvr_info['se_list'] = []
                        srvr_info['description'] = \
                            'Server %s not accessible from Service Engine(s) %s' % \
                            (srvr_name, DbBaseCache.uuid2name(server.se_uuid))
                        srvr_info['se_list'].append(se_uri)
                        srvr_list.append(srvr_info)
                    else:
                        if se_uri not in srvr_info['se_list']:
                            srvr_info['se_list'].append(se_uri)
                            srvr_info['description'] = \
                                srvr_info['description'] + \
                                ', %s' % (DbBaseCache.uuid2name(server.se_uuid))

        #log.info('pool_dict : %s' % (pool_dict))
        srvr_in_err = False
        pool_info = []
        for pool, srvr_list in pool_dict.iteritems():
            if srvr_list and not srvr_in_err:
                srvr_in_err = True
            if not srvr_list:
                continue
            p_info = {}
            p_info['pool_ref'] = pool
            p_info['servers'] = srvr_list
            pool_info.append(p_info)

        if not srvr_in_err:
            return []
        return pool_info

    @api_perf
    def get_scaleoutin_faults(self, uuid, vs_sdb_obj, request, *args, **kwargs):

        scaleout_fault = list()
        if not vs_sdb_obj:
            return scaleout_fault

        vs_runtime = vs_sdb_obj.summary
        if not vs_runtime:
            return scaleout_fault

        if vs_runtime.east_west:
            return scaleout_fault

        for vip_summary in vs_runtime.vip_summary:
            if vip_summary.oper_status and vip_summary.oper_status.state != OPER_UP:
                continue
            if (vip_summary.migrate_in_progress or
                    vip_summary.scalein_in_progress or
                    vip_summary.scaleout_in_progress or
                    vip_summary.user_scaleout_pending):
                # Transient state. So assume no issues
                continue

            if vip_summary.num_se_requested > \
                vip_summary.num_se_assigned or \
                    self.get_test_scaleout_fault_config():
                fault = dict()
                if vip_summary.HasField('scale_status') and len(vip_summary.scale_status.reason):
                        fault['scale_status'] = vip_summary.scale_status.reason[0]
                fault['description'] = \
                    'Virtual Service (vip_id %s) needs %d Services Engines for High Availability. ' \
                    'Currently only %d Service Engine(s) available. Reason:%s'\
                    % (vip_summary.vip_id, vip_summary.num_se_requested, vip_summary.num_se_assigned,
                       fault.get('scale_status', ''))
                fault['vip_id'] = vip_summary.vip_id
                fault['num_se_requested'] = vip_summary.num_se_requested
                fault['num_se_assigned'] = vip_summary.num_se_assigned

                scaleout_fault.append(fault)

        # AV-27251
        if vs_runtime.oper_status.state == OPER_UP:
            for se in vs_sdb_obj.se:
                if se.summary.oper_status.state == OPER_INITIALIZING:
                    fault = dict()
                    fault['description'] = \
                        'Virtual Service (vip_id %s) not ready on Service Engine %s. Reason:%s' \
                        % (se.vip_id, DbBaseCache.uuid2name(se.se_uuid), se.summary.oper_status.reason[0])
                    fault['vip_id'] = se.vip_id
                    fault['se_uuid'] = se.se_uuid
                    scaleout_fault.append(fault)

        return scaleout_fault

    @api_perf
    def get_ssl_cert_expiry_faults(self, uuid, request, *args, **kwargs):
        def _retrieve_expiry_status_str(enum):
            return SSLCertificateExpiryStatus.DESCRIPTOR.\
                   values_by_number[enum].name

        def _datetime_from_str(date_s):
            return datetime.strptime(date_s, "%Y-%m-%d %H:%M:%S")

        ssl_info = []
        db_cache = self._db_cache()
        ssl_key_refs = db_cache.get_children('VirtualService',
                                    uuid=uuid, model_filter=['SSLKeyAndCertificate'])
        # retrieve the test conditions
        test_enabled, cond = self.get_test_ssl_cert_fault_config()
        #log.info('SSL Key and Certs : %s' % (sslkeyandcert_list))
        now = datetime.utcnow()
        for ssl_key_ref in ssl_key_refs:
            ssl_uuid = ssl_key_ref.uuid
            if ssl_uuid in self.ssl_cert_data:
                info = self.ssl_cert_data[ssl_uuid]
                cert_not_after = _datetime_from_str(info['time'])
                if ((cert_not_after <= now) or
                    (test_enabled and cond == 'expired')):
                    ssl_dict = dict()
                    ssl_dict['name'] = DbBaseCache.uuid2name(ssl_uuid)
                    ssl_dict['uri'] = info['uri']
                    ssl_dict['STATUS'] = \
                        _retrieve_expiry_status_str(SSL_CERTIFICATE_EXPIRED)
                    ssl_dict['time'] = info['time']
                    ssl_dict['description'] = '%s expired at %s' % \
                        (ssl_dict['name'],ssl_dict['time'])
                    ssl_info.append(ssl_dict)
                elif (((cert_not_after - now) <=
                        timedelta(days=1)) or
                       (test_enabled and cond == 'expiring')):
                    ssl_dict = dict()
                    ssl_dict['name'] = DbBaseCache.uuid2name(ssl_uuid)
                    ssl_dict['uri'] = info['uri']
                    ssl_dict['STATUS'] = \
                        _retrieve_expiry_status_str(SSL_CERTIFICATE_EXPIRY_WARNING)
                    ssl_dict['time'] = info['time']
                    ssl_dict['description'] = '%s expiring at %s' % \
                        (ssl_dict['name'],ssl_dict['time'])
                    ssl_info.append(ssl_dict)
        return ssl_info

    @api_perf
    def get_debug_trace_status(self, uuid, request, *args, **kwargs):
        # retrieve the test conditions
        capture_test = False
        trace_test = False
        test_enabled, flags = self.get_test_debug_fault_config()
        if test_enabled:
            if 'capture' in flags:
                capture_test = True
            if 'trace' in flags:
                trace_test = True

        d_list = list()
        ds = Datastore()
        vs = ds.get(db_table_name_from_pb(
                                    VirtualServiceProto()),
                                uuid)
        if vs:
            vs_runtime = vs['runtime']
            if vs_runtime.HasField('datapath_debug'):
                if (vs_runtime.datapath_debug.capture or
                    capture_test):
                    d_dict = dict()
                    d_dict['name'] = 'Packet capture'
                    d_dict['packet_capture'] = True
                    d_dict['description'] = 'Packet capture enabled'
                    d_list.append(d_dict)
                if (len(vs_runtime.datapath_debug.flags) or
                    trace_test):
                    d_dict = dict()
                    d_dict['name'] = 'Datapath debugs'
                    d_dict['debug_flags'] = True
                    d_dict['description'] = 'Datapath debugs enabled'
                    d_list.append(d_dict)
        return d_list

    def set_fault_test_config(self):
        # for fault simulation. If /home/admin/fault.json
        # is not present then ignore
        config = {}
        self.test_config = {}
        try:
            fault_simulation_file = '/home/admin/fault.json'
            with open( fault_simulation_file, 'r' ) as f:
                config = ujson.load(f)
        except Exception:
            config = {}

        if config and 'vs_faults' in config:
            self.test_config = config.get('vs_faults')

    def get_test_server_fault_config(self):
        if self.test_config:
            if 'server_faults' in self.test_config:
                return self.test_config['server_faults']
        return False

    def get_test_ssl_cert_fault_config(self):
        if self.test_config:
            if ('ssl_cert_faults' in self.test_config and
                'status' in self.test_config['ssl_cert_faults']):
                return True, self.test_config['ssl_cert_faults']['status']
        return False, ''

    def get_test_debug_fault_config(self):
        if self.test_config:
            if 'debugs' in self.test_config:
                return True, self.test_config['debugs']
        return False, ''

    def get_test_scaleout_fault_config(self):
        if self.test_config:
            if 'scaleout' in self.test_config:
                return self.test_config['scaleout']
        return False

    @api_perf
    def check_debug_for_children(self, uuid, request, args, kwargs):
        db_cache = self._db_cache()
        children = db_cache.get_parents('VirtualService',
                                        uuid=uuid,
					model_filter=['VirtualService'],
					depth=1,
					prune_criteria=0)
        child_capture_on = False
        d_dict = dict()
        for child in children:
            debug_list = self.get_debug_trace_status(child.uuid,
                                                    request,
                                                    args,
                                                    kwargs)
            for debug_dict in debug_list:
                if "packet_capture" in debug_dict:
                    child_capture_on = True
                    d_dict['name'] = 'Packet capture'
                    d_dict['packet_capture'] = True
                    d_dict['description'] = 'Packet capture enabled on child '+child.uuid
                    break
            if child_capture_on:
                break
        return d_dict

    @api_perf
    def get_faults(self, uuid, request, *args, **kwargs):
        self.set_fault_test_config()
        fault_dict = dict()

        vs_cache = self._vs_state_db_cache()
        try:
            vs_sdb_obj = vs_cache.getState(uuid, force_no_rpc=True)
        except:
            log.error('Could not get vs state for %s', uuid)
            vs_sdb_obj = None

        if vs_sdb_obj:
            if vs_sdb_obj.summary.oper_status.state == OPER_UP:
                pool_list = self.get_server_faults(uuid,
                                           vs_sdb_obj,
                                           request,
                                           args,
                                           kwargs)
                if pool_list:
                    fault_dict['server_faults'] = pool_list

                scaleout_list = self.get_scaleoutin_faults(
                                           uuid,
                                           vs_sdb_obj,
                                           request,
                                           args,
                                           kwargs)
                if scaleout_list:
                    fault_dict['scaleout'] = scaleout_list

        ssl_dict = self.get_ssl_cert_expiry_faults(uuid,
                                           request,
                                           args,
                                           kwargs)
        if ssl_dict:
            fault_dict['ssl_cert_faults'] = ssl_dict
        debug_list = self.get_debug_trace_status(uuid,
                                           request,
                                           args,
                                           kwargs)
        child_debug_dict = self.check_debug_for_children(uuid,
                                                    request,
                                                    args,
                                                    kwargs)
        if child_debug_dict:
            add_it = True
            for debug_dict in debug_list:
                if "packet_capture" in debug_dict:
                    add_it = False
            if add_it:
                debug_list.append(child_debug_dict)
        if debug_list:
            fault_dict['debug'] = debug_list
        return fault_dict

    def merge_vip_into_runtime(self, runtime, obj_data):
        for r_vip in runtime.get('vip_summary', []):
            vip_id = r_vip['vip_id']
            for vip in obj_data.get('vip', []):
                if vip['vip_id'] == vip_id:
                    r_vip.update(vip)


    def add_extra_data(self, result, obj_data, request, *args, **kwargs):
        if 'alert' in self.resource_list:
            result['alert'] = self.get_alert_data(obj_data.get('uuid'), request,
                                              *args, **kwargs)
        result['pools'] = []
        result['poolgroups'] = []

        pool_uuids = []
        pool_ref = obj_data.get('pool_ref', '')
        if pool_ref:
            p_uuid = os.path.basename(pool_ref)
            if '#' in p_uuid:
                p_uuid = p_uuid.split('#')[0]
            pool_uuids.append(p_uuid)

        db_cache = self._db_cache()
        pool_refs = db_cache.get_children('VirtualService',
                                    uuid=obj_data['uuid'], model_filter=['Pool'])
        for pool_ref in pool_refs:
            p_uuid = pool_ref.uuid
            if p_uuid and p_uuid not in pool_uuids:
                pool_uuids.append(p_uuid)

        for p_uuid in pool_uuids:
            include_name =  ('include_name' in request.QUERY_PARAMS)
            if include_name:
                p_name = DbBaseCache.uuid2name(p_uuid)
                if not p_name:
                    names = Pool.objects.filter(uuid=p_uuid).values('name')
                    if names:
                        p_name = names[0]['name']
            else:
                p_name = ''
            #Webapp & nginx won't work when import use url_utils
            p_ref = '/api/pool/%s' % p_uuid
            if include_name and p_name:
                p_ref = p_ref + '#%s' % p_name
            result['pools'].append(p_ref)

        pg_refs = db_cache.get_children('VirtualService',
                                    uuid=obj_data['uuid'], model_filter=['PoolGroup'])
        for pg_ref in pg_refs:
            pg_uuid = pg_ref.uuid
            pg_name = ''
            include_name = 'include_name' in request.QUERY_PARAMS
            if include_name:
                pg_name = DbBaseCache.uuid2name(pg_uuid)
                if not pg_name:
                    names = PoolGroup.objects.filter(uuid=pg_uuid).values('name')
                    if names:
                        pg_name = names[0]['name']

            poolgroup_ref = '/api/poolgroup/%s' % pg_uuid
            if include_name and pg_name:
                poolgroup_ref = poolgroup_ref + '#%s' % pg_name
            result['poolgroups'].append(poolgroup_ref)

        app_ref = obj_data.get('application_profile_ref', '')
        app_uuid = slug_from_uri(app_ref)
        app_prof = ApplicationProfile.objects.get(uuid=app_uuid)
        result['app_profile_type'] = app_prof.json_data.get('type')
        result['has_pool_with_realtime_metrics'] = True if Pool.objects.filter(uuid__in=pool_uuids, json_data__analytics_policy__enable_realtime_metrics=True).exists() else False
        # Only get faults for Non E/W VS
        if not obj_data.get('east_west_placement'):
            try:
                # append vs pool server state
                result['faults'] = self.get_faults(obj_data.get('uuid'), request,
                                                  *args, **kwargs)
            except:
                log.error('%s', traceback.format_exc())

        ##runtime needs vip info
        if 'runtime' in self.resource_list and 'runtime' in result:
            self.merge_vip_into_runtime(result['runtime'], obj_data)
        if obj_data.get('type', '') == 'VS_TYPE_VH_CHILD':
            vs_parent_uuid = slug_from_uri(
                                obj_data.get('vh_parent_vs_ref', ''))
            parent_obj = VirtualService.objects.filter(uuid=vs_parent_uuid).first()
            if parent_obj:
                vsvip = VsVip.objects.filter(uuid=parent_obj.vsvip_ref).first()
                if vsvip:
                    result['parent_vs_vip'] = VsVipSerializer(vsvip,
                                                context={'request': request}).data.get('vip', [])


class VirtualServiceListInventoryView(VirtualServiceInventoryCommon, InventoryListView):
    def __init__(self, *args, **kwargs):
        model_details = {
            'model_type': 'VirtualService',
            'list_view': views_vs_pool.VirtualServicePoolList,
            'runtime_cache': VirtualServiceStateDBCache,
            'has_metrics': True
        }
        self.ssl_cert_data = {}
        super(VirtualServiceListInventoryView, self).__init__(
                                                model_details, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.ssl_cert_data = self.get_ssl_cert_data(request)
        return super(VirtualServiceListInventoryView, self).get(
                                                request, *args, **kwargs)

class VirtualServiceDetailInventoryView(VirtualServiceInventoryCommon, InventoryDetailView):
    def __init__(self, *args, **kwargs):
        model_details = {
            'model_type': 'VirtualService',
            'detail_view': views_vs_pool.VirtualServicePoolDetail,
            'runtime_cache': VirtualServiceStateDBCache,
            'has_metrics': True
        }
        self.ssl_cert_data = {}
        super(VirtualServiceDetailInventoryView, self).__init__(
                                                model_details, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.ssl_cert_data = self.get_ssl_cert_data(request)
        return super(VirtualServiceDetailInventoryView, self).get(
                                                request, *args, **kwargs)

class VirtualServiceSummaryInventoryView(VirtualServiceInventoryCommon, InventorySummaryView):
    def __init__(self, *args, **kwargs):
        model_details = {
            'model_type': 'VirtualService',
            'list_view': views_vs_pool.VirtualServicePoolList,
            'runtime_cache': VirtualServiceStateDBCache
        }
        self.ssl_cert_data = {}
        super(VirtualServiceSummaryInventoryView, self).__init__(
                                                model_details, *args, **kwargs)

    def add_extra_data(self, result, obj_data, request, *args, **kwargs):
        super(VirtualServiceSummaryInventoryView, self).add_extra_data(result,
                                                            obj_data, request,
                                                            *args, **kwargs)
        result['vip'] = obj_data.get('vip')
        result['waf_policy_ref'] = obj_data.get('waf_policy_ref')
        result['floating_ip'] = obj_data.get('floating_ip')
        result['fqdn'] = obj_data.get('fqdn', '')
        result['east_west_placement'] = obj_data.get('east_west_placement', False)

class PoolInventoryCommon(InventoryCommonView):
    connected_vs = None
    def parse_config_data(self, config):
        data = {}
        data['name'] = config['name']
        data['uuid'] = config['uuid']
        data['url'] = config['url']
        data['num_servers'] = len(config.get('servers', []))
        if 'default_server_port' in config:
            data['default_server_port'] = config['default_server_port']
        data['tenant_ref'] = config.get('tenant_ref', '')
        data['cloud_ref'] = config.get('cloud_ref')
        data['vrf_ref'] = config.get('vrf_ref', '')
        data['created_by'] = config.get('created_by', '')
        data['enabled'] = config['enabled']
        data['gslb_sp_enabled'] = config.get('gslb_sp_enabled', False)
        return data

    def add_metric_data(self, request, uuid, obj_data):
        obj_data['metrics'] = {}
        db_cache = self._db_cache()
        vs_refs = db_cache.get_parents('Pool', uuid=uuid,
                                            model_filter=['VirtualService'])
        if vs_refs:
            ref = vs_refs[0]
            vs_uuid = ref.uuid

            if hasattr(self, 'metric_data') and self.metric_data:
                if vs_uuid in self.metric_data:
                    obj_data['metrics'] = self.metric_data[vs_uuid]

        self.get_missing_metric_data(request, uuid, obj_data)

    def get_app_profile_type(self, vs_uuid):
        vs = VirtualService.objects.get(uuid=vs_uuid)
        app_uuid = vs.protobuf().application_profile_uuid
        app_prof = ApplicationProfile.objects.get(uuid=app_uuid)
        return app_prof.json_data.get('type')

    def get_pool_group_ref(self, uuid, request, include_name=False, db_cache=None):
        if not db_cache:
            db_cache = self._db_cache()
        pg = db_cache.get_parents('Pool', uuid, model_filter=['PoolGroup'])
        if pg:
            pool_group_ref = [uri_from_slug("poolgroup", _pg.uuid, host=request.get_host(), include_name=include_name, name=_pg.name()) for _pg in pg]
            return pool_group_ref
        else:
            return None


    def add_extra_data(self, result, obj_data, request, *args, **kwargs):
        include_name =  ('include_name' in request.QUERY_PARAMS)
        if 'alert' in self.resource_list:
            result['alert'] = self.get_alert_data(obj_data.get('uuid'), request,
                                              *args, **kwargs)
        db_cache = self._db_cache()

        pool_uuid = obj_data['uuid']
        parent_pool = db_cache.get_parents('Pool', uuid=pool_uuid,
                                            model_filter=['Pool'],
                                            prune_criteria=0)
        #Traverse through the graph to the parent pool which is connected to the VS
        while(parent_pool):
            pool_uuid = parent_pool[0].uuid
            parent_pool = db_cache.get_parents('Pool', uuid=pool_uuid,
                                                model_filter=['Pool'],
                                                prune_criteria=0)

        vs_refs = db_cache.get_parents('Pool', uuid=pool_uuid,
                                            model_filter=['VirtualService'])
        result['virtualservices'] = []
        for ref in vs_refs:
            vs_ref = uri_from_slug("virtualservice", ref.uuid, scheme=None,
                include_name=include_name, name=ref.name(), host=None)
            result['virtualservices'].append(vs_ref)
            if 'app_profile_type' not in result:
                result['app_profile_type'] = self.get_app_profile_type(ref.uuid)

        result['pool_group_refs'] = self.get_pool_group_ref(obj_data.get('uuid'), request, include_name=include_name, db_cache=db_cache)

class PoolListInventoryView(PoolInventoryCommon, InventoryListView):
    def __init__(self, *args, **kwargs):
        model_details = {
            'model_type': 'Pool',
            'list_view': views_pool.PoolList,
            'runtime_cache': PoolStateDBCache,
            'has_metrics': True
        }
        super(PoolListInventoryView, self).__init__(model_details, *args, **kwargs)

class PoolDetailInventoryView(PoolInventoryCommon, InventoryDetailView):
    def __init__(self, *args, **kwargs):
        model_details = {
            'model_type': 'Pool',
            'detail_view': views_pool.PoolDetail,
            'runtime_cache': PoolStateDBCache,
            'has_metrics': True
        }
        super(PoolDetailInventoryView, self).__init__(model_details, *args, **kwargs)

class PoolSummaryInventoryView(PoolInventoryCommon, InventorySummaryView):
    def __init__(self, *args, **kwargs):
        model_details = {
            'model_type': 'Pool',
            'list_view': views_pool.PoolList,
            'runtime_cache': PoolStateDBCache,
        }
        super(PoolSummaryInventoryView, self).__init__(
                                                model_details, *args, **kwargs)

class ServiceEngineInventoryCommon(InventoryCommonView):
    model = ServiceEngine
    def parse_config_data(self, config):
        data = {}
        data['name'] = config['name']
        data['url'] = config['url']
        data['uuid'] = config['uuid']
        data['mgmt_ip_address'] = ''
        data['host_ref'] = config.get('host_ref')
        vnic = config.get('mgmt_vnic')
        if not vnic:
            return data
        networks = vnic.get('vnic_networks')
        if networks and networks[0].get('ip'):
            data['mgmt_ip_address'] = networks[0].get('ip', {}).get('ip_addr')
        data['se_group_ref'] = config.get('se_group_ref', '')
        data['tenant_ref'] = config.get('tenant_ref', '')
        data['cloud_ref'] = config.get('cloud_ref')
        data['enable_state'] = config.get('enable_state')
        data['availability_zone'] = config.get('availability_zone', None)
        return data

    def add_extra_data(self, result, obj_data, request, *args, **kwargs):
        uuid = obj_data.get('uuid')
        if 'alert' in self.resource_list:
            result['alert'] = self.get_alert_data(uuid, request,
                                              *args, **kwargs)
        db_cache = self._db_cache()
        vs_refs = db_cache.get_parents('ServiceEngine', uuid,
                                  model_filter=['VirtualService'], depth=1)
        vs_urls = []
        vs_uuids = []
        include_name = True if 'include_name' in request.QUERY_PARAMS else False
        for ref in vs_refs:
            url = '/api/virtualservice/%s' % ref.uuid
            if include_name:
                url = url + ('#%s' % DbBaseCache.uuid2name(ref.uuid))
            vs_urls.append(url)
            vs_uuids.append(ref.uuid)
        result['config']['virtualservice_refs'] = vs_urls

        # calculate "vs per se" which includes vs of type normal and parent
        # and only virtualservices with non east_west_placement
        vs_qset = VirtualService.objects.filter(uuid__in=vs_uuids)
        type_query = Q(Q(json_data__type='VS_TYPE_NORMAL') | Q(json_data__type='VS_TYPE_VH_PARENT'))
        normal_and_parent_qset = vs_qset.filter(type_query)
        vsvip_uuids = [vs.vsvip_ref for vs in normal_and_parent_qset]
        non_eastwest_vsvips = [vsvip.uuid for vsvip in VsVip.objects.filter(uuid__in=vsvip_uuids, json_data__east_west_placement=False)]
        vs_per_se_uuids = [vs.uuid for vs in normal_and_parent_qset.filter(vsvip_ref__in=non_eastwest_vsvips)]
        vs_per_se_urls = []
        for vs_uuid in vs_per_se_uuids:
            name = DbBaseCache.uuid2name(vs_uuid) if include_name else ''
            url = uri_from_slug('virtualservice', vs_uuid,
                                scheme=get_scheme(request), host=request.get_host(),
                                include_name=include_name, name=name)
            vs_per_se_urls.append(url)
        result['config']['vs_per_se_refs'] = vs_per_se_urls
        


class ServiceEngineListInventoryView(ServiceEngineInventoryCommon, InventoryListView):
    def __init__(self, *args, **kwargs):
        model_details = {
            'model_type': 'ServiceEngine',
            'list_view': views_se.ServiceEngineList,
            'runtime_cache': ServiceEngineStateDBCache,
            'has_metrics': True
        }
        super(ServiceEngineListInventoryView, self).__init__(model_details,
                                                         *args, **kwargs)
class ServiceEngineDetailInventoryView(ServiceEngineInventoryCommon, InventoryDetailView):
    def __init__(self, *args, **kwargs):
        model_details = {
            'model_type': 'ServiceEngine',
            'detail_view': views_se.ServiceEngineDetail,
            'runtime_cache': ServiceEngineStateDBCache
        }
        super(ServiceEngineDetailInventoryView, self).__init__(model_details, *args, **kwargs)

class ServiceEngineSummaryInventoryView(InventorySummaryView):
    def __init__(self, *args, **kwargs):
        model_details = {
            'model_type': 'ServiceEngine',
            'list_view': views_se.ServiceEngineList,
            'runtime_cache': ServiceEngineStateDBCache
        }
        super(ServiceEngineSummaryInventoryView, self).__init__(
                                                model_details, *args, **kwargs)

class PoolListInventoryServerView(PoolInventoryCommon, InventoryListView):
    def __init__(self, *args, ** kwargs):
        model_details = {
            'list_view': views_pool.PoolList,
            'detail_view': PoolInventoryServerView
        }
        super (PoolListInventoryServerView, self).__init__(model_details, *args, **kwargs)

    def get_servers_for_one_pool(self, pool_uuid, request, *args, **kwargs):
        pool_kwargs = copy.deepcopy(kwargs)
        pool_kwargs['slug'] = pool_uuid
        # self.detail_view is paginated all servers might not be returned in rsp
        # page_size =1 will force api to give all servers
        if pool_kwargs.get('custom_params'):
            pool_kwargs['custom_params']['page_size'] = -1
        else:
            pool_kwargs['custom_params'] = {}
            pool_kwargs['custom_params']['page_size'] = -1
        try:
            rsp = self.get_view_data(self.detail_view, request, *args, **pool_kwargs)
            log.error(" %s %s "%(pool_kwargs,len(rsp.data.get('results',[]))))
            return rsp.data.get('results', [])
        except DataException as e:
            #Will throw DataException if ?server=ip:port fails
            return []
        except Exception as e:
            log.error(e)
            log.error(traceback.format_exc())
            #for other cases return empty list if view fails
            return []

    def clean_config_view_params(self, request, kwargs):
        super(PoolListInventoryServerView, self).clean_config_view_params(request, kwargs)
        kwargs.get('custom_params', {}).pop('all_se', None)
        # page_size = -1 will force api to give all results
        kwargs.get('custom_params', {}).pop('page', None)
        kwargs['custom_params']['page_size'] = -1
        # fields uuid , will give only name,url,uuid data
        kwargs['custom_params']['fields'] = 'uuid'

    def get_offset_and_pool_uuids(self,page_index,page_size,pool_uuids,uuid_server_count_dict):
        ''' 
        list of pools each containing some servers
        pool_uuids = list of pools_uuids
        uuid_server_count_dict = dict {pool_uuid:server_count for the pool..,} 
        page_index = page no in the url
        page_size = no of elements to be displayed in page
        start_pool_index = pool in list from where to display servers
        end_pool_index = pool in list till where to display servers
        offset = no of servers to skip in the start_pool_index
        end_reached = no more servers to evaluate
        '''

        servers_displayed = page_size * (page_index - 1)
        servers_to_display = page_size
        start_pool_index = False
        end_pool_index = False
        end_reached = False
        offset = 0
        server_count = 0
        for index,uuid in enumerate(pool_uuids):
            servers_displayed -= uuid_server_count_dict[uuid]
            if servers_displayed<0:
                start_pool_index = index
                offset = servers_displayed + uuid_server_count_dict[uuid]
                server_count = uuid_server_count_dict[uuid] - offset
                while True:
                    try:
                        if server_count > page_size: 
                            end_pool_index = index
                            break
                        server_count += uuid_server_count_dict[pool_uuids[index+1]]
                        index += 1
                    except IndexError:
                        end_pool_index = len(pool_uuids) - 1
                        end_reached = True
                        break
                break
        return start_pool_index,end_pool_index,offset,end_reached

    def get(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        self.get_resource_list(request)
        data = {}
        pool_data = []
        max_paginate_by = common_api_settings.get('MAX_PAGINATE_BY',25)
        paginate_by = common_api_settings.get('PAGINATE_BY',25)
        params = kwargs.get('request_query_params',{})
        try:
            page_size = int(params.get('page_size', paginate_by))
            page_index = int(params.get('page', 1))
        except (TypeError,ValueError):
            raise Exception('That page number is not an integer')
        if page_size == 0:
            raise Exception('Page size zero is not supported')
        if page_size < -1:
            raise Exception('Negative indexing is not supported')
        if page_index < 1:
            raise Exception('That page number is less than 1')
        
        l_kwargs = copy.deepcopy(kwargs)
        ## getting all pool uuids acc. to the filter query params
        l_kwargs['skip_update_realtime_fields'] = True
        self.clean_config_view_params(request, l_kwargs)
        rsp = self.get_view_data(self.list_view, request, *args, **l_kwargs)
        if rsp.status_code != 200:
            return rsp
        pool_data = rsp.data.get('results',[])
        ##
        pool_uuids = [str(rec['uuid']) for rec in pool_data if rec.get('uuid',False)]
        total_server_count,uuid_server_count_dict = get_server_pool_info(pool_uuids)
        # page_size = -1 , then display all results
        if page_size == -1 or total_server_count == 0:
            end_reached = True
        else:
            if (page_size*page_index - total_server_count >= page_size) :
                raise Exception('That page contains no results')
            start_pool_index, end_pool_index, offset, end_reached = self.get_offset_and_pool_uuids(page_index,page_size,pool_uuids,uuid_server_count_dict)
            pool_uuids = pool_uuids[start_pool_index:end_pool_index+1]

        results = []
        # if lot of pools then start a max of int(paginate_by) threads at a time
        for i in range(0,len(pool_uuids),paginate_by):
            list_data = pool_uuids[i:i+paginate_by]
            threads = []
            for uuid in list_data:
                threads.append(gevent.spawn(self.get_servers_for_one_pool,uuid, request, *args, **kwargs))
            gevent.joinall(threads)
            map(lambda x: results.extend(x), [thread.value for thread in threads])
        if not (page_size == -1 or total_server_count == 0):
            results = results[offset:offset+page_size]
        data['count'] = total_server_count
        data['results'] = results
        
        if not end_reached:
            full_uri = request.build_absolute_uri()
            data['next'] = replace_query_param(full_uri,'page',page_index+1)
        rsp = Response(data)
        return rsp

class PoolInventoryServerView(PoolInventoryCommon, InventoryDetailView):
    def __init__(self, *args, **kwargs):
        model_details = {
            'model_type': 'Pool',
            'detail_view': views_pool.PoolDetail,
            'runtime_cache': PoolStateDBCache
        }
        super(PoolInventoryServerView, self).__init__(model_details, *args, **kwargs)
        self.resource_list = ['alert', 'runtime', 'health_score']

    def get_server_runtime(self, pool_uuid, default_port, request, *args, **kwargs):
        data = {}
        count = 0
        try:
            cache = ServerStateDBCache()
            state_pb = cache.getState(pool_uuid)
            if state_pb:
                pb_list = state_pb.summary
                runtime = []
                for pb in pb_list:
                    if pb.is_standby:
                        continue
                    runtime.append(protobuf2dict_withrefs(pb, request))

        except Exception as e:
            log.exception('Pool %s server runtime error:' % pool_uuid)
            data['count'] = 0
            return data
        for s_runtime in runtime:
            ip = None
            if s_runtime.get('ip_addr'):
                ip = s_runtime.get('ip_addr').get('addr')
            oper_status = s_runtime.get('oper_status')
            port = s_runtime.get('port', default_port)
            key = "%s:%d" %(ip, port)
            if key not in data:
                count += 1
            if not ip or not oper_status:
                log.error('Missing runtime info on pool %s server runtime summary: %s'
                           % (pool_uuid, str(s_runtime)))
                continue

            # If server info already exists
            if key in data:
                if (oper_status["state"] == "OPER_UP" and
                        data[key]["oper_status"]["state"] != "OPER_UP"):
                    data[key]["oper_status"]["state"] = oper_status["state"]
                continue

            data[key] = {"oper_status": oper_status}
        data['count'] = count
        return data

    def get_server_metric_data(self, pool_uuid, vs_uuid, request, key='*'):
        """
        Return a map of <server_key> to server metric data
        """
        entity_type = 'virtualservice'
        m_kwargs = {'metrics_entity_type': 'virtualservice',
                    'skip_references':True}
        m_args = []
        query_params = {"pool": pool_uuid,
                        'metric_id': SERVER_METRICS,
                        'server': key,
                        'dimension_aggregation': 'all',
                        'detailed_header': "True",
                        'pad_missing_data': "False"
                        }

        query_params.update(request.QUERY_PARAMS.dict())
        #limit & step are passed from request
        query_params.pop('page_size', None)
        query_params.pop('page', None)
        if not self.m_view:
            m_view = MetricsQueryView()

        m_view.initial(request, *m_args, **m_kwargs)
        try:
            m_view.tenant = self.tenant
            m_view.allowed_tenants = self.allowed_tenants
            m_view.tenant_uuids = self.tenant_uuids
            result_dict, rc, format_type, cache_expiry = \
                    m_view.get_entity_analytics(query_params, entity_type, vs_uuid,
                                                request, *m_args,
                                                **m_kwargs)
        except Exception:
            log.exception('Fail to get server aggregation metric of pool %s' %
                         (pool_uuid))
            return {}
        if not result_dict.get('series'):
            log.warning(
              "Pool %s server aggregation metrics data has no 'series' data" %
                  pool_uuid)
            return {}

        series_data = result_dict.pop('series')
        result = {}
        for s in series_data:
            header = s.get('header')
            if not header:
                continue
            server_key = header.get('server')
            if not server_key:
                log.error('obj_id not found in server metrics data header: %s qp %s',
                          header, query_params)
                continue
            if server_key not in result:
                result[server_key] = {}
            name = header.get('name')
            result[server_key][name] = {
            "header": header
            }
        query_params.pop('dimension_aggregation')
        query_params['limit'] = '1'

        try:
            m_view.tenant = self.tenant
            m_view.allowed_tenants = self.allowed_tenants
            m_view.tenant_uuids = self.tenant_uuids
            sample_dict, rc, format_type, cache_expiry = \
                    m_view.get_entity_analytics(query_params, entity_type, vs_uuid,
                                                request, *m_args,
                                                **m_kwargs)
        except Exception:
            log.exception('Fail to get server metric last sample of pool uuid=%s' %
                         (pool_uuid))
            return {}
        if not sample_dict.get('series'):
            log.warning("Pool %s server metrics last sample data has no 'series' data" %
                        pool_uuid)
            return {}

        series_data = sample_dict.pop('series')
        for s in series_data:
            header = s.get('header')
            if not header:
                continue
            server_key = header.get('obj_id')
            if server_key not in result:
                continue
            name = header.get('name')
            if name not in result[server_key]:
                continue
            result[server_key][name]['data'] = s.get('data', {})

        return result

    def get_server_health_score_data(self, pool_uuid, request, key='*'):
        result = defaultdict(dict)
        if self._need_realtime_hs(request.QUERY_PARAMS):
            hs_params = REALTIME_HS_PARAMS.copy()
            hs_params['server'] = key
            rt_hs_pb = self.get_health_score_data(pool_uuid, request,
                                                  hs_params)
            if not rt_hs_pb or not rt_hs_pb.series:
                log.warning("Pool server realtime healthscore has no 'series'")
                return result
            for s in rt_hs_pb.series:
                server_key = s.header.server
                server_pb = HealthScoreQueryResponse()
                server_series = server_pb.series.add()
                server_series.CopyFrom(s)
                server_hs_data = self.parse_health_scores(server_pb, None)
                result[s.header.pool_uuid][server_key] = server_hs_data
        else:
            hs_params = AVERAGE_HS_PARAMS.copy()
            hs_params['server'] = key
            avg_hs_pb = self.get_health_score_data(pool_uuid, request,
                                                   hs_params)
            if not avg_hs_pb or not avg_hs_pb.series:
                log.warning("Pool server average healthscore has no 'series'")
                return {}
            series_pb = avg_hs_pb.series
            for s in series_pb:
                server_key = s.header.server
                avg_server_pb = HealthScoreQueryResponse()
                server_series = avg_server_pb.series.add()
                server_series.CopyFrom(s)
                server_hs_data = self.parse_health_scores(None, avg_server_pb)
                result[s.header.pool_uuid][server_key] = server_hs_data
        return result

    def parse_server_config(self, config, default_port, s_data, tenant_ref):
        """
        Parse config data in pool db to s_data dict, and return the server key
        """
        s_data['hostname'] = config.get('hostname', '')
        s_data['ratio'] = config.get('ratio', 1)
        s_data['enabled'] = config.get('enabled', True)
        server_port = config.get('port', default_port)
        s_data['port'] = server_port if server_port else default_port
        s_data['default_server_port'] = default_port
        s_data['ip'] = config.get('ip')
        ip = config.get('ip', {}).get('addr', '')
        s_data['tenant_ref'] = tenant_ref

        server_key = "%s:%d" %(ip, s_data['port'])
        return server_key

    def get(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        self.get_resource_list(request)

        rsp = self.get_view_data(self.detail_view, request, *args, **kwargs)
        if rsp.status_code != 200:
            return rsp
        pool_data = rsp.data

        default_port = pool_data.get('default_server_port')
        if not default_port:
            default_port = 80
        pool_uuid = pool_data.get('uuid')
        pool_url = pool_data.get('url')
        tenant_ref = pool_data.get('tenant_ref')

        metrics = {}
        health_scores = {}
        server_runtimes = {}
        pool_runtime = {}

        if 'runtime' in self.resource_list:
            try:
                server_runtimes = self.get_server_runtime(pool_uuid, default_port,
                                                      request, *args, **kwargs)
                pool_runtime = self.get_runtime_data(pool_uuid, request)
            except Exception:
                log.exception('Error in server runtime')

        params = kwargs.get('request_query_params',{})
        page_size = params.get('page_size', api_settings.PAGINATE_BY)
        if str(page_size) == '-1':
            object_list = pool_data.get('servers',[])
            page = None
        else:
            paginator = Paginator(pool_data.get('servers', []), page_size)
            data = {'count': paginator.count}
            page_index = params.get('page', 1)
            page = paginator.page(page_index)
            object_list = page.object_list
        server_keys = [self.parse_server_config(server, default_port, {}, tenant_ref) \
                           for server in object_list]

        request_key = request.QUERY_PARAMS.get('server', '*')
        vs_uuid = ''
        db_cache = self._db_cache()
        vs_refs = db_cache.get_parents('Pool', uuid=pool_uuid,
                                                model_filter=['VirtualService'])
        if vs_refs:
            vs_uuid = vs_refs[0].uuid
        if vs_uuid:
            if server_keys:
                server_key_str = ','.join(server_keys)
            else:
                server_key_str = request_key
            if 'metrics' in self.resource_list:
                metrics = self.get_server_metric_data(pool_uuid, 
                                                      vs_uuid, 
                                                      request,
                                                      key=server_key_str)
            if 'health_score' in self.resource_list:
                health_scores = self.get_server_health_score_data(pool_uuid,
                                                                  request,
                                                                  key=server_key_str)
                health_scores = health_scores.get(pool_uuid, {})
            rsp.data['app_profile_type'] = self.get_app_profile_type(vs_uuid)

        server_list = object_list
        if request_key != '*':
            found_server = None
            #one server only
            for server in server_list:
                if request_key == self.parse_server_config(
                                                server, default_port, {}, tenant_ref):
                    found_server = server
                    break
            if found_server:
                server_list = [found_server]
            else:
                raise DataException('Server with key %s not found' %request_key)

        data = []
        for server in server_list:
            s_data = {'config': {}}
            s_data['pool_ref'] = pool_url
            server_key = self.parse_server_config(server, default_port,
                                                  s_data['config'], tenant_ref)
            if 'runtime' in self.resource_list:
                if server_key in server_runtimes:
                    s_data['runtime'] = {}
                    s_data['runtime'].update(server_runtimes[server_key])
                else:
                    if DEFAULT_NULL_SERVER in server_key:
                        s_data['runtime'] = DEFAULT_NULL_SERVER_STATE
                    elif not server_runtimes.get('count'):
                        s_data['runtime'] = pool_runtime
                    else:
                        s_data['runtime'] = DEFAULT_DOWN_STATE
                    if server_runtimes.get('count'):
                        #server runtime return some data but can't match with server key
                        log.error('Didnot find runtime for server with key %s'
                                   % server_key)
                        log.error('Pool server Runtime data: %s'
                                   % str(server_runtimes))
            if 'metrics' in self.resource_list:
                if metrics and metrics.get(server_key):
                    s_data['metrics'] = metrics.get(server_key)
                else:
                    metric_s = request.QUERY_PARAMS.get('metric_id', None)
                    if not metric_s:
                        metric_s = SERVER_METRICS
                    default_metrics = {}
                    for m_id in metric_s.split(','):
                        default_metrics[m_id] = DEFAULT_METRIC_DATA.copy()
                    s_data['metrics'] = default_metrics

            if 'health_score' in self.resource_list:
                if health_scores and health_scores.get(server_key):
                    s_data['health_score'] = health_scores.get(server_key)
                else:
                    s_data['health_score'] = DEFAULT_HS_DATA.copy()

            data.append(s_data)

        rsp_data = {"count": len(pool_data.get('servers', []))}
        if page and page.has_next():
            full_uri = request.build_absolute_uri()
            rsp_data['next'] = replace_query_param(full_uri, 'page',
                                           page.next_page_number())
        rsp_data['results'] = data
        rsp = Response(rsp_data)
        return rsp

class NetworkInventoryCommon(InventoryCommonView):

    def get_runtime_data(self, obj_uuid, request):
        args = []
        runtime_kwargs = {'slug': obj_uuid,
                          'permission': "PERMISSION_NETWORK"}
        return self.get_view_data(self.runtime_view, request,
                                  *args, **runtime_kwargs).data

    def get_discovery_data(self, obj_uuid, request):
        args = []
        runtime_kwargs = {'slug': obj_uuid,
                          'permission': "PERMISSION_NETWORK"}
        return self.get_view_data(self.discovery_view, request,
                                  *args, **runtime_kwargs).data

    def get_data_for_one_object(self, config_data, request, runtime_data,
                                *args, **kwargs):
        obj_data = dict()
        obj_data['config'] = self.parse_config_data(config_data)
        obj_data['runtime'] = runtime_data
        uuid = config_data['uuid']
        obj_data['uuid'] = uuid
        try:
            obj_data['runtime'] = self.get_runtime_data(uuid, request)
        except Exception as e:
            log.exception('Runtime view exception: ')
            obj_data['runtime'] = {'error': str(e)}
        try:
            obj_data['discovery'] = self.get_discovery_data(uuid, request)
        except Exception as e:
            log.exception('Discovery view exception: ')
            obj_data['discovery'] = {'error': str(e)}
        return obj_data


class NetworkListInventoryView(NetworkInventoryCommon, InventoryListView):
    def __init__(self, *args, **kwargs):
        model_details = {
            'model_type': 'Network',
            'list_view': views_network_custom.NetworkList,
            'runtime_view': views_network.NetworkRuntimeDetail,
            'discovery_view': views_vi_mgr.VIMgrNWRuntimeDetail
        }
        super(NetworkListInventoryView, self).__init__(
            model_details, *args, **kwargs)


class NetworkDetailInventoryView(NetworkInventoryCommon, InventoryDetailView):
    def __init__(self, *args, **kwargs):
        model_details = {
            'model_type': 'Network',
            'detail_view': views_network_custom.NetworkDetail,
            'runtime_view': views_network.NetworkRuntimeDetail,
            'discovery_view': views_vi_mgr.VIMgrNWRuntimeDetail
        }
        super(NetworkDetailInventoryView, self).__init__(
            model_details, *args, **kwargs)

class ServiceEngineGroupInventoryCommon(InventoryCommonView):

    def get_se_data(self, obj_uuid, request, kwargs):
        args = []
        params = {
            'page_size': -1,
            'refers_to': 'serviceenginegroup:' + obj_uuid,
            'include_name': 'true',
            'fields': 'name'
        }
        kwargs['custom_params']= params

        se_rsp = self.get_view_data(self.se_view, request,
                                  *args, **kwargs)
        if se_rsp.status_code != 200:
            log.error('Get SE for SE group %s failed '% obj_uuid)
            return se_rsp.data
        data = []
        for se_data in se_rsp.data.get('results', []):
            data.append(se_data.get('url'))
        return data

    def get_vs_data(self, obj_uuid, request, kwargs):
        args = []
        params = {
            'page_size': -1,
            'refers_to': 'serviceenginegroup:' + obj_uuid,
            'include_name': 'true',
            'fields': 'name'
        }
        kwargs['custom_params']= params
        kwargs['permission'] = 'PERMISSION_VIRTUALSERVICE'

        vs_rsp = self.get_view_data(self.vs_view, request,
                                  *args, **kwargs)
        if vs_rsp.status_code != 200:
            log.error('Get VS for SE group %s failed '% obj_uuid)
            return vs_rsp.data
        data = []
        for vs_data in vs_rsp.data.get('results', []):
            data.append(vs_data.get('url'))
        return data

    def get_data_for_one_object(self, config_data, request, runtime_data,
                                *args, **kwargs):
        obj_data = dict()
        obj_data['config'] = self.parse_config_data(config_data)
        obj_data['runtime'] = runtime_data
        uuid = config_data['uuid']
        obj_data['uuid'] = uuid
        kwargs['skip_query_params'] = True
        try:
            obj_data['serviceengines'] = self.get_se_data(uuid, request, kwargs)
        except Exception as e:
            log.exception('ServiceEngine for SE group view error:')
            obj_data['serviceengines'] = str(e)
        try:
            obj_data['virtualservices'] = self.get_vs_data(uuid, request, kwargs)
        except Exception as e:
            log.exception('VirtualService for SE group view error:')
            obj_data['virtualservices'] = str(e)
        return obj_data

class ServiceEngineGroupListInventoryView(ServiceEngineGroupInventoryCommon,
                                           InventoryListView):
    def __init__(self, *args, **kwargs):
        model_details = {
            'model_type': 'ServiceEngineGroup',
            'list_view': views_se_group.ServiceEngineGroupList,
            'se_view': views_se.ServiceEngineList,
            'vs_view': views_vs_pool.VirtualServicePoolList
        }
        super(ServiceEngineGroupListInventoryView, self).__init__(
            model_details, *args, **kwargs)
        self.resource_list = []

class ServiceEngineGroupDetailInventoryView(ServiceEngineGroupInventoryCommon,
                                             InventoryDetailView):
    def __init__(self, *args, **kwargs):
        model_details = {
            'model_type': 'ServiceEngineGroup',
            'detail_view': views_se_group.ServiceEngineGroupDetail,
            'se_view': views_se.ServiceEngineList,
            'vs_view': views_vs_pool.VirtualServicePoolList
        }
        super(ServiceEngineGroupDetailInventoryView, self).__init__(
            model_details, *args, **kwargs)
        self.resource_list = []

class CloudListInventoryView(InventoryListView):
    def __init__(self, *args, **kwargs):
        model_details = {
            'model_type': 'Cloud',
            'list_view': views_cloud_custom.CloudList,
            'status_view': views_cloud_connector_custom.CloudStatusView
        }
        super(CloudListInventoryView, self).__init__(
            model_details, *args, **kwargs)
        self.resource_list = []

    def get_ipam_provider_type(self, obj_data):
        ipam_type = None
        ipam_provider_ref = obj_data.get('ipam_provider_ref')
        log.debug(obj_data)
        log.debug(ipam_provider_ref)
        if ipam_provider_ref:
            uuid = slug_from_uri(ipam_provider_ref)
            ipam_obj = IpamDnsProviderProfile.objects.filter(uuid=uuid)
            if ipam_obj:
                ipam_type = ipam_obj[0].json_data.get('type')
        return ipam_type

    def get_mvrf_data(self, obj_uuid, request):
        objs = VrfContext.objects.filter(name='management',
                                         cloud_ref__uuid=obj_uuid)
        if len(objs) > 0:
            ser = VrfContextSerializer()
            ser.context['request'] = request
            return ser.to_native(objs[0])
        return {}

    def get_status_data(self, uuid, request):
        args = []
        status_kwargs = {'slug': uuid,
                          'permission': "PERMISSION_CLOUD"}
        return self.get_view_data(self.status_view, request,
                                  *args, **status_kwargs).data

    def get_data_for_one_object(self, config_data, request, runtime_data,
                                *args, **kwargs):
        obj_data = dict()
        obj_data['config'] = self.parse_config_data(config_data)
        obj_data['runtime'] = runtime_data
        uuid = config_data['uuid']
        obj_data['uuid'] = uuid
        obj_data['ipam_provider_type'] = self.get_ipam_provider_type(config_data)
        try:
            obj_data['status'] = self.get_status_data(uuid, request)
            obj_data['mvrf'] = self.get_mvrf_data(uuid, request)
        except Exception as e:
            log.exception('Runtime view exception: ')
            obj_data['status'] = {'error': str(e)}
        return obj_data
#-------------------------------------------------------------------------
class GslbInventoryCommon(InventoryCommonView):
    def parse_config_data(self, config):
        return config

    def get_runtime_data(self, obj_uuid, request):
        """
        GLB-MGR does not have a statedb cache, so we customize the get_runtime
        with a custom API
        """
        args = []
        runtime_kwargs = {'slug': obj_uuid,
                          'permission': "PERMISSION_GSLB"}
        return self.get_view_data(self.runtime_view, request,
                                  *args, **runtime_kwargs).data

class GslbListInventoryView(GslbInventoryCommon, InventoryListView):
    """ GSLB does not have health-score or metrics in this release. """
    def __init__(self, *args, **kwargs):
        model_details = {
            'model_type': 'Gslb',
            'list_view': views_gslb_custom.GslbList,
            'runtime_view':views_gslb_custom.GslbRuntimeSummaryView,
            'has_metrics': False
        }
        super(GslbListInventoryView, self).__init__(
                                                model_details, *args, **kwargs)
        self.skip_hs = True
        self.resource_list = ['runtime']
        return

    @api_perf
    def get_runtime_data_json(self, obj_uuids, request):
        """
        Aggregate the runtime for the obj-list. There is only one
        Gslb object in the entire system. So, we don't need to
        parallelize this operation. [unlike GslbService, which can
        be multiple objects and hence we need to parallelize]
        """
        if not obj_uuids:
            return []
        return [self.get_runtime_data(obj, request) for obj in obj_uuids]

class GslbDetailInventoryView(GslbInventoryCommon, InventoryDetailView):
    """ GSLB does not have health-score or metrics in this release. """
    def __init__(self, *args, **kwargs):
        model_details = {
            'model_type': 'Gslb',
            'detail_view': views_gslb_custom.GslbDetail,
            'runtime_view':views_gslb_custom.GslbRuntimeDetailView,
            'has_metrics': False
        }
        super(GslbDetailInventoryView, self).__init__(
                                                model_details, *args, **kwargs)
        self.skip_hs = True
        self.resource_list = ['runtime']
        return

#-------------------------------------------------------------------------
class GslbServiceInventoryCommon(InventoryCommonView):
    def parse_config_data(self, config):
        return config

    def get_runtime_data(self, obj_uuid, request):
        """
        glb_mgr does not have a statedb cache, we customize the get_runtime
        with a custom API which involves querying the backend glb_mgr.
        """
        args = []
        runtime_kwargs = {'slug': obj_uuid,
                          'permission': "PERMISSION_GSLBSERVICE"}
        return self.get_view_data(self.runtime_view, request,
                                  *args, **runtime_kwargs).data


class GslbServiceListInventoryView(InventoryListView):
    """ GSLB does not have health-score or metrics in this release. """
    def __init__(self, *args, **kwargs):
        model_details = {
            'model_type': 'GslbService',
            'list_view': views_gslb_custom.GslbServiceList,
            'runtime_view':views_gslb_custom.GslbServiceRuntimeView,
            'has_metrics': False
        }

        super(GslbServiceListInventoryView, self).__init__(model_details, *args, **kwargs)
        self.skip_hs = True
        self.resource_list = ['runtime']
        return

    def batch_read_rpc(self, obj_uuids,query_params):
        """
        Notes:
        #1 Creates request msg for RPC 
        #2 Add uuid list to the request msg
        #3 Make rpc call to BatchRead method 
        $4 Returns : RPC response object
        """
        req = RPCRequest()
        req.obj_type = get_obj_type_enum('GslbServiceRuntimeBatch')
        req.read_level = get_info_type_from_filter(query_params, 'SUMMARY')
        req.uuid = obj_uuids[0]
        for obj_uuid in obj_uuids:
           req_obj = req.resource.gslb_service_runtime.add()
           req_obj.uuid = obj_uuid
        set_rpc_filter(query_params,['gs_params_filter'] , req.filter)
        set_rpc_request_meta_data(query_params, req.meta_data)
        batch_rpc = GslbServiceService_Stub(RpcChannel(uuid=req.uuid ))

        try:
            rsp = batch_rpc.BatchRead(AviRpcController(), req)
        except TaskQueueException as e:     
            log.error('Request Timedout %s ',req)
            raise e
        return rsp

    @api_perf
    def get_runtime_data_json(self, obj_uuids, request):
        """
        Aggregate the runtime for the obj-list. We want to parallelize
        this operation because it involves a RPC to the back-end local worker.
        Notes:
        #1 Make uuid batches from uuid list and pass it for RPC call
        #2 Unpack response object to get list of gs_summary for each uuid
        #3 convert proto object to json for ui 
        """
        uuid_cnt = len(obj_uuids)

        if uuid_cnt ==0:
            return []
        runtime_kwargs = {'slug': obj_uuids[0],'permission': "PERMISSION_GSLBSERVICE"}

        query_params = request.QUERY_PARAMS.copy()
        if 'query_params' in runtime_kwargs:
            query_params.update(runtime_kwargs.get('query_params'))
        
        idx =0
        idx_batch =0
        all_object = []
        for idx in xrange(0,uuid_cnt,GSLB_MAX_NUM_OF_OBJS_IN_MSG):
             idx_batch = min(uuid_cnt,idx + GSLB_MAX_NUM_OF_OBJS_IN_MSG)
             uuid_batch = obj_uuids[idx:idx_batch]
             resp =  self.batch_read_rpc(uuid_batch,query_params)

             if resp.HasField('resource'):
                 for gs_summ in resp.resource.batch_gs_summary:
                     all_object.append(pb2json(gs_summ.gs_summary))

        return all_object     

class GslbServiceDetailInventoryView(GslbServiceInventoryCommon, InventoryDetailView):
    """ GSLB does not have health-score or metrics in this release. """
    def __init__(self, *args, **kwargs):
        model_details = {
            'model_type': 'GslbService',
            'detail_view': views_gslb_custom.GslbServiceDetail,
            'runtime_view':views_gslb_custom.GslbServiceRuntimeView,
            'has_metrics': False
        }
        super(GslbServiceDetailInventoryView, self).__init__(
                                                model_details, *args, **kwargs)
        self.skip_hs = True
        self.resource_list = ['runtime']
        return

#-------------------------------------------------------------------------
class PoolGroupInventoryCommon(InventoryCommonView):
    def add_extra_data(self, result, obj_data, request, *args, **kwargs):
        db_cache = self._db_cache()

        poolgroup_uuid = obj_data['uuid']

        vs_refs = db_cache.get_parents('PoolGroup', uuid=poolgroup_uuid,
                                            model_filter=['VirtualService'],
                                            prune_criteria=0)
        if vs_refs:
            result['virtualservices'] = []
            for ref in vs_refs:
                vs_config = {'uuid': ref.uuid}
                try:
                    vs_name = ref.name()
                    vs_config['name'] = vs_name
                except ObjectDoesNotExist:
                    log.error('Virtual service %s is deleted but still in db cache' % ref.uuid)
                    continue
                result['virtualservices'].append(vs_config)

class PoolGroupListInventoryView(PoolGroupInventoryCommon, InventoryListView):
    def __init__(self, *args, **kwargs):
        model_details = {
            'model_type': 'PoolGroup',
            'list_view': views_pool_group.PoolGroupList
        }
        super(PoolGroupListInventoryView, self).__init__(model_details, *args, **kwargs)
        self.resource_list = []

class PoolGroupDetailInventoryView(PoolGroupInventoryCommon, InventoryDetailView):
    def __init__(self, *args, **kwargs):
        model_details = {
            'model_type': 'PoolGroup',
            'detail_view': views_pool_group.PoolGroupDetail
        }
        super(PoolGroupDetailInventoryView, self).__init__(model_details, *args, **kwargs)
        self.resource_list = []

class PoolGroupSummaryInventoryView(PoolGroupInventoryCommon, InventorySummaryView):
    def __init__(self, *args, **kwargs):
        model_details = {
            'model_type': 'PoolGroup',
            'list_view': views_pool_group.PoolGroupList
        }
        super(PoolGroupSummaryInventoryView, self).__init__(
                                                model_details, *args, **kwargs)
        self.resource_list = []

class VsVipInventoryCommon(InventoryCommonView):
    pass

class VsVipListInventoryView(VsVipInventoryCommon, InventoryListView):
    def __init__(self, *args, **kwargs):
        model_details = {
            'model_type': 'VsVip',
            'list_view': views_vs_pool.VsVipList
        }
        super(VsVipListInventoryView, self).__init__(model_details, *args, **kwargs)
        self.resource_list = []

    def add_extra_data(self, result, obj_data, request, *args, **kwargs):
        db_cache = self._db_cache()
        include_name = 'include_name' in request.QUERY_PARAMS
        vsvip_uuid = obj_data['uuid']
        vs_refs = []
        vs_ref_objs = db_cache.get_parents('VsVip', uuid=vsvip_uuid,
                                             model_filter=['VirtualService'])
        for vs in vs_ref_objs:
            vs_refs.append(uri_from_slug("virtualservice", vs.uuid, host=request.get_host(), include_name=include_name, name=vs.name()))
        obj_data['vs_refs'] = vs_refs

class VsVipDetailInventoryView(VsVipInventoryCommon, InventoryDetailView):
    def __init__(self, *args, **kwargs):
        model_details = {
            'model_type': 'VsVip',
            'detail_view': views_vs_pool.VsVipDetail
        }
        super(VsVipDetailInventoryView, self).__init__(model_details, *args, **kwargs)
        self.resource_list = []
#End of file
