#!/bin/bash

############################################################################
#
# AVI CONFIDENTIAL
# __________________
#
# [2013] - [2019] Avi Networks Incorporated
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

VIEWS_FILE_PATCH="/opt/avi/python/lib/avi/rest/views.patch"
cat > $VIEWS_FILE_PATCH <<- EOM
--- /opt/avi/python/lib/avi/rest/views.py   2019-11-26 12:38:27.681371884 +0000
+++ /opt/avi/python/lib/avi/rest/views_new.py   2019-11-26 12:38:21.953452076 +0000
@@ -224,7 +224,7 @@
         if (kwargs.get('scoped', False) and request.DATA and
             (request.method == 'POST' or not request.DATA.get('cloud_ref')) and self.cloud):
             request.DATA['cloud_ref'] = '/api/cloud/%s' % self.cloud.uuid
-
+        log.info('kwargs %s'%(kwargs))
         self._check_params(request, args, kwargs)
         self.kwargs = kwargs
 
@@ -285,7 +285,10 @@
                                     %(model_name, tenant.name))
             if not self.cloud and model_name in ['ServiceEngineGroup', 'VrfContext', 'ServiceEngine']:
                 self.cloud = db_obj.cloud_ref
-
+        log.info('access %s'%(access))
+        log.info('permission %s'%(permission_enum))
+        log.info('tenant %s'%(tenant))
+        log.info('model_name %s'%(model_name))
         self.check_user_tenant_resource(user, tenant, permission_enum, access, model_name)
 
     @api_perf
EOM

SERIALIZER_FILE_PATCH="/opt/avi/python/lib/avi/rest/serializer.patch"
cat > $SERIALIZER_FILE_PATCH <<- EOM
--- /opt/avi/python/lib/avi/rest/serializers.py 2019-11-26 12:38:27.681371884 +0000
+++ /opt/avi/python/lib/avi/rest/serializers_new.py 2019-11-26 12:38:25.133407556 +0000
@@ -155,7 +155,10 @@
     value = u.path
     params = u.query
     match_kwargs = {}
-
+    log.info("uri %s"%(uri))
+    log.info("ref_type %s"%(ref_type))
+    log.info("ref_obj %s"%(ref_obj))
+    log.info("context %s"%(context))
     # Skip resolve for simple generated resource url
     model_name = ref_obj.lower()
     pattern = r'^/api/%s/(?P<slug>[-\w.]+)/?$' % model_name
@@ -243,6 +246,7 @@
             kwargs['tenant_ref'] = context['tenant_ref']
 
     try:
+        log.info('kwargs %s'%(kwargs))
         obj = model_class.objects.get(**kwargs)
     except ObjectDoesNotExist:
         raise
EOM

echo "PATCH FILE CREATED"

echo "APPLYING PATCH"

cd /opt/avi/python/lib/avi/rest

patch < views.patch
patch < serializer.patch

echo "PATCH APPLIED"

systemctl stop aviportal.service

rm $VIEWS_FILE_PATCH
rm $SERIALIZER_FILE_PATCH

