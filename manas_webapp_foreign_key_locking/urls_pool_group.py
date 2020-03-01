
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
import api.views_pool_group

urlpatterns = patterns('',
    
    url(r'^poolgroup/?$',
        api.views_pool_group.PoolGroupList.as_view(),
        name='poolgroup-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_POOLGROUP"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/poolgroup/?$',
        api.views_pool_group.PoolGroupList.as_view(),
        name='poolgroup-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_POOLGROUP"}),  
                
    url(r'^poolgroup/(?P<slug>[-\w.]+)/?$',
        api.views_pool_group.PoolGroupDetail.as_view(),
        name='poolgroup-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_POOLGROUP"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/poolgroup/(?P<slug>[-\w.]+)/?$',
        api.views_pool_group.PoolGroupDetail.as_view(),
        name='poolgroup-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_POOLGROUP"}),
                
        

)
