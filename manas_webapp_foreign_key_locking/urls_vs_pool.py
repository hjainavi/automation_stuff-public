
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
import api.views_vs_pool

urlpatterns = patterns('',
    url(r'^virtualservice/?$',
        api.views_vs_pool.VirtualServicePoolList.as_view(),
        name='virtualservice-list',
        kwargs={'scoped':True, 'scope_visible': False, 'permission': "PERMISSION_VIRTUALSERVICE"}),
    url(r'^virtualservice/(?P<slug>[-\w]+)/?$',
        api.views_vs_pool.VirtualServicePoolDetail.as_view(),
        name='virtualservice-detail',
        kwargs={'scoped':True, 'scope_visible': False, 'permission': "PERMISSION_VIRTUALSERVICE"}),
    url(r'^vsvip/?$',
        api.views_vs_pool.VsVipList.as_view(),
        name='vsvip-list',
        kwargs={'scoped':True, 'scope_visible': False, 'permission': "PERMISSION_VIRTUALSERVICE"}),
    url(r'^vsvip/(?P<slug>[-\w]+)/?$',
        api.views_vs_pool.VsVipDetail.as_view(),
        name='vsvip-detail',
        kwargs={'scoped':True, 'scope_visible': False, 'permission': "PERMISSION_VIRTUALSERVICE"}),
    url(r'^serviceengine/(?P<se_slug>[-\w]+)/virtualservice/?$',
        api.views_vs_pool.VirtualServicePoolList.as_view(),
        name='virtualservice-list-se',
        kwargs={'scoped':True, 'scope_visible': False, 'permission': "PERMISSION_VIRTUALSERVICE"}),
    url(r'^serviceengine/(?P<se_slug>[-\w]+)/virtualservice/(?P<slug>[-\w]+)/?$',
        api.views_vs_pool.VirtualServicePoolDetail.as_view(),
        name='virtualservice-detail-se',
        kwargs={'scoped':True, 'scope_visible': False, 'permission': "PERMISSION_VIRTUALSERVICE"}),
    url(r'^server/enable/?$',
        api.views_vs_pool.BatchPoolServerView.as_view(),
        name='server-batch-enable',
        kwargs={'scoped':True, 'scope_visible': False, 'permission': "PERMISSION_POOL", 'action': 'enable'}),
    url(r'^server/disable/?$',
        api.views_vs_pool.BatchPoolServerView.as_view(),
        name='server-batch-disable',
        kwargs={'scoped':True, 'scope_visible': False, 'permission': "PERMISSION_POOL", 'action': 'disable'}),
    url(r'^server/remove/?$',
        api.views_vs_pool.BatchPoolServerView.as_view(),
        name='server-batch-remove',
        kwargs={'scoped':True, 'scope_visible': False, 'permission': "PERMISSION_POOL", 'action': 'remove'}),
    url(r'^tenant/(?P<tenant>[-\w]+)/virtualservice/?$',
        api.views_vs_pool.VirtualServicePoolList.as_view(),
        name='virtualservice-list-scoped',
        kwargs={'scoped':True, 'scope_visible': True, 'permission': "PERMISSION_VIRTUALSERVICE"}),
    url(r'^tenant/(?P<tenant>[-\w]+)/virtualservice/(?P<slug>[-\w]+)/?$',
        api.views_vs_pool.VirtualServicePoolDetail.as_view(),
        name='virtualservice-detail-scoped',
        kwargs={'scoped':True, 'scope_visible': True, 'permission': "PERMISSION_VIRTUALSERVICE"}),
    url(r'^tenant/(?P<tenant>[-\w]+)/vsvip/?$',
        api.views_vs_pool.VsVipList.as_view(),
        name='vsvip-list-scoped',
        kwargs={'scoped':True, 'scope_visible': True, 'permission': "PERMISSION_VIRTUALSERVICE"}),
    url(r'^tenant/(?P<tenant>[-\w]+)/vsvip/(?P<slug>[-\w]+)/?$',
        api.views_vs_pool.VsVipDetail.as_view(),
        name='vsvip-detail-scoped',
        kwargs={'scoped':True, 'scope_visible': True, 'permission': "PERMISSION_VIRTUALSERVICE"}),
    url(r'^tenant/(?P<tenant>[-\w]+)/serviceengine/(?P<se_slug>[-\w]+)/virtualservice/?$',
        api.views_vs_pool.VirtualServicePoolList.as_view(),
        name='virtualservice-list-scoped-se',
        kwargs={'scoped':True, 'scope_visible': True, 'permission': "PERMISSION_VIRTUALSERVICE"}),
    url(r'^tenant/(?P<tenant>[-\w]+)/serviceengine/(?P<se_slug>[-\w]+)/virtualservice/(?P<slug>[-\w]+)/?$',
        api.views_vs_pool.VirtualServicePoolDetail.as_view(),
        name='virtualservice-detail-scoped',
        kwargs={'scoped':True, 'scope_visible': True, 'permission': "PERMISSION_VIRTUALSERVICE"}),
    url(r'^tenant/(?P<tenant>[-\w]+)/server/enable/?$',
        api.views_vs_pool.BatchPoolServerView.as_view(),
        name='server-batch-enable',
        kwargs={'scoped':True, 'scope_visible': True, 'permission': "PERMISSION_POOL", 'action': 'enable'}),
    url(r'^tenant/(?P<tenant>[-\w]+)/server/disable/?$',
        api.views_vs_pool.BatchPoolServerView.as_view(),
        name='server-batch-disable',
        kwargs={'scoped':True, 'scope_visible': True, 'permission': "PERMISSION_POOL", 'action': 'disable'}),
    url(r'^tenant/(?P<tenant>[-\w]+)/server/remove/?$',
        api.views_vs_pool.BatchPoolServerView.as_view(),
        name='server-batch-remove',
        kwargs={'scoped':True, 'scope_visible': True, 'permission': "PERMISSION_POOL", 'action': 'remove'}),
)
