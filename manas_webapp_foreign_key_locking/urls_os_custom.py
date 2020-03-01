
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
import api.views_os_custom
import api.views_os_lbprov_plugin_custom
import api.views_os_lbprov_audit_custom
import permission.views

urlpatterns = patterns('',
    url(r'^openstack-verify-credentials/?$',
        api.views_os_custom.OsVerifyCredView.as_view(),
        name='openstack-verify-credentials',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),

    url(r'^openstack-get-tenant-networks/?$',
        api.views_os_custom.OsNetworksView.as_view(),
        name='openstack-get-tenant-networks',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),

    url(r'^os_lbprov_plugin/?$',
        api.views_os_lbprov_plugin_custom.OsLbProvPluginView.as_view(),
        name='os_lbprov_plugin',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),

    url(r'^os_lbprov_audit/?$',
        api.views_os_lbprov_audit_custom.OsLbProvAuditView.as_view(),
        name='os_lbprov_audit',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_VIRTUALSERVICE"}),

    url(r'^nuage-verify-credentials/?$',
        api.views_os_custom.NuageVerifyCredView.as_view(),
        name='nuage-verify-credentials',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),

    url(r'^contrail-verify-credentials/?$',
        api.views_os_custom.ContrailVerifyCredView.as_view(),
        name='contrail-verify-credentials',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),

    url(r'^openstack-cleanup/?$',
        api.views_os_custom.os_cleanup,
        name='openstack-cleanup',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
)

