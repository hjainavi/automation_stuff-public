
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

#pylint:  skip-file
from django.conf.urls import patterns, url
import api.views_ipam_dns_provider_profile_custom as IpamDnsProviderProfileCustomViews

urlpatterns = patterns('',
    url(r'^ipamdnsproviderprofilenetworklist/?$',
        IpamDnsProviderProfileCustomViews.IpamDnsProviderProfileNetworkList.as_view(),
        name='ipamdnsprovider-networks',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_IPAMDNSPROVIDERPROFILE"}),
    url(r'^ipamdnsproviderprofiledomainlist/?$',
        IpamDnsProviderProfileCustomViews.IpamDnsProviderProfileDomainList.as_view(),
        name='ipamdnsprovider-domains',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_IPAMDNSPROVIDERPROFILE"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/ipamdnsproviderprofilenetworklist/?$',
        IpamDnsProviderProfileCustomViews.IpamDnsProviderProfileNetworkList.as_view(),
        name='ipamdnsprovider-networks-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_IPAMDNSPROVIDERPROFILE"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/ipamdnsproviderprofiledomainlist/?$',
        IpamDnsProviderProfileCustomViews.IpamDnsProviderProfileDomainList.as_view(),
        name='ipamdnsprovider-domains-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_IPAMDNSPROVIDERPROFILE"}),
    url(r'^ipamdnsproviderprofilelogin/?$',
        IpamDnsProviderProfileCustomViews.IpamDnsProviderProfileLogin.as_view(),
        name='ipamdnsprovider-login',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_IPAMDNSPROVIDERPROFILE"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/ipamdnsproviderprofilelogin/?$',
        IpamDnsProviderProfileCustomViews.IpamDnsProviderProfileLogin.as_view(),
        name='ipamdnsprovider-login-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_IPAMDNSPROVIDERPROFILE"}),
)
