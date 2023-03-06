#!/bin/bash

VIEWS_FILE_PATCH="/opt/avi/python/lib/avi/rest/db_cache.py.patch"
cat > $VIEWS_FILE_PATCH <<- EOM
--- a/lib/avi/rest/db_cache.py
+++ b/lib/avi/rest/db_cache.py
@@ -206,7 +206,7 @@ class DbCache(object):
 
     def _set_references_local_cache(self, pb_val, name, uuid, local_cache_api_server):
         # removing all the relations of the pb_val.name and pb_val.uuid
-        local_cache_api_server["ref_map"]["set"] = [ line for line in local_cache_api_server["ref_map"]["set"] if (line[1] != uuid and line[0] != name) ]
+        local_cache_api_server["ref_map"]["set"] = [ line for line in local_cache_api_server["ref_map"]["set"] if (line[1] != uuid or line[0] != name) ]
         # setting the new relations of the pb_val
         refs = {}
         _pb_get_related_refs(pb_val, refs, None, True)
EOM

echo "PATCH FILE CREATED"

echo "APPLYING PATCH"

cd /opt/avi/python/lib/avi/rest

patch < db_cache.py.patch

echo "PATCH APPLIED"

systemctl stop aviportal.service
systemctl stop maintenanceportal.service

rm $VIEWS_FILE_PATCH

