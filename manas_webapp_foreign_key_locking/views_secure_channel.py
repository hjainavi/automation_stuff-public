
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
from api.models import *
from avi.rest.views import *

    
class SecureChannelMappingList(ListView, ):
    model = SecureChannelMapping
    serializer_class = SecureChannelMappingSerializer
    rpc_data = {
            }
    
    
class SecureChannelMappingDetail(RetrieveView, ):
    model = SecureChannelMapping
    serializer_class = SecureChannelMappingSerializer
    rpc_data = {
            }
            
    
class SecureChannelAvailableLocalIPsList(ListView, ):
    model = SecureChannelAvailableLocalIPs
    serializer_class = SecureChannelAvailableLocalIPsSerializer
    rpc_data = {
            }
    
    
class SecureChannelAvailableLocalIPsDetail(RetrieveView, ):
    model = SecureChannelAvailableLocalIPs
    serializer_class = SecureChannelAvailableLocalIPsSerializer
    rpc_data = {
            }
            
    
class SecureChannelTokenList(ListView, ):
    model = SecureChannelToken
    serializer_class = SecureChannelTokenSerializer
    rpc_data = {
            }
    
    
class SecureChannelTokenDetail(RetrieveView, ):
    model = SecureChannelToken
    serializer_class = SecureChannelTokenSerializer
    rpc_data = {
            }
            
