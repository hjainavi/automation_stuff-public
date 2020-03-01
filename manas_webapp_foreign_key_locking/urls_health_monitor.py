
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
import api.views_health_monitor

urlpatterns = patterns('',
    
    url(r'^healthmonitor/?$',
        api.views_health_monitor.HealthMonitorList.as_view(),
        name='healthmonitor-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_HEALTHMONITOR"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/healthmonitor/?$',
        api.views_health_monitor.HealthMonitorList.as_view(),
        name='healthmonitor-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_HEALTHMONITOR"}),  
                
    url(r'^healthmonitor/(?P<slug>[-\w.]+)/?$',
        api.views_health_monitor.HealthMonitorDetail.as_view(),
        name='healthmonitor-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_HEALTHMONITOR"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/healthmonitor/(?P<slug>[-\w.]+)/?$',
        api.views_health_monitor.HealthMonitorDetail.as_view(),
        name='healthmonitor-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_HEALTHMONITOR"}),
                
            
    url(r'^healthmonitor/(?P<key>[-\w.]+)/federated_info/?$',
        api.views_health_monitor.GslbHealthMonitorRuntimeView.as_view(),
        name='gslbhealthmonitorruntime-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_HEALTHMONITOR"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/healthmonitor/(?P<key>[-\w.]+)/federated_info/?$',
        api.views_health_monitor.GslbHealthMonitorRuntimeView.as_view(),
        name='gslbhealthmonitorruntime-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_HEALTHMONITOR"}),
            

)
