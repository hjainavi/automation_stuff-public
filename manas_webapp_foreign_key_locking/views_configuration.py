
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
import json
import os
import shlex
import subprocess32 as subprocess
import tempfile
import time, datetime
from rest_framework.response import Response

import avi.rest.views as views
from avi.rest.json_io import JSONRenderer,CustomFileResponse
from avi.rest.file_service_utils import parse_fs_uri, serve_file_via_nginx
from avi.rest.error_list import DataException
from avi.rest.pb2model import protobuf2model
from avi.rest.pb2dict import protobuf2dict_withrefs
from avi.rest.url_utils import slug_from_uri
from avi.util.file_utils import copy_file_to_all_controllers

from avi.config_migration.export_import import ConfigExporter, ConfigImporter
from avi.util.cluster_info import get_version_file_content

_EXPORTED_CONFIG = '/var/lib/avi/backup/views_config.json'
_MIGRATED_CONFIG = '/var/lib/avi/backup/views_config_migrated.json'

_TMP_EXPORTED_FILE = '/var/lib/avi/downloads/tmp_exported_config.json'
_DOWNLOADS_DIRECTORY = '/var/lib/avi/downloads/'

log = logging.getLogger(__name__)

class GetVersionView(views.RetrieveView):
    """
    Return the content of file VERSION
    """
    def get(self, request, *args, **kwargs):
            s = get_version_file_content()
            return Response(s)

def _export_config_data_as_string(tenant_name):
    exporter = ConfigExporter()

    data = exporter.configuration_export(tenant_name)
    JSONRenderer.allow_password = True
    r = JSONRenderer()
    data = r.render(data, renderer_context={'indent' : 4 })
    return data

def send_data_as_json_file_response(data):
    JSONRenderer.allow_password = True
    r = JSONRenderer()
    rsp = CustomFileResponse()
    data = r.render(data, renderer_context={'indent' : 4 })
    exported_file_path = _TMP_EXPORTED_FILE
    if not os.path.exists(_DOWNLOADS_DIRECTORY):
        os.makedirs(_DOWNLOADS_DIRECTORY)
    with open(exported_file_path, 'w') as f:
        f.write(data)
    serve_file_via_nginx(rsp,exported_file_path)
    return rsp

