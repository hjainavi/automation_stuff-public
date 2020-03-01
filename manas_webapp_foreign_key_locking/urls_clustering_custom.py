
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
import api.views_clustering_custom

urlpatterns = patterns('',
    url(r'^cluster/?$',
        api.views_clustering_custom.ClusterDetail.as_view(),
        name='cluster-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CONTROLLER"}),
    url(r'^cluster/runtime/?$',
        api.views_clustering_custom.ClusterStatusView.as_view(),
        name='cluster-status',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CONTROLLER"}),
    url(r'^cluster/status/?$',
        api.views_clustering_custom.ClusterNodeStatusView.as_view(),
        name='cluster-status',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CONTROLLER"}),
    url(r'^cluster/reboot/node/?$',
        api.views_clustering_custom.ClusterRebootNode.as_view(),
        name='cluster-reboot',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CONTROLLER"}),
    url(r'^cluster/reboot/?$',
        api.views_clustering_custom.ClusterReboot.as_view(),
        name='cluster-reboot',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CONTROLLER"}),
    url(r'^cluster/upgrade/?$',
        api.views_clustering_custom.ClusterUpgradeView.as_view(),
        name='cluster-upgrade',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CONTROLLER"}),
    url(r'^cluster/upgrade/status/?$',
        api.views_clustering_custom.ClusterUpgradeStatusView.as_view(),
        name='cluster-upgrade-status',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CONTROLLER"}),
    url(r'^cluster/upgrade/history/?$',
        api.views_clustering_custom.ClusterUpgradeHistoryView.as_view(),
        name='cluster-upgrade-history',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CONTROLLER"}),
    url(r'^cluster/rollback/?$',
        api.views_clustering_custom.ClusterRollbackView.as_view(),
        name='cluster-rollback',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CONTROLLER"}),
    url(r'^cluster/(?P<slug>[-\w]+)/?$',
        api.views_clustering_custom.ClusterDetail.as_view(),
        name='cluster-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CONTROLLER"}),
    url(r'^version/controller/?$',
        api.views_clustering_custom.ControllerVersionView.as_view(),
        name='controller-version',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CONTROLLER"}),
    url(r'^diskusage/controller/?$',
        api.views_clustering_custom.ControllerDiskUsageView.as_view(),
        name='controller-diskusage',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CONTROLLER"}),
    url(r'^diskusage/se/?$',
        api.views_clustering_custom.ServiceengineDiskUsageView.as_view(),
        name='serviceengine-diskusage',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CONTROLLER"}),
    url(r'^memoryusage/controller/?$',
        api.views_clustering_custom.ControllerMemoryUsageView.as_view(),
        name='controller-memoryusage',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CONTROLLER"}),
    url(r'^cpuusage/controller/?$',
        api.views_clustering_custom.ControllerCPUUsageView.as_view(),
        name='controller-cpuusage',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CONTROLLER"}),
    url(r'^version/se/?$',
        api.views_clustering_custom.SeVersionView.as_view(),
        name='se-version',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CONTROLLER"}),
    url(r'^version/ui/?$',
        api.views_clustering_custom.UiVersionView.as_view(),
        name='ui-version',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CONTROLLER"}),

)
