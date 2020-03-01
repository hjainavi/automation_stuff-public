
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

#Manual url file for custom urls
from django.conf.urls import patterns, url
import api.views_ssl_custom

urlpatterns = patterns('',
    url(r'^sslkeyandcertificate/(?P<slug>[-\w.]+)/renew/?$',
        api.views_ssl_custom.RenewSSLCertificate.as_view(),
        name='update-ssl',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_SSLKEYANDCERTIFICATE", 'allow_all_tenants': True}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/sslkeyandcertificate/(?P<slug>[-\w.]+)/renew/?$',
        api.views_ssl_custom.RenewSSLCertificate.as_view(),
        name='update-ssl-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_SSLKEYANDCERTIFICATE", 'allow_all_tenants': True}),
    url(r'^sslkeyandcertificate/validate/?$',
        api.views_ssl_custom.ValidateSSL.as_view(),
        name='validate-cert',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_SSLKEYANDCERTIFICATE"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/sslkeyandcertificate/validate/?$',
        api.views_ssl_custom.ValidateSSL.as_view(),
        name='validate-cert-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_SSLKEYANDCERTIFICATE"}),

    url(r'^sslkeyandcertificate/?$',
        api.views_ssl_custom.SSLKeyAndCertificateListView.as_view(),
        name='sslkeyandcertificate-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_SSLKEYANDCERTIFICATE"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/sslkeyandcertificate/?$',
        api.views_ssl_custom.SSLKeyAndCertificateListView.as_view(),
        name='sslkeyandcertificate-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_SSLKEYANDCERTIFICATE"}),  
            
    url(r'^sslkeyandcertificate/(?P<slug>[-\w.]+)/?$',
        api.views_ssl_custom.SSLKeyAndCertificateDetailView.as_view(),
        name='sslkeyandcertificate-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_SSLKEYANDCERTIFICATE"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/sslkeyandcertificate/(?P<slug>[-\w.]+)/?$',
        api.views_ssl_custom.SSLKeyAndCertificateDetailView.as_view(),
        name='sslkeyandcertificate-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_SSLKEYANDCERTIFICATE"}),

    url(r'^pkiprofile/?$',
        api.views_ssl_custom.PKIProfileListView.as_view(),
        name='pki-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_PKIPROFILE"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/pkiprofile/?$',
        api.views_ssl_custom.PKIProfileListView.as_view(),
        name='pki-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_PKIPROFILE"}),

    url(r'^pkiprofile/(?P<slug>[-\w.]+)/?$',
        api.views_ssl_custom.PKIProfileDetailView.as_view(),
        name='pki-details',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_PKIPROFILE"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/pkiprofile/(?P<slug>[-\w.]+)/?$',
        api.views_ssl_custom.PKIProfileDetailView.as_view(),
        name='pki-details-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_PKIPROFILE"}),
   
    url(r'^pkiprofile/(?P<key>[-\w.]+)/federated_info/?$',
        api.views_ssl_custom.GslbPKIProfileRuntimeView.as_view(),
        name='gslbpkiprofileruntime-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_PKIPROFILE"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/pkiprofile/(?P<key>[-\w.]+)/federated_info/?$',
        api.views_ssl_custom.GslbPKIProfileRuntimeView.as_view(),
        name='gslbpkiprofileruntime-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_PKIPROFILE"}),

    url(r'^printssl/?$',
        api.views_ssl_custom.PrintSSL.as_view(),
        name='print-ssl',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_SSLKEYANDCERTIFICATE"}),

    url(r'^sslprofilecheck/?$',
        api.views_ssl_custom.SSLProfileCheck.as_view(),
        name='ssl-profile-check',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_SSLPROFILE"}),

)
