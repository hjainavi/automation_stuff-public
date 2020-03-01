
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

from django.conf.urls import patterns, include, url
import api.views_azure_custom
import permission.views

#aws - verify-creds={vpc}, get-networks = {az:subnets}

urlpatterns = patterns('',

    url(r'^azure-get-virtual-networks/?$',
        api.views_azure_custom.AzureVnetsView.as_view(),
        name='azure-get-virtual-networks',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),

    url(r'^azure-get-subnets/?$',
        api.views_azure_custom.AzureSubnetsView.as_view(),
        name='azure-get-subnets',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),

    url(r'^azure-get-resource-groups/?$',
        api.views_azure_custom.AzureResourceGroupsView.as_view(),
        name='azure-get-resource-groups',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),

    url(r'^azure-get-locations/?$',
        api.views_azure_custom.AzureLocationsView.as_view(),
        name='azure-get-locations',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    
    url(r'^azure-get-albs/?$',
        api.views_azure_custom.AzureAlbsView.as_view(),
        name='azure-get-albs',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
 
    url(r'^azure-all-resources/?$',
        api.views_azure_custom.AzureAllResourcesView.as_view(),
        name='azure-all-resources',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
)
