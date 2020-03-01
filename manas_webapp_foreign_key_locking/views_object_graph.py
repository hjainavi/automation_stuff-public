
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
from avi.rest.views import ListView
from avi.rest.filters import NestedFilter

log = logging.getLogger(__name__)

class ObjectGraphList(ListView):

    def do_get_list(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        n_filter = NestedFilter()
        query_params = request.QUERY_PARAMS
        rsp = {}
        objs =  n_filter.filter_by_references(None, query_params, object_graph=True)
        rsp['results'] = objs
        rsp['count'] = len(objs)
        return Response(rsp)
