
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

#GENERATED FILE 
#pylint:  skip-file
from django.conf.urls import patterns, include, url
import api.views_snmp

urlpatterns = patterns('',
    
    url(r'^snmptrapprofile/?$',
        api.views_snmp.SnmpTrapProfileList.as_view(),
        name='snmptrapprofile-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_SNMPTRAPPROFILE"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/snmptrapprofile/?$',
        api.views_snmp.SnmpTrapProfileList.as_view(),
        name='snmptrapprofile-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_SNMPTRAPPROFILE"}),  
                
    url(r'^snmptrapprofile/(?P<slug>[-\w.]+)/?$',
        api.views_snmp.SnmpTrapProfileDetail.as_view(),
        name='snmptrapprofile-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_SNMPTRAPPROFILE"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/snmptrapprofile/(?P<slug>[-\w.]+)/?$',
        api.views_snmp.SnmpTrapProfileDetail.as_view(),
        name='snmptrapprofile-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_SNMPTRAPPROFILE"}),
                
    
    url(r'^snmptrapprofile/(?P<key>[-\w.]+)/testsnmptrap/?$',
        api.views_snmp.SnmpTrapProfileAlerttestsnmptrapView.as_view(),
        name='snmptrapprofilealerttestsnmptrapview-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_SNMPTRAPPROFILE"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/snmptrapprofile/(?P<key>[-\w.]+)/testsnmptrap/?$',
        api.views_snmp.SnmpTrapProfileAlerttestsnmptrapView.as_view(),
        name='snmptrapprofilealerttestsnmptrapview-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_SNMPTRAPPROFILE" }),
        

)