class ExportConfigView(views.CreateView, views.RetrieveView):
    """
    Export objects configuration, globally or under one tenant
    """
    def _process_export(self, request, *args, **kwargs):
        if 'tenant_ref' in request.QUERY_PARAMS:
            kwargs['tenant'] = slug_from_uri(request.QUERY_PARAMS['tenant_ref'])
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        passphrase = None
        skip_sensitive_fields = False
        if request.method.lower() == 'post':
            passphrase = request.DATA.get('passphrase', None)
            skip_sensitive_fields = request.DATA.get('skip_sensitive_fields', False)
        elif request.method.lower() == 'get':
            passphrase = request.QUERY_PARAMS.get('passphrase', None)
            skip_sensitive_fields = request.QUERY_PARAMS.get('skip_sensitive_fields', False)

        if not skip_sensitive_fields and not passphrase:
            raise DataException('Passphrase is required for exporting configuration!')

        uuid_refs = request.QUERY_PARAMS.get('uuid_refs', False)
        skip_default = request.QUERY_PARAMS.get('skip_default', False)
        ignore_extension = request.QUERY_PARAMS.get('ignore_extension', False)
        include_name = request.QUERY_PARAMS.get('include_name', False)
        recurse = 'recurse' in request.QUERY_PARAMS
        upgrade_mode = 'full_system' in request.QUERY_PARAMS
        exporter = ConfigExporter(passphrase=passphrase, uuid_refs=uuid_refs,
            skip_default=skip_default, ignore_extension=ignore_extension,
            include_name=include_name, upgrade_mode=upgrade_mode,
            skip_sensitive_fields=skip_sensitive_fields)
        obj_type = request.QUERY_PARAMS.get('obj_type', [])
        if obj_type:
            obj_type = obj_type.split(',')
        search = request.QUERY_PARAMS.get('search', [])
        if search:
            search = search.split(',')
        data = exporter.configuration_export(self.tenant.name, obj_type=obj_type, search=search, recurse=recurse)
        return send_data_as_json_file_response(data)

    def post(self, request, *args, **kwargs):
        renderer_classes = (JSONRenderer,)
        return self._process_export(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        #POST preferred method, maintain GET for backwards compatibility
        renderer_classes = (JSONRenderer,)
        return self._process_export(request, *args, **kwargs)

class ExportVirtualServiceView(views.RetrieveView):
    def get(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        include_certs = request.QUERY_PARAMS.get('include_certs', False)
        vs_uuid = kwargs.get('slug')
        data = ConfigExporter().virtualservice_export(vs_uuid, include_certs=include_certs)
        return send_data_as_json_file_response(data)
'''
class BackupConfigView(views.CreateView, views.ListView):
    model = Backup
    serializer_class = BackupSerializer

    """
    Backup object configurations to a file
    """

    @db_transaction
    def _create_db_object(self, request, file_name, timestamp):
        pb = BackupProto()
        pb.name = file_name
        pb.timestamp = timestamp
        pb.username = request.user.username
        url = '/api/fileservice?uri=controller://backups/%s' % file_name
        pb.file_url = url
        pb.tenant_uuid = self.tenant.uuid

        protobuf2model(pb, None, False, skip_unfinished_pb=False)
        return pb

    def post(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        data = _export_config_data_as_string(self.tenant.name)
        current_time = datetime.datetime.now()
        timestamp = time.mktime(current_time.timetuple())
        timestamp_s = current_time.strftime("%Y%m%d_%H%M%S")
        file_name = "backup_%s.txt" % timestamp_s
        backup_dir = '/opt/avi/backups'
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        path = '%s/%s' % (backup_dir, file_name)
        with open(path, "w") as f:
            f.write(data)

        copy_file_to_all_controllers(path, path)
        pb = self._create_db_object(request, file_name, timestamp)

        return Response(protobuf2dict_withrefs(pb, request), status=201)

class BackupConfigViewDetail(views.DetailView):
    model = Backup
    serializer_class = BackupSerializer
'''

class ImportConfigView(views.CreateView):
    """
    Import objects from a config file
    """
    def _import_config(self, data, request):
        if not data:
            raise views.InvalidParamsException(
                'Import configuration file or data not provided')
        uri = data.get('uri')
        configuration = data.get('configuration')
        if uri:
            scheme, path = parse_fs_uri(data['uri'])
            if not path or not os.path.exists(path):
                raise views.InvalidParamsException('Specified import configuration file is not valid')

            with open(path) as f:
                buf = f.read()
            configuration = json.loads(buf)
        elif not configuration:
            raise views.InvalidParamsException(
                'Import configuration file or data not provided')

        config_meta = configuration.get('META', {})

        if config_meta.get('upgrade_mode'):
            raise DataException('Cannot use import API with upgrade config file')
        config_meta['upgrade_mode'] = False  #make sure the file contains the upgrade flag

        if config_meta and config_meta.get('supported_migrations', None):
            config_dir = os.path.dirname(_EXPORTED_CONFIG)
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)

            with open(_EXPORTED_CONFIG, 'w') as f:
                json.dump(configuration, f)

            if os.path.isfile(_MIGRATED_CONFIG):
                os.unlink(_MIGRATED_CONFIG)

            env = os.environ.copy()
            env['PYTHONPATH'] = '/opt/avi/python/lib:/opt/avi/python/bin/portal'
            env['DJANGO_SETTINGS_MODULE'] = 'portal.settings_full'
            s_cmd = 'python /opt/avi/python/bin/upgrade/config_migrator.py --config-file %s ' \
                    '--output-file %s' % (_EXPORTED_CONFIG, _MIGRATED_CONFIG)
            s_cmd_args = shlex.split(s_cmd)
            subprocess.call(s_cmd_args, env=env)

            if not os.path.isfile(_MIGRATED_CONFIG):
                raise DataException('Config Migration Failed.')

            with open(_MIGRATED_CONFIG) as f:
                buf = f.read()
            configuration = json.loads(buf)

        force_mode = request.QUERY_PARAMS.get('force_mode', False)
        importer = ConfigImporter(force_mode=force_mode,cloud=self.cloud,tenant=self.tenant)
        ignore_uuid = request.QUERY_PARAMS.get('ignore_uuid', False)
        importer.keep_uuid = not ignore_uuid
        passphrase = request.DATA.get('passphrase', None)
        importer.passphrase = passphrase
        importer.default_to_fully_qualified_objects(configuration)
        importer.check_exported_config(configuration)
        if not force_mode:
            error_rsp = importer.check_references(configuration)
            if error_rsp:
                return Response(status=400, data=error_rsp)

        importer.configuration_import(configuration, request=request)
        return Response(status=201)

    def post(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        return self._import_config(request.DATA, request)
