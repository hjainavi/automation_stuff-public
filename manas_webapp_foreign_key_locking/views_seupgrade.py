
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
from rest_framework.response import Response

from avi.infrastructure.taskqueue import TaskQueue
from avi.rest.error_list import ServerException, WebappException
from avi.rest.json_db_utils import transform_json_refs_to_uuids
from avi.rest.views import CommonView, SingleObjectView
from avi.protobuf.common_pb2 import NullObj
from avi.protobuf.res_monitor_rpc_pb2 import ResMonService_Stub, ResMonUpgradeService_Stub
from avi.infrastructure.rpc_channel import RpcChannel
from google.protobuf.service import RpcController
from avi.rest.pb2dict import protobuf2dict_withrefs
import avi.protobuf.syserr_pb2 as syserr_pb2
import avi.protobuf.upgrade_pb2 as upgrade_pb2
from avi.util.protobuf import dict2protobuf
from avi.upgrade.upgrade_utils import SE_UPGRADE_IN_PROGRESS_FILE
from avi.upgrade.upgrade_state_utils import set_upgrade_request
import os

log = logging.getLogger(__name__)
HTTP_RPC_TIMEOUT = 3.0


class SeUpgradeView (CommonView, SingleObjectView):
    def post(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)

        log.info('Start SeUpgrade all SE in the system.')
        rsp = {'status': 'se upgrade in progress...'}
        se_upgrade_params_req = upgrade_pb2.SeUpgradeParams()
        se_upgrade_params_req.force = request.DATA.get('force', False)
        se_upgrade_params_req.disruptive = request.DATA.get('disruptive', False)
        se_upgrade_params_req.test = request.DATA.get('test', False)
        se_upgrade_params_req.suspend_on_failure = request.DATA.get('suspend_on_failure', False)
        transform_json_refs_to_uuids(request.DATA)
        if request.DATA.get('se_group_uuids'):
            for se_group_uuid in request.DATA['se_group_uuids']:
                se_upgrade_params_req.se_group_uuids.append(se_group_uuid)
        try:
            # send rpc to Res Monitor
            os.system('sudo touch %s' % SE_UPGRADE_IN_PROGRESS_FILE)
            stub = ResMonService_Stub(RpcChannel())
            stub.SeUpgradeRpc(RpcController(), se_upgrade_params_req)
            set_upgrade_request(request.DATA)
        except Exception as err:
            msg = 'Se Upgrade Error:' + str(err)
            os.system('sudo rm -f %s' % SE_UPGRADE_IN_PROGRESS_FILE)
            raise ServerException(msg)
        return Response(data=rsp, status=200)


class SeUpgradeStatusView (CommonView, SingleObjectView):
    def get(self, request, *args, **kwargs):
        rsp = {}
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)

        log.info('Get SeUpgrade Status')

        try:
            # send rpc to Res Monitor
            req = NullObj()
            stub = ResMonUpgradeService_Stub(RpcChannel())
            rsp_pb = stub.GetSeUpgradeStatus(RpcController(), req)
            rsp = protobuf2dict_withrefs(rsp_pb, request)
        except Exception as err:
            msg = 'SeUpgrade Status Error:' + str(err)
            raise ServerException(msg)
        return Response(data=rsp, status=200)


class SeUpgradePreviewView (CommonView, SingleObjectView):
    def get(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        log.info('Get SeUpgrade Preview')
        try:
            # send rpc to Res Monitor
            req = NullObj()
            stub = ResMonUpgradeService_Stub(RpcChannel())
            rsp_pb = stub.GetSeUpgradePreview(RpcController(), req)
            rsp = protobuf2dict_withrefs(rsp_pb, request)
        except Exception as err:
            msg = 'SeUpgrade Preview Error:' + str(err)
            raise ServerException(msg)
        return Response(data=rsp, status=200)


class SeUpgradeResumeView (CommonView, SingleObjectView):
    def post(self, request, *args, **kwargs):
        rsp_pb = None
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)

        log.info('Resume SeUpgrade')
        transform_json_refs_to_uuids(request.DATA, preserve_uri=True)
        segroup_upgrade_resume_params_req = upgrade_pb2.SeGroupUpgradeResumeParams()
        dict2protobuf(request.DATA, segroup_upgrade_resume_params_req)
        if (segroup_upgrade_resume_params_req.HasField('ignore_failure') or
            len(segroup_upgrade_resume_params_req.se_group_uuids)):
            try:
                # send rpc to Res Monitor
                ts = TaskQueue()
                stub = ResMonUpgradeService_Stub(RpcChannel(transport=ts))
                rsp_pb = stub.SeGroupUpgradeResumeRpc(RpcController(), segroup_upgrade_resume_params_req)
            except Exception as err:
                msg = 'Se Resume Upgrade Error:' + str(err)
                raise ServerException(msg)
        else:
            raise WebappException('Atleast one se_group is expected in input. If you want to ignore please specify "seupgrade ignore_failure"')

        if rsp_pb and syserr_pb2.SYSERR_SUCCESS != rsp_pb.rpc_status:
            raise WebappException(rsp_pb.error_message)
        return Response(data={}, status=200)

