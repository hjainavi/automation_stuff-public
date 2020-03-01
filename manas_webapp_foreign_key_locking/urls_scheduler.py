
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
import api.views_scheduler

urlpatterns = patterns('',
    
    url(r'^scheduler/?$',
        api.views_scheduler.SchedulerList.as_view(),
        name='scheduler-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CONTROLLER"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/scheduler/?$',
        api.views_scheduler.SchedulerList.as_view(),
        name='scheduler-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CONTROLLER"}),  
                
    url(r'^scheduler/(?P<slug>[-\w.]+)/?$',
        api.views_scheduler.SchedulerDetail.as_view(),
        name='scheduler-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CONTROLLER"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/scheduler/(?P<slug>[-\w.]+)/?$',
        api.views_scheduler.SchedulerDetail.as_view(),
        name='scheduler-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CONTROLLER"}),
                
        
    
    url(r'^backupconfiguration/?$',
        api.views_scheduler.BackupConfigurationList.as_view(),
        name='backupconfiguration-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CONTROLLER"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/backupconfiguration/?$',
        api.views_scheduler.BackupConfigurationList.as_view(),
        name='backupconfiguration-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CONTROLLER"}),  
                
    url(r'^backupconfiguration/(?P<slug>[-\w.]+)/?$',
        api.views_scheduler.BackupConfigurationDetail.as_view(),
        name='backupconfiguration-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CONTROLLER"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/backupconfiguration/(?P<slug>[-\w.]+)/?$',
        api.views_scheduler.BackupConfigurationDetail.as_view(),
        name='backupconfiguration-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CONTROLLER"}),
                
        

)
