
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
import api.views_micro_service

urlpatterns = patterns('',
    
    url(r'^microservice/?$',
        api.views_micro_service.MicroServiceList.as_view(),
        name='microservice-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_MICROSERVICE"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/microservice/?$',
        api.views_micro_service.MicroServiceList.as_view(),
        name='microservice-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_MICROSERVICE"}),  
                
    url(r'^microservice/(?P<slug>[-\w.]+)/?$',
        api.views_micro_service.MicroServiceDetail.as_view(),
        name='microservice-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_MICROSERVICE"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/microservice/(?P<slug>[-\w.]+)/?$',
        api.views_micro_service.MicroServiceDetail.as_view(),
        name='microservice-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_MICROSERVICE"}),
                
            
    url(r'^microservice/(?P<key>[-\w.]+)/runtime/detail/?$',
        api.views_micro_service.MicroServiceDetailView.as_view(),
        name='microservicedetail-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_MICROSERVICE"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/microservice/(?P<key>[-\w.]+)/runtime/detail/?$',
        api.views_micro_service.MicroServiceDetailView.as_view(),
        name='microservicedetail-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_MICROSERVICE"}),
                
    url(r'^microservice/(?P<key>[-\w.]+)/runtime/internal/?$',
        api.views_micro_service.MicroServiceInternalView.as_view(),
        name='microserviceinternal-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_MICROSERVICE"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/microservice/(?P<key>[-\w.]+)/runtime/internal/?$',
        api.views_micro_service.MicroServiceInternalView.as_view(),
        name='microserviceinternal-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_MICROSERVICE"}),
            

)
