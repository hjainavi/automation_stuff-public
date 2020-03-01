
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
import api.views_cloud_connector_user_custom as views_cc_custom

urlpatterns = patterns('',    
    url(r'^cloudconnectoruser/?$',
        views_cc_custom.CloudConnectorUserListView.as_view(),
        name='cloud-connector-user-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_USER_CREDENTIAL"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/cloudconnectoruser/?$',
        views_cc_custom.CloudConnectorUserListView.as_view(),
        name='cloud-connector-user-list',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_USER_CREDENTIAL"}),

    url(r'^cloudconnectoruser/(?P<slug>[-\w.]+)/?$',
        views_cc_custom.CloudConnectorUserDetailView.as_view(),
        name='cloud-connector-user-details',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_USER_CREDENTIAL"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/cloudconnectoruser/(?P<slug>[-\w.]+)/?$',
        views_cc_custom.CloudConnectorUserDetailView.as_view(),
        name='cloud-connector-user-details',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_USER_CREDENTIAL"}),

    url(r'^cloudconnectoruser/(?P<slug>[-\w.]+)/test/?$',
        views_cc_custom.CloudConnectorUserTestView.as_view(),
        name='cloud-connector-user-details',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_USER_CREDENTIAL"}),
    url(r'^cloudconnectoruser/(?P<slug>[-\w.]+)/cleanup/?$',
        views_cc_custom.CloudConnectorUserCleanupView.as_view(),
        name='cloud-connector-user-details',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_USER_CREDENTIAL"}),
)
