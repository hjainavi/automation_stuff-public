
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
import copy
import shutil
import tarfile
import glob
import json
import shlex
import re
import itertools
import string
import yaml
import subprocess32 as subprocess

from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from avi.infrastructure.rpc_channel import RpcChannel
from avi.infrastructure.rpc_channel import AviRpcController
from avi.infrastructure.db_base_cache import DbBaseCache
from avi.infrastructure.db_transaction import db_transaction

from avi.rest.json_io import JSONRenderer, CustomFileResponse
from avi.rest.views import RetrieveView, InvalidParamsException, CreateView, ListView
from avi.rest.error_list import PermissionError, DataException, ServerException
from avi.rest.file_service_utils import (
    parse_fs_uri,
    serve_file_via_nginx
)
from avi.rest.pb2model import protobuf2model
from avi.rest.debug_se_utils import mergecap_vs_file, PCAP_DIR, parse_file
from avi.util.pb_post_save_transform import pb_message_post_save_transform
from avi.util.time_utils import epoch_to_iso_string
from avi.util.controller_fab_tasks import execute_task
from avi.util.file_utils import copy_file_to_all_other_controllers
from avi.util.file_utils import remove_files_from_all_other_controllers
from avi.util.host_utils import docker_mode
from avi.util.gslb_util import get_glb_cfg
from avi.util.gslb_util import create_gsops_rpc
from avi.util.gslb_util import gslb_file_upload_checks
from avi.util.gslb_util import gslb_file_delete_checks
from avi.util.gslb_util import gslb_file_upload_process
from avi.util.gslb_util import gslb_fileops_response
from avi.util.pb_resolve import GslbGeoDbProfileResolve
from avi.util.must_check import GslbGeoDbProfileCheck
from avi.util.gslb_api_converter import DS_GEO
from avi.util.safenet_utils import get_safenet_version
from avi.tech_support.tech_support_utils import get_techsupport_status
from avi.infrastructure.clustering.cluster_utils import get_role
import avi.protobuf.syserr_pb2 as syserr
from avi.protobuf.gslb_runtime_pb2 import GSLB_UPDATE
from avi.protobuf.gslb_rpc_pb2 import GslbSiteOpsService_Stub
from api.models import (VirtualService, ControllerProperties)

log = logging.getLogger(__name__)
SE_OVA_DIR = '/opt/avi/se_ova/'
SE_OVA_TAR = 'se.ova'
SE_SCRIPT = '/opt/avi/scripts/generate_se_image.py'
CONTROLLER_DIR = '/var/lib/avi/'
CUSTOM_IPAMDNS_SCRIPTS_DIR = '/var/lib/avi/ipamdnsscripts/'

fs_uri_map = {
    'hsmpackages'          : CONTROLLER_DIR + "hsmpackages",
    'vs-pcap'              : CONTROLLER_DIR + "vs-pcap",
    'uploads'              : CONTROLLER_DIR + "uploads",
    'upgrade_pkgs'         : CONTROLLER_DIR + "upgrade_pkgs",
    'backup'               : CONTROLLER_DIR + "backup",
    'archive'              : CONTROLLER_DIR + "archive",
    'archive/stack_traces' : CONTROLLER_DIR + "archive/stack_traces",
    'gslb'                 : CONTROLLER_DIR + "gslb",
    'gslb/staging'         : CONTROLLER_DIR + "gslb/staging",
    'gslb/staged'          : CONTROLLER_DIR + "gslb/staged",
    'tech_support'         : CONTROLLER_DIR + "tech_support",
    'tech_support/status'  : CONTROLLER_DIR + "tech_support/status",
    'ipamdnsscripts'       : CONTROLLER_DIR + "ipamdnsscripts"
    }

class PathInvalidException(DataException):
    pass

def _file_uri(request, uri):
    return '%s://%s/api/fileservice?uri=%s' % (request.scheme,
                                               request.get_host(), uri)

