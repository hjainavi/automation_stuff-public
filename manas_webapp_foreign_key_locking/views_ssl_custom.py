
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
from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response
from api.models_ssl import PKIProfile, SSLKeyAndCertificate, CertificateManagementProfile
from api.serializers_ssl import (PKIProfileSerializer, SSLKeyAndCertificateSerializer)
from avi.infrastructure.db_transaction import db_transaction
from avi.rest.views import (CreateView, UpdateView, ListView,
                            RetrieveView, DeleteView, GetActionView)
from avi.protobuf_json.protobuf_json import pb2json, json2pb
from avi.protobuf.common_pb2 import (WRITE_ACCESS,
                                      READ_ACCESS)
from avi.protobuf.django_internal_pb2 import PERMISSION_SSLKEYANDCERTIFICATE
from avi.protobuf.ssl_pb2 import (
                                  PKIProfile as PKIProfileProto,
                                  SSLKeyAndCertificate
                                  as SSLKeyAndCertificateProto,
                                  SSLProfile as SSLProfileProto,
                                 )
from avi.util.config_log import add_ssl_export_log
from avi.util.protobuf import dict2protobuf, protobuf2dict
from avi.util.ssl_utils import ( validate_keyandcert, decode_base64_string,
                                parse_pki, print_ssl,
                                calculate_ssl_profile_rating, encrypt_ssl_pb,
                                update_ssl_ref_links, parse_chain_PEM_ssl,
                                renew_management_profile_ssl_certificate,
                                encrypt_private_key_with_passphrase)
from avi.util.pb_post_save_transform import pb_message_post_save_transform
from avi.rest.pb2model import protobuf2model, ModelCreateDisallowed
from avi.rest.json_db_utils import transform_json_refs_to_uuids
from avi.rest.pb_utils import get_pb_from_name_if_exists, get_pb_if_exists
from avi.rest.error_list import DataException, ServerException
from avi.rest.mixins import MixinBase
from avi.rest.db_cache import DbCache
from django.core.exceptions import ObjectDoesNotExist


log = logging.getLogger(__name__)


class CommonCertificateView(MixinBase):

    def handle_ca_certs(self, ssl_pb, tenant):
        log.info('In CommonCertificateView handle_ca_certs')
        ca_ssls = parse_chain_PEM_ssl(ssl_pb)
        new_uuids = []
        new_uuids.append(ssl_pb.uuid)

        #skip the ca certs that already there
        ca_names = [ssl.name for ssl in ca_ssls]
        existed_ca_names = SSLKeyAndCertificate.objects.filter(name__in=ca_names,
                        tenant_ref=tenant).values_list('name', flat=True)
        new_ca_ssls = []
        #save the new ones
        for ca_ssl in ca_ssls:
            if ca_ssl.name in existed_ca_names:
                continue
            new_ca_ssls.append(ca_ssl)
            ca_ssl.tenant_uuid = tenant.uuid
            ca_ssl_row, _ = protobuf2model(ca_ssl, None, False,
                                           skip_unfinished_pb=False,
                                           raise_serializer_error=True)
            new_uuids.append(ca_ssl_row.uuid)
            ca_ssl.uuid = ca_ssl_row.uuid
        return new_uuids, new_ca_ssls

    def update_certs(self, new_ssl, ca_ssls, new_uuids, tenant, is_renewal=False):
        log.info('In CommonCertificateView update_certs')
        ssl_objs = SSLKeyAndCertificate.objects.filter(
                                tenant_ref=tenant).exclude(uuid__in=new_uuids)

        self.ssl_nodes = []
        for ssl_obj in ssl_objs:
            ssl_pb = ssl_obj.protobuf()
            self.ssl_nodes.append({'pb': ssl_pb, 'modify': False, 'rpc_create': False})

        self.ssl_nodes.append({'pb': new_ssl, 'modify':is_renewal, 'rpc_create': not is_renewal})

        for ca_pb in ca_ssls:
            self.ssl_nodes.append({'pb': ca_pb, 'modify':False, 'rpc_create': True})

        update_ssl_ref_links(self.ssl_nodes)

        #save all the modify objs to db
        for node in self.ssl_nodes:
            if node.get('modify'):
                pb = node['pb']
                ssl_row, _ = protobuf2model(pb, None, False,
                                            skip_unfinished_pb=False,
                                            raise_serializer_error=True)

        return self.ssl_nodes

    def run_callback(self):
        """
        Send RPC Create or Update for all the new or updated ssl objects
        """
        log.info('In CommonCertificateView run_callback')
        if self.initial_data:
            return

        for node in self.ssl_nodes:
            pb = node['pb']
            if node.get('rpc_create'):
                method_name = 'post'
            elif node.get('modify'):
                method_name = 'put'
            else:
                continue
            pb_message_post_save_transform(pb)
            self.callback_custom_pre(pb, method_name, None)
            self.callback(pb, method_name, pb_transform=False)
            self.callback_custom_post(pb, method_name, None)

    def generate_config_event(self, request, serializer_class, ssl_row):
        # Generate config event
        context = {'request': request}
        obj_data = serializer_class(ssl_row, context=context).data
        event_data = obj_data.copy()
        if event_data.get('certificate'):
            event_data['certificate'] = event_data.get('certificate').copy()
        self.generate_config_log(request, True, None, event_data)
        return obj_data

