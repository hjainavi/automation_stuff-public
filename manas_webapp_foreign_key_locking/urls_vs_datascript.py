
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
import api.views_vs_datascript

urlpatterns = patterns('',
    
    url(r'^vsdatascriptset/?$',
        api.views_vs_datascript.VSDataScriptSetList.as_view(),
        name='vsdatascriptset-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_VSDATASCRIPTSET"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/vsdatascriptset/?$',
        api.views_vs_datascript.VSDataScriptSetList.as_view(),
        name='vsdatascriptset-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_VSDATASCRIPTSET"}),  
                
    url(r'^vsdatascriptset/(?P<slug>[-\w.]+)/?$',
        api.views_vs_datascript.VSDataScriptSetDetail.as_view(),
        name='vsdatascriptset-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_VSDATASCRIPTSET"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/vsdatascriptset/(?P<slug>[-\w.]+)/?$',
        api.views_vs_datascript.VSDataScriptSetDetail.as_view(),
        name='vsdatascriptset-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_VSDATASCRIPTSET"}),
                
        

)
