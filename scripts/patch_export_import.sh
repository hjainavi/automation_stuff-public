#!/bin/bash

############################################################################
#
# AVI CONFIDENTIAL
# __________________
#
# [2013] - [2020] Avi Networks Incorporated
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

EXPORT_IMPORT_FILE_PATCH="/opt/avi/python/lib/avi/config_migration/export_import.patch"
cat > $EXPORT_IMPORT_FILE_PATCH <<- EOM
--- export_import.py	2019-12-23 06:38:11.000000000 +0000
+++ export_import_new.py	2020-03-19 19:08:14.859843297 +0000
@@ -139,7 +139,7 @@
 class ConfigDataException(Exception):
     pass
 
-def get_key_for_model_obj((model_name, obj_uuid, export_colon_refs, upgrade_mode)):
+def get_key_for_model_obj((model_name, obj_uuid, export_colon_refs)):
     model, _ = get_model_and_serializer(model_name)
     try:
         model_obj = model.objects.get(uuid=obj_uuid)
@@ -156,34 +156,29 @@
             key = model_obj.uuid
     elif hasattr(model_obj, 'name'):
         key_list = []
-        name = urllib.quote(model_obj.name) if upgrade_mode else model_obj.name
         if hasattr(model_obj, 'tenant_ref'):
             tenant_name = model_obj.tenant_ref.name
             if not tenant_name:
                 log.error('Exporting: Bad tenant in obj %s', model_obj)
                 raise Exception('Tenant name could not be determined!')
-            if upgrade_mode:
-                tenant_name = urllib.quote(tenant_name)
             if export_colon_refs:
-                key_list = [tenant_name, name]
+                key_list = [tenant_name, model_obj.name]
             else:
-                key_list = ['?tenant=%s' % tenant_name, 'name=%s' % name]
+                key_list = ['?tenant=%s' % tenant_name, 'name=%s' % model_obj.name]
             if hasattr(model_obj, 'cloud_ref'):
                 cloud_name = model_obj.cloud_ref.name
                 if not cloud_name:
                     log.error('Bad cloud in obj %s', model_obj)
                     raise Exception('Cloud name could not be determined!')
-                if upgrade_mode:
-                    cloud_name = urllib.quote(cloud_name)
                 if export_colon_refs:
                     key_list.append(cloud_name)
                 else:
                     key_list.append('cloud=%s' % cloud_name)
         else:
             if export_colon_refs:
-                key_list = [name]
+                key_list = [model_obj.name]
             else:
-                key_list = ['?name=%s' % name]
+                key_list = ['?name=%s' % model_obj.name]
 
         if export_colon_refs:
             key = ':'.join(key_list)
@@ -209,8 +204,6 @@
 
     if '_last_modified' in data:
         data.pop('_last_modified')
-    if upgrade_mode and data.get('name',False):
-        data['name'] = urllib.quote(data['name'])
 
     if not skip_sensitive_fields:
         decrypt_sensitive_fields(model, data)
@@ -752,14 +745,14 @@
             if len(model_uuids) > PARALLEL_THRESHOLD:
                 connection.close()
                 pool = Pool(cpu_count()/2)
-                map_data = ((model_name, uuid, self.export_colon_refs, self.upgrade_mode) for uuid in model_uuids)
+                map_data = ((model_name, uuid, self.export_colon_refs) for uuid in model_uuids)
                 map_resp = pool.map(get_key_for_model_obj, map_data)
                 [key_map[model_name].update(item) for item in map_resp if item]
                 pool.close()
                 pool.join()
             else:
                 for uuid in model_uuids:
-                    item = get_key_for_model_obj((model_name, uuid, self.export_colon_refs, self.upgrade_mode))
+                    item = get_key_for_model_obj((model_name, uuid, self.export_colon_refs))
                     if item:
                         key_map[model_name].update(item)
         return key_map
@@ -810,8 +803,6 @@
                 upgrade=True)
 
         data['order'] = api_models.pb_ordered
