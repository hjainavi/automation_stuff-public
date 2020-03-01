
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

set -x
set -e
# file for mapping class names to files containing those classes
grep "^class" serializers_* models_* ../permission/models* ../permission/serializers* | awk -f create_mmap.awk > model_mapping.py
rgrep "^from.*Proto$" serializers* models* | awk 'BEGIN{print("pbmap = {");}{printf("\"%s\": \"%s\",\n", $4, $2);}END{print "}";}' > pb_file_mapping.py
# file for pb_map
grep -v import models.py > pb_model_map.py 
sed -i "s/'pb': \([^,]*\),/'pb': '\1',/g" pb_model_map.py
sed -i "s/'pb_extension': \([^N][^,]*\),/'pb_extension': '\1',/g" pb_model_map.py
