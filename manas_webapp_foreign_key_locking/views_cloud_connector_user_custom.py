
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

"""
==========================
Cloud Connector User Views
==========================
"""
import os
import uuid
import subprocess32 as subprocess
import shlex
import json
from tempfile import NamedTemporaryFile
from rest_framework.response import Response
from api.models import SystemConfiguration
from avi.util.ssl_utils import decrypt_string
from avi.util.pb_sensitive import SENSITIVE_TAG
from avi.util.linux_host import test_linux_host_install, cleanup_linux_host
from avi.util.cluster_info import management_ip
from avi.rest.views import (ListView, CreateView, DetailView, PostActionView)
from avi.rest.error_list import ServerException, DataException
from api.models import CloudConnectorUser, CloudConnectorUserSerializer

def _generate_user_key(data):
    if data.get('private_key'):
        if not data.get('public_key'):
            private_file = NamedTemporaryFile(delete=False)
            private_file.write(data.get('private_key'))
            private_file.close()
            public_file = NamedTemporaryFile()
            passphrase = data.get('passphrase')
            if passphrase:
                cmd = ('ssh-keygen -p -P "%s" -N "" -f %s' %
                            (passphrase, private_file.name))
                rsp = subprocess.call(shlex.split(cmd))
                if rsp != 0:
                    raise DataException('Fail to parse this private key with given passphrase')
                with open(private_file.name, 'r') as f:
                    data['private_key'] = f.read()

            cmd = ('ssh-keygen -y -f %s -P ""' % private_file.name)
            try:
                data['public_key'] = subprocess.check_output(shlex.split(cmd))
            except subprocess.CalledProcessError:
                raise DataException('Fail to generate public key from private key input')
            os.unlink(private_file.name)
    elif not data.get('password'):
        # generating key-pair for the case of no password and no private key
        tmp_file = NamedTemporaryFile()
        tmp_file.close()
        path = tmp_file.name
        cmd = 'ssh-keygen -t rsa -q -f %s -N ""' % path
        subprocess.call(shlex.split(cmd))
        with open(path, 'r') as f:
            data['private_key'] = f.read()
        with open(path+'.pub', 'r') as f:
            data['public_key']  = f.read()
        os.unlink(path)
    if not data.get('public_key') and not data.get('password')  and not data.get('azure_userpass') and not data.get('azure_serviceprincipal'):
        raise DataException('Public key data is missing')
    if (data.get('azure_userpass') or data.get('azure_serviceprincipal')) and data.get('password'):
        raise DataException('password cannot be set for azure credentials')


class CloudConnectorUserListView(ListView, CreateView):
    model = CloudConnectorUser
    serializer_class = CloudConnectorUserSerializer

    INTERNAL_USERS = ['aviseuser', 'avictlruser', 'admin', 'cli']
    def do_post_list(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)

        username = request.DATA.get('name', '')
        if not username:
             raise DataException("name is not specified")
        if username in self.INTERNAL_USERS:
             raise DataException("Modification of credentials of internal users not allowed")

        data = request.DATA
        _generate_user_key(data)
        rsp = super(CloudConnectorUserListView, self).do_post_list(request, *args, **kwargs)

        return rsp


class CloudConnectorUserDetailView(DetailView):
    model = CloudConnectorUser
    serializer_class = CloudConnectorUserSerializer

    def do_put_detail(self, request, *args, **kwargs):
        """
        Update old key files
        """
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        data = request.DATA
        username = data.get('name', '')
        old_obj = self.model.objects.filter(uuid=kwargs.get('slug'))
        if old_obj and data.get('private_key', None) == SENSITIVE_TAG:
            private_key = old_obj[0].protobuf().private_key
            if private_key:
                data['private_key'] = decrypt_string(private_key)
        _generate_user_key(data)

        return super(CloudConnectorUserDetailView, self).do_put_detail(request,
                                                             *args, **kwargs)


class CloudConnectorUserTestView(PostActionView):
    model = CloudConnectorUser
    serializer_class = CloudConnectorUserSerializer

    def post(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        data = request.DATA
        s = SystemConfiguration.objects.get().protobuf()
        https_port = s.portal_configuration.https_port
        mgmt_ip = management_ip()
        port = ":%s" % https_port if https_port else ""
        controller = "https://%s%s" % (mgmt_ip, port)
        user = self.model.objects.filter(uuid=kwargs.get('slug'))[0]
        private_key = decrypt_string(user.protobuf().private_key) if user.protobuf().private_key else None
        password = decrypt_string(user.protobuf().password) if user.protobuf().password else None
        resp = test_linux_host_install(data['host'], user.name, private_key, controller, password)
        return Response(status=200, data=resp)


class CloudConnectorUserCleanupView(PostActionView):
    model = CloudConnectorUser
    serializer_class = CloudConnectorUserSerializer

    def post(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        data = request.DATA
        s = SystemConfiguration.objects.get().protobuf()
        https_port = s.portal_configuration.https_port
        mgmt_ip = management_ip()
        port = ":%s" % https_port if https_port else ""
        controller = "https://%s%s" % (mgmt_ip, port)
        user = self.model.objects.filter(uuid=kwargs.get('slug'))[0]
        private_key = decrypt_string(user.protobuf().private_key) if user.protobuf().private_key else None
        password = decrypt_string(user.protobuf().password) if user.protobuf().password else None
        resp = cleanup_linux_host(data['host'], user.name, private_key, controller, password)
        return Response(status=200, data=resp)
