
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

#pylint:  skip-file
from django.conf.urls import patterns, include, url
import api.views_network_custom

urlpatterns = patterns('',

    url(r'^network/(?P<slug>[-\w.]+)/retrieve-ips/?$',
        api.views_network_custom.NetworkRetrieveIps.as_view(),
        name='network-retrieve-ips',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_NETWORK"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/network/(?P<slug>[-\w.]+)/retrieve-ips/?$',
        api.views_network_custom.NetworkRetrieveIps.as_view(),
        name='network-retrive-ips-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_NETWORK"}),

    url(r'^networksubnetlist/?$',
        api.views_network_custom.NetworkSubnetListView.as_view(),
        name='networksubnet-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_NETWORK"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/networksubnetlist/?$',
        api.views_network_custom.NetworkSubnetListView.as_view(),
        name='networksbunet-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_NETWORK"}),

    url(r'^network/?$',
        api.views_network_custom.NetworkList.as_view(),
        name='network-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_NETWORK"}),


    url(r'^tenant/(?P<tenant>[-\w.]+)/network/?$',
        api.views_network_custom.NetworkList.as_view(),
        name='network-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_NETWORK"}),

    url(r'^network/(?P<slug>[-\w.]+)/?$',
        api.views_network_custom.NetworkDetail.as_view(),
        name='network-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_NETWORK"}),

    url(r'^tenant/(?P<tenant>[-\w.]+)/network/(?P<slug>[-\w.]+)/?$',
        api.views_network_custom.NetworkDetail.as_view(),
        name='network-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_NETWORK"}),
)
