
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
import api.views_container_custom

urlpatterns = patterns('',
    url(r'^mesos-serviceengine/?$',
        api.views_container_custom.MesosServiceEngine.as_view(),
        name='mesos-serviceengine',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    url(r'^mesos-verify-login/?$',
        api.views_container_custom.MesosVerifyLogin.as_view(),
        name='mesos-serviceengine',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
    url(r'^k8s-verify-login/?$',
        api.views_container_custom.OshiftK8SVerifyLogin.as_view(),
        name='k8s-serviceengine',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
)
