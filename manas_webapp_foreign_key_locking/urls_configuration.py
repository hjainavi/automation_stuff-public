
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

#Custom urls
from django.conf.urls import patterns, include, url
import api.views_configuration

urlpatterns = patterns('',
    url(r'^cluster/version/?$',
        api.views_configuration.GetVersionView.as_view(),
        name='cluster-version',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_CONTROLLER"}),
    url(r'^configuration/export?$',
        api.views_configuration.ExportConfigView.as_view(),
        name='configuration-export',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_CONTROLLER"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/configuration/export?$',
        api.views_configuration.ExportConfigView.as_view(),
        name='configuration-export-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CONTROLLER"}),
    url(r'^configuration/import?$',
        api.views_configuration.ImportConfigView.as_view(),
        name='configuration-import',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_CONTROLLER"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/configuration/import?$',
        api.views_configuration.ImportConfigView.as_view(),
        name='configuration-import-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CONTROLLER"}),

    url(r'^configuration/export/virtualservice/(?P<slug>[-\w.]+)/?$',
        api.views_configuration.ExportVirtualServiceView.as_view(),
        name='configuration-virtualservice-export',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_VIRTUALSERVICE"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/configuration/export/virtualservice/(?P<slug>[-\w.]+)/?$',
        api.views_configuration.ExportVirtualServiceView.as_view(),
        name='configuration-virtualservice-export-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_VIRTUALSERVICE"}),
)
