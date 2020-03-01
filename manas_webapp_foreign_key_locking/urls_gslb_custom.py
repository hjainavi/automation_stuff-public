
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

"""
File: urls_gslb_custom.py:
This file contains the customized-urls that are outside the api-spec.
These APIs talk to the back-end: glb-mgr. In some cases, the pb2 in
the message(Ex: config messages) shall have to be saved (Ex: Gslb,
GslbService, HealthMonitor) while in other cases such as (Ex:
HealthStatus, siteup, verify) we don't need any db-updates.

01. When a db-model is saved, we will retain the uuid sent from leader.
02. When a db-model is not used, it is similar to the db_model:false
    mechanism used in the api_spec.
03. The url options are as follows:
    a. gslbsiteops/siteconfig: Payload(Glb, GS, GHM), ops=CUD
    b. gslbsiteops/healthstatus: ops=None
    c. gslbsiteops/verify: is used for front-end verification.
    d. gslbsiteops/validate: is used for back-end verification.
    e. gslbsiteops/purge: is used for purging configuration (leader/follower)
    f. gslbsiteops/changeleader: is used for leader-change.
    g. gslbsiteops/maintenancemode: is used to place the leader in maintenance-mode.
    h. gslbsiteops/resync: is used to resync configuration to a member site.
    i. gslbsiteops/staleojectchecks: is used to check if there are any stale objects.
    k. gslbsiteops/staleojectcleanup: is used to cleanup stale objects
04. Only one entry per url (No typical: (r'^tenant/)
05. All gslbsiteops use PERMISSION_GSLB. So, GSLB roles are
    applicable to gslbsiteops.
06. Gslb objects:
    Custom views are used for Gslb object because, we need to housekeep
    System Default HealthMonitor objects for Gslb functionality.
    * Create: Create Gslb + System Default Health Monitors.
    * Update: Only Gslb object. No impact on System Default Health Monitors
    * Delete: Delete SYstem Default Health Monitors + Delete Gslb
    * Read:  Retrieve Gslb runtime info. (Different flavors)
07. GslbService Objects:
    Custom views are used for GslbService objects for realizing Site-Persistence
    functionality.
    * Create: -> Create GslbService,
              -> Create Proxy-pool with appropriate associations.
                 (Stitch HM, APP, PKI, VS.SSL)
              -> Associate VS to newly created Proxy-pool.
                 (Stitch VS --> Proxy-pool)
    * Update: -> Housekeep Proxy-pool
              -> Housekeep VS --> Proxy
    * Delete: -> Remove VS to Proxy-pool association
              -> Delete proxy-pool
              -> Delete GslbService
    * Read:   -> Retrieve GslbService info
"""
from django.conf.urls import patterns, url
import api.views_gslb_custom

