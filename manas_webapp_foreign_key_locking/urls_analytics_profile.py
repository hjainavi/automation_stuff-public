
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

#GENERATED FILE 
#pylint:  skip-file
from django.conf.urls import patterns, include, url
import api.views_analytics_profile

urlpatterns = patterns('',
    
    url(r'^analyticsprofile/?$',
        api.views_analytics_profile.AnalyticsProfileList.as_view(),
        name='analyticsprofile-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_ANALYTICSPROFILE"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/analyticsprofile/?$',
        api.views_analytics_profile.AnalyticsProfileList.as_view(),
        name='analyticsprofile-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_ANALYTICSPROFILE"}),  
                
    url(r'^analyticsprofile/(?P<slug>[-\w.]+)/?$',
        api.views_analytics_profile.AnalyticsProfileDetail.as_view(),
        name='analyticsprofile-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_ANALYTICSPROFILE"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/analyticsprofile/(?P<slug>[-\w.]+)/?$',
        api.views_analytics_profile.AnalyticsProfileDetail.as_view(),
        name='analyticsprofile-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_ANALYTICSPROFILE"}),
                
            
    url(r'^analyticsprofile/(?P<key>[-\w.]+)/runtime/internal/?$',
        api.views_analytics_profile.AnalyticsProfileInternalView.as_view(),
        name='analyticsprofileinternal-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_ANALYTICSPROFILE"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/analyticsprofile/(?P<key>[-\w.]+)/runtime/internal/?$',
        api.views_analytics_profile.AnalyticsProfileInternalView.as_view(),
        name='analyticsprofileinternal-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_ANALYTICSPROFILE"}),
            

)
