
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
import api.views_ipam_dns_provider_profile

urlpatterns = patterns('',
    
    url(r'^ipamdnsproviderprofile/?$',
        api.views_ipam_dns_provider_profile.IpamDnsProviderProfileList.as_view(),
        name='ipamdnsproviderprofile-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_IPAMDNSPROVIDERPROFILE"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/ipamdnsproviderprofile/?$',
        api.views_ipam_dns_provider_profile.IpamDnsProviderProfileList.as_view(),
        name='ipamdnsproviderprofile-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_IPAMDNSPROVIDERPROFILE"}),  
                
    url(r'^ipamdnsproviderprofile/(?P<slug>[-\w.]+)/?$',
        api.views_ipam_dns_provider_profile.IpamDnsProviderProfileDetail.as_view(),
        name='ipamdnsproviderprofile-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_IPAMDNSPROVIDERPROFILE"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/ipamdnsproviderprofile/(?P<slug>[-\w.]+)/?$',
        api.views_ipam_dns_provider_profile.IpamDnsProviderProfileDetail.as_view(),
        name='ipamdnsproviderprofile-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_IPAMDNSPROVIDERPROFILE"}),
                
        

)