class RenewSSLCertificate(CommonCertificateView, UpdateView):
    model = SSLKeyAndCertificate
    serializer_class = SSLKeyAndCertificateSerializer
    rpc_data = {
        'post': {
            'class_name': 'SSLKeyAndCertificate',
            'method_name': 'Update',
            'field_name': 'ssl_key_and_certificate',
            'service_name': 'SSLKeyAndCertificateService_Stub'
        }
    }

    @db_transaction
    def post_transaction(self, request, slug, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)

        ssl_row = SSLKeyAndCertificate.objects.select_for_update().get(uuid=slug)
        ssl_pb = ssl_row.protobuf()

        if not ssl_pb.certificate_management_profile_uuid: # only renew ssl certs that we can  #or not ssl_row.self_signed:
            raise DataException(
                    "Can only renew ssl certificates with management profiles attached")

        certificate_management_profile = get_pb_if_exists(
            CertificateManagementProfile,
            ssl_pb.certificate_management_profile_uuid)
        if not certificate_management_profile:
            raise DataException(
                "CertificateManagementProfile %s does not exist" %
                ssl_pb.certificate_management_profile_uuid)

        ssl_pb = renew_management_profile_ssl_certificate(ssl_pb, certificate_management_profile)
        ssl_pb.tenant_uuid = self.tenant.uuid
        encrypt_ssl_pb(ssl_pb)
        ssl_row, _ = protobuf2model(ssl_pb, None, False,
                                    skip_unfinished_pb=False,
                                    raise_serializer_error=True)
        ssl_pb = ssl_row.protobuf()
        if ssl_pb.certificate.certificate:
            new_uuids, new_ca_ssls = self.handle_ca_certs(ssl_pb, self.tenant)
            self.ssl_nodes = self.update_certs(ssl_pb, new_ca_ssls, new_uuids, self.tenant, is_renewal=True)
        else:
            self.ssl_nodes = []
            self.ssl_nodes.append({'pb': ssl_pb, 'modify':True, 'rpc_create': False})

        # Generate config event
        obj_data = self.generate_config_event(request, self.serializer_class, ssl_row)

        return Response(obj_data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        try:
            self.initial_data = kwargs.get('initial_data', False)
            rsp = self.post_transaction(request, *args, **kwargs)
            self.run_callback()
        except Exception as e:
            self.generate_config_log(request, False, str(e), None)
            raise

        return rsp

def _export_private_key(request, tenant):
    if 'export_key' not in request.QUERY_PARAMS:
        return False
    user = request.user
    if user.is_superuser:
        return True
    for role in map(lambda r: r.role_ref, user.access.filter(Q(tenant_ref=tenant) | Q(all_tenants=True))):
        if not role:
            return False
        role_pb = role.protobuf()
        for p in role_pb.privileges:
            if p.resource == PERMISSION_SSLKEYANDCERTIFICATE:
                if p.type == WRITE_ACCESS:
                    return True

    return False



class SSLKeyAndCertificateListView(CreateView, ListView):
    model = SSLKeyAndCertificate
    serializer_class = SSLKeyAndCertificateSerializer
    rpc_data = {
        'post': {
            'class_name': 'SSLKeyAndCertificate',
            'method_name': 'Create',
            'field_name': 'ssl_key_and_certificate',
            'service_name': 'SSLKeyAndCertificateService_Stub'
        },
        'put': {
            'class_name': 'SSLKeyAndCertificate',
            'method_name': 'Update',
            'field_name': 'ssl_key_and_certificate',
            'service_name': 'SSLKeyAndCertificateService_Stub'
        }
    }

    def update_certs(self, new_ssl):
        ssl_objs = SSLKeyAndCertificate.objects.filter(
                            tenant_ref=self.tenant)

        self.ssl_nodes = []
        for ssl_obj in ssl_objs:
            ssl_pb = ssl_obj.protobuf()
            self.ssl_nodes.append({'pb': ssl_pb, 'modify': False, 'rpc_create': False})
        self.ssl_nodes.append({'pb': new_ssl, 'modify':False, 'rpc_create': True})
        update_ssl_ref_links(self.ssl_nodes)

    def save_callback(self, obj, method_name, old_pb=None):
        # callback data is saved as a part pf post_save in callbacks_custom.
        # Overloading save_callback so that callback_data is not overwritten
        self.callback_data = (self.callback_data, method_name)

    def run_callback(self):
        if self.initial_data:
            return
        (ssl_nodes, method_name) = self.callback_data
        for node in ssl_nodes:
            pb = node['pb']
            if node.get('rpc_create'):
                method_name = 'post'
            elif node.get('modify'):
                method_name = 'put'
            else:
                continue
            pb_message_post_save_transform(pb)
            self.callback_custom_pre(pb, method_name, None)
            self.callback(pb, method_name, pb_transform=False)
            self.callback_custom_post(pb, method_name, None)

    def do_get_list(self, request, *args, **kwargs):
        rsp = super(SSLKeyAndCertificateListView, self).do_get_list(
                                                    request, *args, **kwargs)
        keep_key = _export_private_key(request, self.tenant)
        if keep_key:
            try:
                ssl_uuids = []
                for obj in rsp.data.get('results', []):
                    if obj.get('uuid'):
                        ssl_uuids.append(obj['uuid'])
                add_ssl_export_log(request.user, ssl_uuids,
                                    tenant_uuid=self.tenant.uuid)
            except:
                log.exception('Error when creating event for SSL export')

            for obj_data in rsp.data.get('results', []):
                ssl_pb = SSLKeyAndCertificate.objects.get(uuid=obj_data.get('uuid')).protobuf(decrypt=True)
                if ssl_pb.key:
                    obj_data['key'] = encrypt_private_key_with_passphrase(ssl_pb.key, ssl_pb.key_passphrase)

        return rsp


class SSLKeyAndCertificateDetailView(RetrieveView, UpdateView, DeleteView):
    model = SSLKeyAndCertificate
    serializer_class = SSLKeyAndCertificateSerializer
    rpc_data = {
        'delete': {
            'class_name': 'SSLKeyAndCertificate',
            'method_name': 'Delete',
            'field_name': 'ssl_key_and_certificate',
            'service_name': 'SSLKeyAndCertificateService_Stub'
        },
        'put': {
            'class_name': 'SSLKeyAndCertificate',
            'method_name': 'Update',
            'field_name': 'ssl_key_and_certificate',
            'service_name': 'SSLKeyAndCertificateService_Stub'
        }
    }

    def save_callback(self, obj, method_name, old_pb=None):
        # callback data is saved as a part pf post_save in callbacks_custom.
        # Overloading save_callback so that callback_data is not overwritten
        if method_name == 'delete':
            super(SSLKeyAndCertificateDetailView, self).save_callback(obj, method_name, old_pb)
        elif method_name == 'force_delete':
            self.callback_data = (obj, method_name)
        else:
            self.callback_data = (self.callback_data, method_name)

    def run_callback(self):
        if self.initial_data:
            return

        (ssl_nodes, method_name) = self.callback_data
        if method_name == 'delete':
            super(SSLKeyAndCertificateDetailView, self).run_callback()
        else:
            for node in ssl_nodes:
                pb = node['pb']
                if node.get('rpc_create'):
                    method_name = 'post'
                elif node.get('modify'):
                    method_name = 'put'
                elif node.get('delete'):
                    method_name = 'delete'
                else:
                    continue
                pb_message_post_save_transform(pb)
                self.callback_custom_pre(pb, method_name, None)
                self.callback(pb, method_name, pb_transform=False)
                self.callback_custom_post(pb, method_name, None)


    def do_get_detail(self, request, *args, **kwargs):
        rsp = super(SSLKeyAndCertificateDetailView, self).do_get_detail(
                                                    request, *args, **kwargs)
        keep_key = _export_private_key(request, self.tenant)
        if keep_key:
            try:
                ssl_uuids = [rsp.data.get('uuid', '')]
                add_ssl_export_log(request.user, ssl_uuids,
                                    obj_name=rsp.data.get('name', ''),
                                    tenant_uuid=self.tenant.uuid)
            except:
                log.exception('Error when creating event for SSL export')
            ssl_pb = SSLKeyAndCertificate.objects.get(uuid=rsp.data.get('uuid')).protobuf(decrypt=True)
            if ssl_pb.key:
                rsp.data['key'] = encrypt_private_key_with_passphrase(ssl_pb.key, ssl_pb.key_passphrase)

        return rsp

    def do_delete_detail(self, request, *args, **kwargs):
        existing_ssl_uuids = []
        force_delete = 'force_delete' in kwargs or 'force_delete' in request.QUERY_PARAMS
        if force_delete:
            ssl_refs = []
            slug=kwargs['slug']
            existing_pb = SSLKeyAndCertificate.objects.get(uuid=slug).protobuf()
            db_cache = DbCache()
            connected_models = [o.model_name for o in db_cache.get_parents('SSLKeyAndCertificate', slug=slug, depth=1)]
            if connected_models.count('SSLKeyAndCertificate') != len(connected_models):
                raise DataException('Cannot force_delete this SSLKeyAndCertificate as it is in use by other objects')
            ssl_refs.extend(db_cache.get_parents('SSLKeyAndCertificate', slug=slug, model_filter=['SSLKeyAndCertificate']))
            ssl_refs.extend(db_cache.get_children('SSLKeyAndCertificate', slug=slug, model_filter=['SSLKeyAndCertificate']))
            existing_ssl_uuids = [ref.uuid for ref in ssl_refs]


        rsp = super(SSLKeyAndCertificateDetailView, self).do_delete_detail(request, *args, **kwargs)

        if force_delete and existing_ssl_uuids:
            ssl_objs = SSLKeyAndCertificate.objects.filter(uuid__in=existing_ssl_uuids)
            ssl_nodes = []
            for ssl_obj in ssl_objs:
                ssl_pb = ssl_obj.protobuf()
                ssl_nodes.append({'pb':ssl_pb, 'modify': False, 'rpc_create': False})
            update_ssl_ref_links(ssl_nodes)

            for node in ssl_nodes:
                if node.get('modify'):
                    pb = node['pb']
                    try:
                        ssl_row, is_created = protobuf2model(pb, None, True,
                            skip_unfinished_pb=False,
                            raise_serializer_error=True)
                    except ObjectDoesNotExist:
                        log.error('ObjectDoesNotExist error when updating cert '
                            'chain. Ignoring exception')
                    except ModelCreateDisallowed:
                        log.error('ModelCreateDisallowed error when updating cert '
                            'chain. Ignoring exception.')
            ssl_nodes.append({'pb':existing_pb, 'delete': True, 'rpc_create': False})
            self.save_callback(ssl_nodes, 'force_delete')
        return rsp

class ValidateSSL(CreateView):
    model = SSLKeyAndCertificate

    def post(self, request, *args, **kwargs):
        ssl_input = request.DATA.get('key')
        passphrase = request.DATA.get('key_passphrase')
        cert_s = request.DATA.get('certificate')
        base64 = request.DATA.get('base64', False)
        key_base64 = request.DATA.get('key_base64', False)
        if ssl_input and (base64 or key_base64):
            ssl_input = decode_base64_string(ssl_input)
        if cert_s and request.DATA.get('certificate_base64', False):
            cert_s = decode_base64_string(cert_s)

        if ssl_input:
            ssl_pb = validate_keyandcert(ssl_input, passphrase, cert_s=cert_s)
        elif cert_s:
            cert_pb = print_ssl(cert_s, None, 'cert', exp_err=True)
            ssl_pb = SSLKeyAndCertificateProto()
            ssl_pb.certificate.CopyFrom(cert_pb)
        else:
            raise DataException('No certificate or key input')

        data = pb2json(ssl_pb)

        return Response(data, status=201)

class PrintSSL(CreateView):
    """
    Return the openssl text of certificate or CRL
    """
    def post(self, request, *args, **kwargs):
        data = {}
        obj_type = request.DATA.get('type', 'cert')
        obj_s = request.DATA.get('body', '')
        if obj_s:
            obj_s = decode_base64_string(obj_s)
        url = request.DATA.get('url', None)
        pb = print_ssl(obj_s, url, obj_type)
        data = protobuf2dict(pb)
        return Response(data)

class PKIProfileListView(CreateView, ListView):
    model = PKIProfile
    serializer_class = PKIProfileSerializer
    rpc_data = {
        'post': {
            'class_name': 'PKIProfile',
            'method_name': 'Create',
            'field_name': 'pki_profile',
            'service_name': 'PKIProfileService_Stub'
        }
    }

    @db_transaction
    def do_post_transaction(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)

        self.initial_data = kwargs.get('initial_data', False)

        pki_pb = PKIProfileProto()
        dict2protobuf(request.DATA, pki_pb)
        parse_pki(pki_pb)
        pki_pb.tenant_uuid = self.tenant.uuid
        pki_row, _ = protobuf2model(pki_pb, None, False,
                                    skip_unfinished_pb=False,
                                    raise_serializer_error=True)
        new_pb = pki_row.protobuf()
        self.semantic_check(request_pb=new_pb, existing_pb=None)
        self.save_callback(pki_row, 'post')
        context = {'request': request}
        obj_data = self.serializer_class(pki_row, context=context).data
        self._set_default_obj(new_pb)
        self.generate_config_log(request, True, None, obj_data)
        return Response(obj_data,
                             status=status.HTTP_201_CREATED)


class PKIProfileDetailView(RetrieveView, DeleteView, UpdateView, ):
    model = PKIProfile
    serializer_class = PKIProfileSerializer
    rpc_data = {
        'post': {
            'class_name': 'SSLKeyAndCertificate',
            'method_name': 'Create',
            'field_name': 'ssl_key_and_certificate',
            'service_name': 'SSLKeyAndCertificateService_Stub'
        },
        'put': {
            'class_name': 'PKIProfile',
            'method_name': 'Update',
            'field_name': 'pki_profile',
            'service_name': 'PKIProfileService_Stub'
        },
        'delete': {
            'class_name': 'PKIProfile',
            'method_name': 'Delete',
            'field_name': 'pki_profile',
            'service_name': 'PKIProfileService_Stub'
        }
    }

    @db_transaction
    def do_put_transaction(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)

        self.initial_data = kwargs.get('initial_data', False)

        uuid = kwargs.get('slug')
        pki_obj = PKIProfile.objects.select_for_update().get(uuid=uuid)

        pki_pb = PKIProfileProto()
        dict2protobuf(request.DATA, pki_pb)
        pki_pb.uuid = uuid
        parse_pki(pki_pb)
        if not pki_pb.HasField('tenant_uuid'):
            pki_pb.tenant_uuid = pki_obj.tenant_ref.uuid

        pki_row, _ = protobuf2model(pki_pb, None, False,
                                    skip_unfinished_pb=False,
                                    raise_serializer_error=True)
        new_pb = pki_row.protobuf()
        self.semantic_check(request_pb=new_pb, existing_pb=pki_obj.protobuf())
        self.save_callback(pki_row, 'put')
        context = {'request': request}
        obj_data = self.serializer_class(pki_row, context=context).data
        self.generate_config_log(request, True, None, obj_data)
        return Response(obj_data, status=status.HTTP_200_OK)

class SSLProfileCheck(CreateView):
    """
    Return the input SSLProfile including SSL Ratings
    """
    def post(self, request, *args, **kwargs):
        kwargs['access_mode'] = READ_ACCESS
        self.check_tenant(request, args, kwargs)

        profile_pb = SSLProfileProto()
        transform_json_refs_to_uuids(request.DATA, preserve_uri=True)
        json2pb(profile_pb, request.DATA, replace=True)
        analytics_profile_pb = get_pb_from_name_if_exists('AnalyticsProfile',
                                                    'System-Analytics-Profile')
        if not analytics_profile_pb:
            raise ServerException(
                'Default Analytics Profile System-Analytics-Profile not found')

        calculate_ssl_profile_rating(profile_pb, analytics_profile_pb)

        obj_data = protobuf2dict(profile_pb)
        return Response(obj_data)

class GslbPKIProfileRuntimeView(GetActionView):
    model = PKIProfile
    serializer_class = PKIProfileSerializer
    rpc_data = {'get': {'exclusive': False, 'class_name': 'GslbPKIProfileRuntime', 'service_name': 'GslbPKIProfileRuntimeService_Stub', 'default_filter': 'SUMMARY', 'method_name': 'Read', 'response_field': 'gpki_summary'}}
