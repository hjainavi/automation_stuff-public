
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
import api.views_application_persistence_profile

urlpatterns = patterns('',
    
    url(r'^applicationpersistenceprofile/?$',
        api.views_application_persistence_profile.ApplicationPersistenceProfileList.as_view(),
        name='applicationpersistenceprofile-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_APPLICATIONPERSISTENCEPROFILE"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/applicationpersistenceprofile/?$',
        api.views_application_persistence_profile.ApplicationPersistenceProfileList.as_view(),
        name='applicationpersistenceprofile-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_APPLICATIONPERSISTENCEPROFILE"}),  
                
    url(r'^applicationpersistenceprofile/(?P<slug>[-\w.]+)/?$',
        api.views_application_persistence_profile.ApplicationPersistenceProfileDetail.as_view(),
        name='applicationpersistenceprofile-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_APPLICATIONPERSISTENCEPROFILE"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/applicationpersistenceprofile/(?P<slug>[-\w.]+)/?$',
        api.views_application_persistence_profile.ApplicationPersistenceProfileDetail.as_view(),
        name='applicationpersistenceprofile-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_APPLICATIONPERSISTENCEPROFILE"}),
                
            
    url(r'^applicationpersistenceprofile/(?P<key>[-\w.]+)/federated_info/?$',
        api.views_application_persistence_profile.GslbApplicationPersistenceProfileRuntimeView.as_view(),
        name='gslbapplicationpersistenceprofileruntime-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_APPLICATIONPERSISTENCEPROFILE"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/applicationpersistenceprofile/(?P<key>[-\w.]+)/federated_info/?$',
        api.views_application_persistence_profile.GslbApplicationPersistenceProfileRuntimeView.as_view(),
        name='gslbapplicationpersistenceprofileruntime-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_APPLICATIONPERSISTENCEPROFILE"}),
            

)
