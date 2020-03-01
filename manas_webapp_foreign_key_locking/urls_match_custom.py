
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

#pylint:  skip-file
from django.conf.urls import patterns, url
import api.views_match_custom

urlpatterns = patterns('',
    
    url(r'^geoipdb/?$',
        api.views_match_custom.CountryCodeLookup.as_view(),
        name='geoipdb',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_IPADDRGROUP"}),
)
