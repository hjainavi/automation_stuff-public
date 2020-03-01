
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
import api.views_application_profile

urlpatterns = patterns('',
    
    url(r'^applicationprofile/?$',
        api.views_application_profile.ApplicationProfileList.as_view(),
        name='applicationprofile-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_APPLICATIONPROFILE"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/applicationprofile/?$',
        api.views_application_profile.ApplicationProfileList.as_view(),
        name='applicationprofile-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_APPLICATIONPROFILE"}),  
                
    url(r'^applicationprofile/(?P<slug>[-\w.]+)/?$',
        api.views_application_profile.ApplicationProfileDetail.as_view(),
        name='applicationprofile-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_APPLICATIONPROFILE"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/applicationprofile/(?P<slug>[-\w.]+)/?$',
        api.views_application_profile.ApplicationProfileDetail.as_view(),
        name='applicationprofile-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_APPLICATIONPROFILE"}),
                
            
    url(r'^applicationprofile/(?P<key>[-\w.]+)/runtime/internal/?$',
        api.views_application_profile.ApplicationProfileInternalView.as_view(),
        name='applicationprofileinternal-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_APPLICATIONPROFILE"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/applicationprofile/(?P<key>[-\w.]+)/runtime/internal/?$',
        api.views_application_profile.ApplicationProfileInternalView.as_view(),
        name='applicationprofileinternal-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_APPLICATIONPROFILE"}),
            

)
