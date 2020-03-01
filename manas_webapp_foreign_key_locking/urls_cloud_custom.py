
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
import api.views_cloud_custom

urlpatterns = patterns('',
    url(r'^cloud/?$',
        api.views_cloud_custom.CloudList.as_view(),
        name='cloud-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/cloud/?$',
        api.views_cloud_custom.CloudList.as_view(),
        name='cloud-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD"}),  
            
    url(r'^cloud/(?P<slug>[-\w.]+)/?$',
        api.views_cloud_custom.CloudDetail.as_view(),
        name='cloud-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/cloud/(?P<slug>[-\w.]+)/?$',
        api.views_cloud_custom.CloudDetail.as_view(),
        name='cloud-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD"}),


    url(r'^cloudruntime/?$',
        api.views_cloud_custom.CloudRuntimeList.as_view(),
        name='cloudruntime-list',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    url(r'^cloudruntime/(?P<slug>[-\w.]+)/?$',
        api.views_cloud_custom.CloudRuntimeDetail.as_view(),
        name='cloudruntime-detail',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),

    url(r'^cloud/(?P<slug>[-\w.]+)/runtime/?$',
        api.views_cloud_custom.CloudRuntimeDetail.as_view(),
        name='cloudruntime-detail',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
)
