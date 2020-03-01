
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
import api.views_pool

urlpatterns = patterns('',
    
    url(r'^pool/?$',
        api.views_pool.PoolList.as_view(),
        name='pool-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_POOL"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/pool/?$',
        api.views_pool.PoolList.as_view(),
        name='pool-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_POOL"}),  
                
    url(r'^pool/(?P<slug>[-\w.]+)/?$',
        api.views_pool.PoolDetail.as_view(),
        name='pool-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_POOL"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/pool/(?P<slug>[-\w.]+)/?$',
        api.views_pool.PoolDetail.as_view(),
        name='pool-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_POOL"}),
                
    
    url(r'^pool/(?P<key>[-\w.]+)/scaleout/?$',
        api.views_pool.PoolScaleoutView.as_view(),
        name='poolscaleoutview-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_POOL"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/pool/(?P<key>[-\w.]+)/scaleout/?$',
        api.views_pool.PoolScaleoutView.as_view(),
        name='poolscaleoutview-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_POOL" }),
    
    url(r'^pool/(?P<key>[-\w.]+)/scalein/?$',
        api.views_pool.PoolScaleinView.as_view(),
        name='poolscaleinview-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_POOL"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/pool/(?P<key>[-\w.]+)/scalein/?$',
        api.views_pool.PoolScaleinView.as_view(),
        name='poolscaleinview-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_POOL" }),
            
    url(r'^pool/(?P<key>[-\w.]+)/hmon/?$',
        api.views_pool.HealthMonitorRuntimeView.as_view(),
        name='healthmonitorruntime-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_POOL"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/pool/(?P<key>[-\w.]+)/hmon/?$',
        api.views_pool.HealthMonitorRuntimeView.as_view(),
        name='healthmonitorruntime-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_POOL"}),
                
    url(r'^pool/(?P<key>[-\w.]+)/runtime/server/detail/?$',
        api.views_pool.ServerRuntimeDetailView.as_view(),
        name='serverruntimedetail-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_POOL"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/pool/(?P<key>[-\w.]+)/runtime/server/detail/?$',
        api.views_pool.ServerRuntimeDetailView.as_view(),
        name='serverruntimedetail-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_POOL"}),
                    
    url(r'^pool/(?P<key>[-\w.]+)/connpoolstats/clear/?$',
        api.views_pool.ConnpoolStatsClearView.as_view(),
        name='connpoolstatsclearview-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_POOL"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/pool/(?P<key>[-\w.]+)/connpoolstats/clear/?$',
        api.views_pool.ConnpoolStatsClearView.as_view(),
        name='connpoolstatsclearview-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_POOL"}),
            
    url(r'^pool/(?P<key>[-\w.]+)/runtime/detail/?$',
        api.views_pool.PoolRuntimeDetailView.as_view(),
        name='poolruntimedetail-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_POOL"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/pool/(?P<key>[-\w.]+)/runtime/detail/?$',
        api.views_pool.PoolRuntimeDetailView.as_view(),
        name='poolruntimedetail-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_POOL"}),
                
    url(r'^pool/(?P<key>[-\w.]+)/runtime/server/internal/?$',
        api.views_pool.ServerInternalView.as_view(),
        name='serverinternal-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_POOL"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/pool/(?P<key>[-\w.]+)/runtime/server/internal/?$',
        api.views_pool.ServerInternalView.as_view(),
        name='serverinternal-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_POOL"}),
                
    url(r'^pool/(?P<key>[-\w.]+)/persistence/?$',
        api.views_pool.PersistenceInternalView.as_view(),
        name='persistenceinternal-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_POOL"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/pool/(?P<key>[-\w.]+)/persistence/?$',
        api.views_pool.PersistenceInternalView.as_view(),
        name='persistenceinternal-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_POOL"}),
        
    url(r'^pool/(?P<key>[-\w.]+)/persistence/clear/?$',
        api.views_pool.PersistenceInternalClearView.as_view(),
        name='persistenceinternalclearview-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_POOL"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/pool/(?P<key>[-\w.]+)/persistence/clear/?$',
        api.views_pool.PersistenceInternalClearView.as_view(),
        name='persistenceinternalclearview-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_POOL"}),
                
    url(r'^pool/(?P<key>[-\w.]+)/request_queue/clear/?$',
        api.views_pool.RequestQueueRuntimeClearView.as_view(),
        name='requestqueueruntimeclearview-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_POOL"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/pool/(?P<key>[-\w.]+)/request_queue/clear/?$',
        api.views_pool.RequestQueueRuntimeClearView.as_view(),
        name='requestqueueruntimeclearview-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_POOL"}),
            
    url(r'^pool/(?P<key>[-\w.]+)/httpcachestats/?$',
        api.views_pool.HttpCacheStatsView.as_view(),
        name='httpcachestats-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_POOL"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/pool/(?P<key>[-\w.]+)/httpcachestats/?$',
        api.views_pool.HttpCacheStatsView.as_view(),
        name='httpcachestats-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_POOL"}),
        
    url(r'^pool/(?P<key>[-\w.]+)/httpcachestats/clear/?$',
        api.views_pool.HttpCacheStatsClearView.as_view(),
        name='httpcachestatsclearview-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_POOL"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/pool/(?P<key>[-\w.]+)/httpcachestats/clear/?$',
        api.views_pool.HttpCacheStatsClearView.as_view(),
        name='httpcachestatsclearview-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_POOL"}),
                
    url(r'^pool/(?P<key>[-\w.]+)/stats/clear/?$',
        api.views_pool.PoolStatsClearView.as_view(),
        name='poolstatsclearview-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_POOL"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/pool/(?P<key>[-\w.]+)/stats/clear/?$',
        api.views_pool.PoolStatsClearView.as_view(),
        name='poolstatsclearview-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_POOL"}),
            
    url(r'^pool/(?P<key>[-\w.]+)/connpool/?$',
        api.views_pool.ConnpoolInternalView.as_view(),
        name='connpoolinternal-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_POOL"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/pool/(?P<key>[-\w.]+)/connpool/?$',
        api.views_pool.ConnpoolInternalView.as_view(),
        name='connpoolinternal-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_POOL"}),
        
    url(r'^pool/(?P<key>[-\w.]+)/connpool/clear/?$',
        api.views_pool.ConnpoolInternalClearView.as_view(),
        name='connpoolinternalclearview-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_POOL"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/pool/(?P<key>[-\w.]+)/connpool/clear/?$',
        api.views_pool.ConnpoolInternalClearView.as_view(),
        name='connpoolinternalclearview-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_POOL"}),
            
    url(r'^pool/(?P<key>[-\w.]+)/vs/?$',
        api.views_pool.VsesSharingPoolView.as_view(),
        name='vsessharingpool-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_POOL"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/pool/(?P<key>[-\w.]+)/vs/?$',
        api.views_pool.VsesSharingPoolView.as_view(),
        name='vsessharingpool-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_POOL"}),
                
    url(r'^pool/(?P<key>[-\w.]+)/httpcache/?$',
        api.views_pool.HttpCacheView.as_view(),
        name='httpcache-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_POOL"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/pool/(?P<key>[-\w.]+)/httpcache/?$',
        api.views_pool.HttpCacheView.as_view(),
        name='httpcache-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_POOL"}),
        
    url(r'^pool/(?P<key>[-\w.]+)/httpcache/clear/?$',
        api.views_pool.HttpCacheClearView.as_view(),
        name='httpcacheclearview-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_POOL"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/pool/(?P<key>[-\w.]+)/httpcache/clear/?$',
        api.views_pool.HttpCacheClearView.as_view(),
        name='httpcacheclearview-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_POOL"}),
            
    url(r'^pool/(?P<key>[-\w.]+)/runtime/debug/?$',
        api.views_pool.PoolDebugView.as_view(),
        name='pooldebug-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_POOL"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/pool/(?P<key>[-\w.]+)/runtime/debug/?$',
        api.views_pool.PoolDebugView.as_view(),
        name='pooldebug-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_POOL"}),
                
    url(r'^pool/(?P<key>[-\w.]+)/httpcachestats/detail/?$',
        api.views_pool.HttpCacheStatsDetailView.as_view(),
        name='httpcachestatsdetail-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_POOL"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/pool/(?P<key>[-\w.]+)/httpcachestats/detail/?$',
        api.views_pool.HttpCacheStatsDetailView.as_view(),
        name='httpcachestatsdetail-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_POOL"}),
                
    url(r'^pool/(?P<key>[-\w.]+)/runtime/server/?$',
        api.views_pool.ServerRuntimeSummaryView.as_view(),
        name='serverruntimesummary-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_POOL"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/pool/(?P<key>[-\w.]+)/runtime/server/?$',
        api.views_pool.ServerRuntimeSummaryView.as_view(),
        name='serverruntimesummary-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_POOL"}),
                
    url(r'^pool/(?P<key>[-\w.]+)/runtime/?$',
        api.views_pool.PoolRuntimeSummaryView.as_view(),
        name='poolruntimesummary-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_POOL"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/pool/(?P<key>[-\w.]+)/runtime/?$',
        api.views_pool.PoolRuntimeSummaryView.as_view(),
        name='poolruntimesummary-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_POOL"}),
                
    url(r'^pool/(?P<key>[-\w.]+)/algo/?$',
        api.views_pool.AlgoStatRuntimeView.as_view(),
        name='algostatruntime-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_POOL"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/pool/(?P<key>[-\w.]+)/algo/?$',
        api.views_pool.AlgoStatRuntimeView.as_view(),
        name='algostatruntime-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_POOL"}),
                
    url(r'^pool/(?P<key>[-\w.]+)/runtime/internal/?$',
        api.views_pool.PoolInternalView.as_view(),
        name='poolinternal-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_POOL"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/pool/(?P<key>[-\w.]+)/runtime/internal/?$',
        api.views_pool.PoolInternalView.as_view(),
        name='poolinternal-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_POOL"}),
                
    url(r'^pool/(?P<key>[-\w.]+)/runtime/server/hmonstat/?$',
        api.views_pool.HealthMonitorStatRuntimeView.as_view(),
        name='healthmonitorstatruntime-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_POOL"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/pool/(?P<key>[-\w.]+)/runtime/server/hmonstat/?$',
        api.views_pool.HealthMonitorStatRuntimeView.as_view(),
        name='healthmonitorstatruntime-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_POOL"}),
            

)
