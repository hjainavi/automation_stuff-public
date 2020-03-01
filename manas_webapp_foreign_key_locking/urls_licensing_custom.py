
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
import api.views_licensing_custom

urlpatterns = patterns('',
    url(r'^license/?$',
        api.views_licensing_custom.Licensing.as_view(),
        name='license',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_CONTROLLER"}),
    url(r'^license-toggle-enforcement/?$',
        api.views_licensing_custom.LicensingToggleEnforcement.as_view(),
        name='license',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_CONTROLLER"}),
    url(r'^license/(?P<slug>[-\w.]+)/?$',
        api.views_licensing_custom.LicensingDelete.as_view(),
        name='license-delete',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_CONTROLLER"}),
    )
