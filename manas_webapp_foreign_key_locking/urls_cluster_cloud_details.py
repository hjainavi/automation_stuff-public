
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
import api.views_cluster_cloud_details as views_cc_details

urlpatterns = patterns('',    
    url(r'^clusterclouddetails/?$',
        views_cc_details.ClusterCloudDetailsListView.as_view(),
        name='cluster-cloud-details-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CONTROLLER"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/clusterclouddetails/?$',
        views_cc_details.ClusterCloudDetailsListView.as_view(),
        name='cluster-cloud-details-list',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CONTROLLER"}),

    url(r'^clusterclouddetails/(?P<slug>[-\w.]+)/?$',
        views_cc_details.ClusterCloudDetailsView.as_view(),
        name='cluster-cloud-details',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CONTROLLER"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/clusterclouddetails/(?P<slug>[-\w.]+)/?$',
        views_cc_details.ClusterCloudDetailsView.as_view(),
        name='cluster-cloud-details',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CONTROLLER"}),

)
