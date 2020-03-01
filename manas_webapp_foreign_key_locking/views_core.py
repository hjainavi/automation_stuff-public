

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
import gzip
import glob
import logging
from datetime import datetime
from contextlib import contextmanager
import magic
from rest_framework.response import Response
from avi.rest.views import DetailView, CreateView
from avi.remote_task.client import execute_remote_task
from avi.util.host_ip import get_se_info
from avi.util.se_sshfs import ServiceEngineSSHFS
from avi.util.zk_utils import get_controller_ips
from avi.util.controller_sshfs import ControllerSSHFS
from avi.util.constants import (CORE_DUMP_PATH, STACK_TRACES_PATH)
from avi.protobuf.log_core_manager_grpc_pb2 import CoreHistory, CorePurge
from avi.protobuf_json.protobuf_json import pb2json
LOG = logging.getLogger(__name__)

@contextmanager
def ignored(*exception):
    """
    This decorator is added to ignore exception;
    is similar to try catch block with ignoring
    exception. Added this to ignore sshfs related
    issue even if node is down and continue for
    other nodes.
    """
    try:
        yield
    except exception as e:
        LOG.error('Error:%s', str(e))

class CoreView(DetailView):
    """
    Implementation of view to process cores
    """

    def pb_sort_repeated_field(self, repeated_field, field_name):
        """
        This function arranges the elements in a repeated field based on a field.
        Copied from pb_transform function: __ordered_by_transform
        """
        repeated_field.sort(key=lambda msg: getattr(msg, field_name))
        return

    def do_get_action(self, request, *args, **kwargs):
        """
        Overides the default do_get_action command.
        """
        msg = self.show_cores_history()
        data = pb2json(msg)
        return Response(data=data)

    def _read_syslogs(self, msg, node_name, node_path):
        """
        This will read all available syslogs and returns the updated core_dict
        Notes:
        01. Using Magic to check whether file is archive or normal log file.
        02. In case of archive we are using gzip library to read content.
        """
        node_syslog_list = glob.iglob(node_path)
        for log in node_syslog_list:
            if os.path.isfile(log):
                with magic.Magic() as m:
                    ftype = m.id_filename(log)
                if 'gzip compressed data' in ftype:
                    fopen_hdlr = gzip.open
                else:
                    fopen_hdlr = open
                with fopen_hdlr(log) as fd:
                    self._process_log_file(fd, msg, node_name)
        return

    def _process_log_file(self, fd, msg, node_name):
        """
        Processes Logs and creates core dict to process
        Notes:
        01. Syslog and output snapshots:
            * syslog: Oct  4 13:48:02 Avi-Controller log_core_manager.py: \
              vs_mgr_0 crash -- Pls investigate further. \
              core_archive.20181004_134725.tar.gz generated
            *  parsed_output:
               timestamp: Oct 4 13:48:02
               node: node1.controller.local
               core_archive: core_archive.20181004_134725.tar.gz
               reason: vs_mgr_0 crash -- Pls investigate further.\
                       core_archive.20181004_134725.tar.gz generated

        02. core_name parse logic: in below parse logic we parsed core_name
            assuming core name always start with `core_archive.`
        03. reason parsing: we are putting all message in log file as reason
            by splitting using `log_core_manager.py:` as its log source for this.
        """
        for line in fd:
            # Refer Notes
            if 'Pls investigate further' in line:
                core_entry = msg.corehistoryinfo.add()
                core_entry.node = node_name
                core_entry.timestamp = " ".join(line.split(" ")[0:3])
                core_entry.core_archive = "core_archive.%s" % line.split("core_archive.")[1].split(" ")[0]
                core_entry.reason = line.split("log_core_manager.py:")[1]
        return

    def show_cores_history(self):
        """
        This function will access the 'syslog' files on cluster + SE nodes
        and retrieve the crash los.

        Notes:
        01. Ignore node and continue if node is down or unreachable.
        """
        msg = CoreHistory()
        # collect history from controller cluster
        ip_list, _ = get_controller_ips()
        for ip_item in ip_list:
            with ignored(Exception):
                with ControllerSSHFS(ip_item, prefix='core_history_') as ctrl_sshfs:
                    mnt_path = ctrl_sshfs.get_mnt_path()
                    node_path = os.path.join(mnt_path, 'var/log/syslog*')
                    self._read_syslogs(msg, ip_item, node_path)

        # collect history from SE
        se_info = get_se_info()
        for status, se_uuid, se_name, _ in se_info:
            if status:
                with ignored(Exception):
                    with ServiceEngineSSHFS(se_uuid, prefix='core_history_') as mnt_path:
                        node_path = os.path.join(mnt_path, 'var/log/syslog*')
                        self._read_syslogs(msg, se_name, node_path)
            else:
                core_entry = msg.corehistoryinfo.add()
                core_entry.node = se_name
                core_entry.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                core_entry.core_archive = "Unknown"
                core_entry.reason = "SE Unreachable; Review SE logs"

        self.pb_sort_repeated_field(msg.corehistoryinfo, 'timestamp')
        return msg


