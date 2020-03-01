
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
import api.views_se_datastore_debug

urlpatterns = patterns('',
    
    url(r'^se_datastore/status/?$',
        api.views_se_datastore_debug.SeDatastoreStatusList.as_view(),
        name='se_datastore/status-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_INTERNAL"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/se_datastore/status/?$',
        api.views_se_datastore_debug.SeDatastoreStatusList.as_view(),
        name='se_datastore/status-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_INTERNAL"}),  
                
    url(r'^se_datastore/status/(?P<slug>[-\w.]+)/?$',
        api.views_se_datastore_debug.SeDatastoreStatusDetail.as_view(),
        name='se_datastore/status-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_INTERNAL"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/se_datastore/status/(?P<slug>[-\w.]+)/?$',
        api.views_se_datastore_debug.SeDatastoreStatusDetail.as_view(),
        name='se_datastore/status-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_INTERNAL"}),
                
        
    
    url(r'^se_datastore/diff_queue/?$',
        api.views_se_datastore_debug.DiffQueueStatusList.as_view(),
        name='se_datastore/diff_queue-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_INTERNAL"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/se_datastore/diff_queue/?$',
        api.views_se_datastore_debug.DiffQueueStatusList.as_view(),
        name='se_datastore/diff_queue-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_INTERNAL"}),  
                
    url(r'^se_datastore/diff_queue/(?P<slug>[-\w.]+)/?$',
        api.views_se_datastore_debug.DiffQueueStatusDetail.as_view(),
        name='se_datastore/diff_queue-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_INTERNAL"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/se_datastore/diff_queue/(?P<slug>[-\w.]+)/?$',
        api.views_se_datastore_debug.DiffQueueStatusDetail.as_view(),
        name='se_datastore/diff_queue-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_INTERNAL"}),
                
        

)
