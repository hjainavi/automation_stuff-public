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

from django.conf.urls import patterns, url
import api.views_jobmanager_custom

urlpatterns = patterns('',
    url(r'^jobmanager/auth-token-job/?$',
       api.views_jobmanager_custom.AuthTokenJob.as_view(),
       name='jobmanager-auth-token-job',
       kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_INTERNAL", 'allow_all_tenants': True}),

    url(r'^jobmanager/session-job/?$',
       api.views_jobmanager_custom.SessionJob.as_view(),
       name='jobmanager-session-job',
       kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_INTERNAL", 'allow_all_tenants': True}),

    url(r'^jobmanager/secure-channel-cleanup-job/?$',
       api.views_jobmanager_custom.SecureChannelCleanupJob.as_view(),
       name='jobmanager-secure-channel-cleanup-job',
       kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_INTERNAL", 'allow_all_tenants': True}),

    url(r'^jobmanager/consistency-check-job/?$',
       api.views_jobmanager_custom.ConsistencyCheckJob.as_view(),
       name='jobmanager-consistency-check-job',
       kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_INTERNAL", 'allow_all_tenants': True}),

    url(r'^jobmanager/pkiprofile-job/(?P<job_uuid>[-\w.]+)/?$',
        api.views_jobmanager_custom.PkiProfileJob.as_view(),
        name='pkiprofile-job',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_INTERNAL", 'allow_all_tenants': True}),
)