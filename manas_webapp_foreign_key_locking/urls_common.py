
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
import api.views_common

urlpatterns = patterns('',
    url(r'^tenant/?$',
        api.views_common.TenantList.as_view(),
        name='tenant-list',
        kwargs={'scoped':False, 'scope_visible': False, 'permission': "PERMISSION_TENANT"}),
    url(r'^tenant/(?P<slug>[-\w]+)/?$',
        api.views_common.TenantDetail.as_view(),
        name='tenant-detail',
        kwargs={'scoped':False, 'scope_visible': False, 'permission': "PERMISSION_TENANT"}),
    url(r'^tenant-inventory/?$',
        api.views_common.TenantInventory.as_view(),
        name='tenant-inventory',
        kwargs={'scoped':False, 'scope_visible': False, 'permission': "PERMISSION_TENANT"}),
)