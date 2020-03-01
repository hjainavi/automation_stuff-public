
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
import api.views_cloud_connector_custom as views_cc_custom
from api.views_cloud_connector_custom import (CCAutoscaleGroupView,
    CCAutoscaleGroupServersListView, CCAutoscaleGroupListView)

urlpatterns = patterns('',
    url('', include('api.urls_os_custom')),
    url('', include('api.urls_aws_custom')),
    url('', include('api.urls_azure_custom')),
    url('', include('api.urls_container_custom')),
    url('', include('api.urls_gcp_custom')),
    url('', include('api.urls_cloudstack_custom')),
    url('', include('api.urls_vca_custom')),
    url('', include('api.urls_bm_custom')),

    url(r'^cloud/(?P<slug>[-\w.]+)/flavors/?$',
        views_cc_custom.CCFlavorsView.as_view(),
        name='cloud-flavors',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),

    url(r'^cloud/(?P<slug>[-\w.]+)/internals/?$',
        views_cc_custom.CCInternalsView.as_view(),
        name='cloud-internals',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),

    url(r'^cloud/(?P<slug>[-\w.]+)/gc/?$',
        views_cc_custom.CCGarbageCollView.as_view(),
        name='cloud-gc',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),

    url(r'^cloud/(?P<slug>[-\w.]+)/status/?$',
        views_cc_custom.CloudStatusView.as_view(),
        name='cloud-status',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),

    url(r'^cloud/(?P<slug>[-\w.]+)/health/?$',
        views_cc_custom.CCHealthCheckView.as_view(),
        name='cloud-health',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),

    url(r'^cloud/(?P<slug>[-\w.]+)/availability-zones/?$',
        views_cc_custom.CCAvailabilityZonesView.as_view(),
        name='cloud-availability-zone1',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),

    url(r'^cloud/(?P<slug>[-\w.]+)/securitygroups/?$',
        views_cc_custom.CCSecurityGroupsView.as_view(),
        name='cloud-secutirygroups',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),

    # get list of all autoscalegroup
    url(r'^cloud/(?P<slug>[-\w.]+)/autoscalegroup/?$',
        CCAutoscaleGroupListView.as_view(),
        name='cloud-autoscalegroup',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),

    url(r'^cloud/(?P<slug>[-\w.]+)/autoscalegroup/(?P<group_name>[-\w.@]+)/?$',
        CCAutoscaleGroupView.as_view(),
        name='cloud-autoscalegroup',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),

    url(r'^cloud/(?P<slug>[-\w.]+)/autoscalegroup/(?P<group_name>[-\w.@]+)/servers?$',
        CCAutoscaleGroupServersListView.as_view(),
        name='cloud-autoscalegroupservers',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),

    # this is for all clouds
    url(r'^cloud-internals/?$',
        views_cc_custom.CCInternalsView.as_view(),
        name='all-clouds-internals',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),

    # this is for vCenter Cloud only
    url(r'^cloud/(?P<slug>[-\w.]+)/diag/?$',
        views_cc_custom.CCCloudDiagViews.as_view(),
        name='cloud-diag',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
)
