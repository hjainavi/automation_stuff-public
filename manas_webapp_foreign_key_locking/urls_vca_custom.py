
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
import api.views_vca_custom
import permission.views

urlpatterns = patterns('',
    url(r'^vca-get-instances/?$',
        api.views_vca_custom.VcaInstancesView.as_view(),
        name='vca-get-instances',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_CONTROLLER"}),

    url(r'^vca-verify-credentials/?$',
        api.views_vca_custom.VcaVerifyCredView.as_view(),
        name='vca-verify-credentials',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_CONTROLLER"}),

    url(r'^vca-get-networks/?$',
        api.views_vca_custom.VcaSubnetsView.as_view(),
        name='vca-get-networks',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_CONTROLLER"}),

    url(r'^vca-get-vdcs/?$',
        api.views_vca_custom.VcaVdcsView.as_view(),
        name='vca-get-vdcs',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_CONTROLLER"}),
)
