
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

import json
import logging

from django.db import connection
from django.http.response import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response

from avi.protobuf.alerts_pb2 import AlertState

from api.models import Alert, ActionGroupConfig, AlertConfig
from avi.rest.views import ListView
from avi.util.time_utils import duration_to_start_stop, epoch_to_iso_string
from avi.rest.error_list import DataException

@api_view(['POST'])
def reset(request):
    try:
        Alert.objects.all().delete()
        ActionGroupConfig.objects.all().delete()
        AlertConfig.objects.all().delete()
    except Exception as e:
        print str(e)
    return HttpResponse(
            json.dumps({'status': 'Alerts reset'}),
            mimetype='application/json',
            status=200)

log = logging.getLogger(__name__)

class AlertCountView(ListView):
    SQL_QUERY = ('SELECT COUNT(*), CEIL((timestamp-1)/ %s)*%s as groupts'
                    ' FROM api_alert  WHERE timestamp BETWEEN %s and %s ')
    SQL_GROUP_BY = 'GROUP BY groupts order by groupts %s'

    def get(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)

        step = request.QUERY_PARAMS.get('step', None)
        duration = request.QUERY_PARAMS.get('duration', None)
        if not step or not duration:
            raise DataException('Missing parameters duration or step')

        try:
            step = int(step)
            duration = int(duration)
        except ValueError:
            raise DataException('Parameters step & duration must be integers')

        query = self.SQL_QUERY
        start, stop = duration_to_start_stop(duration)
        query_params = [step, step, start, stop]

        if 'state' in request.QUERY_PARAMS:
            state_s = request.QUERY_PARAMS.get('state')
            enum = AlertState.Value(state_s)
            query = query + 'AND state=%s '
            query_params.append(enum)
        if 'related_refs.contains' in request.QUERY_PARAMS:
            uuid = request.QUERY_PARAMS.get('related_refs.contains')
            #query = query + "AND related_refs ILIKE '%s' " % param
            param = '%%' + str(uuid) + ',%%'
            query = query + "AND related_refs ILIKE %s "
            query_params.append(param)

        if 'event_pages.contains' in request.QUERY_PARAMS:
            page_s = request.QUERY_PARAMS.get('event_pages.contains')
            #query = query + "AND event_pages ILIKE '%s' " % param
            query = query + "AND event_pages ILIKE %s "
            param = '%%' + str(page_s) + ',%%'
            query_params.append(param)

        order_by = request.QUERY_PARAMS.get('sort', 'timestamp')
        sort_order = '' if order_by.find('-') == -1 else 'desc'
        query = query + self.SQL_GROUP_BY % sort_order

        cursor = connection.cursor()
        cursor.execute(query, query_params)
        data_list = cursor.fetchall()
        result = []
        for row in data_list:
            count, timestamp = row
            d = {'timestamp': epoch_to_iso_string(int(timestamp)),
                 'value': int(count),
                 'end': epoch_to_iso_string(int(timestamp)),
                 'start': epoch_to_iso_string(int(timestamp-step))
                 }
            result.append(d)

        rsp = {'count': len(result),
                'result': result
                }

        return Response(rsp)
