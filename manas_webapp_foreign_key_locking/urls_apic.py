
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
import api.views_apic

urlpatterns = patterns('',
    
    url(r'^apicdevpkgver/?$',
        api.views_apic.ApicDevicePkgVerList.as_view(),
        name='apicdevpkgver-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/apicdevpkgver/?$',
        api.views_apic.ApicDevicePkgVerList.as_view(),
        name='apicdevpkgver-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD"}),  
                
    url(r'^apicdevpkgver/(?P<slug>[-\w.]+)/?$',
        api.views_apic.ApicDevicePkgVerDetail.as_view(),
        name='apicdevpkgver-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/apicdevpkgver/(?P<slug>[-\w.]+)/?$',
        api.views_apic.ApicDevicePkgVerDetail.as_view(),
        name='apicdevpkgver-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD"}),
                
        
    
    url(r'^apic/internal/?$',
        api.views_apic.ApicAgentInternalList.as_view(),
        name='apic/internal-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/apic/internal/?$',
        api.views_apic.ApicAgentInternalList.as_view(),
        name='apic/internal-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD"}),  
                
    url(r'^apic/internal/(?P<slug>[-\w.]+)/?$',
        api.views_apic.ApicAgentInternalDetail.as_view(),
        name='apic/internal-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/apic/internal/(?P<slug>[-\w.]+)/?$',
        api.views_apic.ApicAgentInternalDetail.as_view(),
        name='apic/internal-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD"}),
                
    
    url(r'^apic/verify/login/?$',
        api.views_apic.ApicAgentInternalVerifyapicloginView.as_view(),
        name='apicagentinternalverifyapicloginview-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/apic/verify/login/?$',
        api.views_apic.ApicAgentInternalVerifyapicloginView.as_view(),
        name='apicagentinternalverifyapicloginview-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD" }),
        
    
    url(r'^apictenants/?$',
        api.views_apic.APICTenantsList.as_view(),
        name='apictenants-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/apictenants/?$',
        api.views_apic.APICTenantsList.as_view(),
        name='apictenants-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD"}),  
                
    url(r'^apictenants/(?P<slug>[-\w.]+)/?$',
        api.views_apic.APICTenantsDetail.as_view(),
        name='apictenants-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/apictenants/(?P<slug>[-\w.]+)/?$',
        api.views_apic.APICTenantsDetail.as_view(),
        name='apictenants-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD"}),
                
        
    
    url(r'^apicgraphinstances/?$',
        api.views_apic.APICGraphInstancesList.as_view(),
        name='apicgraphinstances-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/apicgraphinstances/?$',
        api.views_apic.APICGraphInstancesList.as_view(),
        name='apicgraphinstances-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD"}),  
                
    url(r'^apicgraphinstances/(?P<slug>[-\w.]+)/?$',
        api.views_apic.APICGraphInstancesDetail.as_view(),
        name='apicgraphinstances-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/apicgraphinstances/(?P<slug>[-\w.]+)/?$',
        api.views_apic.APICGraphInstancesDetail.as_view(),
        name='apicgraphinstances-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD"}),
                
        
    
    url(r'^apicepgeps/?$',
        api.views_apic.APICEpgEpsList.as_view(),
        name='apicepgeps-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/apicepgeps/?$',
        api.views_apic.APICEpgEpsList.as_view(),
        name='apicepgeps-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD"}),  
                
    url(r'^apicepgeps/(?P<slug>[-\w.]+)/?$',
        api.views_apic.APICEpgEpsDetail.as_view(),
        name='apicepgeps-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/apicepgeps/(?P<slug>[-\w.]+)/?$',
        api.views_apic.APICEpgEpsDetail.as_view(),
        name='apicepgeps-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD"}),
                
        
    
    url(r'^apicvmmdomains/?$',
        api.views_apic.APICVmmDomainsList.as_view(),
        name='apicvmmdomains-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/apicvmmdomains/?$',
        api.views_apic.APICVmmDomainsList.as_view(),
        name='apicvmmdomains-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD"}),  
                
    url(r'^apicvmmdomains/(?P<slug>[-\w.]+)/?$',
        api.views_apic.APICVmmDomainsDetail.as_view(),
        name='apicvmmdomains-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/apicvmmdomains/(?P<slug>[-\w.]+)/?$',
        api.views_apic.APICVmmDomainsDetail.as_view(),
        name='apicvmmdomains-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD"}),
                
        
            
    
    url(r'^apictransaction/flap/?$',
        api.views_apic.APICTransactionFlapFlapView.as_view(),
        name='apictransactionflapflapview-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/apictransaction/flap/?$',
        api.views_apic.APICTransactionFlapFlapView.as_view(),
        name='apictransactionflapflapview-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD" }),
        
    
    url(r'^apic/ciftable/?$',
        api.views_apic.CIFTableList.as_view(),
        name='apic/ciftable-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/apic/ciftable/?$',
        api.views_apic.CIFTableList.as_view(),
        name='apic/ciftable-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD"}),  
                
    url(r'^apic/ciftable/(?P<slug>[-\w.]+)/?$',
        api.views_apic.CIFTableDetail.as_view(),
        name='apic/ciftable-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/apic/ciftable/(?P<slug>[-\w.]+)/?$',
        api.views_apic.CIFTableDetail.as_view(),
        name='apic/ciftable-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD"}),
                
        
    
    url(r'^apicepgs/?$',
        api.views_apic.APICEpgsList.as_view(),
        name='apicepgs-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/apicepgs/?$',
        api.views_apic.APICEpgsList.as_view(),
        name='apicepgs-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD"}),  
                
    url(r'^apicepgs/(?P<slug>[-\w.]+)/?$',
        api.views_apic.APICEpgsDetail.as_view(),
        name='apicepgs-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/apicepgs/(?P<slug>[-\w.]+)/?$',
        api.views_apic.APICEpgsDetail.as_view(),
        name='apicepgs-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD"}),
                
        
    
    url(r'^apiclifsruntime/?$',
        api.views_apic.APICLifsRuntimeList.as_view(),
        name='apiclifsruntime-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/apiclifsruntime/?$',
        api.views_apic.APICLifsRuntimeList.as_view(),
        name='apiclifsruntime-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD"}),  
                
    url(r'^apiclifsruntime/(?P<slug>[-\w.]+)/?$',
        api.views_apic.APICLifsRuntimeDetail.as_view(),
        name='apiclifsruntime-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/apiclifsruntime/(?P<slug>[-\w.]+)/?$',
        api.views_apic.APICLifsRuntimeDetail.as_view(),
        name='apiclifsruntime-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD"}),
                
        

)