class FileServiceView(RetrieveView):
    renderer_classes = (JSONRenderer,)
    parser_classes = (JSONParser,)

    def generate_md5_checksum(self, file_path):
        import hashlib
        BLOCKSIZE = 1048576
        hasher = hashlib.md5()
        with open(file_path, 'rb') as afile:
            buf = afile.read(BLOCKSIZE)
            while len(buf) > 0:
                hasher.update(buf)
                buf = afile.read(BLOCKSIZE)
        return hasher.hexdigest()

    def _read_meta_file(self, meta_path, file_dict):
        if os.path.isfile(meta_path):
            with open(meta_path, 'r') as f:
                meta = json.load(f)
                file_dict.update(meta)

    def parse_upgrade_pkg(self, filename, file_dict):
        try:
            if docker_mode():
                cmd = 'tar --to-stdout -xvf %s repositories' % filename
                s = subprocess.check_output(cmd.split())
                repositories = json.loads(s)
                tag = repositories.values()[0].keys()[0]
                version, build, _ = tag.split('-')
                file_dict['version'] = {
                    'Product': 'controller',
                    'ProductName': 'Avi Cloud Controller',
                    'Version' : version,
                    'build': build,
                    'Tag': tag
                }
            else:
                cmd = 'tar --to-stdout -xvf %s bootstrap/VERSION' % filename
                s = subprocess.check_output(cmd.split())
                file_dict['version'] = yaml.load(s)
        except:
            pass

    def _get_file(self, request, *args, **kwargs):
        """
        Additional Check to prevent directory traversal for fileservices
        - ../ are not allowed.
        - All file endpoints are allowed
        - sub dir can only be one of:
            * hsmpackages
            * uploads
            * upgrade_pkgs
            * archive
            * archive/stack_traces,
            * backup
            * vs-pcap
            * gslb
            * gslb/staging
            * gslb/staged
            * tech_support
            * tech_support/status
        """
        uri = request.QUERY_PARAMS['uri']
        scheme, path = parse_fs_uri(uri)
        if '..' in path:
            raise PermissionError('Invalid URI :%s '  %(uri))

        sub_uri = ""
        if os.path.isdir(path):
            sub_uri = uri.replace('controller://','')
            abs_path = fs_uri_map.get(sub_uri, None)

            if not abs_path:
                raise PermissionError('Invalid Directory URI :%s '  %(uri))

        # Deal with the special case URI of vs-pcap scheme
        if scheme == 'vs-pcap':
            if path:
                #force mergecap
                vs_uuid = path
                path = mergecap_vs_file(vs_uuid)
                if not path:
                    raise DataException('No pcap files found for virtual service %s'
                                        % vs_uuid)
            else:
                path = PCAP_DIR
        elif not path:
            raise PathInvalidException('Invalid URI specified')
        if not os.path.exists(path):
            raise PathInvalidException('Specified URI does not exist: %s' % uri)
        if os.path.isdir(path):

            rsp_files = {}
            rsp_files['results'] = []
            files = self._filter_tenant_files(scheme, path)
            for filename in files:

                if not filename or filename.endswith('.meta'):
                    continue
                file_path = '%s/%s' % (path, filename)
                if os.path.isdir(file_path):
                    continue
                file_dict = {}
                if 'vs' in filename:
                    vs_uuid = re.split('[_ .]', filename)[1]
                    log.info("vs uuid %s", vs_uuid)
                    file_dict['name'] = DbBaseCache.uuid2name(vs_uuid) #vs-uuid.pcap
                if scheme == 'vs-pcap' or path.endswith('vs-pcap'):
                    file_url = 'controller://vs-pcap/' + filename
                    file_dict['url'] = _file_uri(request, file_url)
                    if file_path.endswith('.pcap'):
                        meta_path = file_path.replace('.pcap', '.meta')
                    elif file_path.endswith('.txt'):
                        meta_path = file_path.replace('.txt', '.meta')
                    elif file_path.endswith('.tar'):
                        meta_path = file_path.replace('.tar', '.meta')
                    self._read_meta_file(meta_path, file_dict)
                else:
                    file_dict['url'] = _file_uri(
                        request, os.path.join(uri, filename))
                stat = os.stat(file_path)
                file_dict['modified'] = epoch_to_iso_string(stat.st_mtime)
                file_dict['timestamp'] = stat.st_mtime
                if 'compute_checksum' in request.QUERY_PARAMS:
                    file_dict['md5checksum'] = self.generate_md5_checksum(file_path)
                if not os.path.isdir(file_path):
                    file_dict['size'] = stat.st_size
                else:
                    file_dict['size'] = 'dir'
                if sub_uri == 'archive':
                    stack_trace_file = glob.glob('%s/stack_traces/*%s*' %(abs_path, filename.split('.')[1]))
                    if stack_trace_file:
                        with open(stack_trace_file[0]) as f:
                            file_dict['stack_trace'] = f.read()
                if sub_uri == 'tech_support':
                    file_dict['status'] = get_techsupport_status(filename=filename)
                if os.path.basename(path) == 'upgrade_pkgs':
                    self.parse_upgrade_pkg(file_path, file_dict)
                rsp_files['results'].append(file_dict)
            rsp_files['count'] = len(rsp_files['results'])

            #sort by timestamp
            rsp_files['results'].sort(key=lambda x: x.get('timestamp', 0),
                                      reverse=True)
            for f in rsp_files['results']:
                f.pop('timestamp', 0)
            rsp = Response(rsp_files)
        else:
            rsp = CustomFileResponse()
            serve_file_via_nginx(rsp, path)
        return rsp

    def get(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)

        rsp = self._get_file(request, args, kwargs)
        return rsp

    def _filter_tenant_files(self, scheme, path):
        """
        Filter pcap files belongs to logged in user tenant.

        Args:
            scheme:
            path:

        Returns: list of files

        """
        files = os.listdir(path)
        # return all files if schema is not vs-pcap
        if scheme != 'vs-pcap' and not path.endswith('vs-pcap'):
            return files

        filtered_files = []
        # if all tenants to be allowed verify file against all
        if self.all_tenants:
            filters = {}
        else:
            filters = {'tenant_ref__in' : [self.tenant]}
        vs_list = VirtualService.objects.filter(**filters).values_list('uuid', flat=True)
        # Inner parsing function to parse filtered cap files and avoid None Object exception

        if files:
            filtered_files = itertools.ifilter(lambda file_name: parse_file(file_name) in vs_list, files)
        return filtered_files

    def delete(self, request, *args, **kwargs):
        """
        This function deletes files using standard http syntax.
        """
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)

        uri = request.QUERY_PARAMS['uri']
        _, path = parse_fs_uri(uri)

        if os.path.isdir(path):
            raise PathInvalidException('Cannot purge a directory')

        if os.path.dirname(path) == CUSTOM_IPAMDNS_SCRIPTS_DIR.rstrip('/'):
            remove_files_from_all_other_controllers([path])
        gslb_file_delete_checks(path)
        if os.path.isfile(path):
            os.unlink(path)
        return Response(status=204)

    @db_transaction
    def post(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)

        case_number = request.DATA.get('case_number', None)
        token = request.DATA.get('portal_token', None)
        if not case_number:
            raise ServerException('Missing Case number')

        ctrl_prop_pb = ControllerProperties.objects.get().protobuf(decrypt=True)
        if not token:
            token = getattr(ctrl_prop_pb, 'portal_token', None)
            if not token:
                raise ServerException('Missing Token to access the portal')
        else:
            ctrl_prop_pb.portal_token = token
            protobuf2model(ctrl_prop_pb, None, False, skip_unfinished_pb=False)

        uri = request.QUERY_PARAMS['uri'] + request.DATA['filename']
        _, outfile = parse_fs_uri(uri)

        if os.path.isfile(outfile):
            cmd = '/opt/avi/scripts/attach2case.py -H avinetworks.com -t %s -P -p https %s %s' %(token, case_number, outfile)
            proc = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            _, err = proc.communicate()
            if err:
                raise ServerException('Upload Failed: %s' %err)
            else:
                return Response(data='Upload Successful', status=200)
        else:
            raise ServerException('Please provide a valid core file name')

