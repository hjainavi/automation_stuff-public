
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
import api.views_network_profile

urlpatterns = patterns('',
    
    url(r'^networkprofile/?$',
        api.views_network_profile.NetworkProfileList.as_view(),
        name='networkprofile-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_NETWORKPROFILE"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/networkprofile/?$',
        api.views_network_profile.NetworkProfileList.as_view(),
        name='networkprofile-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_NETWORKPROFILE"}),  
                
    url(r'^networkprofile/(?P<slug>[-\w.]+)/?$',
        api.views_network_profile.NetworkProfileDetail.as_view(),
        name='networkprofile-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_NETWORKPROFILE"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/networkprofile/(?P<slug>[-\w.]+)/?$',
        api.views_network_profile.NetworkProfileDetail.as_view(),
        name='networkprofile-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_NETWORKPROFILE"}),
                
            
    url(r'^networkprofile/(?P<key>[-\w.]+)/runtime/internal/?$',
        api.views_network_profile.NetworkProfileInternalView.as_view(),
        name='networkprofileinternal-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_NETWORKPROFILE"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/networkprofile/(?P<key>[-\w.]+)/runtime/internal/?$',
        api.views_network_profile.NetworkProfileInternalView.as_view(),
        name='networkprofileinternal-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_NETWORKPROFILE"}),
            

)
