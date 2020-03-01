
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
import api.views_analysis

urlpatterns = patterns('',
    url(r'^virtualservice/(?P<key>[-\w.]+)/analysis/?$',
        api.views_analysis.VsAnalysisView.as_view(),
        name='vsanalysis',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_VIRTUALSERVICE"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/virtualservice/(?P<key>[-\w.]+)/analysis/?$',
        api.views_analysis.VsAnalysisView.as_view(),
        name='vsanalysis-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_VIRTUALSERVICE"}),

    url(r'^serviceengine/(?P<key>[-\w.]+)/analysis/?$',
        api.views_analysis.SeAnalysisView.as_view(),
        name='seanalysis',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_VIRTUALSERVICE"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/serviceengine/(?P<key>[-\w.]+)/analysis/?$',
        api.views_analysis.SeAnalysisView.as_view(),
        name='seanalysis-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_VIRTUALSERVICE"}),

    url(r'^virtualservice/analysis/?$',
        api.views_analysis.VsAnalysisSummaryView.as_view(),
        name='vsanalysissummary',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_VIRTUALSERVICE"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/virtualservice/analysis/?$',
        api.views_analysis.VsAnalysisSummaryView.as_view(),
        name='vsanalysissummary-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_VIRTUALSERVICE"}),

    url(r'^serviceengine/analysis/?$',
        api.views_analysis.SeAnalysisSummaryView.as_view(),
        name='seanalysissummary',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_VIRTUALSERVICE"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/serviceengine/analysis/?$',
        api.views_analysis.SeAnalysisSummaryView.as_view(),
        name='seanalysissummary-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_VIRTUALSERVICE"}),

    url(r'^cloud/(?P<key>[-\w.]+)/analysis/?$',
        api.views_analysis.CloudAnalysisView.as_view(),
        name='cloudanalysis',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_VIRTUALSERVICE"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/cloud/(?P<key>[-\w.]+)/analysis/?$',
        api.views_analysis.CloudAnalysisView.as_view(),
        name='cloudanalysis-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_VIRTUALSERVICE"}),
)
