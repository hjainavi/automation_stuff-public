
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
import api.views_seupgrade

urlpatterns = patterns('',
    url(r'^seupgrade/?$',
        api.views_seupgrade.SeUpgradeView.as_view(),
        name='seupgrade',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CONTROLLER"}),
    url(r'^seupgrade/status?$',
        api.views_seupgrade.SeUpgradeStatusView.as_view(),
        name='seupgradestatus',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CONTROLLER"}),
    #url(r'^seupgrade/statusdetail?$',
    #    api.views_seupgrade.SeUpgradeStatusDetailView.as_view(),
    #    name='seupgradestatusdetail',
    #    kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CONTROLLER"}),
    url(r'^seupgrade/preview?$',
        api.views_seupgrade.SeUpgradePreviewView.as_view(),
        name='seupgradepreview',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CONTROLLER"}),
    url(r'^seupgrade/resume?$',
        api.views_seupgrade.SeUpgradeResumeView.as_view(),
        name='seupgraderesume',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CONTROLLER"})
)
