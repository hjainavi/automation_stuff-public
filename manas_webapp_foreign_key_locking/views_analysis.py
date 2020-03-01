
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

import logging
from rest_framework.response import Response
from avi.rest.error_list import ServerException
from avi.rest.views import (CommonView, SingleObjectView)
from avi.rest.pb2dict import protobuf2dict_withrefs
from nonportal.management.commands.analysis import VsAnalysis, SeAnalysis
from nonportal.management.commands.analysis import VsAnalysisSummary, SeAnalysisSummary
from nonportal.management.commands.analysis import CloudAnalysisSummary

log = logging.getLogger(__name__)
HTTP_RPC_TIMEOUT = 3.0

class VsAnalysisView(CommonView, SingleObjectView):
    def get(self, request, *args, **kwargs):
        rsp = {}
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        #log.info("run vs analysis:%s", request)
        params = kwargs.get('key')
        try:
            log.info("run vs analysis:%s", params)
            vs_analysis = VsAnalysis()
            rsp_pb = vs_analysis.run_analysis(params=params)
            rsp = protobuf2dict_withrefs(rsp_pb, request)
        except Exception as err:
            msg = 'VsAnalysis failed with %s' %(str(err))
            raise ServerException(msg)
        return Response(data=rsp, status=200)

class SeAnalysisView(CommonView, SingleObjectView):
    def get(self, request, *args, **kwargs):
        rsp = {}
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        params = kwargs.get('key')
        try:
            log.info("run se analysis:%s", params)
            se_analysis = SeAnalysis()
            rsp_pb = se_analysis.run_analysis(params=params)
            rsp = protobuf2dict_withrefs(rsp_pb, request)
        except Exception as err:
            msg = 'SeAnalysis failed with %s' %(str(err))
            raise ServerException(msg)
        return Response(data=rsp, status=200)

class VsAnalysisSummaryView(CommonView, SingleObjectView):
    def get(self, request, *args, **kwargs):
        rsp = {}
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        #log.info("run vs analysis:%s", request)
        #params = kwargs.get('key')
        try:
            log.info("run vs analysis summary for all vs")
            vs_analysis_summary = VsAnalysisSummary()
            rsp_pb = vs_analysis_summary.run_analysis()
            rsp = protobuf2dict_withrefs(rsp_pb, request)
        except Exception as err:
            msg = 'VsAnalysisSummary failed with %s' %(str(err))
            raise ServerException(msg)
        return Response(data=rsp, status=200)

class SeAnalysisSummaryView(CommonView, SingleObjectView):
    def get(self, request, *args, **kwargs):
        rsp = {}
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        #params = kwargs.get('key')
        try:
            log.info("run se analysis summary for all se")
            se_analysis_summary = SeAnalysisSummary()
            rsp_pb = se_analysis_summary.run_analysis()
            rsp = protobuf2dict_withrefs(rsp_pb, request)
        except Exception as err:
            msg = 'SeAnalysisSummary failed with %s' %(str(err))
            raise ServerException(msg)
        return Response(data=rsp, status=200)

class CloudAnalysisView(CommonView, SingleObjectView):
    def get(self, request, *args, **kwargs):
        rsp = {}
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        params = kwargs.get('key')
        try:
            log.info("run cloud analysis:%s", params)
            c_analysis = CloudAnalysisSummary()
            rsp_pb = c_analysis.run_analysis(params=params)
            rsp = protobuf2dict_withrefs(rsp_pb, request)
        except Exception as err:
            msg = 'CloudAnalysis failed with %s' %(str(err))
            raise ServerException(msg)
        return Response(data=rsp, status=200)