-        if self.upgrade_mode:
-            data['url_encode'] = True
         return data
 
 
@@ -982,7 +973,6 @@
         self.cloud = cloud
         self.tenant = tenant
         self.force_api_versioning = False
-        self.url_encode = False
 
     def _create_existed_object_map(self, backup_mode):
         """
@@ -990,7 +980,7 @@
         Obj_type -> obj_name:tenant_ref -> uuid
         """
         results = {}
-        exporter = ConfigExporter(backup_mode=backup_mode, upgrade_mode=self.upgrade_mode)
+        exporter = ConfigExporter(backup_mode=backup_mode)
 
         tenant_list = exporter._export_model('Tenant')
         self.tenant_uuid2name = self._populate_uuid2name_map(tenant_list)
@@ -1008,7 +998,7 @@
             if len(obj_uuids) > PARALLEL_THRESHOLD:
                 connection.close()
                 pool = Pool(cpu_count()/2)
-                map_data = ((model_name, uuid, self.export_colon_refs, self.upgrade_mode) for uuid in obj_uuids)
+                map_data = ((model_name, uuid, self.export_colon_refs) for uuid in obj_uuids)
                 map_resp = pool.map(get_key_for_model_obj, map_data)
                 for item in map_resp:
                     if item:
@@ -1021,7 +1011,7 @@
                     obj = model.objects.get(uuid=uuid)
                     if not hasattr(obj, 'uuid'):
                         continue
-                    item = get_key_for_model_obj((model_name, uuid, False, self.upgrade_mode))
+                    item = get_key_for_model_obj((model_name, uuid, False))
                     if item:
                         (uuid, key) = item.popitem()
                         results[model_name][key] = uuid
@@ -1039,8 +1029,6 @@
             tenant_uuid = slug_from_uri(obj_data.get('tenant_ref'))
             if tenant_uuid and self.tenant_uuid2name.get(tenant_uuid):
                 tenant_name = self.tenant_uuid2name.get(tenant_uuid)
-        if self.upgrade_mode and self.url_encode:
-            tenant_name = urllib.unquote(tenant_name) 
         post_transform(pb, tenant_name=tenant_name)
         new_obj = protobuf2dict_withrefs(pb, None)
         if 'extension' in obj_data:
@@ -1058,14 +1046,6 @@
             obj.object_uuid = new_uuid
             obj.save()
 
-    def quote_unquote_values(self, obj_data, list_of_fields,quote=True):
-        for field in list_of_fields:
-            if obj_data.get(field, False):
-                if quote:
-                    obj_data[field] = urllib.quote(obj_data[field])
-                else:
-                    obj_data[field] = urllib.unquote(obj_data[field])
-
 
     @db_transaction
     def _save_object_to_db(self, model_class, serializer_class, obj_data):
@@ -1109,8 +1089,6 @@
         #use obj key to search in existed objects
         key = self.get_key_for_object(model_name, obj_data)
         this_model_map = self.existed_obj_map[model_name]
-        if self.upgrade_mode and self.url_encode:
-            self.quote_unquote_values(obj_data, ['name', 'tenant_name', 'cloud_name'], quote=False)
         obj_data = self._run_pb_default(obj_data, serializer_class, key)
 
         if key in this_model_map:  #update obj
@@ -1795,8 +1773,6 @@
         user = None
         request_context = {}
         meta = configuration.get('META', {})
-        if meta.get('url_encode',False):
-            self.url_encode = True
         # Removing version check to allow import export across versions
         #self.check_version(meta)
 
EOM


echo "PATCH FILE CREATED"

echo "APPLYING PATCH"

cd /opt/avi/python/lib/avi/config_migration/

patch < export_import.patch

echo "PATCH APPLIED"

systemctl stop aviportal.service
systemctl stop maintenanceportal.service

rm $EXPORT_IMPORT_FILE_PATCH

