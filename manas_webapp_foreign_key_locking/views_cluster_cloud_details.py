
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

"""
==========================
Cloud Connector User Views
==========================
"""
import os
import uuid
import shlex
import json
from tempfile import NamedTemporaryFile
from rest_framework.response import Response
from api.models import SystemConfiguration
from avi.util.ssl_utils import decrypt_string
from avi.util.pb_sensitive import SENSITIVE_TAG
from avi.util.linux_host import test_linux_host_install, cleanup_linux_host
from avi.util.cluster_info import management_ip
from avi.rest.views import (ListView, CreateView, DetailView, PostActionView)
from avi.rest.error_list import ServerException, DataException
from api.models import ClusterCloudDetails, ClusterCloudDetailsSerializer

class ClusterCloudDetailsListView(ListView, CreateView):
    model = ClusterCloudDetails
    serializer_class = ClusterCloudDetailsSerializer

    def do_post_list(self, request, *args, **kwargs):
        rsp = super(ClusterCloudDetailsListView, self).do_post_list(request, *args, **kwargs)

        return rsp


class ClusterCloudDetailsView(DetailView):
    model = ClusterCloudDetails
    serializer_class = ClusterCloudDetailsSerializer

    def do_put_detail(self, request, *args, **kwargs):
        return super(ClusterCloudDetailsView, self).do_put_detail(request,
                                                             *args, **kwargs)
