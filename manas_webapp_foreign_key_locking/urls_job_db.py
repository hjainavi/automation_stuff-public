
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
import api.views_job_db

urlpatterns = patterns('',
    
    url(r'^jobs/?$',
        api.views_job_db.JobEntryList.as_view(),
        name='jobs-list',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_INTERNAL"}),

    
    url(r'^tenant/(?P<tenant>[-\w.]+)/jobs/?$',
        api.views_job_db.JobEntryList.as_view(),
        name='jobs-list-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_INTERNAL"}),  
                
    url(r'^jobs/(?P<slug>[-\w.]+)/?$',
        api.views_job_db.JobEntryDetail.as_view(),
        name='jobs-detail',
        kwargs={'scoped': True, 'scope_visible': False, 'permission': "PERMISSION_INTERNAL"}),
    
    url(r'^tenant/(?P<tenant>[-\w.]+)/jobs/(?P<slug>[-\w.]+)/?$',
        api.views_job_db.JobEntryDetail.as_view(),
        name='jobs-detail-scoped',
        kwargs={'scoped': True, 'scope_visible': True, 'permission': "PERMISSION_INTERNAL"}),
                
        

)
