

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
from api.views_inventory_controller import LicensingView, ChangelogView,\
        IpPropertiesView, ControllerView

urlpatterns = patterns(
    '',
    url(r'^ipproperties/?$',
        IpPropertiesView.as_view(),
        name='ipproperties',
        kwargs={'scoped': True, 'scope_visible': False,
                'permission': "PERMISSION_CONTROLLER"}),
    url(r'^changelog/?$',
        ChangelogView.as_view(),
        name='changelog',
        kwargs={'scoped': True, 'scope_visible': False,
                'permission': "PERMISSION_CONTROLLER"}),
    url(r'^tenant/(?P<tenant>[-\w]+)/changelog/?$',
        ChangelogView.as_view(),
        name='changelog',
        kwargs={'scoped': True, 'scope_visible': False,
                'permission': "PERMISSION_CONTROLLER"}),
    url(r'^licenseusage/?$',
        LicensingView.as_view(),
        name='license-usage',
        kwargs={'scoped': True, 'scope_visible': False,
                'permission': "PERMISSION_CONTROLLER"}),
    url(r'^tenant/(?P<tenant>[-\w]+)/licenseusage/?$',
        LicensingView.as_view(),
        name='license-usage',
        kwargs={'scoped': True, 'scope_visible': False,
                'permission': "PERMISSION_CONTROLLER"}),
    url(r'^controller-inventory/?$',
        ControllerView.as_view(),
        name='controller-inventory',
        kwargs={'scoped': True, 'scope_visible': False,
                'permission': "PERMISSION_CONTROLLER"}),
)
