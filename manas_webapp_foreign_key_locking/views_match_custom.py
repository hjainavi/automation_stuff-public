
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
import json
from rest_framework.response import Response

from avi.protobuf.match_pb2 import IpAddrGroup
from avi.protobuf import webapp_err_pb2 as weberr
from avi.util.protobuf import protobuf2dict
from avi.rest.views import RetrieveView
from avi.rest.error_list import DataException

IP_GROUP_DIR = '/var/lib/avi/etc/ipgroups'
COUNTRY_CODE_JSON = '/var/lib/avi/etc/ipgroups/country_codes.json'

class CountryCodeLookup(RetrieveView):    
    model = None
    
    def get(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)

        codes = request.QUERY_PARAMS.get('countries')
        if not codes:
            with open(COUNTRY_CODE_JSON) as f:
                data = json.load(f)
            return Response(data)

        codes = codes.split(',')
        data = {'addrs':[], 'ranges':[], 'prefixes':[]}
        
        for code in codes:
            file_path = os.path.join(IP_GROUP_DIR, code.upper())
            if not os.path.exists(file_path):
                raise DataException(
                    err=weberr.WEBERR_CHECK_IP_ADDR_GROUP_BAD_COUNTRY_CODE,
                    params={'country_code':code})
            with open(file_path) as f:
                s = f.read()
            ip_addr_group = IpAddrGroup()
            ip_addr_group.ParseFromString(s)
            ip_data = protobuf2dict(ip_addr_group)
            if ip_data.get('addrs'):
                data['addrs'].extend(ip_data['addrs'])
            if ip_data.get('ranges'):
                data['ranges'].extend(ip_data['ranges'])
            if ip_data.get('prefixes'):
                data['prefixes'].extend(ip_data['prefixes'])

        return Response(data)
