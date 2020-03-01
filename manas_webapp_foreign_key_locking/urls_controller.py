
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
import api.views_controller
urlpatterns = patterns('',

    url(r'^controller/enableassert?$',
        api.views_controller.enable_assert,
        name='controller-enable-assert',
        kwargs={'scoped':True, 'scope_visible': False, 'permission': "PERMISSION_INTERNAL"}),
    url(r'^tenant/(?P<tenant>[-\w]+)/controller/enableassert/?$',
        api.views_controller.enable_assert,
        name='controller-enable-assert-scoped',
        kwargs={'scoped':True, 'scope_visible': True, 'permission': "PERMISSION_INTERNAL"}),
	url(r'^controller/disableassert?$',
        api.views_controller.disable_assert,
        name='controller-disable-assert',
        kwargs={'scoped':True, 'scope_visible': False, 'permission': "PERMISSION_INTERNAL"}),
    url(r'^tenant/(?P<tenant>[-\w]+)/controller/disableassert/?$',
        api.views_controller.disable_assert,
        name='controller-disable-assert-scoped',
        kwargs={'scoped':True, 'scope_visible': True, 'permission': "PERMISSION_INTERNAL"}),
)
