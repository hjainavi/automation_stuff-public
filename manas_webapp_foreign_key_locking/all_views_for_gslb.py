
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

# Filename: all_views_for_gslb:
#
# Description:
# Custom file containing gslb-required views. We want to do RPC callbacks 
# in an agnostic manner in the views_gslb_custom.py.run_callback.  For
# fedarated objects that go to vs-mgr ex:hm, we want to invoke the view 
# specific callback.  
# 
# Example: 
# HealthMonitor goes to vs-mgr; We want to invoke the appropriate HM
# view based on the pb_type and method.  So, HM create will translate
# HealthMonitorList view while HM update/delete will map to HealthMonitor
# Detail view.
#
# Notes:
# Q1. Why not use all_views.py? 
#     The tool generated code does not include 'custom-views'.  Unfortunately,
#     the PKIProfile is present in views_ssl_custom and does NOT get included
#     in the all_views.  We have 2 choices.
#
#     Choice 1:
#     Fix the python/bin/proto2model/ViewGenerator.py to somehow include
#     a selected list of custom files.
#
#     Choice 2:
#     Have a limited 'all_views_for_gslb.py' file that is hand-crafted.

#pylint:  skip-file
from views_health_monitor import *
from views_ssl_custom import *
from views_application_persistence_profile import *
from views_pool import *
from views_vs import *
