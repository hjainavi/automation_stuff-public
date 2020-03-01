
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

import os
import time
import shlex
import logging
import threading
from datetime import datetime
import subprocess32 as subprocess

#Django + avi.rest
from rest_framework.response import Response
from api.models import SystemConfiguration
from api.models import ControllerProperties
from avi.rest.views import DetailView, CreateView
from avi.rest.pb2model import protobuf2model
from avi.rest.error_list import ServerException
from avi.infrastructure.rpc_channel import RpcChannel
from avi.infrastructure.rpc_channel import RpcTimedOut
from avi.infrastructure.rpc_channel import AviRpcController

# Avi protobuf
from avi.protobuf_json.protobuf_json import pb2json
import avi.protobuf.syserr_pb2 as syserr
from avi.protobuf.tech_support_pb2 import TechSupportParams
from avi.protobuf.tech_support_pb2 import TechSupportMessage
from avi.protobuf.tech_support_rpc_pb2 import TechSupportRpcService_Stub

# Avi util
from avi.util.syserr_formatters import get_syserr_format_string
from avi.util.file_lock_utils import FileLock, UnableToLockException

# tech-support
from avi.tech_support import tech_support
from avi.tech_support.tech_support_utils import get_techsupport_status
from avi.tech_support.tech_support_utils import unlink_latest_status_mapping

log = logging.getLogger(__name__)
tech_support_lock_file = "/var/lib/avi/tech_support.LOCK"

# Ret-types
TS_RET_TYPE_FILE = 1
TS_RET_TYPE_STATUS = 2


class TechSupportCommonView(DetailView):
    """
    Implements the tech-support view.
    """
    def check_ts_input(self, **kwargs):
        """
        This function evaluates the ts_inputs.
        """
        # Lemons?
        level = kwargs.get('level')
        slug = kwargs.get('slug', None)
        status_code = tech_support.eval_techsupport_inputs(level, slug)
        if status_code != syserr.SYSERR_SUCCESS:
            raise ServerException(get_syserr_format_string(status_code))
        return level, slug

    def parse_request(self, request, level, slug=None):
        """
        Common function to parse the request and populate a dict.
        """
        cmd_args = {}
        cmd_args['level'] = level
        cmd_args['timestamp'] = datetime.now().strftime('%Y%m%d-%H%M%S')
        if slug:
            cmd_args['uuid'] = slug
        cmd_args['case_number'] = request.QUERY_PARAMS.get('case_number', None)
        log.info('cmd_args = %s', cmd_args)
        return cmd_args

    def create_rsp(self, ret_val):
        """
        Based on the status-type, we create the appopriate response.
        For a file, we set the appropriate headers, so that NGNIX
        will push the file out.

        01. For CLI, this file will not be displayed on the console.
            Whereas, the status will be still displayed. (CLI comes
            before NGINX)
        """
        ret_type, ret_obj = ret_val # unpack
        if ret_type == TS_RET_TYPE_STATUS:
            rsp = Response(data=ret_obj)
        else:
            rsp = Response()
            rsp['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(ret_obj)
            rsp['X-Accel-Redirect'] = '/export/%s' % ret_obj
        return rsp

    def create_response_message(self, status_code):
        """
        Creates Response
        """
        status = TechSupportMessage()
        status.status_code = status_code
        status.status = get_syserr_format_string(status.status_code)
        return pb2json(status)


class TechSupportView(TechSupportCommonView, CreateView):
    """
    Implemented this view for calling tech-support collection synchronously.
    We will initiate tech-support collection and user control will be blocked
    until techsupport collection completes.
    """

    def execute_ts_collection(self, request, level, slug=None):
        """
        Executes the ts-collection and returns a filename
        """
        cmd_args = self.parse_request(request, level, slug=slug)
        try:
            outfile = tech_support.show(**cmd_args)
            if not outfile or not os.path.exists(outfile):
                msg = 'Tech-support collection file error @ level:{x}'.format(x=level)
                log.error(msg)
                raise ServerException(msg)
        except (ValueError, KeyError):
            msg = 'Tech-support collection error @ level:{x}'.format(x=level)
            log.error(msg)
            raise ServerException(msg)
        return (TS_RET_TYPE_FILE, outfile)

    def execute_ts_command(self, request, **kwargs):
        """
        Execute ts status or collect ts-logs.  Ensure only one
        ts instance is invoked at any point in time.
        """
        level, slug = self.check_ts_input(**kwargs)
        try:
            with FileLock(tech_support_lock_file, block=False):
                if level == 'status':
                    return self.execute_ts_status(**kwargs)
                else:
                    unlink_latest_status_mapping()
                    return self.execute_ts_collection(request, level, slug=slug)
        except UnableToLockException:
            msg = 'Tech support is already in progress'
            log.error(msg)
            raise ServerException(msg)

    def execute_ts_status(self, **kwargs):
        """
        Retrieves the ts-status in a json blob.
        if slug == None, then the status will return errors.
        if slug == 'all' then the status will return errors + warnings for visibility.
        """
        slug = kwargs.get('slug', None)
        data = get_techsupport_status(slug=slug)
        return (TS_RET_TYPE_STATUS, data)

    def do_get_action(self, request, *args, **kwargs):
        """
        Overides the default do_get_action command.
        """
        ret_val = self.execute_ts_command(request, **kwargs)
        return self.create_rsp(ret_val)

    def do_post_action(self, request, *args, **kwargs):
        """
        Executes tech-support collection and attaches it a case.
        """
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

        ret_val = self.execute_ts_command(request, **kwargs)
        ret_type, ret_obj = ret_val
        if ret_type == TS_RET_TYPE_FILE:
            syscfg = SystemConfiguration.objects.get().protobuf(decrypt=True)

            proxy_setting = None
            if syscfg.HasField('proxy_configuration') and syscfg.proxy_configuration:
                proxy = syscfg.proxy_configuration
                if proxy.host and proxy.port:
                    if proxy.username and proxy.password:
                        proxy_setting = '%s:%s@%s:%s' %(proxy.username, proxy.password,
                                                        proxy.host, proxy.port)
                    else:
                        proxy_setting = '%s:%s' % (proxy.host, proxy.port)

            env = os.environ.copy()
            if proxy_setting:
                env['http_proxy'] = 'http://%s' %proxy_setting
                env['https_proxy'] = 'https://%s' %proxy_setting

            cmd = '/opt/avi/scripts/attach2case.py -H avinetworks.com -t %s -P -p https %s %s'\
                  %(token, case_number, ret_obj)
            proc = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, env=env)
            _, err = proc.communicate()
            if err:
                raise ServerException('Upload Failed: %s' %err)
            else:
                return Response(data='Upload Successful')
        else:
            return self.create_rsp(ret_val)