urlpatterns = patterns('',

    url(r'^gslbsiteops/siteconfig/(?P<slug>[-\w.]+)/?$',
        api.views_gslb_custom.GslbSiteOpsSiteConfigView.as_view(),
        name='gslbsiteopssiteconfig-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_GSLB"}),

    url(r'^gslbsiteops/healthstatus/(?P<slug>[-\w.]+)/?$',
        api.views_gslb_custom.GslbSiteOpsHealthStatusView.as_view(),
        name='gslbsiteopshealthstatusview-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_GSLB"}),

    url(r'^gslbsiteops/verify/?$',
        api.views_gslb_custom.GslbSiteOpsVerifyView.as_view(),
        name='gslbsiteopsverifyview-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_GSLB"}),

    url(r'^gslbsiteops/validate/?$',
        api.views_gslb_custom.GslbSiteOpsValidateView.as_view(),
        name='gslbsiteopsvalidateview-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_GSLB"}),

    url(r'^gslbsiteops/purge/?$',
        api.views_gslb_custom.GslbSiteOpsPurgeView.as_view(),
        name='gslbsiteopspurgeview-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_GSLB"}),

    url(r'^gslbsiteops/changeleader/?$',
        api.views_gslb_custom.GslbSiteOpsChangeLeaderView.as_view(),
        name='gslbsiteopschangeleaderview-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_GSLB"}),

    url(r'^gslbsiteops/maintenancemode/?$',
        api.views_gslb_custom.GslbSiteOpsMaintenanceModeView.as_view(),
        name='gslbsiteopsmaintenancemodeview-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_GSLB"}),

    url(r'^gslbsiteops/resync/?$',
        api.views_gslb_custom.GslbSiteOpsResyncView.as_view(),
        name='gslbsiteopsresyncview-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_GSLB"}),

    url(r'^gslbsiteops/staleobjectchecks/?$',
        api.views_gslb_custom.GslbSiteOpsStaleObjectChecks.as_view(),
        name='gslbsiteopsstaleobjectchecksview-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_GSLB"}),

    url(r'^gslbsiteops/staleobjectcleanup/?$',
        api.views_gslb_custom.GslbSiteOpsStaleObjectCleanup.as_view(),
        name='gslbsiteopsstaleobjectcleanupiew-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_GSLB"}),

    # Gslb custom-views: Refer Notes 06.
    url(r'^gslb/?$',
        api.views_gslb_custom.GslbList.as_view(),
        name='gslb-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_GSLB"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/gslb/?$',
        api.views_gslb_custom.GslbList.as_view(),
        name='gslb-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_GSLB"}),

    url(r'^gslb/(?P<slug>[-\w.]+)/?$',
        api.views_gslb_custom.GslbDetail.as_view(),
        name='gslb-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_GSLB"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/gslb/(?P<slug>[-\w.]+)/?$',
        api.views_gslb_custom.GslbDetail.as_view(),
        name='gslb-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_GSLB"}),

    url(r'^gslb/(?P<key>[-\w.]+)/runtime/internal/?$',
        api.views_gslb_custom.GslbRuntimeInternalView.as_view(),
        name='gslbruntimeinternal-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_GSLB"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/gslb/(?P<key>[-\w.]+)/runtime/internal/?$',
        api.views_gslb_custom.GslbRuntimeInternalView.as_view(),
        name='gslbruntimeinternal-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_GSLB"}),

    url(r'^gslb/(?P<key>[-\w.]+)/runtime/detail/?$',
        api.views_gslb_custom.GslbRuntimeDetailView.as_view(),
        name='gslbruntimedetail-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_GSLB"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/gslb/(?P<key>[-\w.]+)/runtime/detail/?$',
        api.views_gslb_custom.GslbRuntimeDetailView.as_view(),
        name='gslbruntimedetail-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_GSLB"}),

    url(r'^gslb/(?P<key>[-\w.]+)/runtime/?$',
        api.views_gslb_custom.GslbRuntimeSummaryView.as_view(),
        name='gslbruntimesummary-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_GSLB"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/gslb/(?P<key>[-\w.]+)/runtime/?$',
        api.views_gslb_custom.GslbRuntimeSummaryView.as_view(),
        name='gslbruntimesummary-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_GSLB"}),

    # GslbService Custom views: Refer Notes 07
    url(r'^gslbservice/?$',
        api.views_gslb_custom.GslbServiceList.as_view(),
        name='gslbservice-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_GSLBSERVICE"}),

    url(r'^tenant/(?P<tenant>[-\w.]+)/gslbservice/?$',
        api.views_gslb_custom.GslbServiceList.as_view(),
        name='gslbservice-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_GSLBSERVICE"}),

    url(r'^gslbservice/(?P<slug>[-\w.]+)/?$',
        api.views_gslb_custom.GslbServiceDetail.as_view(),
        name='gslbservice-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_GSLBSERVICE"}),

    url(r'^tenant/(?P<tenant>[-\w.]+)/gslbservice/(?P<slug>[-\w.]+)/?$',
        api.views_gslb_custom.GslbServiceDetail.as_view(),
        name='gslbservice-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_GSLBSERVICE"}),

    url(r'^gslbservice/(?P<key>[-\w.]+)/runtime/?$',
        api.views_gslb_custom.GslbServiceRuntimeView.as_view(),
        name='gslbserviceruntime-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_GSLBSERVICE"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/gslbservice/(?P<key>[-\w.]+)/runtime/?$',
        api.views_gslb_custom.GslbServiceRuntimeView.as_view(),
        name='gslbserviceruntime-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_GSLBSERVICE"})
)
#End of file
