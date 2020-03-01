
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
import api.views_waf_policy

urlpatterns = patterns('',
    
    url(r'^wafpolicy/?$',
        api.views_waf_policy.WafPolicyList.as_view(),
        name='wafpolicy-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_WAFPOLICY"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/wafpolicy/?$',
        api.views_waf_policy.WafPolicyList.as_view(),
        name='wafpolicy-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_WAFPOLICY"}),  
                
    url(r'^wafpolicy/(?P<slug>[-\w.]+)/?$',
        api.views_waf_policy.WafPolicyDetail.as_view(),
        name='wafpolicy-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_WAFPOLICY"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/wafpolicy/(?P<slug>[-\w.]+)/?$',
        api.views_waf_policy.WafPolicyDetail.as_view(),
        name='wafpolicy-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_WAFPOLICY"}),
                
        
    
    url(r'^wafcrs/?$',
        api.views_waf_policy.WafCRSList.as_view(),
        name='wafcrs-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_WAFPOLICY"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/wafcrs/?$',
        api.views_waf_policy.WafCRSList.as_view(),
        name='wafcrs-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_WAFPOLICY"}),  
                
    url(r'^wafcrs/(?P<slug>[-\w.]+)/?$',
        api.views_waf_policy.WafCRSDetail.as_view(),
        name='wafcrs-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_WAFPOLICY"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/wafcrs/(?P<slug>[-\w.]+)/?$',
        api.views_waf_policy.WafCRSDetail.as_view(),
        name='wafcrs-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_WAFPOLICY"}),
                
        

)
