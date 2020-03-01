
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
from avi.rest.views import RetrieveView
from avi.infrastructure.datastore import Datastore
from avi.infrastructure.shard_watcher import ShardWatcher
from django.http import JsonResponse

log = logging.getLogger(__name__)

class ShardDetail(RetrieveView):
    def get(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)

        input_uuid = kwargs.get('input_uuid')
        if input_uuid is None:
            return JsonResponse({'error': 'no input uuid'}, status=400)
        input_uuid = str(input_uuid)
        shard_uuid = kwargs.get('shard_uuid')

        sw = ShardWatcher.get_instance()
        pr = sw.get(Datastore(), shard_uuid, input_uuid)

        if pr is None:
            return JsonResponse({'error': 'shard does not exist'}, status=400)

        return JsonResponse({'shard_uuid': shard_uuid, 'input_uuid': input_uuid, 'host': pr.host, 'port': pr.port}, status=200)

