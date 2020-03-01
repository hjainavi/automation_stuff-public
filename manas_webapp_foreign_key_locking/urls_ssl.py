
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
import api.views_ssl

urlpatterns = patterns('',
    
    url(r'^sslprofile/?$',
        api.views_ssl.SSLProfileList.as_view(),
        name='sslprofile-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_SSLPROFILE"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/sslprofile/?$',
        api.views_ssl.SSLProfileList.as_view(),
        name='sslprofile-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_SSLPROFILE"}),  
                
    url(r'^sslprofile/(?P<slug>[-\w.]+)/?$',
        api.views_ssl.SSLProfileDetail.as_view(),
        name='sslprofile-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_SSLPROFILE"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/sslprofile/(?P<slug>[-\w.]+)/?$',
        api.views_ssl.SSLProfileDetail.as_view(),
        name='sslprofile-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_SSLPROFILE"}),
                
        
    
    url(r'^certificatemanagementprofile/?$',
        api.views_ssl.CertificateManagementProfileList.as_view(),
        name='certificatemanagementprofile-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CERTIFICATEMANAGEMENTPROFILE"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/certificatemanagementprofile/?$',
        api.views_ssl.CertificateManagementProfileList.as_view(),
        name='certificatemanagementprofile-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CERTIFICATEMANAGEMENTPROFILE"}),  
                
    url(r'^certificatemanagementprofile/(?P<slug>[-\w.]+)/?$',
        api.views_ssl.CertificateManagementProfileDetail.as_view(),
        name='certificatemanagementprofile-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CERTIFICATEMANAGEMENTPROFILE"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/certificatemanagementprofile/(?P<slug>[-\w.]+)/?$',
        api.views_ssl.CertificateManagementProfileDetail.as_view(),
        name='certificatemanagementprofile-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CERTIFICATEMANAGEMENTPROFILE"}),
                
        

)
