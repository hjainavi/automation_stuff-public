
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
import api.views_object_graph

urlpatterns = patterns('',
    url(r'^object-graph/?$',
        api.views_object_graph.ObjectGraphList.as_view(),
        name='objectgraph-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_VIRTUALSERVICE"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/objectgraph/?$',
        api.views_object_graph.ObjectGraphList.as_view(),
        name='object-graph-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_VIRTUALSERVICE"}),

)
