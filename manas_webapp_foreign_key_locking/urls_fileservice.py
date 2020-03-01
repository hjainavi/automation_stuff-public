
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
import api.views_fileservice

urlpatterns = patterns('',
    url(r'^fileservice/?$', 
        api.views_fileservice.FileServiceView.as_view(),
        name='fileserviceview-detail',
        kwargs={'permission': "PERMISSION_EXEMPT"},
        ),
    url(r'^fileservice/uploads/?$', 
        api.views_fileservice.FileServiceUploadView.as_view(),
        name='fileserviceuploadview',
        kwargs={'permission': "PERMISSION_CONTROLLER"}
        ),
    url(r'^fileservice/hsmpackages/?$', 
        api.views_fileservice.FileServiceUploadView.as_view(),
        name='fileservicehsmpackagesview',
        kwargs={'permission': "PERMISSION_CONTROLLER", 'hsmpackages' : True}
        ),
    url(r'^fileservice/seova/?$', 
        api.views_fileservice.FileServiceSeOVAView.as_view(),
        name='fileservice-se-ova-view',
        kwargs={'permission': "PERMISSION_CLOUD"},
        ),
    url(r'^fileservice/seova/se.qcow2$',
        api.views_fileservice.FileServiceSeOVAQCow2View.as_view(),
        name='fileservice-se-ova-qcow2-view',
        kwargs={'permission': "PERMISSION_CLOUD"},
        ),
    url(r'^fileservice/scripts/?$', 
        api.views_fileservice.FileServiceScriptsView.as_view(),
        name='fileservice-scripts-view',
        kwargs={'permission': "PERMISSION_EXEMPT"},
        ),
    url(r'^fileservice/gslb/?$', 
        api.views_fileservice.FileServiceUploadView.as_view(),
        name='fileserviceuploadview',
        kwargs={'permission': "PERMISSION_CONTROLLER", 'gslb' : True}
        ),
    url(r'^fileservice/gslbsiteops/fileconfig/(?P<slug>[-\w.]+)?$', 
        api.views_fileservice.FileServiceUploadView.as_view(),
        name='fileserviceuploadview',
        kwargs={'permission': "PERMISSION_CONTROLLER", 'gslbsiteops' : True}
        ),
    url(r'^fileservice/ipamdnsscripts/?$',
        api.views_fileservice.FileServiceUploadView.as_view(),
        name='fileservice-ipamdnsscripts',
        kwargs={'permission': "PERMISSION_CONTROLLER", 'ipamdnsscripts' : True}
        ),
)

