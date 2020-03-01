
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
import api.views_autoscale_mgr

urlpatterns = patterns('',
    
    url(r'^autoscale_mgr/?$',
        api.views_autoscale_mgr.AutoScaleStateList.as_view(),
        name='autoscale_mgr-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_VIRTUALSERVICE"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/autoscale_mgr/?$',
        api.views_autoscale_mgr.AutoScaleStateList.as_view(),
        name='autoscale_mgr-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_VIRTUALSERVICE"}),  
                
    url(r'^autoscale_mgr/(?P<slug>[-\w.]+)/?$',
        api.views_autoscale_mgr.AutoScaleStateDetail.as_view(),
        name='autoscale_mgr-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_VIRTUALSERVICE"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/autoscale_mgr/(?P<slug>[-\w.]+)/?$',
        api.views_autoscale_mgr.AutoScaleStateDetail.as_view(),
        name='autoscale_mgr-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_VIRTUALSERVICE"}),
                
        

)
