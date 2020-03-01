############################################################################
#
# AVI CONFIDENTIAL
# __________________
#
# [2013] - [2017] Avi Networks Incorporated
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

from avi.rest.views import UpdateView
from avi.rest.api_perf import api_perf
from avi.rest.api_version import api_version
from avi.rest.error_list import DataException
from avi.rest.pb2model import protobuf2model

from api.models import WafPolicy, WafCRS
from views_waf_policy import WafPolicyDetail

from avi.rest.url_utils import slug_for_obj_uri
from avi.util.pb_resolve import WafPolicyResolve
from avi.util.must_check import WafPolicyCheck

from avi.util.wafcrs import wafcrs_migrate_policy

log = logging.getLogger(__name__)

class WafPolicyCRSUpdate(UpdateView):
    @api_version
    @api_perf
    def do_put_action(self, request, *args, **kwargs):
        response = {
        }
        self.callback_data = None
        waf_crs_ref = request.DATA.get('waf_crs_ref', None)
        commit = request.DATA.get('commit', False)
        if not waf_crs_ref:
            raise DataException('WafCRS reference required for update')
        if commit not in (True, False):
            raise DataException('Value of commit must be true or false.')
        waf_crs_uuid = slug_for_obj_uri(waf_crs_ref, WafCRS)
        if not waf_crs_uuid:
            raise DataException('WafCRS reference for update does not exist')
        waf_policy_uuid = kwargs.get('slug', None)
        if not waf_policy_uuid:
            return Response(status=400)
        waf_policy_pb = WafPolicy.objects.select_for_update().get(uuid=waf_policy_uuid, tenant_ref=self.tenant).protobuf()

        old_pb = WafPolicy.pb_class()
        old_pb.MergeFrom(waf_policy_pb)
        waf_crs_pb = WafCRS.objects.get(uuid=waf_crs_uuid).protobuf()

        # replace CRS groups and crs uuid
        del waf_policy_pb.crs_groups[:]
        waf_policy_pb.crs_groups.extend(waf_crs_pb.groups)
        waf_policy_pb.waf_crs_uuid = waf_crs_uuid

        try:
            # migrate, copy data and set new rules to force_detection
            res = wafcrs_migrate_policy(old_pb, waf_policy_pb)
            # check the new policy
            WafPolicyResolve(waf_policy_pb, old_pb)
            WafPolicyCheck(waf_policy_pb, old_pb)
            response.update(res)
        except Exception as e:
            log.exception("wafcrs_migrate_policy")
            raise
        if commit:
            new_obj, _ = protobuf2model(waf_policy_pb, None, True, run_default_function=False)
            new_pb = new_obj.protobuf()
            self.callback_data = (new_pb, old_pb)
        response["commit"] = commit
        return Response(status=200, data=response)


    @api_perf
    def run_callback(self):
        if self.callback_data is None:
            return
        method = 'put'
        new_pb, old_pb = self.callback_data
        waf_policy_view = WafPolicyDetail()
        waf_policy_view.request = self.request
        waf_policy_view.old_pb = old_pb
        waf_policy_view.callback_data = new_pb, method
        waf_policy_view.run_callback()
