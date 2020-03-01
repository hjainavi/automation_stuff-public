
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

from rest_framework.response import Response
from permission.models import SystemDefaultObject
from avi.util.pb_default import generate_default_values
from avi.rest.views import (ListView)
from avi.rest.view_utils import get_model_from_name, NO_CUSTOM_DEFAULT_OBJS
from avi.infrastructure.db_base_cache import DbBaseCache
from avi.rest.url_utils import uri_from_slug

import logging
log = logging.getLogger(__name__)



def _get_system_default_objects(request, include_name=False):
    uuids = {}
    urls = {}
    include_false_defaults = [model.lower()
                              for model in NO_CUSTOM_DEFAULT_OBJS]
    scheme = request.scheme
    host = request.get_host()
    for obj in SystemDefaultObject.objects.all():
        name = ''
        if obj.object_model not in uuids:
            uuids[obj.object_model] = []
        if obj.object_model not in urls:
            urls[obj.object_model] = []
        if (obj.default or
                (obj.object_model == 'tenant' and
                 obj.object_uuid == 'admin') or
                (obj.object_model in include_false_defaults)):

            uuids[obj.object_model].append(obj.object_uuid)
            model = get_model_from_name(obj.object_model)
            if include_name:
                name = DbBaseCache.uuid2name(obj.object_uuid)
            url = uri_from_slug(model.__name__, obj.object_uuid, scheme=scheme, host=host, include_name=include_name, name=name)
            urls[obj.object_model].append(url)
    return (uuids, urls)


class DefaultValueView(ListView):
    model = None
    serializer_class = None

    def get(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        include_name = 'include_name' in request.QUERY_PARAMS or 'include_name' in kwargs
        data = generate_default_values(request, tenant_name=self.tenant.name)
        default_uuids, default_refs = _get_system_default_objects(request, include_name=include_name)
        data['default'] = default_uuids
        data['default_refs'] = default_refs
        # data['default'] = _get_system_default_objects()
        rsp = Response(data)
        return rsp
