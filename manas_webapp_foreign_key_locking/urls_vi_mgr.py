
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
import api.views_vi_mgr

urlpatterns = patterns('',
    
    url(r'^vimgrvcenterdatacenters/?$',
        api.views_vi_mgr.VIDCInfoList.as_view(),
        name='vimgrvcenterdatacenters-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/vimgrvcenterdatacenters/?$',
        api.views_vi_mgr.VIDCInfoList.as_view(),
        name='vimgrvcenterdatacenters-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD"}),  
                
    url(r'^vimgrvcenterdatacenters/(?P<slug>[-\w.]+)/?$',
        api.views_vi_mgr.VIDCInfoDetail.as_view(),
        name='vimgrvcenterdatacenters-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/vimgrvcenterdatacenters/(?P<slug>[-\w.]+)/?$',
        api.views_vi_mgr.VIDCInfoDetail.as_view(),
        name='vimgrvcenterdatacenters-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD"}),
                
        
    
    url(r'^vimgrsevmruntime/?$',
        api.views_vi_mgr.VIMgrSEVMRuntimeList.as_view(),
        name='vimgrsevmruntime-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/vimgrsevmruntime/?$',
        api.views_vi_mgr.VIMgrSEVMRuntimeList.as_view(),
        name='vimgrsevmruntime-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD"}),  
                
    url(r'^vimgrsevmruntime/(?P<slug>[-\w.]+)/?$',
        api.views_vi_mgr.VIMgrSEVMRuntimeDetail.as_view(),
        name='vimgrsevmruntime-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/vimgrsevmruntime/(?P<slug>[-\w.]+)/?$',
        api.views_vi_mgr.VIMgrSEVMRuntimeDetail.as_view(),
        name='vimgrsevmruntime-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD"}),
                
        
    
    url(r'^vimgrnwruntime/?$',
        api.views_vi_mgr.VIMgrNWRuntimeList.as_view(),
        name='vimgrnwruntime-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/vimgrnwruntime/?$',
        api.views_vi_mgr.VIMgrNWRuntimeList.as_view(),
        name='vimgrnwruntime-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD"}),  
                
    url(r'^vimgrnwruntime/(?P<slug>[-\w.]+)/?$',
        api.views_vi_mgr.VIMgrNWRuntimeDetail.as_view(),
        name='vimgrnwruntime-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/vimgrnwruntime/(?P<slug>[-\w.]+)/?$',
        api.views_vi_mgr.VIMgrNWRuntimeDetail.as_view(),
        name='vimgrnwruntime-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD"}),
                
        
    
    url(r'^vimgrvcenternetworks/?$',
        api.views_vi_mgr.VIPGNameInfoList.as_view(),
        name='vimgrvcenternetworks-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/vimgrvcenternetworks/?$',
        api.views_vi_mgr.VIPGNameInfoList.as_view(),
        name='vimgrvcenternetworks-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD"}),  
                
    url(r'^vimgrvcenternetworks/(?P<slug>[-\w.]+)/?$',
        api.views_vi_mgr.VIPGNameInfoDetail.as_view(),
        name='vimgrvcenternetworks-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/vimgrvcenternetworks/(?P<slug>[-\w.]+)/?$',
        api.views_vi_mgr.VIPGNameInfoDetail.as_view(),
        name='vimgrvcenternetworks-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD"}),
                
        
    
    url(r'^vimgrclusterruntime/?$',
        api.views_vi_mgr.VIMgrClusterRuntimeList.as_view(),
        name='vimgrclusterruntime-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/vimgrclusterruntime/?$',
        api.views_vi_mgr.VIMgrClusterRuntimeList.as_view(),
        name='vimgrclusterruntime-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD"}),  
                
    url(r'^vimgrclusterruntime/(?P<slug>[-\w.]+)/?$',
        api.views_vi_mgr.VIMgrClusterRuntimeDetail.as_view(),
        name='vimgrclusterruntime-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/vimgrclusterruntime/(?P<slug>[-\w.]+)/?$',
        api.views_vi_mgr.VIMgrClusterRuntimeDetail.as_view(),
        name='vimgrclusterruntime-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD"}),
                
        
    
    url(r'^vimgrcontrollerruntime/?$',
        api.views_vi_mgr.VIMgrControllerRuntimeList.as_view(),
        name='vimgrcontrollerruntime-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/vimgrcontrollerruntime/?$',
        api.views_vi_mgr.VIMgrControllerRuntimeList.as_view(),
        name='vimgrcontrollerruntime-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD"}),  
                
    url(r'^vimgrcontrollerruntime/(?P<slug>[-\w.]+)/?$',
        api.views_vi_mgr.VIMgrControllerRuntimeDetail.as_view(),
        name='vimgrcontrollerruntime-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/vimgrcontrollerruntime/(?P<slug>[-\w.]+)/?$',
        api.views_vi_mgr.VIMgrControllerRuntimeDetail.as_view(),
        name='vimgrcontrollerruntime-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD"}),
                
        
    
    url(r'^vcenter/interestedvms/?$',
        api.views_vi_mgr.InterestedVMsList.as_view(),
        name='vcenter/interestedvms-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/vcenter/interestedvms/?$',
        api.views_vi_mgr.InterestedVMsList.as_view(),
        name='vcenter/interestedvms-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD"}),  
                
    url(r'^vcenter/interestedvms/(?P<slug>[-\w.]+)/?$',
        api.views_vi_mgr.InterestedVMsDetail.as_view(),
        name='vcenter/interestedvms-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/vcenter/interestedvms/(?P<slug>[-\w.]+)/?$',
        api.views_vi_mgr.InterestedVMsDetail.as_view(),
        name='vcenter/interestedvms-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD"}),
                
        
    
    url(r'^vimgrdcruntime/?$',
        api.views_vi_mgr.VIMgrDCRuntimeList.as_view(),
        name='vimgrdcruntime-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/vimgrdcruntime/?$',
        api.views_vi_mgr.VIMgrDCRuntimeList.as_view(),
        name='vimgrdcruntime-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD"}),  
                
    url(r'^vimgrdcruntime/(?P<slug>[-\w.]+)/?$',
        api.views_vi_mgr.VIMgrDCRuntimeDetail.as_view(),
        name='vimgrdcruntime-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/vimgrdcruntime/(?P<slug>[-\w.]+)/?$',
        api.views_vi_mgr.VIMgrDCRuntimeDetail.as_view(),
        name='vimgrdcruntime-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD"}),
                
        
    
    url(r'^vcenter/interestedhosts/?$',
        api.views_vi_mgr.InterestedHostsList.as_view(),
        name='vcenter/interestedhosts-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/vcenter/interestedhosts/?$',
        api.views_vi_mgr.InterestedHostsList.as_view(),
        name='vcenter/interestedhosts-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD"}),  
                
    url(r'^vcenter/interestedhosts/(?P<slug>[-\w.]+)/?$',
        api.views_vi_mgr.InterestedHostsDetail.as_view(),
        name='vcenter/interestedhosts-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/vcenter/interestedhosts/(?P<slug>[-\w.]+)/?$',
        api.views_vi_mgr.InterestedHostsDetail.as_view(),
        name='vcenter/interestedhosts-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD"}),
                
        
    
    url(r'^vimgrvmruntime/?$',
        api.views_vi_mgr.VIMgrVMRuntimeList.as_view(),
        name='vimgrvmruntime-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/vimgrvmruntime/?$',
        api.views_vi_mgr.VIMgrVMRuntimeList.as_view(),
        name='vimgrvmruntime-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD"}),  
                
    url(r'^vimgrvmruntime/(?P<slug>[-\w.]+)/?$',
        api.views_vi_mgr.VIMgrVMRuntimeDetail.as_view(),
        name='vimgrvmruntime-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/vimgrvmruntime/(?P<slug>[-\w.]+)/?$',
        api.views_vi_mgr.VIMgrVMRuntimeDetail.as_view(),
        name='vimgrvmruntime-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD"}),
                
        
    
    url(r'^vimgrvcenterruntime/?$',
        api.views_vi_mgr.VIMgrVcenterRuntimeList.as_view(),
        name='vimgrvcenterruntime-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/vimgrvcenterruntime/?$',
        api.views_vi_mgr.VIMgrVcenterRuntimeList.as_view(),
        name='vimgrvcenterruntime-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD"}),  
                
    url(r'^vimgrvcenterruntime/(?P<slug>[-\w.]+)/?$',
        api.views_vi_mgr.VIMgrVcenterRuntimeDetail.as_view(),
        name='vimgrvcenterruntime-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/vimgrvcenterruntime/(?P<slug>[-\w.]+)/?$',
        api.views_vi_mgr.VIMgrVcenterRuntimeDetail.as_view(),
        name='vimgrvcenterruntime-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD"}),
                
    
    url(r'^vimgrvcenterruntime/(?P<key>[-\w.]+)/spawn/?$',
        api.views_vi_mgr.VIMgrVcenterRuntimeSpawnView.as_view(),
        name='vimgrvcenterruntimespawnview-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/vimgrvcenterruntime/(?P<key>[-\w.]+)/spawn/?$',
        api.views_vi_mgr.VIMgrVcenterRuntimeSpawnView.as_view(),
        name='vimgrvcenterruntimespawnview-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD" }),
    
    url(r'^vimgrvcenterruntime/(?P<key>[-\w.]+)/remove/?$',
        api.views_vi_mgr.VIMgrVcenterRuntimeRemoveView.as_view(),
        name='vimgrvcenterruntimeremoveview-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/vimgrvcenterruntime/(?P<key>[-\w.]+)/remove/?$',
        api.views_vi_mgr.VIMgrVcenterRuntimeRemoveView.as_view(),
        name='vimgrvcenterruntimeremoveview-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD" }),
    
    url(r'^vimgrvcenterruntime/(?P<key>[-\w.]+)/setmgmtip/?$',
        api.views_vi_mgr.VIMgrVcenterRuntimeSetmgmtipView.as_view(),
        name='vimgrvcenterruntimesetmgmtipview-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/vimgrvcenterruntime/(?P<key>[-\w.]+)/setmgmtip/?$',
        api.views_vi_mgr.VIMgrVcenterRuntimeSetmgmtipView.as_view(),
        name='vimgrvcenterruntimesetmgmtipview-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD" }),
    
    url(r'^vimgrvcenterruntime/(?P<key>[-\w.]+)/modifymgmtip/?$',
        api.views_vi_mgr.VIMgrVcenterRuntimeModifymgmtipView.as_view(),
        name='vimgrvcenterruntimemodifymgmtipview-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/vimgrvcenterruntime/(?P<key>[-\w.]+)/modifymgmtip/?$',
        api.views_vi_mgr.VIMgrVcenterRuntimeModifymgmtipView.as_view(),
        name='vimgrvcenterruntimemodifymgmtipview-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD" }),
    
    url(r'^vimgrvcenterruntime/(?P<key>[-\w.]+)/setvnic/?$',
        api.views_vi_mgr.VIMgrVcenterRuntimeSetvnicView.as_view(),
        name='vimgrvcenterruntimesetvnicview-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/vimgrvcenterruntime/(?P<key>[-\w.]+)/setvnic/?$',
        api.views_vi_mgr.VIMgrVcenterRuntimeSetvnicView.as_view(),
        name='vimgrvcenterruntimesetvnicview-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD" }),
    
    url(r'^vimgrvcenterruntime/(?P<key>[-\w.]+)/modifyvnic/?$',
        api.views_vi_mgr.VIMgrVcenterRuntimeModifyvnicView.as_view(),
        name='vimgrvcenterruntimemodifyvnicview-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/vimgrvcenterruntime/(?P<key>[-\w.]+)/modifyvnic/?$',
        api.views_vi_mgr.VIMgrVcenterRuntimeModifyvnicView.as_view(),
        name='vimgrvcenterruntimemodifyvnicview-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD" }),
    
    url(r'^vimgrvcenterruntime/retrieve/portgroups/?$',
        api.views_vi_mgr.VIMgrVcenterRuntimeRetrievevcenterdcnwsView.as_view(),
        name='vimgrvcenterruntimeretrievevcenterdcnwsview-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/vimgrvcenterruntime/retrieve/portgroups/?$',
        api.views_vi_mgr.VIMgrVcenterRuntimeRetrievevcenterdcnwsView.as_view(),
        name='vimgrvcenterruntimeretrievevcenterdcnwsview-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD" }),
    
    url(r'^vimgrvcenterruntime/initiate/rediscover/?$',
        api.views_vi_mgr.VIMgrVcenterRuntimeRediscoverView.as_view(),
        name='vimgrvcenterruntimerediscoverview-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/vimgrvcenterruntime/initiate/rediscover/?$',
        api.views_vi_mgr.VIMgrVcenterRuntimeRediscoverView.as_view(),
        name='vimgrvcenterruntimerediscoverview-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD" }),
    
    url(r'^vimgrvcenterruntime/(?P<key>[-\w.]+)/getnetworks/?$',
        api.views_vi_mgr.VIMgrVcenterRuntimeGetnetworksView.as_view(),
        name='vimgrvcenterruntimegetnetworksview-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/vimgrvcenterruntime/(?P<key>[-\w.]+)/getnetworks/?$',
        api.views_vi_mgr.VIMgrVcenterRuntimeGetnetworksView.as_view(),
        name='vimgrvcenterruntimegetnetworksview-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD" }),
    
    url(r'^vimgrvcenterruntime/verify/login/?$',
        api.views_vi_mgr.VIMgrVcenterRuntimeVerifyloginView.as_view(),
        name='vimgrvcenterruntimeverifyloginview-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/vimgrvcenterruntime/verify/login/?$',
        api.views_vi_mgr.VIMgrVcenterRuntimeVerifyloginView.as_view(),
        name='vimgrvcenterruntimeverifyloginview-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD" }),
    
    url(r'^vimgrvcenterruntime/openstack/verify/login/?$',
        api.views_vi_mgr.VIMgrVcenterRuntimeOs_Verify_LoginView.as_view(),
        name='vimgrvcenterruntimeos_verify_loginview-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/vimgrvcenterruntime/openstack/verify/login/?$',
        api.views_vi_mgr.VIMgrVcenterRuntimeOs_Verify_LoginView.as_view(),
        name='vimgrvcenterruntimeos_verify_loginview-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD" }),
    
    url(r'^vimgrvcenterruntime/aws/verify/login/?$',
        api.views_vi_mgr.VIMgrVcenterRuntimeAws_Verify_LoginView.as_view(),
        name='vimgrvcenterruntimeaws_verify_loginview-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/vimgrvcenterruntime/aws/verify/login/?$',
        api.views_vi_mgr.VIMgrVcenterRuntimeAws_Verify_LoginView.as_view(),
        name='vimgrvcenterruntimeaws_verify_loginview-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD" }),
    
    url(r'^vimgrvcenterruntime/fault/inject/?$',
        api.views_vi_mgr.VIMgrVcenterRuntimeFaultinjectView.as_view(),
        name='vimgrvcenterruntimefaultinjectview-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/vimgrvcenterruntime/fault/inject/?$',
        api.views_vi_mgr.VIMgrVcenterRuntimeFaultinjectView.as_view(),
        name='vimgrvcenterruntimefaultinjectview-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD" }),
    
    url(r'^vimgrvcenterruntime/delete/network/?$',
        api.views_vi_mgr.VIMgrVcenterRuntimeDeletenetworkView.as_view(),
        name='vimgrvcenterruntimedeletenetworkview-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/vimgrvcenterruntime/delete/network/?$',
        api.views_vi_mgr.VIMgrVcenterRuntimeDeletenetworkView.as_view(),
        name='vimgrvcenterruntimedeletenetworkview-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD" }),
    
    url(r'^vimgrvcenterruntime/vcenter/status/?$',
        api.views_vi_mgr.VIMgrVcenterRuntimeVcenterstatusView.as_view(),
        name='vimgrvcenterruntimevcenterstatusview-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/vimgrvcenterruntime/vcenter/status/?$',
        api.views_vi_mgr.VIMgrVcenterRuntimeVcenterstatusView.as_view(),
        name='vimgrvcenterruntimevcenterstatusview-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD" }),
    
    url(r'^vimgrvcenterruntime/vcenter/diag/?$',
        api.views_vi_mgr.VIMgrVcenterRuntimeVcenterdiagView.as_view(),
        name='vimgrvcenterruntimevcenterdiagview-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/vimgrvcenterruntime/vcenter/diag/?$',
        api.views_vi_mgr.VIMgrVcenterRuntimeVcenterdiagView.as_view(),
        name='vimgrvcenterruntimevcenterdiagview-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD" }),
    
    url(r'^vimgrvcenterruntime/controller/ipsubnet/?$',
        api.views_vi_mgr.VIMgrVcenterRuntimeControlleripsubnetsView.as_view(),
        name='vimgrvcenterruntimecontrolleripsubnetsview-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/vimgrvcenterruntime/controller/ipsubnet/?$',
        api.views_vi_mgr.VIMgrVcenterRuntimeControlleripsubnetsView.as_view(),
        name='vimgrvcenterruntimecontrolleripsubnetsview-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD" }),
    
    url(r'^vimgrvcenterruntime/generate/event/?$',
        api.views_vi_mgr.VIMgrVcenterRuntimeGeneventView.as_view(),
        name='vimgrvcenterruntimegeneventview-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/vimgrvcenterruntime/generate/event/?$',
        api.views_vi_mgr.VIMgrVcenterRuntimeGeneventView.as_view(),
        name='vimgrvcenterruntimegeneventview-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD" }),
            
    url(r'^vimgrvcenterruntime/(?P<key>[-\w.]+)/networksubnetvms/?$',
        api.views_vi_mgr.VINetworkSubnetVMsView.as_view(),
        name='vinetworksubnetvms-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/vimgrvcenterruntime/(?P<key>[-\w.]+)/networksubnetvms/?$',
        api.views_vi_mgr.VINetworkSubnetVMsView.as_view(),
        name='vinetworksubnetvms-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD"}),
                
    url(r'^vimgrvcenterruntime/(?P<key>[-\w.]+)/redis/?$',
        api.views_vi_mgr.VIDatastoreContentsView.as_view(),
        name='vidatastorecontents-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/vimgrvcenterruntime/(?P<key>[-\w.]+)/redis/?$',
        api.views_vi_mgr.VIDatastoreContentsView.as_view(),
        name='vidatastorecontents-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD"}),
                
    url(r'^vimgrvcenterruntime/(?P<key>[-\w.]+)/datastores/?$',
        api.views_vi_mgr.VIDatastoreView.as_view(),
        name='vidatastore-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/vimgrvcenterruntime/(?P<key>[-\w.]+)/datastores/?$',
        api.views_vi_mgr.VIDatastoreView.as_view(),
        name='vidatastore-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD"}),
                
    url(r'^vimgrvcenterruntime/(?P<key>[-\w.]+)/subfolders/?$',
        api.views_vi_mgr.VISubfoldersView.as_view(),
        name='visubfolders-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/vimgrvcenterruntime/(?P<key>[-\w.]+)/subfolders/?$',
        api.views_vi_mgr.VISubfoldersView.as_view(),
        name='visubfolders-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD"}),
                
    url(r'^vimgrvcenterruntime/(?P<key>[-\w.]+)/hostresources/?$',
        api.views_vi_mgr.VIHostResourcesView.as_view(),
        name='vihostresources-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/vimgrvcenterruntime/(?P<key>[-\w.]+)/hostresources/?$',
        api.views_vi_mgr.VIHostResourcesView.as_view(),
        name='vihostresources-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD"}),
            
    
    url(r'^vcenter/sevmcreateprogress/?$',
        api.views_vi_mgr.SEVMCreateProgressList.as_view(),
        name='vcenter/sevmcreateprogress-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/vcenter/sevmcreateprogress/?$',
        api.views_vi_mgr.SEVMCreateProgressList.as_view(),
        name='vcenter/sevmcreateprogress-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD"}),  
                
    url(r'^vcenter/sevmcreateprogress/(?P<slug>[-\w.]+)/?$',
        api.views_vi_mgr.SEVMCreateProgressDetail.as_view(),
        name='vcenter/sevmcreateprogress-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/vcenter/sevmcreateprogress/(?P<slug>[-\w.]+)/?$',
        api.views_vi_mgr.SEVMCreateProgressDetail.as_view(),
        name='vcenter/sevmcreateprogress-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD"}),
                
        
    
    url(r'^vimgrhostruntime/?$',
        api.views_vi_mgr.VIMgrHostRuntimeList.as_view(),
        name='vimgrhostruntime-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/vimgrhostruntime/?$',
        api.views_vi_mgr.VIMgrHostRuntimeList.as_view(),
        name='vimgrhostruntime-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD"}),  
                
    url(r'^vimgrhostruntime/(?P<slug>[-\w.]+)/?$',
        api.views_vi_mgr.VIMgrHostRuntimeDetail.as_view(),
        name='vimgrhostruntime-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/vimgrhostruntime/(?P<slug>[-\w.]+)/?$',
        api.views_vi_mgr.VIMgrHostRuntimeDetail.as_view(),
        name='vimgrhostruntime-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD"}),
                
    
    url(r'^vimgrhostruntime/(?P<key>[-\w.]+)/accessible/?$',
        api.views_vi_mgr.VIMgrHostRuntimeMakeaccessibleView.as_view(),
        name='vimgrhostruntimemakeaccessibleview-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/vimgrhostruntime/(?P<key>[-\w.]+)/accessible/?$',
        api.views_vi_mgr.VIMgrHostRuntimeMakeaccessibleView.as_view(),
        name='vimgrhostruntimemakeaccessibleview-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CLOUD" }),
        

)
