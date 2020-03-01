
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


import base64, logging, os
from rest_framework import status
from rest_framework.response import Response
from api.models_ping_access_agent import PingAccessAgent
from api.models_pool import Pool
from api.models_ssl import PKIProfile, SSLProfile
from api.serializers_ping_access_agent import PingAccessAgentSerializer
from avi.infrastructure.db_transaction import db_transaction
from avi.protobuf.ssl_pb2 import SSLCertificate
from avi.protobuf_json.protobuf_json import pb2json
from avi.rest.error_list import DataException
from avi.rest.pb_utils import get_pb_if_exists
from avi.rest.view_utils import MultipleViewCUD
from avi.rest.views import CreateView, ListView, DetailView
from avi.util.ssl_utils import _load_cert_to_x509_obj, _parse_x509_to_cert_pb

log = logging.getLogger(__name__)

    
def _agent_versions_to_ssl_versions(version):
    switcher = {
        "TLSv1.1": "SSL_VERSION_TLS1_1",
        "TLSv1.2": "SSL_VERSION_TLS1_2",
        "TLSv1": "SSL_VERSION_TLS1",
    }
    return switcher.get(version, "")

def _agent_ciphers_to_ssl_ciphers(cipher):
    switcher = {
        "TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256": "ECDHE-ECDSA-AES128-GCM-SHA256:",
        "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256": "ECDHE-RSA-AES128-GCM-SHA256:",
        "TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA256": "ECDHE-RSA-AES128-CBC-SHA256:",
        "TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA256": "ECDHE-ECDSA-AES128-CBC-SHA256:",
        "TLS_RSA_WITH_AES_128_GCM_SHA256": "AES128-GCM-SHA256:",
        "TLS_RSA_WITH_AES_128_CBC_SHA256": "AES128-CBC-SHA256:",
    }
    return switcher.get(cipher, "")

def _key_value_exists(properties_vars, key):
    v = properties_vars.get(key)
    if v and v.strip():
        return v
    return None

def _create_ssl_profile(properties_vars, agent_name):
    ssl_p = {}
    ssl_p['name'] = agent_name + "_ssl"

    agent_versions = _key_value_exists(properties_vars, 'agent.ssl.protocols')
    if agent_versions is not None:
    	ssl_versions = []
	versions = agent_versions.split(", ")
	for version in versions:
	    myversion = {}
	    myversion['type'] = _agent_versions_to_ssl_versions(version)
	    ssl_versions.append(myversion)
	ssl_p['accepted_versions'] = ssl_versions

    agent_ciphers = _key_value_exists(properties_vars, 'agent.ssl.ciphers')
    if agent_ciphers is not None:
	ssl_ciphers = ""
	ciphers = agent_ciphers.split(",")
	for cipher in ciphers:
	    ssl_ciphers = ssl_ciphers + _agent_ciphers_to_ssl_ciphers(cipher)
	ssl_p['accepted_ciphers'] = ssl_ciphers[:-1] 

    return ssl_p

def _create_pki_profile(properties_vars, agent_name):
    encoded_truststore = _key_value_exists(properties_vars, 'agent.engine.configuration.bootstrap.truststore')
    if encoded_truststore is None:
        return {}

    pki_p = {}
    cert_pb = SSLCertificate()
    pki_p['name'] = agent_name + "_pki"
    pki_p['crl_check'] = False

    cert_s = base64.b64decode(encoded_truststore)
    cert_obj = _load_cert_to_x509_obj(cert_s)
    _parse_x509_to_cert_pb(cert_s, cert_obj, cert_pb)
    certs = []
    certs.append(pb2json(cert_pb))
    pki_p['ca_certs'] = certs
    return pki_p


def _create_pool(properties_vars, agent_name):
    pool = {}
    pool['name'] = agent_name + "_pool"
    pool['max_concurrent_connections_per_server'] = properties_vars['agent.engine.configuration.maxConnections']
    pool['server_timeout'] = properties_vars['agent.engine.configuration.timeout']
    pool['default_server_port'] = 3030
    
    primary_svr = properties_vars['agent.engine.configuration.host'] + ":" + properties_vars['agent.engine.configuration.port']
    all_srvs = primary_svr
    svr_reselect = False
    failover_hosts = _key_value_exists(properties_vars, 'agent.engine.configuration.failover.hosts')
    if failover_hosts is not None:
        all_srvs = all_srvs + "," + failover_hosts
        svr_reselect = True
    if all_srvs.endswith(","):
        all_srvs = all_srvs[:-1]
    servers = []
    ip_ports = all_srvs.split(",")
    for ip_port in ip_ports:
        myserver = {}
        ip, port = ip_port.split(":")
        myserver['port'] = port
        myserver_ip = {}
        myserver_ip['type'] = "V4"
        myserver_ip['addr'] = ip
        myserver['ip'] = myserver_ip
        servers.append(myserver)
    pool['servers'] = servers

    if svr_reselect:
        server_reselect = {}
        server_reselect['enabled'] = True
        server_reselect['retry_nonidempotent'] = False
	failover_retries = _key_value_exists(properties_vars, 'agent.engine.configuration.failover.maxRetries')
	if failover_retries is not None:
            server_reselect['num_retries'] = failover_retries
        failover_timeout = _key_value_exists(properties_vars, 'agent.engine.configuration.failover.failedRetryTimeout')
        if failover_timeout is not None:
            server_reselect['retry_timeout'] = failover_timeout
        pool['server_reselect'] = server_reselect

    pool['ssl_profile_ref'] = "/api/sslprofile/?name=" + agent_name + "_ssl"
    pool['pki_profile_ref'] = "/api/pkiprofile/?name=" + agent_name + "_pki"
    hms = ["/api/healthmonitor/?name=System-PingAccessAgent"]
    pool['health_monitor_refs'] = hms
    return pool, primary_svr

