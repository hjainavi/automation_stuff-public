
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

from avi.rest.views import SingleObjectView, CommonView
from avi.rest.views import JSONRenderer, JSONParser, NestedFilter
from avi.rest.views import Response
import logging

log = logging.getLogger(__name__)


class PathInvalidException(Exception):
    pass


class UiErrorFullView(SingleObjectView, CommonView):
    renderer_classes = (JSONRenderer,)
    parser_classes = (JSONParser,)
    filter_backend = NestedFilter

    def post(self, request, *args, **kwargs):

        log.error(request.DATA)

        r_status = 200
        r_msg = {'Saved ui error'}
        rsp = Response(data=r_msg, status=r_status)
        return rsp
