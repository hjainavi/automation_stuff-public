

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

from api.models_secure_channel import SecureChannelMapping
from api.serializers_secure_channel import SecureChannelMappingSerializer
import logging

from rest_framework.decorators import (api_view)
from rest_framework.response import Response
from avi.rest.views import (ListView, RetrieveView)
from permission.secure_channel_utils import (import_secure_channel_token,
                                             generate_secure_channel_token,
                                             update_secure_channel_status_all)

log = logging.getLogger(__name__)

@api_view(['POST'])
def import_token(request, *args, **kwargs):
    try:
        rsp = import_secure_channel_token(request.DATA)
    except Exception as e:
        log.error('Failed to import secure channel token: %s' % str(e))
        raise e
    return Response(rsp)


class SecureChannelToken(RetrieveView):
    """
    Get a new secure token for SE creation given Tenant & Cloud scope
    """
    def get(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        rsp = generate_secure_channel_token(
            token=None, tenant_uuid=self.tenant.uuid,
            cloud_uuid=self.cloud.uuid if self.cloud else '')
        return Response(rsp)


class SecureChannelStatus(ListView):
    model = SecureChannelMapping
    serializer_class = SecureChannelMappingSerializer
    rpc_data = {}

    def get(self, request, *args, **kwargs):
        update_secure_channel_status_all()
        return super(SecureChannelStatus, self).get(request, *args, **kwargs)
