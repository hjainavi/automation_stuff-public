
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
import api.views_aws_custom
import permission.views

#aws - verify-creds={vpc}, get-networks = {az:subnets}

urlpatterns = patterns('',
    url(r'^aws-get-regions/?$',
        api.views_aws_custom.AwsRegionsView.as_view(),
        name='aws-get-regions',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),

    url(r'^aws-verify-credentials/?$',
        api.views_aws_custom.AwsVerifyCredView.as_view(),
        name='aws-verify-credentials',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),

    url(r'^aws-get-networks/?$',
        api.views_aws_custom.AwsSubnetsView.as_view(),
        name='aws-get-networks',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),

    url(r'^aws-get-assume-roles/?$',
        api.views_aws_custom.AwsAssumeRolesView.as_view(),
        name='aws-get-assume-roles',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),

    url(r'^aws-get-kms-cmks/?$',
        api.views_aws_custom.AwsKmsCmksView.as_view(),
        name='aws-get-kms-cmks',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_CLOUD"}),
)
