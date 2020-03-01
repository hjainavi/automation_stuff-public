
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
import api.views_match

urlpatterns = patterns('',
    
    url(r'^ipaddrgroup/?$',
        api.views_match.IpAddrGroupList.as_view(),
        name='ipaddrgroup-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_IPADDRGROUP"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/ipaddrgroup/?$',
        api.views_match.IpAddrGroupList.as_view(),
        name='ipaddrgroup-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_IPADDRGROUP"}),  
                
    url(r'^ipaddrgroup/(?P<slug>[-\w.]+)/?$',
        api.views_match.IpAddrGroupDetail.as_view(),
        name='ipaddrgroup-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_IPADDRGROUP"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/ipaddrgroup/(?P<slug>[-\w.]+)/?$',
        api.views_match.IpAddrGroupDetail.as_view(),
        name='ipaddrgroup-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_IPADDRGROUP"}),
                
        
    
    url(r'^stringgroup/?$',
        api.views_match.StringGroupList.as_view(),
        name='stringgroup-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_STRINGGROUP"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/stringgroup/?$',
        api.views_match.StringGroupList.as_view(),
        name='stringgroup-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_STRINGGROUP"}),  
                
    url(r'^stringgroup/(?P<slug>[-\w.]+)/?$',
        api.views_match.StringGroupDetail.as_view(),
        name='stringgroup-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_STRINGGROUP"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/stringgroup/(?P<slug>[-\w.]+)/?$',
        api.views_match.StringGroupDetail.as_view(),
        name='stringgroup-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_STRINGGROUP"}),
                
        
    
    url(r'^microservicegroup/?$',
        api.views_match.MicroServiceGroupList.as_view(),
        name='microservicegroup-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_MICROSERVICEGROUP"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/microservicegroup/?$',
        api.views_match.MicroServiceGroupList.as_view(),
        name='microservicegroup-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_MICROSERVICEGROUP"}),  
                
    url(r'^microservicegroup/(?P<slug>[-\w.]+)/?$',
        api.views_match.MicroServiceGroupDetail.as_view(),
        name='microservicegroup-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_MICROSERVICEGROUP"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/microservicegroup/(?P<slug>[-\w.]+)/?$',
        api.views_match.MicroServiceGroupDetail.as_view(),
        name='microservicegroup-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_MICROSERVICEGROUP"}),
                
            
    url(r'^microservicegroup/(?P<key>[-\w.]+)/runtime/detail/?$',
        api.views_match.MicroServiceGroupDetailView.as_view(),
        name='microservicegroupdetail-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_MICROSERVICEGROUP"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/microservicegroup/(?P<key>[-\w.]+)/runtime/detail/?$',
        api.views_match.MicroServiceGroupDetailView.as_view(),
        name='microservicegroupdetail-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_MICROSERVICEGROUP"}),
            

)