def _create_ping_agent(properties, primary_server, agent_name):
    ping = {}
    ping['name'] = agent_name
    ping['pingaccess_pool_ref'] = "/api/pool/?name=" + agent_name + "_pool"
    ping['properties_file_data'] = properties
    primary_svr = {}
    ip, port = primary_server.split(":")
    primary_svr['port'] = port
    primary_svr_ip= {}
    primary_svr_ip['type'] = "V4"
    primary_svr_ip['addr'] = ip
    primary_svr['ip'] = primary_svr_ip
    ping['primary_server'] = primary_svr
    return ping

def create_ping_subobjects(properties, agent_name):
    obj_list = []
    properties = os.linesep.join([s for s in properties.splitlines() if s])
    properties_vars = {}
    pairs = properties.split("\n")
    for p in pairs:
        var, val = p.split("=", 1)
        properties_vars[var] = val
    pki_profile = _create_pki_profile(properties_vars, agent_name)
    obj_list.append({'model_name': 'pkiprofile', 'data': pki_profile})
    ssl_profile = _create_ssl_profile(properties_vars, agent_name)
    obj_list.append({'model_name': 'sslprofile', 'data': ssl_profile})
    pool, primary_svr = _create_pool(properties_vars, agent_name)
    obj_list.append({'model_name': 'pool', 'data': pool})
    ping_agent = _create_ping_agent(properties, primary_svr, agent_name)
    obj_list.append({'model_name': 'pingaccessagent', 'data': ping_agent})
    log.info(obj_list)
    return obj_list


class PingAccessAgentList(CreateView, ListView, ):
    macro_view = None
    model = PingAccessAgent
    serializer_class = PingAccessAgentSerializer
    rpc_data = {
        
        'post': {
            'class_name': 'PingAccessAgent',
            'method_name': 'Create',
            'field_name': 'ping_access_agent',
            'service_name': 'PingAccessAgentService_Stub',
            'module': 'avi.protobuf.ping_access_agent_pb2'
        },
            }

    
    @db_transaction
    def do_post_transaction(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        properties = request.DATA.get('properties_file_data')
        name = request.DATA.get('name')
        if PingAccessAgent.objects.filter(name=name, tenant_ref=self.tenant).exists():
            raise DataException('PingAccessAgent with this Name, Tenant ref already exists')
        ping_objects = create_ping_subobjects(properties, name)
        self.macro_view = MultipleViewCUD(request)
        rsp = self.macro_view.process_list_no_txn('post', self.tenant, ping_objects, request.user)
        return Response(rsp[-1], status=status.HTTP_201_CREATED)

    def run_callback(self):
        if self.macro_view:
            self.macro_view.run_callback()
        else:
            super(PingAccessAgentList, self).run_callback()

    
    

class PingAccessAgentDetail(DetailView):
    macro_view = None
    model = PingAccessAgent
    serializer_class = PingAccessAgentSerializer
    rpc_data = {
        
        'patch': {
            'class_name': 'PingAccessAgent',
            'method_name': 'Update',
            'field_name': 'ping_access_agent',
            'service_name': 'PingAccessAgentService_Stub',
            'module': 'avi.protobuf.ping_access_agent_pb2'
        },
        
        'delete': {
            'class_name': 'PingAccessAgent',
            'method_name': 'Delete',
            'field_name': 'ping_access_agent',
            'service_name': 'PingAccessAgentService_Stub',
            'module': 'avi.protobuf.ping_access_agent_pb2'
        },
            }


    @db_transaction
    def do_delete_transaction(self, request, *args, **kwargs):
        self.check_tenant(request, args, kwargs)
        self.check_user(request, args, kwargs)
        self.macro_view = MultipleViewCUD(request)
        macro_lst = [{'model_name': 'PingAccessAgent', 'data': {'uuid': kwargs['slug']}}]
        paa_pb = PingAccessAgent.objects.get(uuid=kwargs['slug']).protobuf()
        pool_pb = get_pb_if_exists(Pool, paa_pb.pingaccess_pool_uuid)
        if pool_pb:
            macro_lst.append({'model_name': 'Pool', 'data': {'uuid': pool_pb.uuid}})
            ssl_pb = get_pb_if_exists(SSLProfile, pool_pb.ssl_profile_uuid)
            pki_pb = get_pb_if_exists(PKIProfile, pool_pb.pki_profile_uuid)
            if pki_pb and pki_pb.name.startswith(paa_pb.name):
                macro_lst.append({'model_name': 'PKIProfile', 'data': {'uuid': pki_pb.uuid}})
            if ssl_pb and ssl_pb.name.startswith(paa_pb.name):
                macro_lst.append({'model_name': 'SSLProfile', 'data': {'uuid': ssl_pb.uuid}})

        rsp = self.macro_view.process_list_no_txn('delete', self.tenant, macro_lst, self.request.user)
        return Response(rsp, status=204)


    def run_callback(self):
        if self.macro_view:
            self.macro_view.run_callback()
        else:
            super(PingAccessAgentDetail, self).run_callback()