class TechSupportViewV2(TechSupportCommonView):
    """
    Implemented this view for calling tech-support collection asynchronously.
    1. We will initiate tech-support collection and return control to user.
    2. User will check tech-support status until techsupport collection completes.
    3. GET - for show tech-support [ level ].
    """

    def invoke_ts_rpc(self, msg, file_lock):
        """
	Function delegates the tech-support collection to generic_config_handler
        via rpc.  This is a blocking call and after the task gets completed, the
	file_lock will be released.
        """
        rpc_channel = RpcChannel(uuid=msg.uuid)
        rpc_stub = TechSupportRpcService_Stub(rpc_channel)
        try:
            rpc_stub.Post(AviRpcController(timeout=900), msg)
        except RpcTimedOut:
            log.error('RPC timeout %s', msg)
        finally:
            file_lock.unlock()
        return

    def execute_ts_collection(self, request, level, file_lock, slug=None):
        """
        Executes the ts-collection in a separate thread.
        """
        cmd_args = self.parse_request(request, level, slug=slug)
        msg = TechSupportParams()
        msg.uuid = 'ts-dummy-uuid'
        msg.level = cmd_args['level']
        msg.start_timestamp = cmd_args['timestamp']
        if cmd_args.get('uuid'):
            msg.slug = slug
        if cmd_args.get('case_number'):
            msg.case_number = cmd_args.get('case_number')
        ts_thread = threading.Thread(target=self.invoke_ts_rpc, args=(msg, file_lock))
        ts_thread.start()
        time.sleep(1)
        return

    def execute_ts_command(self, request, **kwargs):
        """
        Execute ts status or collect ts-logs.  Ensure only one
        ts instance is invoked at any point in time.
        """
        level, slug = self.check_ts_input(**kwargs)
        if level == 'status':
            status_code = syserr.SYSERR_TECH_SUPPORT_INPUT_INVALID_LEVEL
            raise ServerException(get_syserr_format_string(status_code))

        try:
            file_lock = FileLock(tech_support_lock_file, block=False)
            file_lock.lock()
            unlink_latest_status_mapping()
            self.execute_ts_collection(request, level, file_lock, slug=slug)
            status_code = syserr.SYSERR_TECH_SUPPORT_COLLECTION_STARTED
            return self.create_response_message(status_code)
        except UnableToLockException:
            status_code = syserr.SYSERR_TECH_SUPPORT_COLLECTION_ONGOING
            raise ServerException(get_syserr_format_string(status_code))

    def do_get_action(self, request, *args, **kwargs):
        """
        Executes tech-support collection and attaches it a case.
        """
        ret_obj = self.execute_ts_command(request, **kwargs)
        return Response(data=ret_obj)


class TechSupportStatusViewV2(TechSupportCommonView):
    """
    Implemented this view for calling tech-support status.
    GET - for show tech-support status.
    """

    def execute_ts_status(self, ts_in_progress, slug, request):
        """
        Retrieves the ts-status in a json blob.
        """
        filename = request.QUERY_PARAMS.get('filename', None)
        return get_techsupport_status(slug=slug,
                                      filename=filename,
                                      ts_in_progress=ts_in_progress)

    def do_get_action(self, request, *args, **kwargs):
        """
        Overides the default do_get_action command.
        """
        _, slug = self.check_ts_input(**kwargs)
        try:
            with FileLock(tech_support_lock_file, block=False):
                ts_in_progress = False
        except UnableToLockException:
            ts_in_progress = True
        ret_obj = self.execute_ts_status(ts_in_progress, slug, request)
        return Response(data=ret_obj)
# End of file