class CorePurgeView(CreateView):
    """ Interface to cleanup cores + stacktraces across all the nodes """

    def do_post_action(self, request, *args, **kwargs):
        """
        Overides the default do_post_action command.
        :return:
        """
        core_purge = self._cleanup_cores()
        data = pb2json(core_purge)
        rsp = Response(data=data, status=201)
        return rsp

    def _cleanup_cores(self):
        """
        Remove all available cores and stack traces on controller and SE

        Notes:
        01. We access controller and SE nodes via SSHFS.
        02. Even though SSHFS can be read-write, the user/credentials
            used does not have the right permissions to delete. Instead
            it has to be done via a execute_remote_task.
        03. Ignore node and continue if node is down or un-accesible
        """
        core_purge = CorePurge()
        ip_list, _ = get_controller_ips()
        for ip_item in ip_list:
            with ignored(Exception):
                with ControllerSSHFS(ip_item, prefix='core_purge_') as ctrl_sshfs:
                    mnt_path = ctrl_sshfs.get_mnt_path()
                    core = core_purge.core_purge_info.add()
                    core.node_uuid = ip_item
                    self._delete_cores(ip_item, mnt_path, core)

        # remove cores from SE
        se_info = get_se_info()
        for status, se_uuid, se_name, se_ip in se_info:
            if status:
                with ignored(Exception):
                    with ServiceEngineSSHFS(se_uuid, prefix='core_purge_') as mnt_path:
                        core = core_purge.core_purge_info.add()
                        core.node_uuid = se_name
                        self._delete_cores(se_ip, mnt_path, core)
            else:
                core = core_purge.core_purge_info.add()
                core.node_uuid = se_name
                core.path = "SE Unreachable; Cleanup not done"
        return core_purge

    def _delete_files(self, node_ip, mnt_path, archive_path, core):
        """
        Accept the path and delete core file

        Notes:
        01. We list all files iterating over glob path but we delete all the files
            one-shot via the execute_remote_task with the cmd. rm -f /<local-path>/*
        """
        # This will list all core files present in archive directory
        file_paths = []
        for path in glob.iglob(os.path.join(mnt_path, archive_path.strip("/"), "*")):
            if not os.path.isdir(path):
                # Remove core from host
                local_path = os.path.join("/", path.split(mnt_path)[1])
                core.path.append(local_path)
                file_paths.append(local_path)
                LOG.info("Core Purge: Deleting %s", local_path)

        cmd = "rm -f %s" % (" ".join(file_paths))
        execute_remote_task(cmd=cmd, hosts=[node_ip])
        return

    def _delete_cores(self, node_ip, mnt_path, core):
        """
        Form core path and stack traces and delete cores and stack traces
        """
        self._delete_files(node_ip, mnt_path, CORE_DUMP_PATH, core)
        self._delete_files(node_ip, mnt_path, STACK_TRACES_PATH, core)
        return
# End of file
