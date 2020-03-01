

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

from datetime import datetime, timedelta
from django.http.response import HttpResponse
from json import dumps
import logging
import ujson
from rest_framework import generics
from rest_framework.parsers import JSONParser
import dateutil.parser
import time

from shlex import split
from subprocess import (check_output, CalledProcessError)

from avi.rest import mixins
from avi.rest.json_io import JSONRenderer
from avi.rest.views import CommonView
from avi.util.changelog_api import ChangelogApi
from avi.util.ipproperties import IpProperties
from avi.infrastructure.rpc_channel import RpcChannel
from avi.infrastructure.clustering.cluster_utils import get_cluster_runtime_state
from google.protobuf.service import RpcController
from avi.protobuf import syserr_pb2
from avi.visibility.controller_metrics import ControllerMetrics
from avi.protobuf.license_rpc_pb2 import (LicenseService_Stub, LicenseReq)
from avi.rest.pb_utils import get_pb_from_name_if_exists, get_pb_if_exists
from api.models import BackupConfiguration


log = logging.getLogger(__name__)

SERVER_LIC_EARLY_WARNING = 5
CORE_LIC_EARLY_WARNING = 5


class LicensingView(mixins.RetrieveModelMixin,
                    generics.SingleObjectAPIView,
                    CommonView):
    renderer_classes = (JSONRenderer,)
    parser_classes = (JSONParser,)

    def get(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        cm = ControllerMetrics()
        request_params = request.QUERY_PARAMS.dict()
        start = request_params.get('start')
        stop = request_params.get('stop')
        limit = int(request_params.get('limit', 288))
        step = int(request_params.get('step', 300))
        se_throughputs = bool(request_params.get('se_throughputs', False))
        vs_throughput = bool(request_params.get('vs_throughput', False))
        filter_pertenant = bool(request_params.get('filter_pertenant', False))
        resp_dic = cm.get_license_usage(start=start, stop=stop,
                                        limit=limit, step=step,
                                        se_throughputs=se_throughputs,
                                        vs_throughput=vs_throughput,
                                        filter_pertenant=filter_pertenant)
        resp_json = dumps(resp_dic, indent=0, sort_keys=True)
        query_rsp = HttpResponse(resp_json, status=200,
                                 content_type='text/json')
        return query_rsp


class ChangelogView(mixins.RetrieveModelMixin,
                    generics.SingleObjectAPIView,
                    CommonView):

    def get(self, request, *args, **kwargs):

        CHANGELOG_HISTORY_DAYS = 365
        history_days = datetime.now() - timedelta(days=CHANGELOG_HISTORY_DAYS)

        clog_api = ChangelogApi()
        clog_api.update_pkglog('openssl', history_days)
        resp_dict = clog_api.changelogs
        resp_json = dumps(resp_dict, indent=0, sort_keys=True)
        query_rsp = HttpResponse(resp_json, status=200,
                                 content_type='text/json')
        return query_rsp


ipprop = IpProperties()
class IpPropertiesView(mixins.RetrieveModelMixin,
                    generics.SingleObjectAPIView,
                    CommonView):

    def get(self, request, *args, **kwargs):
        resp_dict = dict()

        # IPs
        if 'ip' in request.QUERY_PARAMS:
            ips2qry = request.QUERY_PARAMS['ip'].strip().split(',')
            if len(ips2qry): resp_dict['ipdata'] = dict()
            for ip in ips2qry:
                resp_dict['ipdata'].update(ipprop.ip2as(ip, 0))
        # ASNs
        if 'asn' in request.QUERY_PARAMS:
            asns2qry = request.QUERY_PARAMS['asn'].strip().split(',')
            if len(asns2qry): resp_dict['asdata'] = dict()
            for asn in asns2qry:
                resp_dict['asdata'].update(ipprop.as2name(int(asn)))

        resp_json = dumps(resp_dict, indent=0, sort_keys=True)
        query_rsp = HttpResponse(resp_json, status=200,
                                 content_type='text/json')
        return query_rsp

class ControllerView(mixins.RetrieveModelMixin,
                    generics.SingleObjectAPIView,
                    CommonView):
    renderer_classes = (JSONRenderer,)
    parser_classes = (JSONParser,)

    def _get_license_info(self):
        req = LicenseReq()
        rpc_rsp = LicenseService_Stub(RpcChannel()).\
              ReadLicense(RpcController(), req)
        if rpc_rsp:
            if rpc_rsp.ret_status == syserr_pb2.SYSERR_SUCCESS:
                if rpc_rsp.HasField('controller_license'):
                    return rpc_rsp.controller_license
        return None

    def set_fault_test_config(self):
        # for fault simulation. If /home/admin/fault.json
        # is not present then ignore
        config = {}
        self.test_config = {}
        try:
            fault_simulation_file = '/home/admin/fault.json'
            with open( fault_simulation_file, 'r' ) as f:
                config = ujson.load(f)
        except Exception as e:
            print str(e)
            config = {}

        if config and 'controller_faults' in config:
            self.test_config = config.get('controller_faults')

    def get_test_license_expiry_fault_config(self):
        if self.test_config:
            if ('license_expiry' in self.test_config):
                return True, self.test_config['license_expiry']
        return False, ''

    def get_test_license_count_fault_config(self):
        if self.test_config:
            if ('license_count' in self.test_config):
                return True, self.test_config['license_count']
        return False, ''

    def get_test_cluster_inactive_fault_config(self):
        if self.test_config:
            if ('cluster' in self.test_config):
                return True, self.test_config['cluster']
        return False, ''

    def get_lic_info(self, request, *args, **kwargs):
        def _datetime_from_str(date_s):
            return dateutil.parser.parse(date_s)


        lic_exp_list = list()
        now = datetime.utcnow()
        license_info = self._get_license_info()
        if not license_info:
            return lic_exp_list

        test_enabled, cond = self.get_test_license_expiry_fault_config()
        for license in license_info.licenses:
            if ((_datetime_from_str(license.valid_until) <= now) or
                (test_enabled and cond == 'expired')):
                l_info = dict()
                l_info['name'] = license.license_name
                l_info['valid_until'] = license.valid_until
                l_info['status'] = 'LICENSE_EXPIRED'
                desc_str = 'License %s expired.' % (license.license_name)
                l_info['description'] = desc_str
                lic_exp_list.append(l_info)
            elif ((_datetime_from_str(license.valid_until) - now) <=
                       timedelta(days=1) or
                  (test_enabled and cond == 'expiring')):
                l_info = dict()
                l_info['name'] = license.license_name
                l_info['valid_until'] = license.valid_until
                l_info['status'] = 'LICENSE_EXPIRING'
                desc_str = 'License %s expiring.' % (license.license_name)
                l_info['description'] = desc_str
                lic_exp_list.append(l_info)

        lic_exceeded_list = list()
        cm = ControllerMetrics()
        request_params = request.QUERY_PARAMS.dict()
        start = request_params.get('start')
        stop = request_params.get('stop')
        limit = int(request_params.get('limit', 288))
        step = int(request_params.get('step', 300))
        se_throughputs = bool(request_params.get('se_throughputs', False))
        vs_throughput = bool(request_params.get('vs_throughput', False))
        filter_pertenant = bool(request_params.get('filter_pertenant', False))
        resp_dic = cm.get_license_usage(start=start, stop=stop,
                                        limit=limit, step=step,
                                        se_throughputs=se_throughputs,
                                        vs_throughput=vs_throughput,
                                        filter_pertenant=filter_pertenant)
        #log.info('resp_dic : %s' % (resp_dic))
        test_enabled, cond = self.get_test_license_count_fault_config()

        unaccounted_expired_bursts = [x for x in license_info.expired_burst_resources if not x.accounted_license_id]
        avail_cores = resp_dic['licensed_cores'] + max(0, license_info.burst_cores - len(unaccounted_expired_bursts))
        if ((resp_dic['num_se_vcpus'] > avail_cores) or
              (test_enabled and cond == 'expired')):
            d = dict()
            d['licensed_cores'] = \
                resp_dic['licensed_cores']
            d['num_se_vcpus'] = \
                resp_dic['num_se_vcpus']
            d['reason'] = 'EXPIRED'
            d['description'] = 'Core based license count exceeded.'
            lic_exceeded_list.append(d)
        lic_info = list()
        lic_info = lic_exp_list + lic_exceeded_list

        lic_fault_info = dict()
        if lic_info:
            lic_fault_info['license_faults'] = lic_info
        #log.info('lic_fault_info : %s' % (lic_fault_info))
        return lic_fault_info

    def _get_cluster_faults(self):
        cluster_faults = {}
        cluster_state = get_cluster_runtime_state()

        inactive_nodes = []
        test_enabled, test_cluster = self.get_test_cluster_inactive_fault_config()
        for node in cluster_state.get('node_states', []):
            if node.get('state') != 'CLUSTER_ACTIVE' or test_enabled:
                node_state = {}
                node_state['name'] = node.get('name')
                node_state['state'] = node.get('state')
                if test_enabled and test_cluster:
                    node_state['state'] = test_cluster.get('node_state', 'CLUSTER_INACTIVE')
                inactive_nodes.append(node_state)
        if inactive_nodes or test_enabled:
            cluster_faults['inactive_nodes'] = inactive_nodes
            cluster_faults['cluster_state'] = cluster_state.get('cluster_state', {}).get('state')
            if test_enabled and test_cluster:
                cluster_faults['cluster_state'] = test_cluster.get('cluster_state', 'CLUSTER_UP_HA_COMPROMISED')
            cluster_faults['description'] = '%d node(s) of cluster not UP' % len(inactive_nodes)

        if cluster_faults:
            return [cluster_faults]
        else:
            return []

    def _get_config_backup_scheduler_faults(self):
        scheduler_faults = []
        backup_scheduler_pb = get_pb_from_name_if_exists('Scheduler', 'Default-Scheduler')
        if backup_scheduler_pb:
            if not backup_scheduler_pb.enabled:
                backup_scheduler_faults = {}
                backup_scheduler_faults['backup_scheduler_name'] = backup_scheduler_pb.name
                backup_scheduler_faults['status'] = backup_scheduler_pb.enabled
                backup_scheduler_faults['description'] = 'Configuration backup through %s has been disabled.' %backup_scheduler_pb.name
                scheduler_faults.append(backup_scheduler_faults)
            if backup_scheduler_pb.backup_config_uuid:
                backup_configuration_pb = get_pb_if_exists(BackupConfiguration, backup_scheduler_pb.backup_config_uuid)
                if backup_configuration_pb and not backup_configuration_pb.backup_passphrase:
                    backup_scheduler_faults = {}
                    backup_scheduler_faults['backup_scheduler_name'] = backup_scheduler_pb.name
                    backup_scheduler_faults['status'] = backup_scheduler_pb.enabled
                    backup_scheduler_faults['description'] = 'Passphrase is required for configuration backup.'
                    scheduler_faults.append(backup_scheduler_faults)
        return scheduler_faults

    def _get_db_migration_faults(self):
        migration_faults = {}

        migration_status, migration_timestamp = "", None

        try:
            migration_status = check_output(split("/bin/bash /opt/avi/python/lib/avi/util/postgres_tasks.sh "
                                                  "--name metrics --task get_migration_status"))
        except CalledProcessError:
            pass

        try:
            migration_timestamp = check_output(split("/bin/bash /opt/avi/python/lib/avi/util/postgres_tasks.sh "
                                                  "--name metrics --task get_migration_timestamp"))
        except CalledProcessError:
            pass

        if "pending" in migration_status and migration_timestamp:
            current_epoch = time.time()
            migration_timestamp = float(migration_timestamp)
            human_timestamp = time.strftime("%Z - %Y/%m/%d, %H:%M:%S", time.localtime(migration_timestamp))
            if migration_timestamp > current_epoch:
                migration_faults['migration_name'] = 'postgres-migration'
                migration_faults['description'] = 'Postgres metrics migration is scheduled for %s. Please keep in ' \
                                                  'mind that some metrics information will be unavailable before that ' \
                                                  'time.' % human_timestamp
            else:
                migration_faults['migration_name'] = 'postgres-migration'
                migration_faults['description'] = 'Postgres metrics migration has been in-progress since %s. Please keep in ' \
                                                  'mind that some metrics information will be unavailable while the migration ' \
                                                  'completes.' % human_timestamp

        if migration_faults:
            return [migration_faults]
        else:
            return []

    def get(self, request, *args, **kwargs):

        #log.info('start')
        obj_data = {}

        '''
        Retrieve Controller Faults only
        for superusers
        '''
        if request.user.is_superuser:
            self.set_fault_test_config()
            resp_dic = self.get_lic_info(request, args, kwargs)
            count = 0
            if resp_dic:
                count = count + 1
                obj_data['results'] = resp_dic
            obj_data['count'] = count

            cluster_faults = self._get_cluster_faults()
            if cluster_faults:
                if 'results' not in obj_data:
                    obj_data['results'] = {}
                count = count + 1
                obj_data['results']['cluster_faults'] = cluster_faults

            migration_faults = self._get_db_migration_faults()
            if migration_faults:
                if 'results' not in obj_data:
                    obj_data['results'] = {}
                count = count + 1
                obj_data['results']['migration_faults'] = migration_faults

            backup_scheduler_faults = self._get_config_backup_scheduler_faults()
            if backup_scheduler_faults:
                if 'results' not in obj_data:
                    obj_data['results'] = {}
                count = count + 1
                obj_data['results']['backup_scheduler_faults'] = backup_scheduler_faults

        if 'results' in obj_data:
            obj_data['count'] = count
        resp_json = dumps(obj_data, indent=0, sort_keys=True)
        query_rsp = HttpResponse(resp_json, status=200,
                                 content_type='text/json')
        #log.info('end')
        return query_rsp