class FileServiceUploadView(CreateView):
    """
    Generic interface to upload/delete files into the controller-cluster.
    Replication to all the cluster-members is done in this interface. Extend
    to appropriate flavors by kwargs- HSM, GSLB.
    """

    def hsmpackages_check(self, dest_dir, file_name):
        """
        HSM specific checks:
        The current implementation is constrained to the following:
          - Path needs to be hsmpackages
          - File needs to be nfast.tar
        """
        if dest_dir != '/var/lib/avi/hsmpackages':
            raise InvalidParamsException('File URI must be controller://hsmpackages')
        if (file_name != 'thales.tar' and
                file_name != "thales_security_world.tar" and
                file_name != "safenet.tar" and
                file_name != "cloudhsm.tar"):
            if file_name.startswith("thales"):
                raise PathInvalidException(
                'Supported packages are thales.tar and thales_security_world.tar')
            elif file_name.startswith("safenet"):
                raise PathInvalidException(
                    'Supported packages are safenet.tar')
            else:
                raise PathInvalidException('Package not supported')
        return

    def custom_ipamdnsscripts_check(self, dest_dir, file_name):
        """
        Allows only python files with PEP8 module name enforced
        """
        if dest_dir != CUSTOM_IPAMDNS_SCRIPTS_DIR.rstrip('/'):
            raise InvalidParamsException("File URI must be "
                        "controller://ipamdnsscripts")

        # PEP8 file requirements
        if not file_name.endswith('.py'):
            raise PathInvalidException('Only python modules are supported')

        tfile_name = file_name.rstrip('.py')
        if tfile_name.lower() != tfile_name:
            raise PathInvalidException("PEP8: module name must contain all "
                        "lower case characters.")

        pep8_unallowed_specials = string.punctuation.replace('_', '')
        if any(sc in pep8_unallowed_specials for sc in tfile_name):
            raise PathInvalidException("PEP8: module name has unallowed "
                        "special characters, only '_' allowed.")
        return

    def upload_file_part(self, uploaded_obj, file_path, request, **kwargs):
        """ Multipart/form-data file intermediate chunk handling """
        if (hasattr(uploaded_obj, 'temporary_file_path')
                and uploaded_obj.temporary_file_path()):
            temp_path = uploaded_obj.temporary_file_path()
            shutil.move(temp_path, file_path)
        else:
            with open(file_path, "wb") as f:
                for chunk in uploaded_obj.chunks():
                    f.write(chunk)
        os.chmod(file_path, 0o644)
        return

    def collate_files(self, file_path):
        """ Multipart/form-data collate flag handling """
        if os.path.exists(file_path):
            os.remove(file_path)
        files = sorted(glob.glob('%s*' % file_path))
        with open(file_path, 'wb') as outfile:
            for filename in files:
                with open(filename, "rb") as f:
                    outfile.write(f.read())
                os.unlink(filename)
        return

    def upload_file_end(self, file_path, request, **kwargs):
        """
        Multipart/form-data end of file handling.  Based on kwargs, we can
        execute appropriate triggers to back-end entities such as HSM/GSLB.
        """
        if kwargs.get('hsmpackages'):
            hsmtype = request.QUERY_PARAMS.get('hsmtype')
            if not hsmtype:
                raise InvalidParamsException('Need to specify hsmtype')
            copy_file_to_all_other_controllers(file_path, '/var/lib/avi/hsmpackages/')
            execute_task('hsmpackage_install', hsmtype=hsmtype, hsmpackage=file_path, controller=True)
        elif kwargs.get('gslb'):
            geo_cfg = gslb_file_upload_process(file_path, request, 'gslb')
            self.process_geo_update(geo_cfg)
        elif kwargs.get('gslbsiteops'):
            gslb_file_upload_process(file_path, request, 'gslbsiteops')
        elif kwargs.get('ipamdnsscripts'):
            copy_file_to_all_other_controllers(file_path, CUSTOM_IPAMDNS_SCRIPTS_DIR)

    def post(self, request, *args, **kwargs):
        """
        This function handles the post functionality File upload api,
        accepting multipart/form-data.  The following high level checks
        are done.

        Notes:
        01. Multipart/form-data format
            -> {"file": <file data>,
            -> "uri": path to save file}
            -> request.FILES : file_name -> file contents
        02. Multipart/form-data could translate to multiple posts. Here
            is one representative sequence from the UI.
            hsmpackages?hsmtype=t&part=1 (start)
            hsmpackages?hsmtype=t&part=2 (intermediate chunk)
            hsmpackages?hsmtype=t&collate=true (end)
        03. When multiple files are uploaded using multipart encoder,
            via say REST-API, it will have the following format.

            request.FILES <MultiValueDict: {
            u'thales.zip':
            [<TemporaryUploadedFile: thales.zip (application/octet-stream)>],
            u'def.txt':
            [<TemporaryUploadedFile: def.txt (application/octet-stream)>],
            u'abc.txt':
            [<TemporaryUploadedFile: abc.txt (application/octet-stream)>]
            }>
        04. UI Scalabity: Background on flags: part & collate
            If the UI tries to upload the entire file as one monolithic
            file, it may result in timeouts or take inordinate time to
            complete.  UI needs to chunk the file-uploads to make it
            scalable and timebound.  To achieve these goals we use two
            flags:
            * part = identifies the chunk.
            * collate = identifies the last chunk.
            Both these flags are carried in the query_params. We upload ONLY
            one file through the UI interface.

            High Level Overview of a sequence:
            *********************************
            T1. hsmpackages?hsmtype=t&part=1 (start)
            T2. hsmpackages?hsmtype=t&part=2 (intermediate chunk)
            T3. hsmpackages?hsmtype=t&collate=true (end)

            Details of the sequence:
            ************************
            T1 Details:
            ----------
            request.FILES:
            <MultiValueDict: {
            u'file':
            [ <TemporaryUploadedFile: thales.tar (application/octet-stream)>]
            }>
            request.DATA:
            <QueryDict: {u'uri': [u'controller://hsmpackages']}>
            request.QUERY_PARAMS:
            <QueryDict: {u'part': [u'1'], u'hsmtype': [u't']}>

            T2 Details:
            ----------
            request.FILES:
            request.FILES:
            <MultiValueDict: {
            u'file':
            [<TemporaryUploadedFile: thales.tar (application/octet-stream)>]
            }>
            request.DATA:
            <QueryDict: {u'uri': [u'controller://hsmpackages']}>
            request.QUERY_PARAMS:
            <QueryDict: {u'part': [u'2'], u'hsmtype': [u't']}>

            T3 Details:
            ----------
            request.FILES: None
            request.DATA:
            {u'uri': u'controller://hsmpackages', u'filename': u'thales.tar'}
            request.QUERY_PARAMS:
            <QueryDict: {u'hsmtype': [u't'], u'collate': [u'true']}>

        05. The rest-api framework and UI framework are mutually exclusive.
            rest-api does not use query-params and supports multiple files,
            while UI uses query-params and supports only a single file.
        """
        if request.DATA.get('uri', False):
            if 'upgrade_pkgs' in request.DATA['uri'] and get_role() != 'master':
                raise PermissionError("An upgrade can only be initiated from the controller cluster leader."
                                      "Please Retry at the Leader")

        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)

        part = int(request.QUERY_PARAMS.get('part', 0))
        collate = True if 'collate' in request.QUERY_PARAMS else False
        if collate:
            # Refer Notes: T3
            file_name = request.DATA.get('filename', None)
            params = {'file_name': file_name,
                      'uploaded_obj':None,
                      'collate': collate,
                      'part': part
                     }
            self.process_file(request, params, args, kwargs)
        else:
            #  Refer Notes; T1, T2 & Rest-api
            for _, value in request.FILES.iteritems():
                uploaded_obj = value
                file_name = uploaded_obj.name
                params = {'file_name': file_name,
                          'uploaded_obj':uploaded_obj,
                          'collate': False,
                          'part': part
                         }
                self.process_file(request, params, args, kwargs)

        if kwargs.get('gslbsiteops'):
            rsp = gslb_fileops_response(request, file_name, syserr.SYSERR_SUCCESS)
            return Response(rsp, status=201)
        else:
            return Response(status=201)

    def process_file(self, request, params, args, kwargs):
        """
        This function process the file.
        * Check tenant, user, params
        * Extract flags, filename
        * Validate URI, filename, paths
        * Application specific checks
        * Flag specific handling
        """
        # file_name checks
        file_name = params['file_name']
        if file_name is None:
            raise DataException('File data is empty')

        if '..' in file_name:
            raise PermissionError('File name cannot include ".." '
                                  'parent directory: ' +file_name)

        if set('[`~!@#$%^&*()+{}":;\']+$').intersection(file_name):
            raise PermissionError('File name cannot have special character')

        # URI checks
        uri = request.DATA.get('uri', None)
        if not uri:
            log.error('No URI For file: ' + str(request.DATA))
            raise InvalidParamsException('File URI is not declared')

        if uri.startswith('controller://'):
            new_dir = uri.replace('controller://', '')
            if '..' in new_dir:
                raise PermissionError('File URI cannot include ".." '
                                      'parent directory: ' +new_dir)
            new_dir = new_dir.lstrip('/')
            new_dir = os.path.join('/var/lib/avi', new_dir)
        else:
            raise PermissionError('File URI needs to be a controller path and'
                                  'start with controller://, but has value: '
                                  + uri)
        # Application specific checks
        if kwargs.get('hsmpackages'):
            self.hsmpackages_check(new_dir, file_name)
        elif kwargs.get('gslb'):
            gslb_file_upload_checks('gslb', new_dir, request)
        elif kwargs.get('gslbsiteops'):
            gslb_file_upload_checks('gslbsiteops', new_dir, request)
        elif kwargs.get('ipamdnsscripts'):
            self.custom_ipamdnsscripts_check(new_dir, file_name)

        # OS checks on file_path
        if not os.path.exists(new_dir):
            try:
                os.makedirs(new_dir)
            except OSError as e:
                #for race condition
                if not os.path.isdir(new_dir):
                    log.error('Cannot make dir for path %s: %s' %
                              (new_dir, str(e)))
                    raise InvalidParamsException(
                        'Invalid file directory : ' +  new_dir)

        if os.path.isfile(new_dir):
            raise InvalidParamsException(
                'Input file directory is an existed file :'+new_dir)

        file_path = os.path.join(new_dir, file_name)
        # UI multiparts (part = 1, 2...) handling
        part = params['part']
        if part:
            file_path = '%s_%04d' % (file_path, int(part))

        # Flags: part/collate handling
        collate = params['collate']
        upload_file = (part or not collate)
        upload_file_end = (not part or collate)

        if upload_file:
            uploaded_obj = params['uploaded_obj']
            self.upload_file_part(uploaded_obj, file_path, request, **kwargs)
        if collate:
            self.collate_files(file_path)
        if upload_file_end:
            self.upload_file_end(file_path, request, **kwargs)

        if kwargs.get('hsmpackages') and request.QUERY_PARAMS.get('hsmtype') == 'safenet':
            hsm_version = get_safenet_version()
            ctrl_prop_pb = ControllerProperties.objects.get().protobuf(decrypt=True)
            if ctrl_prop_pb.safenet_hsm_version != hsm_version:
                ctrl_prop_pb.safenet_hsm_version = hsm_version
                protobuf2model(ctrl_prop_pb, None, False, skip_unfinished_pb=False)
        return Response(status=201)

    @db_transaction
    def _commit_geo_to_db(self, geo_cfg):
        """ Update the latest revision to Database """
        protobuf2model(geo_cfg, None, True, run_default_function=False)
        return

    def process_geo_update(self, geo_cfg):
        """
        We want to simulate an event as if the user triggered a put via the
        web-portal.  This translates to the following sequence. [resolve->
        must_check -> commit the updated-object to the db -> RPC to backend]
        This function sequences the above steps.
        """
        if geo_cfg:
            existing_pb = copy.deepcopy(geo_cfg)
            GslbGeoDbProfileResolve(geo_cfg)
            GslbGeoDbProfileCheck(geo_cfg, existing_pb)
            self._commit_geo_to_db(geo_cfg)
            msg = create_gsops_rpc(get_glb_cfg(), "Geo_Update")
            entry = msg.resource.gs_ops.objs.add()
            entry.ops = GSLB_UPDATE
            entry.ds_name = DS_GEO
            entry.geo.CopyFrom(geo_cfg)
            pb_message_post_save_transform(msg)
            rpc_stub = GslbSiteOpsService_Stub(RpcChannel())
            rpc_stub.SiteConfig(AviRpcController(), msg)
        return


