
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
import api.views_nsx

urlpatterns = patterns('',
    
    url(r'^nsx/securitygroup/ips/?$',
        api.views_nsx.NsxSgIpsList.as_view(),
        name='nsx/securitygroup/ips-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/nsx/securitygroup/ips/?$',
        api.views_nsx.NsxSgIpsList.as_view(),
        name='nsx/securitygroup/ips-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD"}),  
                
    url(r'^nsx/securitygroup/ips/(?P<slug>[-\w.]+)/?$',
        api.views_nsx.NsxSgIpsDetail.as_view(),
        name='nsx/securitygroup/ips-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/nsx/securitygroup/ips/(?P<slug>[-\w.]+)/?$',
        api.views_nsx.NsxSgIpsDetail.as_view(),
        name='nsx/securitygroup/ips-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD"}),
                
        
    
    url(r'^nsx/internal/cli/?$',
        api.views_nsx.NsxAgentInternalCliList.as_view(),
        name='nsx/internal/cli-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/nsx/internal/cli/?$',
        api.views_nsx.NsxAgentInternalCliList.as_view(),
        name='nsx/internal/cli-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD"}),  
                
    url(r'^nsx/internal/cli/(?P<slug>[-\w.]+)/?$',
        api.views_nsx.NsxAgentInternalCliDetail.as_view(),
        name='nsx/internal/cli-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/nsx/internal/cli/(?P<slug>[-\w.]+)/?$',
        api.views_nsx.NsxAgentInternalCliDetail.as_view(),
        name='nsx/internal/cli-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD"}),
                
        
            
    
    url(r'^nsx/securitygroup/all/?$',
        api.views_nsx.NsxSgInfoNsxsecuritygroupsView.as_view(),
        name='nsxsginfonsxsecuritygroupsview-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/nsx/securitygroup/all/?$',
        api.views_nsx.NsxSgInfoNsxsecuritygroupsView.as_view(),
        name='nsxsginfonsxsecuritygroupsview-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD" }),
        
            
    
    url(r'^nsx/verify/login/?$',
        api.views_nsx.NsxAgentInternalVerifynsxloginView.as_view(),
        name='nsxagentinternalverifynsxloginview-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/nsx/verify/login/?$',
        api.views_nsx.NsxAgentInternalVerifynsxloginView.as_view(),
        name='nsxagentinternalverifynsxloginview-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD" }),
    
    url(r'^nsx/clear/internal/?$',
        api.views_nsx.NsxAgentInternalClearnsxdbobjectsView.as_view(),
        name='nsxagentinternalclearnsxdbobjectsview-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/nsx/clear/internal/?$',
        api.views_nsx.NsxAgentInternalClearnsxdbobjectsView.as_view(),
        name='nsxagentinternalclearnsxdbobjectsview-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD" }),
    
    url(r'^nsx/resync/internal/?$',
        api.views_nsx.NsxAgentInternalInitiatensxresyncView.as_view(),
        name='nsxagentinternalinitiatensxresyncview-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/nsx/resync/internal/?$',
        api.views_nsx.NsxAgentInternalInitiatensxresyncView.as_view(),
        name='nsxagentinternalinitiatensxresyncview-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD" }),
    
    url(r'^nsx/reprogram/internal/?$',
        api.views_nsx.NsxAgentInternalReprogramavinsxobjectsView.as_view(),
        name='nsxagentinternalreprogramavinsxobjectsview-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/nsx/reprogram/internal/?$',
        api.views_nsx.NsxAgentInternalReprogramavinsxobjectsView.as_view(),
        name='nsxagentinternalreprogramavinsxobjectsview-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD" }),
    
    url(r'^nsx/fault/inject/?$',
        api.views_nsx.NsxAgentInternalNsxfaultinjectView.as_view(),
        name='nsxagentinternalnsxfaultinjectview-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/nsx/fault/inject/?$',
        api.views_nsx.NsxAgentInternalNsxfaultinjectView.as_view(),
        name='nsxagentinternalnsxfaultinjectview-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD" }),
        

)
