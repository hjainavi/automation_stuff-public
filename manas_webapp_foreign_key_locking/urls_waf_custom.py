############################################################################
#
# AVI CONFIDENTIAL
# __________________
#
# [2013] - [2017] Avi Networks Incorporated
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

#Manual url file for custom urls
from django.conf.urls import patterns, url
import api.views_waf_custom

urlpatterns = patterns('',
    url(r'^wafpolicy/(?P<slug>[-\w.]+)/update-crs-rules/?$',
        api.views_waf_custom.WafPolicyCRSUpdate.as_view(),
        name='update-crs',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_WAFPOLICY"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/wafpolicy/(?P<slug>[-\w.]+)/update-crs-rules/?$',
        api.views_waf_custom.WafPolicyCRSUpdate.as_view(),
        name='update-crs-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_WAFPOLICY"}),
)
