
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
import api.views_system

urlpatterns = patterns('',
            
    url(r'^systemconfiguration/?$',
        api.views_system.SystemConfigurationDetail.as_view(),
        name='systemconfiguration-detail',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_SYSTEMCONFIGURATION"}),
            
    
    url(r'^testemail/?$',
        api.views_system.SystemConfigurationSystestemailView.as_view(),
        name='systemconfigurationsystestemailview-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_SYSTEMCONFIGURATION"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/testemail/?$',
        api.views_system.SystemConfigurationSystestemailView.as_view(),
        name='systemconfigurationsystestemailview-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_SYSTEMCONFIGURATION" }),
        
    
    url(r'^controllersite/?$',
        api.views_system.ControllerSiteList.as_view(),
        name='controllersite-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CONTROLLERSITE"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/controllersite/?$',
        api.views_system.ControllerSiteList.as_view(),
        name='controllersite-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CONTROLLERSITE"}),  
                
    url(r'^controllersite/(?P<slug>[-\w.]+)/?$',
        api.views_system.ControllerSiteDetail.as_view(),
        name='controllersite-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CONTROLLERSITE"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/controllersite/(?P<slug>[-\w.]+)/?$',
        api.views_system.ControllerSiteDetail.as_view(),
        name='controllersite-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CONTROLLERSITE"}),
                
        

)
