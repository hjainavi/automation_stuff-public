
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
import api.views_alerts

urlpatterns = patterns('',
    
    url(r'^alertsyslogconfig/?$',
        api.views_alerts.AlertSyslogConfigList.as_view(),
        name='alertsyslogconfig-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_ALERTSYSLOGCONFIG"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/alertsyslogconfig/?$',
        api.views_alerts.AlertSyslogConfigList.as_view(),
        name='alertsyslogconfig-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_ALERTSYSLOGCONFIG"}),  
                
    url(r'^alertsyslogconfig/(?P<slug>[-\w.]+)/?$',
        api.views_alerts.AlertSyslogConfigDetail.as_view(),
        name='alertsyslogconfig-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_ALERTSYSLOGCONFIG"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/alertsyslogconfig/(?P<slug>[-\w.]+)/?$',
        api.views_alerts.AlertSyslogConfigDetail.as_view(),
        name='alertsyslogconfig-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_ALERTSYSLOGCONFIG"}),
                
    
    url(r'^alertsyslogconfig/(?P<key>[-\w.]+)/testsyslog/?$',
        api.views_alerts.AlertSyslogConfigAlerttestsyslogView.as_view(),
        name='alertsyslogconfigalerttestsyslogview-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_ALERTSYSLOGCONFIG"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/alertsyslogconfig/(?P<key>[-\w.]+)/testsyslog/?$',
        api.views_alerts.AlertSyslogConfigAlerttestsyslogView.as_view(),
        name='alertsyslogconfigalerttestsyslogview-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_ALERTSYSLOGCONFIG" }),
        
    
    url(r'^alertscriptconfig/?$',
        api.views_alerts.AlertScriptConfigList.as_view(),
        name='alertscriptconfig-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_ALERTCONFIG"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/alertscriptconfig/?$',
        api.views_alerts.AlertScriptConfigList.as_view(),
        name='alertscriptconfig-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_ALERTCONFIG"}),  
                
    url(r'^alertscriptconfig/(?P<slug>[-\w.]+)/?$',
        api.views_alerts.AlertScriptConfigDetail.as_view(),
        name='alertscriptconfig-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_ALERTCONFIG"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/alertscriptconfig/(?P<slug>[-\w.]+)/?$',
        api.views_alerts.AlertScriptConfigDetail.as_view(),
        name='alertscriptconfig-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_ALERTCONFIG"}),
                
        
    
    url(r'^alertemailconfig/?$',
        api.views_alerts.AlertEmailConfigList.as_view(),
        name='alertemailconfig-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_ALERTEMAILCONFIG"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/alertemailconfig/?$',
        api.views_alerts.AlertEmailConfigList.as_view(),
        name='alertemailconfig-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_ALERTEMAILCONFIG"}),  
                
    url(r'^alertemailconfig/(?P<slug>[-\w.]+)/?$',
        api.views_alerts.AlertEmailConfigDetail.as_view(),
        name='alertemailconfig-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_ALERTEMAILCONFIG"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/alertemailconfig/(?P<slug>[-\w.]+)/?$',
        api.views_alerts.AlertEmailConfigDetail.as_view(),
        name='alertemailconfig-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_ALERTEMAILCONFIG"}),
                
    
    url(r'^alertemailconfig/(?P<key>[-\w.]+)/testemail/?$',
        api.views_alerts.AlertEmailConfigAlerttestemailView.as_view(),
        name='alertemailconfigalerttestemailview-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_ALERTEMAILCONFIG"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/alertemailconfig/(?P<key>[-\w.]+)/testemail/?$',
        api.views_alerts.AlertEmailConfigAlerttestemailView.as_view(),
        name='alertemailconfigalerttestemailview-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_ALERTEMAILCONFIG" }),
        
    
    url(r'^alert/?$',
        api.views_alerts.AlertList.as_view(),
        name='alert-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_ALERT"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/alert/?$',
        api.views_alerts.AlertList.as_view(),
        name='alert-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_ALERT"}),  
                
    url(r'^alert/(?P<slug>[-\w.]+)/?$',
        api.views_alerts.AlertDetail.as_view(),
        name='alert-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_ALERT"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/alert/(?P<slug>[-\w.]+)/?$',
        api.views_alerts.AlertDetail.as_view(),
        name='alert-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_ALERT"}),
                
        
    
    url(r'^alertconfig/?$',
        api.views_alerts.AlertConfigList.as_view(),
        name='alertconfig-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_ALERTCONFIG"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/alertconfig/?$',
        api.views_alerts.AlertConfigList.as_view(),
        name='alertconfig-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_ALERTCONFIG"}),  
                
    url(r'^alertconfig/(?P<slug>[-\w.]+)/?$',
        api.views_alerts.AlertConfigDetail.as_view(),
        name='alertconfig-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_ALERTCONFIG"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/alertconfig/(?P<slug>[-\w.]+)/?$',
        api.views_alerts.AlertConfigDetail.as_view(),
        name='alertconfig-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_ALERTCONFIG"}),
                
        
            
    
    url(r'^alertparams/set/?$',
        api.views_alerts.AlertParamsSetView.as_view(),
        name='alertparamssetview-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_CONTROLLER"}),
    url(r'^tenant/(?P<tenant>[-\w.]+)/alertparams/set/?$',
        api.views_alerts.AlertParamsSetView.as_view(),
        name='alertparamssetview-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_CONTROLLER" }),
        
    
    url(r'^actiongroupconfig/?$',
        api.views_alerts.ActionGroupConfigList.as_view(),
        name='actiongroupconfig-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_ACTIONGROUPCONFIG"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/actiongroupconfig/?$',
        api.views_alerts.ActionGroupConfigList.as_view(),
        name='actiongroupconfig-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_ACTIONGROUPCONFIG"}),  
                
    url(r'^actiongroupconfig/(?P<slug>[-\w.]+)/?$',
        api.views_alerts.ActionGroupConfigDetail.as_view(),
        name='actiongroupconfig-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_ACTIONGROUPCONFIG"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/actiongroupconfig/(?P<slug>[-\w.]+)/?$',
        api.views_alerts.ActionGroupConfigDetail.as_view(),
        name='actiongroupconfig-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_ACTIONGROUPCONFIG"}),
                
        
    
    url(r'^alertobjectlist/?$',
        api.views_alerts.AlertObjectListList.as_view(),
        name='alertobjectlist-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_ALERTCONFIG"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/alertobjectlist/?$',
        api.views_alerts.AlertObjectListList.as_view(),
        name='alertobjectlist-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_ALERTCONFIG"}),  
                
    url(r'^alertobjectlist/(?P<slug>[-\w.]+)/?$',
        api.views_alerts.AlertObjectListDetail.as_view(),
        name='alertobjectlist-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_ALERTCONFIG"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/alertobjectlist/(?P<slug>[-\w.]+)/?$',
        api.views_alerts.AlertObjectListDetail.as_view(),
        name='alertobjectlist-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_ALERTCONFIG"}),
                
        

)
