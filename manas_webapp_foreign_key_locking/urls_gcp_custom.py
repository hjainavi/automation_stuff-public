
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
import api.views_gcp_custom


urlpatterns = patterns('',

    url(r'^gcp-get-regions/?$',
        api.views_gcp_custom.RegionsView.as_view(),
        name='gcp-get-regions',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),

    url(r'^gcp-get-zones/?$',
       api.views_gcp_custom.ZonesView.as_view(),
       name='gcp-get-zones',
       kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),

    url(r'^gcp-get-networks/?$',
        api.views_gcp_custom.NetworksView.as_view(),
        name='gcp-get-networks',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),

    url(r'^gcp-get-subnets/?$',
       api.views_gcp_custom.SubnetsView.as_view(),
       name='gcp-get-subnets',
       kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
   )
