
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

from rest_framework.decorators import api_view
from django.http.response import HttpResponse, HttpResponseRedirect
from avi.infrastructure.rpc_channel import RpcChannel
from google.protobuf.service import RpcController
from avi.protobuf.common_pb2 import *
from avi.protobuf.vi_mgr_rpc_pb2 import *
import json
from api.models import VIMgrVcenterRuntime
from avi.util.protobuf import protobuf2dict

@api_view(['GET'])
def inventory(request, *args, **kwargs):
    try:
        req = VIVcenterInventoryProgressReq()
        #req.vcenter_ip.type = IpAddr()
        #req.vcenter_ip.type = V4
        #req.vcenter_ip.addr = vCenterConfiguration.objects.all()[0].vcenter_address.addr
        #status = VIMgrService_Stub(RpcChannel()).VIQueryVcenterInventoryProgress(RpcController(), req)

        vcenter = VIMgrVcenterRuntime.objects.all()[0]
        vcenter_progress = VIVcenterInventoryProgressRsp()
        vcenter_progress.progress = vcenter.progress
        vcenter_progress.num_dcs = vcenter.num_dcs
        vcenter_progress.num_hosts = vcenter.num_hosts
        vcenter_progress.num_clusters = vcenter.num_clusters
        vcenter_progress.num_vms = vcenter.num_vms
        vcenter_progress.num_nws = vcenter.num_nws

        rsp = HttpResponse(json.dumps(protobuf2dict(vcenter_progress)),
                           content_type='application/json',
                           status=200)
    except Exception as e:
        vcenter_progress = VIVcenterInventoryProgressRsp()
        vcenter_progress.progress = 0
        vcenter_progress.num_dcs = 0
        vcenter_progress.num_hosts = 0
        vcenter_progress.num_clusters = 0
        vcenter_progress.num_vms = 0
        vcenter_progress.num_nws = 0
        rsp = HttpResponse(json.dumps(protobuf2dict(vcenter_progress)),
                           content_type='application/json',
                           status=200)
    return rsp
