
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
import api.views_network_policy

urlpatterns = patterns('',
    
    url(r'^networksecuritypolicy/?$',
        api.views_network_policy.NetworkSecurityPolicyList.as_view(),
        name='networksecuritypolicy-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_NETWORKSECURITYPOLICY"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/networksecuritypolicy/?$',
        api.views_network_policy.NetworkSecurityPolicyList.as_view(),
        name='networksecuritypolicy-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_NETWORKSECURITYPOLICY"}),  
                
    url(r'^networksecuritypolicy/(?P<slug>[-\w.]+)/?$',
        api.views_network_policy.NetworkSecurityPolicyDetail.as_view(),
        name='networksecuritypolicy-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_NETWORKSECURITYPOLICY"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/networksecuritypolicy/(?P<slug>[-\w.]+)/?$',
        api.views_network_policy.NetworkSecurityPolicyDetail.as_view(),
        name='networksecuritypolicy-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_NETWORKSECURITYPOLICY"}),
                
        

)