class FileServiceSeOVAView(CreateView, ListView):
    model = None

    def get_permissions(self):
        """
        Allow no authentation for GET request
        """
        unauthenticated = ControllerProperties.objects.get().protobuf().allow_unauthenticated_apis
        if getattr(self, 'request', None) and self.request.method == 'GET' and unauthenticated:
            return [AllowAny()]
        return super(FileServiceSeOVAView, self).get_permissions()

    def post(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)

        data = request.DATA if request.DATA else {}
        file_format = data.get('file_format', 'ova')
        tar_path = SE_OVA_DIR + SE_OVA_TAR
        ovf_file = SE_OVA_DIR + 'se.ovf'
        qcow2_file = SE_OVA_DIR + 'se.qcow2'
        docker_file = SE_OVA_DIR + 'se_docker.tgz'
        if file_format.lower() == 'ova':
            file_path = tar_path
            if not os.path.exists(file_path):
                if os.path.exists(ovf_file):
                    # create tarball
                    tar = tarfile.open(file_path, "w")
                    tar.add(ovf_file, arcname='se.ovf')
                    tar.add(SE_OVA_DIR + 'se-disk1.vmdk',
                            arcname='se-disk1.vmdk')
                    tar.add(SE_OVA_DIR + 'se.mf', arcname='se.mf')
                    tar.close()
        elif file_format.lower() == 'docker':
            file_path = docker_file
        else:
            file_path = qcow2_file

        if not os.path.exists(file_path):
            s_cmd = ('%s --imagetype %s' %
                     (SE_SCRIPT, file_format))
            s_cmd_args = shlex.split(s_cmd)
            try:
                subprocess.call(s_cmd_args)
            except:
                log.exception('SE OVA gen script failure')
                raise ServerException('Failed to generate SE image')
            if not os.path.exists(file_path):
                log.error('SE generated file not found: %s ' % file_path)
                raise ServerException('Failed to generate SE Image')

        return Response(status=201)

    def get(self, request, *args, **kwargs):
        unauthenticated = ControllerProperties.objects.get().protobuf().allow_unauthenticated_apis
        if not unauthenticated:
            self.check_tenant(request, args, kwargs)
            self.check_user(request, args, kwargs)

        file_format = request.QUERY_PARAMS.get('file_format', 'ova')
        tar_path = SE_OVA_DIR + SE_OVA_TAR
        qcow2_file = SE_OVA_DIR + 'se.qcow2'
        docker_file = SE_OVA_DIR + 'se_docker.tgz'
        if file_format.lower() == 'ova':
            file_path = tar_path
        elif file_format.lower() == 'docker':
            file_path = docker_file
        else:
            file_path = qcow2_file
        if not os.path.exists(file_path):
            raise DataException('No %s file found'% file_format)
        rsp = CustomFileResponse()
        serve_file_via_nginx(rsp, file_path)
        return rsp

class FileServiceScriptsView(RetrieveView):
    model = None
    permission_classes = (AllowAny,)
    def get(self, request, *args, **kwargs):

        file_name = request.QUERY_PARAMS.get('file', 'avi_agent.sh')
        file_path = None

        if file_name == 'avi_agent.sh':
            file_path = '/opt/avi/scripts/avi_agent.sh'

        if not file_path or not os.path.exists(file_path):
            raise ServerException('%s file not found' % file_path)

        rsp = CustomFileResponse()
        serve_file_via_nginx(rsp, file_path)
        return rsp

class FileServiceSeOVAQCow2View(RetrieveView):
    permission_classes = (AllowAny,)
    model = None
    def get(self, request, *args, **kwargs):

        qcow2_file = SE_OVA_DIR + 'se.qcow2'
        if os.path.exists(qcow2_file):
            file_path = qcow2_file
        else:
            raise ServerException('No qcow2 file found')

        rsp = CustomFileResponse()
        serve_file_via_nginx(rsp, file_path)
        return rsp
# End of file
