
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
import api.views_server_autoscale

urlpatterns = patterns('',
    
    url(r'^serverautoscalepolicy/?$',
        api.views_server_autoscale.ServerAutoScalePolicyList.as_view(),
        name='serverautoscalepolicy-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_AUTOSCALE"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/serverautoscalepolicy/?$',
        api.views_server_autoscale.ServerAutoScalePolicyList.as_view(),
        name='serverautoscalepolicy-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_AUTOSCALE"}),  
                
    url(r'^serverautoscalepolicy/(?P<slug>[-\w.]+)/?$',
        api.views_server_autoscale.ServerAutoScalePolicyDetail.as_view(),
        name='serverautoscalepolicy-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_AUTOSCALE"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/serverautoscalepolicy/(?P<slug>[-\w.]+)/?$',
        api.views_server_autoscale.ServerAutoScalePolicyDetail.as_view(),
        name='serverautoscalepolicy-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_AUTOSCALE"}),
                
        
    
    url(r'^autoscalelaunchconfig/?$',
        api.views_server_autoscale.AutoScaleLaunchConfigList.as_view(),
        name='autoscalelaunchconfig-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_AUTOSCALE"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/autoscalelaunchconfig/?$',
        api.views_server_autoscale.AutoScaleLaunchConfigList.as_view(),
        name='autoscalelaunchconfig-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_AUTOSCALE"}),  
                
    url(r'^autoscalelaunchconfig/(?P<slug>[-\w.]+)/?$',
        api.views_server_autoscale.AutoScaleLaunchConfigDetail.as_view(),
        name='autoscalelaunchconfig-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_AUTOSCALE"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/autoscalelaunchconfig/(?P<slug>[-\w.]+)/?$',
        api.views_server_autoscale.AutoScaleLaunchConfigDetail.as_view(),
        name='autoscalelaunchconfig-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_AUTOSCALE"}),
                
        

)
