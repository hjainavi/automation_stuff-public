#!/bin/bash

VIEWS_INVENTORY_PATCH="/opt/avi/python/bin/portal/api/views_inventory.patch"
cat > $VIEWS_INVENTORY_PATCH <<- EOM
--- views_inventory.py	2021-07-29 10:10:35.745977913 +0000
+++ views_inventory_new.py	2021-07-29 10:10:52.673976920 +0000
@@ -76,6 +76,7 @@
 from avi.infrastructure.taskqueue import TaskQueueException
 from rest_framework import status
 from avi.protobuf.gslb_pb2 import REPLICATION_MODE_CONTINUOUS
+from concurrent.futures import ThreadPoolExecutor
 
 log = logging.getLogger(__name__)
 
@@ -933,16 +934,18 @@
                                                        self.model_type, uuids)
 
         threads = []
-        for (index, config_data) in enumerate(list_data['results']):
-            try:
-                runtime_data_obj = runtime_data[index]
-            except IndexError:
-                runtime_data_obj = None
-            threads.append(gevent.spawn(self.get_data_for_one_object,
-                                        config_data, request,
-                                        runtime_data_obj, *args, **kwargs))
-        gevent.joinall(threads)
-        data['results'] = [thread.value for thread in threads]
+        with ThreadPoolExecutor(max_workers=20) as executor:
+            for (index, config_data) in enumerate(list_data['results']):
+                try:
+                    runtime_data_obj = runtime_data[index]
+                except IndexError:
+                    runtime_data_obj = None
+                future = executor.submit(self.get_data_for_one_object,
+                                            config_data, request,
+                                            runtime_data_obj, *args, **kwargs)
+                threads.append(future)
+        
+        data['results'] = [thread.result(timeout=150) for thread in threads]
 
         if not self.resource_list or 'upgradestatus' in self.resource_list:
             # Refer note 01
@@ -1406,7 +1409,8 @@
         except Exception as e:
             log.error('%s', traceback.format_exc())        
         return shared_vip_fault
-    
+   
+
     @api_perf
     def get_ssl_cert_ocsp_status_faults(self, uuid, request, *args, **kwargs):
         def _retrieve_ocsp_cert_status_str(enum):
@@ -1435,6 +1439,12 @@
                         ssl_info.append(ssl_dict)
         return ssl_info
 
+    @api_perf
+    def get_children_get_ssl_cert_expiry_faults(self,uuid):
+        db_cache = self._db_cache()
+        ssl_key_refs = db_cache.get_children('VirtualService',uuid=uuid, model_filter=['SSLKeyAndCertificate'])
+        return ssl_key_refs
+
 
     @api_perf
     def get_ssl_cert_expiry_faults(self, uuid, request, *args, **kwargs):
@@ -1446,9 +1456,9 @@
             return datetime.strptime(date_s, "%Y-%m-%d %H:%M:%S")
 
         ssl_info = []
+        ssl_key_refs = self.get_children_get_ssl_cert_expiry_faults(uuid)
         db_cache = self._db_cache()
-        ssl_key_refs = db_cache.get_children('VirtualService',
-                                    uuid=uuid, model_filter=['SSLKeyAndCertificate'])
+        
         # retrieve the test conditions
         test_enabled, cond = self.get_test_ssl_cert_fault_config()
         #log.info('SSL Key and Certs : %s' % (sslkeyandcert_list))
@@ -1560,15 +1570,21 @@
         return False
 
     @api_perf
-    def check_debug_for_children(self, uuid, request, args, kwargs):
+    def get_parents_check_debug_for_children(self,uuid):
+
         db_cache = self._db_cache()
         children = db_cache.get_parents('VirtualService',
                                         uuid=uuid,
 					model_filter=['VirtualService'],
 					depth=1,
 					prune_criteria=0)
+        return children
+
+    @api_perf
+    def check_debug_for_children(self, uuid, request, args, kwargs):
         child_capture_on = False
         d_dict = dict()
+        children = self.get_parents_check_debug_for_children(uuid)
         for child in children:
             debug_list = self.get_debug_trace_status(child.uuid,
                                                     request,
EOM

echo "PATCH FILE CREATED"
echo "APPLYING PATCH"
cd /opt/avi/python/bin/portal/api/
patch < views_inventory.patch

echo "PATCH APPLIED"
systemctl stop aviportal.service
systemctl stop maintenanceportal.service

rm $VIEWS_INVENTORY_PATCH




