
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
import api.views_techsupport

urlpatterns = patterns(
    '',
    url(r'^techsupportv2/(?P<level>[-\w.]+)/?$',
        api.views_techsupport.TechSupportViewV2.as_view(),
        name='techsupportview',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_TECHSUPPORT"}),
    url(r'^techsupportv2/(?P<level>[-\w.]+)/(?P<slug>[-\w.]+)/?$',
        api.views_techsupport.TechSupportViewV2.as_view(),
        name='techsupportview-key',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_TECHSUPPORT"}),
    url(r'^techsupportstatusv2/?$',
        api.views_techsupport.TechSupportStatusViewV2.as_view(),
        name='techsupportview',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_TECHSUPPORT", 'level': 'status'}),
    url(r'^techsupportstatusv2/(?P<slug>[-\w.]+)/?$',
        api.views_techsupport.TechSupportStatusViewV2.as_view(),
        name='techsupportview-key',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_TECHSUPPORT", 'level':'status'}),

)
