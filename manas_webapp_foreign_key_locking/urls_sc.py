
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
import api.views_sc

urlpatterns = patterns('',
    
    url(r'^scpoolserverstateinfo/?$',
        api.views_sc.SCPoolServerStateInfoList.as_view(),
        name='scpoolserverstateinfo-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CONTROLLER"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/scpoolserverstateinfo/?$',
        api.views_sc.SCPoolServerStateInfoList.as_view(),
        name='scpoolserverstateinfo-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CONTROLLER"}),  
                
    url(r'^scpoolserverstateinfo/(?P<slug>[-\w.]+)/?$',
        api.views_sc.SCPoolServerStateInfoDetail.as_view(),
        name='scpoolserverstateinfo-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CONTROLLER"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/scpoolserverstateinfo/(?P<slug>[-\w.]+)/?$',
        api.views_sc.SCPoolServerStateInfoDetail.as_view(),
        name='scpoolserverstateinfo-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CONTROLLER"}),
                
        
    
    url(r'^scvsstateinfo/?$',
        api.views_sc.SCVsStateInfoList.as_view(),
        name='scvsstateinfo-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CONTROLLER"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/scvsstateinfo/?$',
        api.views_sc.SCVsStateInfoList.as_view(),
        name='scvsstateinfo-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CONTROLLER"}),  
                
    url(r'^scvsstateinfo/(?P<slug>[-\w.]+)/?$',
        api.views_sc.SCVsStateInfoDetail.as_view(),
        name='scvsstateinfo-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CONTROLLER"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/scvsstateinfo/(?P<slug>[-\w.]+)/?$',
        api.views_sc.SCVsStateInfoDetail.as_view(),
        name='scvsstateinfo-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CONTROLLER"}),
                
        

)
