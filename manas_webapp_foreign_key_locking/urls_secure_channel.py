
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
import api.views_secure_channel

urlpatterns = patterns('',
    
    url(r'^securechannel/?$',
        api.views_secure_channel.SecureChannelMappingList.as_view(),
        name='securechannel-list',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_CONTROLLER"}),

                
    url(r'^securechannel/(?P<slug>[-\w.]+)/?$',
        api.views_secure_channel.SecureChannelMappingDetail.as_view(),
        name='securechannel-detail',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_CONTROLLER"}),
                
        
    
    url(r'^securechannel/?$',
        api.views_secure_channel.SecureChannelAvailableLocalIPsList.as_view(),
        name='securechannel-list',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_CONTROLLER"}),

                
    url(r'^securechannel/(?P<slug>[-\w.]+)/?$',
        api.views_secure_channel.SecureChannelAvailableLocalIPsDetail.as_view(),
        name='securechannel-detail',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_CONTROLLER"}),
                
        
    
    url(r'^securechannel/?$',
        api.views_secure_channel.SecureChannelTokenList.as_view(),
        name='securechannel-list',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_CONTROLLER"}),

                
    url(r'^securechannel/(?P<slug>[-\w.]+)/?$',
        api.views_secure_channel.SecureChannelTokenDetail.as_view(),
        name='securechannel-detail',
        kwargs={'scoped': False, 'scope_visible': False, 'permission': "PERMISSION_CONTROLLER"}),
                
        

)
