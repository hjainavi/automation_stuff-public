
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
import api.views_placement

urlpatterns = patterns('',
    
    url(r'^placement/stats/?$',
        api.views_placement.PlacementStatsList.as_view(),
        name='placement/stats-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_INTERNAL"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/placement/stats/?$',
        api.views_placement.PlacementStatsList.as_view(),
        name='placement/stats-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_INTERNAL"}),  
                
    url(r'^placement/stats/(?P<slug>[-\w.]+)/?$',
        api.views_placement.PlacementStatsDetail.as_view(),
        name='placement/stats-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_INTERNAL"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/placement/stats/(?P<slug>[-\w.]+)/?$',
        api.views_placement.PlacementStatsDetail.as_view(),
        name='placement/stats-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_INTERNAL"}),
                
        
    
    url(r'^placement/status/?$',
        api.views_placement.PlacementStatusList.as_view(),
        name='placement/status-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_INTERNAL"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/placement/status/?$',
        api.views_placement.PlacementStatusList.as_view(),
        name='placement/status-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_INTERNAL"}),  
                
    url(r'^placement/status/(?P<slug>[-\w.]+)/?$',
        api.views_placement.PlacementStatusDetail.as_view(),
        name='placement/status-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_INTERNAL"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/placement/status/(?P<slug>[-\w.]+)/?$',
        api.views_placement.PlacementStatusDetail.as_view(),
        name='placement/status-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_INTERNAL"}),
                
        
    
    url(r'^placement/consumers/?$',
        api.views_placement.SeConsumerProtoList.as_view(),
        name='placement/consumers-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_INTERNAL"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/placement/consumers/?$',
        api.views_placement.SeConsumerProtoList.as_view(),
        name='placement/consumers-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_INTERNAL"}),  
                
    url(r'^placement/consumers/(?P<slug>[-\w.]+)/?$',
        api.views_placement.SeConsumerProtoDetail.as_view(),
        name='placement/consumers-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_INTERNAL"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/placement/consumers/(?P<slug>[-\w.]+)/?$',
        api.views_placement.SeConsumerProtoDetail.as_view(),
        name='placement/consumers-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_INTERNAL"}),
                
        
    
    url(r'^placement/createpending/?$',
        api.views_placement.SeCreatePendingProtoList.as_view(),
        name='placement/createpending-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_INTERNAL"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/placement/createpending/?$',
        api.views_placement.SeCreatePendingProtoList.as_view(),
        name='placement/createpending-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_INTERNAL"}),  
                
    url(r'^placement/createpending/(?P<slug>[-\w.]+)/?$',
        api.views_placement.SeCreatePendingProtoDetail.as_view(),
        name='placement/createpending-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_INTERNAL"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/placement/createpending/(?P<slug>[-\w.]+)/?$',
        api.views_placement.SeCreatePendingProtoDetail.as_view(),
        name='placement/createpending-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_INTERNAL"}),
                
        
    
    url(r'^placement/vip/?$',
        api.views_placement.SeVipProtoList.as_view(),
        name='placement/vip-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_INTERNAL"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/placement/vip/?$',
        api.views_placement.SeVipProtoList.as_view(),
        name='placement/vip-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_INTERNAL"}),  
                
    url(r'^placement/vip/(?P<slug>[-\w.]+)/?$',
        api.views_placement.SeVipProtoDetail.as_view(),
        name='placement/vip-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_INTERNAL"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/placement/vip/(?P<slug>[-\w.]+)/?$',
        api.views_placement.SeVipProtoDetail.as_view(),
        name='placement/vip-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_INTERNAL"}),
                
        
    
    url(r'^placement/resources/?$',
        api.views_placement.SeResourceProtoList.as_view(),
        name='placement/resources-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_INTERNAL"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/placement/resources/?$',
        api.views_placement.SeResourceProtoList.as_view(),
        name='placement/resources-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_INTERNAL"}),  
                
    url(r'^placement/resources/(?P<slug>[-\w.]+)/?$',
        api.views_placement.SeResourceProtoDetail.as_view(),
        name='placement/resources-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_INTERNAL"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/placement/resources/(?P<slug>[-\w.]+)/?$',
        api.views_placement.SeResourceProtoDetail.as_view(),
        name='placement/resources-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_INTERNAL"}),
                
        
    
    url(r'^placement/vrf/?$',
        api.views_placement.RmVrfProtoList.as_view(),
        name='placement/vrf-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_INTERNAL"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/placement/vrf/?$',
        api.views_placement.RmVrfProtoList.as_view(),
        name='placement/vrf-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_INTERNAL"}),  
                
    url(r'^placement/vrf/(?P<slug>[-\w.]+)/?$',
        api.views_placement.RmVrfProtoDetail.as_view(),
        name='placement/vrf-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_INTERNAL"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/placement/vrf/(?P<slug>[-\w.]+)/?$',
        api.views_placement.RmVrfProtoDetail.as_view(),
        name='placement/vrf-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_INTERNAL"}),
                
        
    
    url(r'^placement/globals/?$',
        api.views_placement.PlacementGlobalsList.as_view(),
        name='placement/globals-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_INTERNAL"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/placement/globals/?$',
        api.views_placement.PlacementGlobalsList.as_view(),
        name='placement/globals-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_INTERNAL"}),  
                
    url(r'^placement/globals/(?P<slug>[-\w.]+)/?$',
        api.views_placement.PlacementGlobalsDetail.as_view(),
        name='placement/globals-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_INTERNAL"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/placement/globals/(?P<slug>[-\w.]+)/?$',
        api.views_placement.PlacementGlobalsDetail.as_view(),
        name='placement/globals-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_INTERNAL"}),
                
        

)
