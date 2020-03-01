
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
import api.views_django

urlpatterns = patterns('',
    
    url(r'^useractivity/?$',
        api.views_django.UserActivityList.as_view(),
        name='useractivity-list',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_USER"}),

                
    url(r'^useractivity/(?P<slug>[-\w.]+)/?$',
        api.views_django.UserActivityDetail.as_view(),
        name='useractivity-detail',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_USER"}),
                
        
    
    url(r'^useraccountprofile/?$',
        api.views_django.UserAccountProfileList.as_view(),
        name='useraccountprofile-list',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_USER"}),

                
    url(r'^useraccountprofile/(?P<slug>[-\w.]+)/?$',
        api.views_django.UserAccountProfileDetail.as_view(),
        name='useraccountprofile-detail',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_USER"}),
                
        

)
