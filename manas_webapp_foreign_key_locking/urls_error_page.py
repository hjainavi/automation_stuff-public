
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
import api.views_error_page

urlpatterns = patterns('',
    
    url(r'^errorpageprofile/?$',
        api.views_error_page.ErrorPageProfileList.as_view(),
        name='errorpageprofile-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_ERRORPAGEPROFILE"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/errorpageprofile/?$',
        api.views_error_page.ErrorPageProfileList.as_view(),
        name='errorpageprofile-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_ERRORPAGEPROFILE"}),  
                
    url(r'^errorpageprofile/(?P<slug>[-\w.]+)/?$',
        api.views_error_page.ErrorPageProfileDetail.as_view(),
        name='errorpageprofile-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_ERRORPAGEPROFILE"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/errorpageprofile/(?P<slug>[-\w.]+)/?$',
        api.views_error_page.ErrorPageProfileDetail.as_view(),
        name='errorpageprofile-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_ERRORPAGEPROFILE"}),
                
        
    
    url(r'^errorpagebody/?$',
        api.views_error_page.ErrorPageBodyList.as_view(),
        name='errorpagebody-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_ERRORPAGEBODY"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/errorpagebody/?$',
        api.views_error_page.ErrorPageBodyList.as_view(),
        name='errorpagebody-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_ERRORPAGEBODY"}),  
                
    url(r'^errorpagebody/(?P<slug>[-\w.]+)/?$',
        api.views_error_page.ErrorPageBodyDetail.as_view(),
        name='errorpagebody-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_ERRORPAGEBODY"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/errorpagebody/(?P<slug>[-\w.]+)/?$',
        api.views_error_page.ErrorPageBodyDetail.as_view(),
        name='errorpagebody-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_ERRORPAGEBODY"}),
                
        

)
