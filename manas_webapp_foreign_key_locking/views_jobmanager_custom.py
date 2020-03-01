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
from datetime import datetime, timedelta
from django.views.generic import View
from django.http import JsonResponse
from permission.models import AuthToken
from avi.rest.session_utils import cleanup_sessions
from permission.secure_channel_utils import (check_unknown_se_entries)
from nonportal.management.commands.consistency_checker import ConfigConsistencyChecker
from api.models_se import ServiceEngine
from api.models_job_db import JobEntry
from api.models_controller_properties import ControllerProperties
from api.models_ssl import PKIProfile
from avi.protobuf.ssl_rpc_pb2 import PKIProfileService_Stub
from avi.rest.pb2model import protobuf2model
import avi.rest.callbacks as callbacks
from avi.util.gslb_util import get_glb_cfg
from avi.util.cluster_info import cluster_uuid as cluster_uuid_ref
from avi.util.ssl_utils import update_crl_urls
from avi.infrastructure.rpc_channel import RpcChannel
from google.protobuf.service import RpcController
from avi.rest.views import PostActionView
from avi.infrastructure.db_transaction import db_transaction

log = logging.getLogger(__name__)

class AuthTokenJob(PostActionView):
    def do_post_action(self, request, *args, **kwargs):

        response_data = {}
        try:
            AuthToken.delete_expired()
            response_data['Success'] = "AuthTokenJob Successfully Completed"
        except Exception as e:
            response_data['Exception'] = str(e)

        return JsonResponse(response_data, status=200)

class SessionJob(PostActionView):
    def do_post_action(self, request, *args, **kwargs):

        response_data = {}
        try:
            cleanup_sessions()
            response_data['Success'] = "SessionJob Successfully Completed"
        except Exception as e:
            response_data['Exception'] = str(e)

        return JsonResponse(response_data, status=200)

class SecureChannelCleanupJob(PostActionView):
    def do_post_action(self, request, *args, **kwargs):

        response_data = {}
        try:
            se_uuids = [ se['uuid'] for se in ServiceEngine.objects.values('uuid')]
            check_unknown_se_entries(se_uuids)
            response_data['Success'] = "ServiceEngineJob Successfully Completed"
        except Exception as e:
            response_data['Exception'] = str(e)

        return JsonResponse(response_data, status=200)

class ConsistencyCheckJob(PostActionView):
    def do_post_action(self, request, *args, **kwargs):

        response_data = {}
        try:
            ccc = ConfigConsistencyChecker()
            ccc.config_consistency_check()
            response_data['Success'] = "ConsistencyCheckJob Successfully Completed"
        except Exception as e:
            response_data['Exception'] = str(e)

        return JsonResponse(response_data, status=200)

def datetime_to_str(d):
    return d.strftime("%Y-%m-%d %H:%M:%S")

def datetime_from_str(date_s):
    return datetime.strptime(date_s, "%Y-%m-%d %H:%M:%S")

def _handle_crl_update(crl_pb, job_pb, delta, last_refreshed, need_update, now):
    if last_refreshed + delta <= now:
        if update_crl_urls(crl_pb):
            need_update = True
        last_refreshed = now
    next_update = last_refreshed + delta
    if datetime_from_str(job_pb.expires_at) > next_update:
        job_pb.expires_at = datetime_to_str(next_update)
        job_pb.subjobs[0].expires_at = datetime_to_str(next_update)
    crl_pb.last_refreshed = datetime_to_str(last_refreshed)
    return need_update

@db_transaction
def process_pkiprofile_job(job_uuid):
    """
    Process the pki-profile.
    Federated objects should be rotated only on the Gslb Leader.
    """
    now = datetime.utcnow()
    job = JobEntry.objects.get(uuid=job_uuid)
    job_pb = job.protobuf()

    pki_profile_refresh_period = (
            ControllerProperties.objects.get(id=1).protobuf().process_pki_profile_timeout_period
        )
    pki_profile_refresh_period_timedelta = timedelta(minutes=pki_profile_refresh_period)

    job_pb.expires_at = datetime_to_str(now+pki_profile_refresh_period_timedelta)
    job_pb.subjobs[0].expires_at = datetime_to_str(now+pki_profile_refresh_period_timedelta)
    job_pb.subjobs[0].metadata = datetime_to_str(now)
    query = PKIProfile.objects.filter(uuid=job_pb.obj_key)
    if not query:
        print 'PKIProfile not found: %s' % job_pb.obj_key
        return
    pki_pb = query[0].protobuf()
    if pki_pb.is_federated:
        glb_cfg = get_glb_cfg()
        if glb_cfg:
            if glb_cfg.leader_cluster_uuid != cluster_uuid_ref():
                print 'Federated PKIProfile %s not processed on Follower' % pki_pb.name
                return

    need_update = False
    for crl_pb in pki_pb.crls:
        if not crl_pb.server_url:
            continue

        if not crl_pb.last_refreshed:
            crl_pb.last_refreshed = datetime_to_str(now)
        last_refreshed = datetime_from_str(crl_pb.last_refreshed)

        if crl_pb.update_interval:
            delta = timedelta(minutes=crl_pb.update_interval)
            need_update = _handle_crl_update(crl_pb, job_pb, delta, last_refreshed, need_update, now)
        else:
            need_update = _handle_crl_update(crl_pb, job_pb, pki_profile_refresh_period_timedelta, last_refreshed, need_update, now)
    
    if need_update:
        print 'Updating CRL URLs of PKIProfile %s' % job_pb.obj_key
        protobuf2model(pki_pb, None, True)
        req = callbacks.new_rpc_req(pki_pb, 'PKIProfile', 'pki_profile')
        PKIProfileService_Stub(RpcChannel()).Update(RpcController(), req)
    else:
        protobuf2model(pki_pb, None, True)

    protobuf2model(job_pb, None, False, skip_unfinished_pb=False)

class PkiProfileJob(PostActionView):
    def do_post_action(self, request, *args, **kwargs):
        response_data = {}
        try:
            job_uuid = kwargs.get('job_uuid')
            process_pkiprofile_job(job_uuid)
            response_data['Success'] = "PkiProfileCrlUpdateJob Successfully Completed for job: %s" % job_uuid
        except Exception as e:
            response_data['Exception'] = str(e)

        return JsonResponse(response_data, status=200)
    