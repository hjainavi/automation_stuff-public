
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

from django.conf.urls import patterns, include, url
import api.views_bm_custom
import permission.views

urlpatterns = patterns('',
    url(r'^bm-verify-credentials/?$',
        api.views_bm_custom.BmVerifyCredView.as_view(),
        name='bm-verify-credentials',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),

    url(r'^cloud/(?P<slug>[-\w.]+)/hosts/?$',
        api.views_bm_custom.BmHostsView.as_view(),
        name='bm-get-hosts',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
)
