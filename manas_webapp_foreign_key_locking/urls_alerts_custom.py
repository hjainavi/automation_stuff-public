
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
import api.views_alerts_custom

urlpatterns = patterns('',
    
    url(r'^alertreset/?$',
        api.views_alerts_custom.reset,
        name='alertreset',
        kwargs={'permission': "PERMISSION_ALERT"}
        ),
    url(r'^alert-count/?$',
        api.views_alerts_custom.AlertCountView.as_view(),
        name='alert-count',
        kwargs={'permission': "PERMISSION_ALERT"}
        ),

)
