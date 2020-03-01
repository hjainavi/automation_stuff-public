
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

from avi.rest.error_list import ServerException
from avi.rest.views import (CommonView, SingleObjectView)
from avi.util.protobuf import protobuf2dict
from nonportal.management.commands.consistency_checker import ConfigConsistencyChecker

log = logging.getLogger(__name__)
HTTP_RPC_TIMEOUT = 3.0

class ConsistencyCheckView (CommonView, SingleObjectView):
    def get(self, request, *args, **kwargs):
        rsp = {}
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)

        params = request.QUERY_PARAMS

        try:
            ccc = ConfigConsistencyChecker()
            rsp_pb = ccc.config_consistency_check(params=params)
            rsp = protobuf2dict(rsp_pb)
        except Exception as err:
            msg = 'ConsistencyCheck failed with %s' %(str(err))
            raise ServerException(msg)
        return Response(data=rsp, status=200)
