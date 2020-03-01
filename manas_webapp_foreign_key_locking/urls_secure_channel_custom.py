
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

from django.conf.urls import patterns, url
import api.views_secure_channel_custom

urlpatterns = patterns('',
    url(r'^securetoken-generate/?$',
        api.views_secure_channel_custom.SecureChannelToken.as_view(),
        name='secure_token_generate',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_SE_TOKEN"}),
    url(r'^securetoken-import/?$',
        api.views_secure_channel_custom.import_token,
        name='secure_token_import',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CONTROLLER"}),
    url(r'^securechannel-status/?$',
        api.views_secure_channel_custom.SecureChannelStatus.as_view(),
        name='secure_channel_status',
        kwargs={'scoped': True,
                'scope_visible': False,
                'permission': "PERMISSION_CONTROLLER"}),
)
