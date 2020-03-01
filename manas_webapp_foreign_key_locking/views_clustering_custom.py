
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
Cluster Manager Views
=====================
"""

import json
import logging
import os
import shlex
import string
import tarfile
import traceback
from datetime import datetime
from distutils.version import LooseVersion

import yaml
from api.models import ServiceEngine
from api.models import Alert
from api.models import CPUUsageInfoProto
from api.models import DiskUsageInfoProto
from api.models import MemoryUsageInfoProto
from api.models_secure_channel import SecureChannelMapping
from avi.config_migration.export_import import ConfigExporter
from avi.infrastructure.clustering.cluster_config import (
    ClusterConfig)
from avi.infrastructure.clustering.cluster_setup import (
    ClusterSetup)
from avi.infrastructure.clustering.cluster_state_mgr import ControllerWorkersStateMgr
from avi.infrastructure.clustering.cluster_utils import (
    get_cluster_config, reboot_cluster, reboot_cluster_node,
    get_cluster_runtime_state, get_role)
from avi.infrastructure.db_base_cache import DbBaseCache
from avi.infrastructure.services import Services
import avi.protobuf.upgrade_pb2 as upgrade_pb
from avi.protobuf import clustering_pb2
from avi.protobuf.disk_size_pb2 import DiskUsageInfo
from avi.protobuf.clustering_pb2 import Cluster as ClusterPb
from avi.protobuf.upgrade_pb2 import SystemUpgradeState, SystemUpgradeHistory
from avi.protobuf.resource_usage_pb2 import MemoryUsageInfo, CPUUsageInfo
from avi.protobuf_json.protobuf_json import json2pb
from avi.protobuf_json.protobuf_json import pb2json
from avi.rest.error_list import ServerException, PermissionError, DataException
from avi.rest.file_service_utils import parse_fs_uri
from avi.rest.json_db_utils import transform_json_refs_to_uuids
from avi.rest.json_io import JSONRenderer
from avi.rest.pb2dict import protobuf2dict_withrefs, protobuf2dict
from avi.rest.view_utils import process_view_request
from avi.rest.views import (
    RetrieveView, UpdateView, PostActionView, CreateView, ListView
)
from avi.rest.api_version import api_version
from avi.upgrade.migration.migrate_utils import (
    get_pkg_migrations, get_current_version_migrations,
    migration_versions_to_apply)
from avi.rest.error_list import MigrationError
from avi.upgrade.upgrade_state_utils import upgrade_state
from avi.upgrade.upgrade_utils import (
    check_free_space_for_upgrade, start_upgrade_coordinator, get_version, get_patch_version,
    get_se_version, get_disk_usage, get_disk_usage_se, upgrade_rollback_in_progress,
    get_cpu_usage, UPGRADE_ROLLEDBACK_FILE_PATH, DOCKER_UPGRADE_ROLLEDBACK_FILE_PATH,
    min_version_incompatible, ROLLBACK_REQUESTED_FILE_PATH, DOCKER_ROLLBACK_REQUESTED_FILE_PATH,
    check_all_se_upgrade_ready, upgrade_already_rebooted, se_upgrade_in_progress, UpgradeError,
    get_se_upgrade_preview, get_upgrade_status, validate_patch_version, patch_rollback_in_progress,
    extract_manifest_from_package, get_patch_image_name_from_manifest, get_memory_usage)
from avi.util.cluster_info import get_controller_vm_info
from avi.util.controller_fab_tasks import execute_task
from avi.util.exceptions import ServerError
from avi.util.host_utils import docker_mode, get_cmdline
from avi.util.protobuf import dict2protobuf
from avi.util.protobuf import enum_digit_to_name
from avi.util.sshciphers_util import update_ssh_ciphers_or_macs
from avi.util.cluster_info import get_controller_version
from avi.util.constants import PATCH_PATH, PATCH_IMAGE_PATH, PATCH_MANIFEST_YAML
from avi.util.pb_check import pb_message_check_recursive
from avi.infrastructure.db_transaction import db_transaction
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from permission.secure_channel_utils import export_se_secure_channel_mapping
from rest_framework import permissions
from rest_framework.response import Response
import subprocess32 as subprocess
from subprocess32 import CalledProcessError, check_output
from concurrent.futures import ThreadPoolExecutor, as_completed

log = logging.getLogger(__name__)
HTTP_RPC_TIMEOUT = 3.0
MAX_ALERT_CONFIG = 200


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


class ClusterDetail(RetrieveView, UpdateView):

    def get(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)

        cluster_pb = get_cluster_config()
        if cluster_pb.uuid:
            if kwargs.get('slug', False):
                if cluster_pb.uuid == kwargs.get('slug'):
                    rsp = protobuf2dict(cluster_pb)
                    ret = 200
                else:
                    rsp = {'error':'Cluster object not found'}
                    ret = 404
            else:
                rsp = protobuf2dict(cluster_pb)
                ret = 200
        else:
            log.error('Unable to get cluster config')
            rsp = {}
            ret = 503
        return Response(data=rsp, status=ret)

    def put(self, request, *args, **kwargs):

        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)

        pw_map = {}
        for node in request.DATA['nodes']:
            pw_map[node['ip']['addr']] = node.get('password')
            # Remove password from request.DATA so it will not be persisted
            if 'password' in node:
                del node['password']

        log.info('Cluster Dict: %s %s' % (type(request.DATA), request.DATA))

        cluster_pb = get_cluster_config()
        if not request.DATA.get('name', False) and cluster_pb.name:
            request.DATA['name'] = cluster_pb.name
        if not request.DATA.get('uuid', False) and cluster_pb.uuid:
            request.DATA['uuid'] = cluster_pb.uuid
        new_cluster_pb = dict2protobuf(request.DATA, ClusterPb())
        pb_message_check_recursive(new_cluster_pb)

        user = request.user.username if request.user else 'unknown'
        log.info('user %s changing cluster config.' % user)

        setup = ClusterSetup(new_cluster_pb, user, pw_map=pw_map)
        try:
            setup.start()
        except (Exception, SystemExit) as ex:
            setup.error(ex)
            raise ServerError('Cluster configuration failed. %s' % ex)

        log.info('Applying new cluster config: %s' % new_cluster_pb)
        return Response(data=pb2json(new_cluster_pb), status=200)


class ClusterReboot(PostActionView):
    def _export_license(self):
        exporter = ConfigExporter(upgrade_mode=True)
        data = exporter.license_export()
        with open('/var/lib/avi/etc/controller_license_config.json', 'w') as f:
            json.dump(data, f)
        log.info('Export license to file')


    def _cleanup_restore_iptables_file(self):
        """
        Cleanup restore IPtables file.
        Returns:
        """
        execute_task('cleanup_iptables_files', controller=True)


    def post(self, request, *args, **kwargs):
        role = get_role()
        if role != 'master':
            raise PermissionError('The cluster can only be rebooted from the '
                                  'controller cluster leader.')
        data = request.DATA
        log.info('cluster reboot: data = %s' % data)
        try:
            if data['mode'] in [clustering_pb2.REBOOT_CLEAN,
                                enum_digit_to_name(clustering_pb2.RebootMode,
                                                   clustering_pb2.REBOOT_CLEAN)]:
                self._export_license()
                export_se_secure_channel_mapping()
                self._cleanup_restore_iptables_file()
                # Cleanup SSH Ciphers and HMACS after reboot clean
                update_ssh_ciphers_or_macs([], [], local=True)
            reboot_cluster('127.0.0.1', data['mode'])
        except ServerError as err:
            log.exception(err)
            return HttpResponse(status=500)
        return JSONResponse({'status': 'Rebooting the cluster in %s mode.' % data['mode']},
                            status=200)


class ClusterRebootNode(PostActionView):
    def post(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)

        node_name = request.DATA.get('node_name', '')
        log.info('node reboot: node_name = %s' % node_name)

        node = ClusterConfig().get_node_from_name(node_name)
        try:
            reboot_cluster_node(node.vm_hostname)
        except ServerError as err:
            log.exception(err)
            return HttpResponse(status=500)
        return JSONResponse({'status': ('Rebooting the cluster node %s with ip '
                                        '%s') % (node_name, node.ip.addr)},
                            status=200)


class ClusterUpgradeStatusView(ListView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        status_pb = get_upgrade_status()
        status = protobuf2dict_withrefs(status_pb, request)
        log.info('upgrade status:%s' % status)
        return Response(data=status, status=200)

class ClusterUpgradeHistoryView(ListView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        log.info('get upgrade history')

        api = '/api/analytics/logs?type=2&filter=eq(event_id,[SYSTEM_UPGRADE_COMPLETE,' \
              'SYSTEM_ROLLBACK_COMPLETE,SYSTEM_UPGRADE_ABORTED,SYSTEM_ROLLBACK_ABORTED])' \
              '&page_size=9'
        log.info("%s", api)
        custom_view_kwargs = {'version': get_controller_version()}
        upgrade_events_rsp = process_view_request(api, 'GET', None, request.user,
                                                  custom_view_kwargs=custom_view_kwargs,
                                                  return_error_rsp=True)
        if upgrade_events_rsp.status_code != 200:
            log.error('%s Bad response status %d: %s' % (api, upgrade_events_rsp.status_code,
                                                         upgrade_events_rsp.data))
            return Response(data=upgrade_events_rsp.data, status=upgrade_events_rsp.status_code)

        log.info("%s", upgrade_events_rsp)
        upgrade_history_pb = SystemUpgradeHistory()

        for upg_ev in json.loads(upgrade_events_rsp.content)['results']:
            log.info("\n*** %s", upg_ev['event_details'])
            if 'system_upgrade_details' not in upg_ev['event_details']:
                log.info("** system_upgrade_details not in event_details **")
                continue
            if 'upgrade_status' not in upg_ev['event_details']['system_upgrade_details']:
                log.info("** upgrade_status not in system_upgrade_details **")
                continue
            upg_status_pb = SystemUpgradeState()
            json2pb(upg_status_pb,
                    upg_ev['event_details']['system_upgrade_details']['upgrade_status'],
                    replace=True)
            up = upgrade_history_pb.upgrade_events.add()
            up.CopyFrom(upg_status_pb)

        log.info("\nupgrade_history:%s\n", upgrade_history_pb)
        return Response(data=protobuf2dict_withrefs(upgrade_history_pb, request), status=200)

class ClusterUpgradeView(CreateView):

    @db_transaction
    def check_and_purge_alert_config(self, check_only):
        num_alerts = Alert.objects.count()
        log.info('check_only=%s, num_alerts=%d, max=%d' % (check_only, num_alerts,
                                                           MAX_ALERT_CONFIG))
        if num_alerts < MAX_ALERT_CONFIG:
            return
        if check_only and num_alerts > MAX_ALERT_CONFIG:
            raise Exception('Too many Alerts(%d) in the system,\n'
                            'Continuing with upgrade will keep the last %d alerts and purge '
                            'the rest.'
                            % (num_alerts, MAX_ALERT_CONFIG))
        older_alerts = Alert.objects.all().order_by('timestamp')[MAX_ALERT_CONFIG:].select_for_update()
        log.info('start purging %d alerts' % len(older_alerts))
        for alert in older_alerts:
            alert.delete()
        log.info('end purging %d alerts' % len(older_alerts))

    def post(self, request, *args, **kwargs):
        log.info('System Upgrade: begin checks')
        role = get_role(timeout=30)
        if role != 'master':
            raise PermissionError(
                'An upgrade can only be initiated from the controller cluster '
                'leader. Please retry at the leader.')
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        disruptive = request.DATA.get('disruptive', False)
        force = request.DATA.get('force', False)
        patch = request.DATA.get('patch', False)

        patch_img_name = ''
        text = check_output(["cat", "/bootstrap/VERSION"])
        cur_ver_dict = yaml.load(text)
        cur_ver = str(cur_ver_dict.get('Version'))
        cur_tag = str(cur_ver_dict.get('Tag', cur_ver))
        min_ver = new_ver = new_tag = 'new'
        skip_min_ver_chk = False
        img_name = ''

        ctlrs = Services.get_configured_cluster_members()
        controller_ips = [node['ip'] for node in ctlrs]

        # Necessary for upgrading and rolling back controllers on Kubernetes
        kubernetes_info = request.DATA.get("kubernetes_info", {})
        if kubernetes_info:
            if not docker_mode():
                raise DataException("Deployment is not a docker deployment. Kubernetes deployment"
                                    " only works with Docker.")

            kubernetes_password = kubernetes_info.get('password', '')
            kubernetes_cluster_ip = kubernetes_info.get('cluster_ip', '')
            kubernetes_service_account = kubernetes_info.get('service_account', '')
            selected_namespace = kubernetes_info.get('selected_namespace', 'default')
            target_image_location = kubernetes_info.get('target_image_location', None)
            previous_image_location = kubernetes_info.get('previous_image_location', None)

            cluster_parameters = [kubernetes_password, kubernetes_cluster_ip,
                                  kubernetes_service_account, selected_namespace,
                                  target_image_location, previous_image_location]
            if any(cluster_parameters) and not all(cluster_parameters):
                raise DataException("Kubernetes cluster parameters specified but not all the "
                                    "necessary parameters")

            resources = kubernetes_info.get('resources', [])
            for index, resource in enumerate(resources):
                resource_type = resource.get('resource_type', '')
                resource_name = resource.get('resource_name', '')
                node_parameters = [resource_type, resource_name]
                if not all(node_parameters):
                    raise DataException("Kubernetes node parameters for item (%d) specified but"
                                        " not all the necessary parameters" % index)

            kubernetes_asset_dir = "/vol/kubernetes-assets"
            try:
                os.makedirs(kubernetes_asset_dir)
            except OSError, e:
                if e.errno != os.errno.EEXIST:
                    raise
                log.info("Kubernetes assets folder already exists")

            with open("%s/kubernetes-info.txt" % kubernetes_asset_dir, 'w') as f:
                f.write(json.dumps(kubernetes_info))

            upgrade_request = {
                'se_fast': disruptive,
                'clean': request.DATA.get('clean', False),
                'force': force, 'patch': patch,
                'patch_img_name': patch_img_name,
                'suspend_on_failure': request.DATA.get('suspend_on_failure', False),
                'se_group_uuids': request.DATA.get('se_group_uuids')
            }
            upgrade_info = {'from_version':cur_tag,
                            'to_version': None,
                            'start_time': str(datetime.now())}
            log.info('Starting upgrade coordinator on ctlrs %s', controller_ips)
            start_upgrade_coordinator(controller_ips, upgrade_request, upgrade_info, patch=patch)

            rsp = {'status': 'upgrade in progress...'}
            return Response(data=rsp, status=200)

        if not isinstance(force, bool):
            raise DataException('Force must be a boolean value')
        if not isinstance(disruptive, bool):
            raise DataException('Disruptive must be a boolean value')

        # check if upgrade is already in progress
        if upgrade_already_rebooted() or se_upgrade_in_progress() or upgrade_rollback_in_progress():
            raise UpgradeError('Upgrade already in progress')

        val = upgrade_state()
        if val in [upgrade_pb.UPGRADE_STARTED, upgrade_pb.UPGRADE_WAITING,
                   upgrade_pb.UPGRADE_IN_PROGRESS]:
            raise UpgradeError('Upgrade already in progress')

        log.info('Checking disk space on controllers')
        try:
            check_free_space_for_upgrade(controller_ips)
        except (Exception, UpgradeError) as e:
            log.info('check_free_space failed')
            raise DataException(e)

        log.info('Upgrading the system.')
        try:
            _scheme, path = parse_fs_uri(request.DATA.get('image_path'))
        except AttributeError:
            path = ''

        if patch:
            # get the current version and the version of the pkg
            exit_code = os.system('cd /tmp && tar -xf %s bootstrap/VERSION' % (path))
            if exit_code != 0:
                raise DataException('Invalid Patch package. VERSION manifest file is missing.')
            text = check_output(["cat", "/tmp/bootstrap/VERSION"])
            new_ver_dict = yaml.load(text)
            new_ver = str(new_ver_dict.get('Version'))
            min_ver = str(new_ver_dict.get('min_version'))
            new_tag = str(new_ver_dict.get('Tag'))
            if LooseVersion(new_ver) != LooseVersion(cur_ver):
                log.error('Base Version %s is incompatible with %s.' %
                          (new_ver, cur_ver))
                raise DataException('Base Version %s is incompatible with current version %s' %
                                    (new_ver, cur_ver))
            validate_patch_version(cur_ver_dict, new_ver_dict, path)
            new_patch_ver = str(new_ver_dict.get('patch', ''))
            new_tag = "%s-%s" % (cur_tag, new_patch_ver)
            # create directory to store patch packages if not exists
            if not os.path.exists(PATCH_IMAGE_PATH):
                os.mkdir(PATCH_IMAGE_PATH)
            # extracting manifest to /tmp to figure out recent patch
            extract_manifest_from_package(path)
            manifest_path = "/tmp/%s" % PATCH_MANIFEST_YAML
            if os.path.exists(manifest_path):
                patch_img_name = get_patch_image_name_from_manifest(manifest_path)
                if not patch_img_name:
                    # cleaning up the directory if package found invalid
                    os.system('rm -rf /var/lib/avi/upgrade_pkgs/*')
                    raise DataException("Invalid package, patch type missing in manifest file.")
            else:
                # cleaning up the directory if package found invalid
                os.system('rm -rf /var/lib/avi/upgrade_pkgs/*')
                raise DataException("Invalid package, No manifest file found.")
            # move patch package in /var/lib/avi/patch_pkgs/ only in case of patch upgrade
            os.system('mv %s /var/lib/avi/patch_pkgs/%s' % (path, patch_img_name))
        else:
            patch_pkg_path = ''
            if 'patch_path' in request.DATA:
                try:
                    _scheme, patch_pkg_path = parse_fs_uri(request.DATA.get('patch_path'))
                except AttributeError:
                    patch_pkg_path = ''
            if not docker_mode():
                # Verify signature and checksum.
                log.info('Checking contents of upgrade pkg %s', path)
                try:
                    check_output(["/opt/avi/bootstrap/avibootstrap.sh", "--verify",
                                  "--var=Product:controller", "--keydir=/bootstrap",
                                  "--pkg=%s" % (path)])
                except CalledProcessError as e:
                    log.info('Checksum verification of %s failed' % os.path.basename(path))
                    raise DataException('Checksum verification of %s failed' %
                                        os.path.basename(path))

                # Verify that the target pkg has all the necessary migrations
                next_ver_migrations = get_pkg_migrations(path)
                current_ver_migrations = get_current_version_migrations()
                try:
                    migration_versions_to_apply(current_ver_migrations, next_ver_migrations)
                except MigrationError:
                    log.info('Upgrade package is incompatible with currently running version.')
                    raise DataException('Upgrade package is incompatible with currently '
                                        'running version.')

                os.system('cd /tmp && tar -xf %s bootstrap/VERSION' % (path))
                text = check_output(["cat", "/tmp/bootstrap/VERSION"])
                new_ver_dict = yaml.load(text)
                new_ver = str(new_ver_dict.get('Version'))
                min_ver = str(new_ver_dict.get('min_version'))
                new_tag = str(new_ver_dict.get('Tag'))
                # verifies packages in case of patch update with system upgrade
                if patch_pkg_path:
                    os.system('cd /tmp && tar -xf %s bootstrap/VERSION' % patch_pkg_path)
                    patch_version_dict = yaml.load(text)
                    patch_base_version = str(patch_version_dict.get('Version'))
                    if LooseVersion(new_ver) != LooseVersion(patch_base_version):
                        log.error('system package version %s is incompatible with patch '
                                  'version %s.' % (new_ver, patch_base_version))
                        # cleaning up the directory if package found invalid
                        os.system('rm -rf /var/lib/avi/upgrade_pkgs/*')
                        raise DataException('system package version %s is incompatible with '
                                            'patch version %s' % (new_ver, patch_base_version))
            else:
                skip_min_ver_chk = True
                cur_ver = str(cur_ver_dict.get('Tag'))
                cur_tag = str(cur_ver_dict.get('Tag'))
                try:
                    with tarfile.open(path, 'r') as img_file:
                        valid = False
                        try:
                            img_file.extract('repositories', path='/tmp')
                            valid = True
                        except KeyError:
                            pass
                    if not valid:
                        raise DataException('Upgrade package is not a valid docker image')
                    with open('/tmp/repositories', 'r') as f:
                        tags = json.loads(f.read())
                        if 'avinetworks/controller' not in tags.keys():
                            raise DataException('Upgrade package is not a valid Controller '
                                                'docker image')
                        new_ver = tags['avinetworks/controller'].keys()[0]
                        new_tag = new_ver
                except DataException:
                    raise
                except:
                    log.error(traceback.format_exc())
                    raise DataException('Could not validate Upgrade package')

            if not force:
                warnings = []
                if not skip_min_ver_chk:
                    # Check the min_version in the package to make sure running version is
                    # compatible
                    log.info('Checking min version. New %s, need at least %s, have %s' %
                            (new_ver, min_ver, cur_ver))
                    if min_version_incompatible('/bootstrap/VERSION', '/tmp/bootstrap/VERSION'):
                        min_version_warning = 'Version %s is incompatible with %s. Need at least' \
                                              ' %s.' % (new_ver, cur_ver, min_ver)
                        log.info('min_version_warning: %s' % min_version_warning)
                        warnings.append("Warning:" + min_version_warning)

                os.system('rm -f /tmp/bootstrap/VERSION')

                # Check if VSs will be disrupted
                preview = None
                try:
                    preview = get_se_upgrade_preview()
                except Exception as e:
                    log.error(traceback.format_exc())
                else:
                    if preview and len(preview.vs_errors):
                        disrupted_vs_warning = ['Warning: Traffic to following Virtual Services '
                                                'will be disrupted:']
                        for vs_error in preview.vs_errors:
                            reasons = ','.join(reason for reason in vs_error.reason)
                            dvs = '{:20}'.format('VS:' + DbBaseCache.uuid2name(vs_error.vs_uuid)) +\
                                '{:20}'.format(' Tenant:' + DbBaseCache.uuid2tenantname(vs_error.vs_uuid)) +\
                                ' Reason:' + ','.join(reason for reason in vs_error.reason)
                            disrupted_vs_warning.append(dvs)
                        log.info("disrupted_vs_warning: %s" % disrupted_vs_warning)
                        warnings.extend(disrupted_vs_warning)
                        warnings.append("")

                if cur_ver == new_ver:
                    same_version_warning = 'Already running version %s' % (new_ver)
                    log.info("same_version_warning: %s" % same_version_warning)
                    warnings.append("Warning: " + same_version_warning)
                    warnings.append("")

                # Check if SE's are upgrade ready
                try:
                    check_all_se_upgrade_ready()
                except Exception as e:
                    warnings.append("Warning: " + e.message)

                # check if number of alerts configured is > 200
                try:
                    self.check_and_purge_alert_config(check_only=True)
                except Exception as e:
                    warnings.append("Warning: " + e.message)

                if warnings:
                    final_warning = "\n".join(warnings)
                    log.error("upgrade_warnings: \n%s", final_warning)
                    raise DataException('%s' % final_warning)

            else:
                log.info('force option specified. Skipping all version and SE upgrade ready '
                         'checks.')

            if LooseVersion(cur_tag) > LooseVersion(new_tag):
                log.info('cur_tag(%s) is greater than the new_tag(%s)' % (cur_tag, new_tag))
                raise DataException('Running version(%s) is greater than the requested '
                                    'version(%s)' % (cur_tag, new_tag))

            img_name = 'controller.pkg' if not docker_mode() else 'controller_docker.tgz'
            if patch_pkg_path:
                extract_manifest_from_package(patch_pkg_path)
                manifest_path = "/tmp/%s" % PATCH_MANIFEST_YAML
                if os.path.exists(manifest_path):
                    patch_img_name = get_patch_image_name_from_manifest(manifest_path)
                    if not patch_img_name:
                        # cleaning up the directory if package found invalid
                        os.system('rm -rf /var/lib/avi/upgrade_pkgs/*')
                        raise DataException("Invalid package, patch type missing in manifest "
                                            "file.")
                else:
                    # cleaning up the directory if package found invalid
                    os.system('rm -rf /var/lib/avi/upgrade_pkgs/*')
                    raise DataException("Invalid package, No manifest file found.")
                # keep patch package in upgrade_pkgs in upgrade+patch scenario, will move to
                # curr partition to avoid patch package overriding after rollback happens
                pkg_path = '/var/lib/avi/upgrade_pkgs/%s' % patch_img_name
                if patch_pkg_path != pkg_path:
                    os.system('mv %s %s' % (patch_pkg_path, pkg_path))

            os.system('mv %s /var/lib/avi/upgrade_pkgs/%s' % (path, img_name))

        try:
            self.check_and_purge_alert_config(check_only=False)
        except Exception as e:
            log.error('failed to purge alerts, continue')
            pass

        if docker_mode():
            os.system('rm -f %s' % DOCKER_UPGRADE_ROLLEDBACK_FILE_PATH)
            os.system('rm -f %s' % DOCKER_ROLLBACK_REQUESTED_FILE_PATH)
        else:
            os.system('rm -f %s' % UPGRADE_ROLLEDBACK_FILE_PATH)
            os.system('rm -f %s' % ROLLBACK_REQUESTED_FILE_PATH)

        log.info('Setting cluster runtime state to upgrade in progress')
        ControllerWorkersStateMgr.set_upgrade_in_progress()

        transform_json_refs_to_uuids(request.DATA)

        upgrade_request = {
            'se_fast': disruptive,
            'clean': request.DATA.get('clean', False),
            'force': force, 'patch': patch,
            'patch_img_name': patch_img_name,
            'suspend_on_failure': request.DATA.get('suspend_on_failure', False),
            'se_group_uuids': request.DATA.get('se_group_uuids')
        }
        upgrade_info = {'from_version':cur_tag,
                        'to_version':new_tag,
                        'start_time': str(datetime.now())}
        log.info('Starting upgrade coordinator on ctlrs %s', controller_ips)
        start_upgrade_coordinator(controller_ips, upgrade_request, upgrade_info, patch=patch)

        rsp = {'status': 'upgrade in progress...'}
        return Response(data=rsp, status=200)

class UiUpgradeView(CreateView):
    def post(self, request, *args, **kwargs):
        rsp = {}
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)

        controller_ips = ['127.0.0.1']

        controller_arg_str = string.join([('-c %s' % ip)
                                          for ip in controller_ips], ' ')

        try:
            _, path = parse_fs_uri(request.DATA.get('image_path'))
            image_str = '-i %s' % path
        except AttributeError:
            image_str = '-i /tmp/avi/avi_ui.tar.gz'
        try:
            s_cmd = 'python /opt/avi/boot/upgrade_system.py %s %s --ui-only' %\
                 (controller_arg_str, image_str)
            s_cmd_args = shlex.split(s_cmd)
            subprocess.call(s_cmd_args, close_fds=True)
        except ValueError:
            msg = 'Could not find the images at %s.' % path
            raise ServerException(msg)

        rsp = {'status': 'upgrade in progress...'}
        return Response(data=rsp, status=200)


class ControllerVersionView(ListView):
    def get(self, request, *args, **kwargs):
        rsp = []
        ctlrs = get_cluster_config().nodes
        for ctlr in ctlrs:
            response_dict = {'name': ctlr.name,
                             'version': get_version(ctlr.vm_hostname)}
            patch_version = get_patch_version(ctlr.vm_hostname, 'controller')
            if patch_version:
                response_dict['patch'] = patch_version
            rsp.append(response_dict)
        return Response(data=rsp, status=200)


class UiVersionView(ListView):
    def get(self, request, *args, **kwargs):
        rsp = []
        ctlrs = get_cluster_config().nodes
        for ctlr in ctlrs:
            response_dict = {'name': ctlr.name,
                             'version': get_version(ctlr.ip.addr)}
            patch_version = get_patch_version(ctlr.ip.addr, 'ui')
            if patch_version:
                response_dict['patch'] = patch_version
            rsp.append(response_dict)
        return Response(data=rsp, status=200)


class UpgradeRollbackView(ListView):
    def post(self, request, *args, **kwargs):
        _ = request.DATA.get('controller')
        _ = request.DATA.get('se')
        rsp = {}
        return Response(data=rsp, status=200)


class ClusterRollbackView(CreateView):
    def post(self, request, *args, **kwargs):
        log.info('API: start rollback')
        patch_type = request.DATA.get('patch_type', None)
        role = get_role(timeout=30)
        if role != 'master':
            raise PermissionError(
                'A rollback can only be initiated from the controller cluster '
                'leader. Please retry at the leader.')
        rsp = {}
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)

        ctlrs = Services.get_configured_cluster_members()
        controller_ips = [node['ip'] for node in ctlrs]

        log.info('Rollback the system (USER REQUESTED)')

        # check if upgrade is already in progress
        if upgrade_already_rebooted() or se_upgrade_in_progress() or \
                upgrade_rollback_in_progress():
            raise UpgradeError('Upgrade already in progress')

        # check if rollback is already in progress
        if patch_rollback_in_progress():
            raise UpgradeError('Patch Rollback already in progress')

        text = check_output(["cat", "/bootstrap/VERSION"])
        cur_ver_dict = yaml.load(text)
        cur_ver = str(cur_ver_dict.get('Version'))
        cur_tag = cur_ver_dict.get('Tag', '')
        upgrade_request = {'rollback_requested': True}

        kubernetes_info = request.DATA.get("kubernetes_info", {})
        if kubernetes_info:
            kubernetes_password = kubernetes_info.get('password', '')
            kubernetes_cluster_ip = kubernetes_info.get('cluster_ip', '')
            kubernetes_service_account = kubernetes_info.get('service_account', '')
            selected_namespace = kubernetes_info.get('selected_namespace', 'default')
            target_image_location = kubernetes_info.get('target_image_location', None)
            previous_image_location = kubernetes_info.get('previous_image_location', None)

            cluster_parameters = [kubernetes_password, kubernetes_cluster_ip,
                                  kubernetes_service_account, selected_namespace,
                                  target_image_location, previous_image_location]
            if any(cluster_parameters) and not all(cluster_parameters):
                raise DataException("Kubernetes cluster parameters specified but not all "
                                    "the necessary parameters")

            resources = kubernetes_info.get('resources', [])
            for index, resource in enumerate(resources):
                resource_type = resource.get('resource_type', '')
                resource_name = resource.get('resource_name', '')
                node_parameters = [resource_type, resource_name]
                if not all(node_parameters):
                    raise DataException("Kubernetes node parameters for item (%d) specified "
                                        "but not all the necessary parameters" % index)

            kubernetes_asset_dir = "/vol/kubernetes-assets"
            try:
                os.makedirs(kubernetes_asset_dir)
            except OSError, e:
                if e.errno != os.errno.EEXIST:
                    raise
                log.info("Kubernetes assets folder already exists")

            with open("%s/kubernetes-info.txt" % kubernetes_asset_dir, 'w') as f:
                f.write(json.dumps(kubernetes_info))

            upgrade_info = {
                'from_version': cur_tag,
                'to_version': None,
                'start_time': str(datetime.now())
            }
            log.info('Starting upgrade_coordinator(rollback) on ctlrs %s', controller_ips)
            start_upgrade_coordinator(controller_ips, upgrade_request,
                                      upgrade_info, rollback=True)

            rsp = {'status': 'rollback in progress...'}
            return Response(data=rsp, status=200)

        #FIXME: on any server error here, set upgrade status to ABORTED ?
        #FIXME: check for rollback in progress
        this_uuid = get_controller_vm_info()[0]

        if docker_mode():
            os.system('rm -f %s' % DOCKER_UPGRADE_ROLLEDBACK_FILE_PATH)
            os.system('rm -f %s' % DOCKER_ROLLBACK_REQUESTED_FILE_PATH)
        else:
            os.system('rm -f %s' % UPGRADE_ROLLEDBACK_FILE_PATH)
            os.system('rm -f %s' % ROLLBACK_REQUESTED_FILE_PATH)

        if patch_type:
            prev_tag = cur_tag

            fd = open('/bootstrap/VERSION', 'r')
            data = yaml.load(fd)
            # Do validations before rollback patch starts
            prev_patch_version = _validate_patch_rollback_from_patch_type(data, patch_type)

            # use manifest from tmp path, which is extracted by last patch which applied
            # for SE we do not extract pkg on controller so patch_manifest is not present on
            # PATCH_PATH so for rollback for keeping generic approach make use of
            # /tmp/patch_manifest.yml
            patch_manifest_path = os.path.join('/tmp/patch_manifest.yml')

            if not os.path.exists(patch_manifest_path):
                raise ServerError("Patch  manifest file %s not found" % patch_manifest_path)
            upgrade_request.update({'patch_version': prev_patch_version, 'patch_type': patch_type})
            log.info("patch version is %s and patch rollback type is %s " %
                     (prev_patch_version, patch_type))
        else:
            if docker_mode():
                MOUNT_POINT = '/vol'
                if not os.path.exists("%s/root1/VERSION" % MOUNT_POINT) or not \
                        os.path.exists("%s/root2/VERSION" % MOUNT_POINT):
                    log.info('root1 or root2 not available, nothing to rollback')
                    raise ServerError('System not upgraded earlier, nothing to rollback')
                cur_root, prev_root = ('%s/curr' % MOUNT_POINT, '%s/prev' % MOUNT_POINT)
            else:
                MOUNT_POINT = '/host'
                if not os.path.exists("%s/root1" % MOUNT_POINT) or not \
                        os.path.exists("%s/root2" % MOUNT_POINT):
                    log.info('/host/root1 or /host/root2 not available, nothing to rollback')
                    raise ServerError('System not upgraded earlier, nothing to rollback')
                cur_root, prev_root = get_cmdline()

            if not cur_root or not prev_root:
                log.info('Could not find current and previous root '
                         'filesystems, unable to rollback')
                raise ServerError('Could not find current and previous root '
                                  'filesystems, unable to rollback')
            text = check_output(["cat", prev_root + "/bootstrap/VERSION"])
            prev_ver_dict = yaml.load(text)
            prev_ver = str(prev_ver_dict.get('Version'))
            prev_tag = prev_ver_dict.get('Tag', '')

            if not cur_tag or not prev_tag:
                log.info('Could not find current and previous version tags, '
                         'unable to rollback')
                raise ServerError('Could not find current and previous version tags, '
                                  'unable to rollback')

            if LooseVersion(prev_tag) > LooseVersion(cur_tag):
                errstr = 'Cannot rollback from a older version(%s) to newer version(%s)' % \
                         (cur_tag, prev_tag)
                log.info(errstr)
                raise ServerError(errstr)

        log.info('Setting cluster runtime state to upgrade in progress (rollback)')
        ControllerWorkersStateMgr.set_upgrade_in_progress(True)

        upgrade_info = {'from_version':cur_tag, 'to_version':prev_tag,
                        'start_time': str(datetime.now())}
        log.info('Starting upgrade_coordinator(rollback) on ctlrs %s', controller_ips)
        start_upgrade_coordinator(controller_ips, upgrade_request,
                                  upgrade_info, rollback=True)

        rsp = {'status': 'rollback in progress...'}
        return Response(data=rsp, status=200)


def _validate_patch_rollback_from_patch_type(data, patch_type):
    """

    :param patch_type:
    :return:
    """
    if patch_type == "se":
        prev_patch_key = "prev_se_patch"
        patch_key = "se_patch"
    else:
        # for full and controller patch
        prev_patch_key = "prev_patch"
        patch_key = "patch"

    prev_patch_version = data.get(prev_patch_key, None)
    patch_version = data.get(patch_key, None)

    # Rollback happen only once to its previous version only. Multiple rollback one after
    # another not supported
    if patch_version and prev_patch_version and (patch_version == prev_patch_version):
        raise ServerError("System is already rolled back to previous version.")

    if not prev_patch_version:
        raise ServerError("System is already at base version")

    return prev_patch_version


def _get_se_ip(se_pb):
    ip = None
    try:
        ip = SecureChannelMapping.objects.get(uuid=se_pb.uuid).protobuf().local_ip
    except ObjectDoesNotExist:
        pass
    # If no local IP, try using remote IP
    if not ip:
        if se_pb.HasField('mgmt_vnic'):
            vnics = se_pb.mgmt_vnic.vnic_networks
        else:
            vnics = []
        if len(vnics) > 0:
            ip = vnics[0].ip.ip_addr.addr
    return ip


class SeVersionView(ListView):
    def get_se_details(self, se):
        se_pb = se.protobuf()
        patch_version = None
        ip = _get_se_ip(se_pb)
        if not ip:
            version = 'Unknown'
        else:
            try:
                version = get_se_version(ip)
            except:
                version = 'Unknown'
            patch_version = get_patch_version(ip, "se")
        response_dict = {'name': se_pb.name, 'version': version}
        if patch_version:
            response_dict['patch'] = patch_version
        return response_dict

    def get(self, request, *args, **kwargs):
        ses = ServiceEngine.objects.all()
        rsp = []

        # Added multi-threading support for getting SE. Limiting max threads to 15,
        # to prevent memory spike.
        # Observation : On a setup of 43 SEs, N/6 threads were needed to prevent Service Timeout
        if ses.exists():
            num_threads = 1 + round(ses.count() / 4) if ses.count() / 4 < 15 else 15
            pool = ThreadPoolExecutor(num_threads)
            threads_pool = [pool.submit(self.get_se_details, se) for se in ses]
            rsp = [r.result() for r in as_completed(threads_pool, timeout=60)]
        return Response(data=rsp, status=200)


class ControllerDiskUsageView(RetrieveView):
    model = DiskUsageInfoProto

    @api_version
    def do_get_action(self, request, *args, **kwargs):
        """
        Retrieves the Disk usage info; We use do_get_action
        instead of 'get' so that 'api_versioning' can be done
        via the api_versioning infra.
        """
        du_pb = DiskUsageInfo()
        controllers = get_cluster_config().nodes
        for ctlr in controllers:
            disk_info = get_disk_usage(ctlr.ip.addr)
            du = du_pb.disk_usage_on_nodes.add()
            du.name = ctlr.name
            json2pb(du.disk_info, disk_info)
        return Response(pb2json(du_pb))


class ControllerMemoryUsageView(RetrieveView):
    model = MemoryUsageInfoProto

    @api_version
    def do_get_action(self, request, *args, **kwargs):
        """
        Retrieves the memory usage info.  We use do_get_action
        to ensure api_versioning can be done via the api_version
        infra.
        """
        mu_pb = MemoryUsageInfo()
        controllers = get_cluster_config().nodes
        for ctrl in controllers:
            mem = mu_pb.mem_usage_on_nodes.add()
            mem.name = ctrl.name
            mem_info = get_memory_usage(ctrl.ip.addr)
            json2pb(mem.mem_info, mem_info)
        return Response(pb2json(mu_pb))

class ServiceengineDiskUsageView(ListView):
    model = DiskUsageInfoProto

    @api_version
    def do_get_action(self, request, *args, **kwargs):
        """
        Retrieves the service-engine usage info.  Note it is not
        a bounded operation if the number of service-engines are
        high.
        """
        du_pb = DiskUsageInfo()
        ses = ServiceEngine.objects.all()
        for se in ses:
            se_pb = se.protobuf()
            ip = _get_se_ip(se_pb)
            if not ip:
                usage = 'Unknown'
            else:
                try:
                    usage = get_disk_usage_se(ip)
                except:
                    usage = 'Unknown'

            du = du_pb.disk_usage_on_nodes.add()
            du.name = se_pb.name
            json2pb(du.disk_info, usage)
        return Response(pb2json(du_pb))


class ControllerCPUUsageView(RetrieveView):
    model = CPUUsageInfoProto

    @api_version
    def do_get_action(self, request, *args, **kwargs):
        """
        Retrieves the CPU usage info.  api_versioning
        will be done via the api_version.
        """
        cpu_pb = CPUUsageInfo()
        controllers = get_cluster_config().nodes
        for ctrl in controllers:
            cpu = cpu_pb.cpu_usage_on_nodes.add()
            cpu.name = ctrl.name
            cpu_info = get_cpu_usage(ctrl.ip.addr)
            json2pb(cpu.cpu_info, cpu_info)
        return Response(pb2json(cpu_pb))


class ClusterStatusView(ListView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        rsp = get_cluster_runtime_state()
        return Response(data=rsp, status=200)


class ClusterNodeStatusView(ListView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        rsp = get_cluster_runtime_state(nodes_only=True)
        return Response(data=rsp, status=200)
# End of file
