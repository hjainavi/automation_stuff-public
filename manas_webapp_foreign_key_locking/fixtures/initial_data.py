
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

import sys
import json
import re
import math
from avi.protobuf.autoscale_mgr_rpc_pb2 import AutoScaleService
from avi.protobuf.cloud_connector_rpc_pb2 import CloudConnectorService
from avi.util.get_default_password import get_default_password
from avi.util.controller_cert import get_controller_ssl_key_cert
from operator import itemgetter
sys.path.insert(1, "/opt/avi/python/lib")
sys.path.append("/opt/avi/python/bin/portal")

"""
==========================
Initial Data Configuration
==========================

Configures the initial set of objects in the system
"""
from avi.alert.alert_objlib import AlertConfigObjs, AlertEmailConfigObjs,\
    AlertSyslogConfigObjs, AlertScriptConfigObjs, ActionGroupConfigObjs,\
    AlertObjectListConfigObjs
from avi.protobuf.events_pb2 import EventId
from avi.rest.pb2dict import protobuf2dict_withrefs
from avi.protobuf.options_pb2 import ACTIONGROUP_HIGH, ACTIONGROUP_LOW, ACTIONGROUP_MEDIUM, \
    ACTIONGROUP_SYSLOG_CONFIG, ACTIONGROUP_SYSLOG_SYSTEM, ACTIONGROUP_SE_GRP_FLAVOR_UPDATE,\
    sysev_alert_options, service_q_name
from avi.protobuf.alerts_pb2 import EVENTS_OBJECT_LIST, METRICS_OBJECT_LIST
from avi.protobuf import alerts_pb2

from api.fixtures.initial_data_templates import APPLICATION_ADMIN, APPLICATION_OPERATOR, \
    TENANT_ADMIN, SYSTEM_ADMIN, SECURITY_ADMIN, WAF_ADMIN

ALERT_EMAIL_CONFIGS = AlertEmailConfigObjs()
ALERT_SYSLOG_CONFIGS = AlertSyslogConfigObjs()
ALERT_SCRIPT_CONFIGS = AlertScriptConfigObjs()
ACTION_GROUP_CONFIGS = ActionGroupConfigObjs()
ROOT_CA_DATA, SECURE_CHANNEL_CERT_DATA = get_controller_ssl_key_cert()


def _data_from_pb(pb_path, pb, method='post'):
    '''
    returns configuration data from the protobuf
    Args:
        @param: pb_path: this is path API needs to use to create this object.
        @param: pb: protobuf representing the configuration.
    '''
    data = {}
    data['path'] = pb_path
    data['method'] = method
    data['data'] = protobuf2dict_withrefs(pb, None, skip_references=True,
                                          slug_is_name=True)
    return data


def _add_system_event_config_objs(original_data_list, tenant_uuid):
    '''
    Args:
        @param: cfg_data_list: list of the configuration data for initial setup
    Return:
        new copy of the default obj list with appended alert config objects
    '''
    cfg_data_list = list(original_data_list)
    if tenant_uuid:
        alert_config_objs = AlertConfigObjs(tenant_uuid=tenant_uuid)
    else:
        alert_config_objs = AlertConfigObjs()

    ac_list = []
    ev_id_desc = EventId.DESCRIPTOR
    for edesc in ev_id_desc.values:
        if not edesc.has_options:
            continue
        foptions = edesc.GetOptions()
        if not foptions or not foptions.HasExtension(sysev_alert_options):
            continue
        sysev_alert_opts = foptions.Extensions[sysev_alert_options]
        if sysev_alert_opts.name not in ac_list:
            ac_list.append(sysev_alert_opts.name)

    for ac_name in ac_list:
        alert_config_pb = alert_config_objs.systemEventConfigObject(ac_name)
        if alert_config_pb:
            cfg_obj = _data_from_pb(alert_config_objs.apiPath(), alert_config_pb)
            cfg_data_list.append(cfg_obj)

    '''
        Special Alerts being configured to send Events to Syslog Server
        by default
    '''
    alert_config_pb = alert_config_objs.autoAlertConfigObject('Syslog-Config-Events')
    if alert_config_pb:
        cfg_obj = _data_from_pb(alert_config_objs.apiPath(), alert_config_pb)
        cfg_data_list.append(cfg_obj)

    alert_config_pb = alert_config_objs.autoAlertConfigObject('Syslog-System-Events')
    if alert_config_pb:
        cfg_obj = _data_from_pb(alert_config_objs.apiPath(), alert_config_pb)
        cfg_data_list.append(cfg_obj)

    '''
    alertobjectlist contains the list of objects for which
    alerts can be configured. The list is different for events and
    metrics
    '''
    object_list_config_objs = AlertObjectListConfigObjs(tenant_uuid=tenant_uuid)
    cfg_pb = object_list_config_objs.configObject(EVENTS_OBJECT_LIST)
    if cfg_pb:
        cfg_obj = _data_from_pb(object_list_config_objs.apiPath(), cfg_pb)
        cfg_data_list.append(cfg_obj)
    cfg_pb = object_list_config_objs.configObject(METRICS_OBJECT_LIST)
    if cfg_pb:
        cfg_obj = _data_from_pb(object_list_config_objs.apiPath(), cfg_pb)
        cfg_data_list.append(cfg_obj)

    return cfg_data_list


def _get_aws_flavor_regex():
    '''
    Filter the instances of type C, M, R and T in AWS.
    '''
    return '[ctmr][0-9]+[n]?\..*'


def _get_aws_flavor_data():
    fname = '/opt/avi/python/bin/cloud_connector/aws/data/instances.json'
    with open(fname) as file:
        flavors = json.load(file)
    flvs = list()
    for f in flavors:
        ftype = f['instance_type']
        fdisk = f['storage']['size'] if f['storage'] else 0
        fmem  = f['memory']
        # Ignore instances that don't match regex filter
        if not re.match(_get_aws_flavor_regex(), ftype):
            continue
        # Ignore instances of previous generation
        gen = f['generation']
        if gen != 'current':
            continue
        # filter out ineligible flavors
        mindisk = max(math.ceil(fmem * 2 + 5), 10)
        if fmem < 1 or (fdisk and fdisk < mindisk):
            continue
        flv   = {'id': ftype, 'name': ftype,
                 'max_nics': f['vpc']['max_enis'],
                 'max_ips_per_nic': f['vpc']['ips_per_eni'],
                 'cost': f['pricing']['us-east-1']['linux'],
                 'ram_mb': f['memory']*1024, 'disk_gb': fdisk, 'vcpus': f['vCPU']}
        flvs.append(flv)
    # Sort by cost
    flvs.sort(key=itemgetter('cost'))
    return flvs

DATA_LIST = [
    {'path': '/api/cloud',
     'method': 'post',
     'data': {
         "name": 'Default-Cloud',
         "vtype": "CLOUD_NONE"
     }
     },
    {'path': '/api/stringgroup',
     'method': 'post',
     'data': {
         "name": "System-Compressible-Content-Types",
         "kv": [
             {
                 "key": "text/html"
             },
             {
                 "key": "text/xml"
             },
             {
                 "key": "text/plain"
             },
             {
                 "key": "text/css"
             },
             {
                 "key": "text/javascript"
             },
             {
                 "key": "application/javascript"
             },
             {
                 "key": "application/x-javascript"
             },
             {
                 "key": "application/xml"
             },
             {
                 "key": "application/pdf"
             },
         ]
     }
     },
    {'path': '/api/stringgroup',
     'method': 'post',
     'data': {
         "name": "System-Devices-Mobile",
         "kv": [
             {
                 "key": "iPhone"
             },
             {
                 "key": "iPod"
             },
             {
                 "key": "Android"
             },
             {
                 "key": "BB10"
             },
             {
                 "key": "BlackBerry"
             },
             {
                 "key": "webOS"
             },
             {
                 "key": "IEMobile"
             },
             {
                 "key": "iPad"
             },
             {
                 "key": "PlayBook"
             },
             {
                 "key": "Xoom"
             },
             {
                 "key": "P160U"
             },
             {
                 "key": "SCH-I800"
             },
             {
                 "key": "Nexus 7"
             },
             {
                 "key": "Touch"
             },
         ]
     }
     },
    {'path': '/api/stringgroup',
     'method': 'post',
     'data': {
         "name": "System-Cacheable-Resource-Types",
         "kv": [
             {
                 "key": "image/.*"
             },
             {
                 "key": "text/css"
             },
             {
                 "key": ".*/javascript"
             },
             {
                 "key": "application/x-javascript"
             },
             {
                 "key": "application/pdf"
             },
         ]
     }
     },
    {'path': '/api/stringgroup',
     'method': 'post',
     'data': {
         "name": "System-Rewritable-Content-Types",
         "kv": [
             {
                 "key": "text/html"
             },
             {
                 "key": "text/plain"
             },
             {
                 "key": "text/javascript"
             },
             {
                 "key": "text/uri-list"
             },
             {
                 "key": "text/xml"
             },
         ]
     }
     },
    {'path': '/api/networkprofile',
     'method': 'post',
     'data': {
         'name': 'System-TCP-Proxy',
         'profile': {
             'type': 'PROTOCOL_TYPE_TCP_PROXY',
             'tcp_proxy_profile': {
                 'automatic': True,
             }
         }
     }
    },
    {'path': '/api/networkprofile',
     'method': 'post',
     'data': {
         'name': 'System-TCP-Fast-Path',
         'profile': {
             'type': 'PROTOCOL_TYPE_TCP_FAST_PATH',
             'tcp_fast_path_profile': {
                 'session_idle_timeout': 300,
                 'enable_syn_protection': False,
             }
         }
     }
    },
    {'path': '/api/networkprofile',
     'method': 'post',
     'data': {
         'name': 'System-UDP-Fast-Path',
         'profile': {
             'type': 'PROTOCOL_TYPE_UDP_FAST_PATH',
             'udp_fast_path_profile': {
                 'per_pkt_loadbalance': 0,
                 'snat' : 1
             }
         }
     }
    },
    {'path': '/api/networkprofile',
     'method': 'post',
     'data': {
         'name': 'System-UDP-Per-Pkt',
         'profile': {
             'type': 'PROTOCOL_TYPE_UDP_FAST_PATH',
             'udp_fast_path_profile': {
                 'per_pkt_loadbalance': 1,
                 'snat' : 1
             }
         }
     }
    },
    {'path': '/api/networkprofile',
     'method': 'post',
     'data': {
         'name': 'System-UDP-No-SNAT',
         'profile': {
             'type': 'PROTOCOL_TYPE_UDP_FAST_PATH',
             'udp_fast_path_profile': {
                 'snat' : 0
             }
         }
     }
    },
    {'path': '/api/applicationprofile',
     'method': 'post',
     'data': {
         'name': 'System-Secure-HTTP',
         'type': 'APPLICATION_PROFILE_TYPE_HTTP',
         'http_profile': {
             'connection_multiplexing_enabled': True,
             'ssl_everywhere_enabled': True,
             'hsts_enabled': True,
             'secure_cookie_enabled': True,
             'httponly_enabled': True,
             'http_to_https': True,
             'server_side_redirect_to_https': True,
             'x_forwarded_proto_enabled': True,
             'compression_profile': {
                 'compression': False,
                 'type': 'AUTO_COMPRESSION',
                 'remove_accept_encoding_header': True,
                 'compressible_content_ref': '/api/stringgroup?name=System-Compressible-Content-Types'
             },
             'cache_config': {
                 'enabled': False,
                 'mime_types_group_refs': ['/api/stringgroup?name=System-Cacheable-Resource-Types']
             }
         }
     }
     },
    {'path': '/api/applicationprofile',
     'method': 'post',
     'data': {
         'name': 'System-HTTP',
         'type': 'APPLICATION_PROFILE_TYPE_HTTP',
         'http_profile': {
             'connection_multiplexing_enabled': True,
             'compression_profile': {
                 'compression': False,
                 'type': 'AUTO_COMPRESSION',
                 'remove_accept_encoding_header': True,
                 'compressible_content_ref': '/api/stringgroup?name=System-Compressible-Content-Types'
             },
             'cache_config': {
                 'enabled': False,
                 'mime_types_group_refs': ['/api/stringgroup?name=System-Cacheable-Resource-Types']
             }
         }
     }
     },
    {'path': '/api/applicationprofile',
     'method': 'post',
     'data': {
         'name': 'System-SSL-Application',
         'type': 'APPLICATION_PROFILE_TYPE_SSL',
     }
     },
    {'path': '/api/applicationprofile',
     'method': 'post',
     'data': {
         'name': 'System-L4-Application',
         'type': 'APPLICATION_PROFILE_TYPE_L4',
     }
     },
    {'path': '/api/applicationprofile',
     'method': 'post',
     'data': {
         'name': 'System-Syslog',
         'type': 'APPLICATION_PROFILE_TYPE_SYSLOG',
     }
     },
    {'path': '/api/applicationprofile',
     'method': 'post',
     'data': {
         'name': 'System-DNS',
         'type': 'APPLICATION_PROFILE_TYPE_DNS',
     }
     },
    {'path': '/api/analyticsprofile',
     'method': 'post',
     'data': {
         'name': 'System-Analytics-Profile',
         'exclude_tcp_reset_as_error': True,
         'exclude_client_close_before_request_as_error': True,
         'exclude_http_error_codes': [ 475 ]
        }
     },
    {'path': '/api/role',
     'method': 'post',
     'data': APPLICATION_ADMIN
     },
    {'path': '/api/role',
     'method': 'post',
     'data': TENANT_ADMIN
     },
    {'path': '/api/role',
     'method': 'post',
     'data': SYSTEM_ADMIN
     },
    {'path': '/api/role',
     'method': 'post',
     'data': APPLICATION_OPERATOR
     },
    {'path': '/api/role',
     'method': 'post',
     'data': SECURITY_ADMIN
     },
    {'path': '/api/role',
     'method': 'post',
     'data': WAF_ADMIN
     },
    {'path': '/api/useraccountprofile',
     'method': 'post',
     'data' :  {
         "name" : "Default-User-Account-Profile",
         "max_password_history_count": 0,
         "max_login_failure_count" : 20,
         "account_lock_timeout" : 30,
         "max_concurrent_sessions" : 0,
         "credentials_timeout_threshold" : 0
         }
    },
    {'path': '/api/useraccountprofile',
     'method': 'post',
     'data' :  {
         "name" : "No-Lockout-User-Account-Profile",
         "max_password_history_count": 0,
         "max_login_failure_count" : 0,
         "account_lock_timeout" : 30,
         "max_concurrent_sessions" : 0,
         "credentials_timeout_threshold" : 0
         }
    },
    {'path': '/api/user/user-1',
     'method': 'put',
     'data': {
         "username": "admin",
         "password": get_default_password(),
         "full_name": "System Administrator",
         "is_active": True,
         "is_superuser": True,
         "default_tenant_ref": "/api/tenant/admin",
         "access": [
             {
                 "role_ref": "/api/role?name=System-Admin",
                 "tenant_ref": "/api/tenant/admin"
             },
             {
                 "role_ref": "/api/role?name=Tenant-Admin",
                 "all_tenants": True
             }
         ],
         "user_profile_ref" : "/api/useraccountprofile?name=Default-User-Account-Profile",
         }
    },
    {'path': '/api/user',
     'method': 'post',
     'data': {
         "username": "avisystemuser",
         "full_name": "Avi System User",
         "is_active": True,
         "is_superuser": True,
         "default_tenant_ref": "/api/tenant/admin",
         "access": [
             {
                 "role_ref": "/api/role?name=System-Admin",
                 "tenant_ref": "/api/tenant/admin"
             }
         ],
         "user_profile_ref" : "/api/useraccountprofile?name=No-Lockout-User-Account-Profile",
         }
    },
    {'path': '/api/debugcontroller',
     'method': 'post',
     'data': {
         "name": "task_queue_debug",
         "sub_module": "TASK_QUEUE_DEBUG",
         "trace_level": "TRACE_LEVEL_ERROR",
         "log_level": "LOG_LEVEL_ERROR",
     }
     },
    {'path': '/api/debugcontroller',
     'method': 'post',
     'data': {
         "name": "rpc_infra_debug",
         "sub_module": "RPC_INFRA_DEBUG",
         "trace_level": "TRACE_LEVEL_ERROR",
         "log_level": "LOG_LEVEL_ERROR",
     }
     },
    {'path': '/api/debugcontroller',
     'method': 'post',
     'data': {
         "name": "job_mgr_debug",
         "sub_module": "JOB_MGR_DEBUG",
         "trace_level": "TRACE_LEVEL_ERROR",
         "log_level": "LOG_LEVEL_ERROR",
     }
     },
    {'path': '/api/debugcontroller',
     'method': 'post',
     'data': {
         "name": "transaction_debug",
         "sub_module": "TRANSACTION_DEBUG",
         "trace_level": "TRACE_LEVEL_ERROR",
         "log_level": "LOG_LEVEL_ERROR",
     }
     },
    {'path': '/api/debugcontroller',
     'method': 'post',
     'data': {
         "name": "virtualservice_debug",
         "sub_module": "VIRTUALSERVICE_DEBUG",
         "trace_level": "TRACE_LEVEL_DEBUG",
         "log_level": "LOG_LEVEL_ERROR",
     }
     },
    {'path': '/api/debugcontroller',
     'method': 'post',
     'data': {
         "name": "res_mgr_debug",
         "sub_module": "RES_MGR_DEBUG",
         "trace_level": "TRACE_LEVEL_DEBUG_DETAIL",
         "log_level": "LOG_LEVEL_ERROR",
     }
     },
    {'path': '/api/debugcontroller',
     'method': 'post',
     'data': {
         "name": "se_mgr_debug",
         "sub_module": "SE_MGR_DEBUG",
         "trace_level": "TRACE_LEVEL_DEBUG_DETAIL",
         "log_level": "LOG_LEVEL_ERROR",
     }
     },
    {'path': '/api/debugcontroller',
     'method': 'post',
     'data': {
         "name": "vi_mgr_debug",
         "sub_module": "VI_MGR_DEBUG",
         "trace_level": "TRACE_LEVEL_DEBUG_DETAIL",
         "log_level": "LOG_LEVEL_ERROR",
     }
     },
    {'path': '/api/debugcontroller',
     'method': 'post',
     'data': {
         "name": "metrics_mgr_debug",
         "sub_module": "METRICS_MGR_DEBUG",
         "trace_level": "TRACE_LEVEL_ERROR",
         "log_level": "LOG_LEVEL_ERROR",
     }
     },
    {'path': '/api/debugcontroller',
     'method': 'post',
     'data': {
         "name": "hs_mgr_debug",
         "sub_module": "HS_MGR_DEBUG",
         "trace_level": "TRACE_LEVEL_ERROR",
         "log_level": "LOG_LEVEL_ERROR",
     }
     },
    {'path': '/api/debugcontroller',
     'method': 'post',
     'data': {
         "name": "alert_mgr_debug",
         "sub_module": "ALERT_MGR_DEBUG",
         "trace_level": "TRACE_LEVEL_ERROR",
         "log_level": "LOG_LEVEL_ERROR",
     }
     },
    {'path': '/api/debugcontroller',
     'method': 'post',
     'data': {
         "name": AutoScaleService.DESCRIPTOR.GetOptions().Extensions[service_q_name],
         "sub_module": "AUTOSCALE_MGR_DEBUG",
         "trace_level": "TRACE_LEVEL_ERROR",
         "log_level": "LOG_LEVEL_INFO",
     }
     },
    {'path': '/api/debugcontroller',
     'method': 'post',
     'data': {
         "name": "apic_agent_debug",
         "sub_module": "APIC_AGENT_DEBUG",
         "trace_level": "TRACE_LEVEL_ERROR",
         "log_level": "LOG_LEVEL_ERROR",
     }
     },
    {'path': '/api/debugcontroller',
     'method': 'post',
     'data': {
         "name": "nsx_agent_debug",
         "sub_module": "NSX_AGENT_DEBUG",
         "trace_level": "TRACE_LEVEL_ERROR",
         "log_level": "LOG_LEVEL_ERROR",
     }
     },
    {'path': '/api/debugcontroller',
     'method': 'post',
     'data': {
         "name": "redis_infra_debug",
         "sub_module": "REDIS_INFRA_DEBUG",
         "trace_level": "TRACE_LEVEL_ERROR",
         "log_level": "LOG_LEVEL_ERROR",
     }
     },
    {'path': '/api/debugcontroller',
     'method': 'post',
     'data': {
         "name": CloudConnectorService.DESCRIPTOR.GetOptions().Extensions[service_q_name],
         "sub_module": "CLOUD_CONNECTOR_DEBUG",
         "trace_level": "TRACE_LEVEL_ERROR",
         "log_level": "LOG_LEVEL_INFO",
     }
     },
    {'path': '/api/debugcontroller',
     'method': 'post',
     'data': {
         "name": "mesos_metrics_debug",
         "sub_module": "MESOS_METRICS_DEBUG",
         "trace_level": "TRACE_LEVEL_ERROR",
         "log_level": "LOG_LEVEL_ERROR",
        }
     },
    {'path': '/api/debugcontroller',
     'method': 'post',
     'data': {
         "name": "metricsapi_srv_debug",
         "sub_module": "METRICSAPI_SRV_DEBUG",
         "trace_level": "TRACE_LEVEL_ERROR",
         "log_level": "LOG_LEVEL_ERROR",
      }
     },
    {'path': '/api/debugcontroller',
     'method': 'post',
     'data': {
         "name": "se_rpc_proxy_debug",
         "sub_module": "SE_RPC_PROXY_DEBUG",
         "trace_level": "TRACE_LEVEL_ERROR",
         "log_level": "LOG_LEVEL_ERROR",
        }
     },
    {'path': '/api/sslprofile',
     'method': 'post',
     'data': {
         "name": "System-Standard",
         "type" : "SSL_PROFILE_TYPE_APPLICATION",
         "cipher_enums":[
             "TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256",
             "TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA",
             "TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA",
             "TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384",
             "TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA256",
             "TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA384",
             "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256",
             "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
             "TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA",
             "TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA256",
             "TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA",
             "TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA384",
             "TLS_RSA_WITH_AES_128_GCM_SHA256",
             "TLS_RSA_WITH_AES_256_GCM_SHA384",
             "TLS_RSA_WITH_AES_128_CBC_SHA256",
             "TLS_RSA_WITH_AES_256_CBC_SHA256",
             "TLS_RSA_WITH_AES_128_CBC_SHA",
             "TLS_RSA_WITH_AES_256_CBC_SHA",
             "TLS_RSA_WITH_3DES_EDE_CBC_SHA",
         ],
         #"accepted_ciphers": "aECDSA:aECDH:kEDH:kRSA:!LOW:!EXP:!RC4",
         "accepted_versions": [
             {"type": "SSL_VERSION_TLS1"},
             {"type": "SSL_VERSION_TLS1_1"},
             {"type": "SSL_VERSION_TLS1_2"}
         ]
     }
     },
    {'path': '/api/sslprofile',
     'method': 'post',
     'data': {
         "name": "System-Standard-Portal",
         "type" : "SSL_PROFILE_TYPE_SYSTEM",
         "cipher_enums":[
             "TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256",
             "TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA",
             "TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA",
             "TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384",
             "TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA256",
             "TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA384",
             "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256",
             "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
             "TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA",
             "TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA256",
             "TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA",
             "TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA384",
             "TLS_RSA_WITH_AES_128_GCM_SHA256",
             "TLS_RSA_WITH_AES_256_GCM_SHA384",
             "TLS_RSA_WITH_AES_128_CBC_SHA256",
             "TLS_RSA_WITH_AES_256_CBC_SHA256",
             "TLS_RSA_WITH_AES_128_CBC_SHA",
             "TLS_RSA_WITH_AES_256_CBC_SHA",
             "TLS_RSA_WITH_3DES_EDE_CBC_SHA",
         ],
         #"accepted_ciphers": "aECDSA:aECDH:kEDH:kRSA:!LOW:!EXP:!RC4",
         "accepted_versions": [
             {"type": "SSL_VERSION_TLS1"},
             {"type": "SSL_VERSION_TLS1_1"},
             {"type": "SSL_VERSION_TLS1_2"}
         ]
     }
     },
    {'path': '/api/healthmonitor',
     'method': 'post',
     'data': {
         "name": "System-HTTP",
         "receive_timeout": 4,
         "successful_checks": 3,
         "failed_checks": 3,
         "send_interval": 10,
         "type": "HEALTH_MONITOR_HTTP",
         "http_monitor": {
             "http_request": "HEAD / HTTP/1.0",
             "http_response_code": [
                'HTTP_2XX',
                'HTTP_3XX'
             ]
         }
     }
     },
     {'path': '/api/healthmonitor',
     'method': 'post',
     'data': {
         "name": "System-HTTPS",
         "receive_timeout": 4,
         "successful_checks": 3,
         "failed_checks": 3,
         "send_interval": 10,
         "type": "HEALTH_MONITOR_HTTPS",
         "https_monitor": {
             "http_request": "HEAD / HTTP/1.0",
             "http_response_code": [
                'HTTP_2XX',
                'HTTP_3XX'
             ]
         }
     }
    },
    {'path': '/api/healthmonitor',
     'method': 'post',
     'data': {
         "name": "System-Ping",
         "receive_timeout": 4,
         "rise_limit": 3,
         "fall_limit": 3,
         "send_interval": 10,
         "type": "HEALTH_MONITOR_PING",
     }
    },
    {'path': '/api/healthmonitor',
     'method': 'post',
     'data': {
         "name": "System-TCP",
         "receive_timeout": 4,
         "rise_limit": 3,
         "fall_limit": 3,
         "send_interval": 10,
         "type": "HEALTH_MONITOR_TCP",
         "tcp_monitor": {
         },
     }
    },
    {'path': '/api/healthmonitor',
     'method': 'post',
     'data': {
         "name": "System-UDP",
         "receive_timeout": 2,
         "rise_limit": 3,
         "fall_limit": 3,
         "send_interval": 4,
         "type": "HEALTH_MONITOR_UDP",
         "udp_monitor": {
             "udp_request": "EnterYourRequestDataHere"
         }
     }
    },
    {'path': '/api/healthmonitor',
     'method': 'post',
     'data': {
         "name": "System-DNS",
         "receive_timeout": 4,
         "rise_limit": 3,
         "fall_limit": 3,
         "send_interval": 6,
         "type": "HEALTH_MONITOR_DNS",
         "dns_monitor": {
             "query_name": "www.google.com",
         },
     }
    },
    {'path': '/api/healthmonitor',
     'method': 'post',
     'data': {
         "name": "System-Xternal-Perl",
         "receive_timeout": 10,
         "rise_limit": 3,
         "fall_limit": 3,
         "send_interval": 30,
         "type": "HEALTH_MONITOR_EXTERNAL",
         "external_monitor": {
             "command_code": "#!/usr/bin/perl -w\n"
                             "my $ip= $ARGV[0];\n"
                             "my $port = $ARGV[1];\n"
                             "my $curl_out = `curl -v \"$ip\":\"$port\" 2>&1`;\n"
                             "if (index($curl_out, \"200 OK\") != -1) {\n"
                             "    print \"Server is up\n\";\n"
                             "}\n"

         },
     }
    },
    {'path': '/api/healthmonitor',
     'method': 'post',
     'data': {
         "name": "System-Xternal-Shell",
         "receive_timeout": 10,
         "rise_limit": 3,
         "fall_limit": 3,
         "send_interval": 30,
         "type": "HEALTH_MONITOR_EXTERNAL",
         "external_monitor": {
             "command_code": "#!/bin/bash\n"
                             "#curl -v $IP:$PORT >/run/hmuser/$HM_NAME.$IP.$PORT.out\n"
                             "curl -v $IP:$PORT"
         },
     }
     },
    {'path': '/api/healthmonitor',
     'method': 'post',
     'data': {
         "name": "System-Xternal-Python",
         "receive_timeout": 10,
         "rise_limit": 3,
         "fall_limit": 3,
         "send_interval": 30,
         "type": "HEALTH_MONITOR_EXTERNAL",
         "external_monitor": {
             "command_code": "#!/usr/bin/python\n"
                             "import sys\n"
                             "import httplib\n"
                             "conn = httplib.HTTPConnection(sys.argv[1]+':'+sys.argv[2])\n"
                             "conn.request(\"HEAD\", \"/index.html\")\n"
                             "r1 = conn.getresponse()\n"
                             "if r1.status == 200:\n"
                             "    print r1.status, r1.reason\n"
         },
     }
     },
    {'path': '/api/healthmonitor',
     'method': 'post',
     'data': {
         "name": "System-PingAccessAgent",
         "type": "HEALTH_MONITOR_HTTPS",
         "monitor_port": 3000,
         "https_monitor":{
             "http_request": "GET /pa/heartbeat.ping HTTP/1.1",
             "http_response_code": ["HTTP_2XX"],
             "ssl_attributes": {
                 "ssl_profile_ref": "/api/sslprofile?name=System-Standard"
             }
         }
     }
     },
    {'path': '/api/serviceenginegroup',
     'method': 'post',
     'data': {
         "name": "Default-Group",
     }
     },
    {'path': '/api/sslkeyandcertificate',
     'method': 'post',
     'data': {
         "name": "System-Default-Cert",
         "type": "SSL_CERTIFICATE_TYPE_VIRTUALSERVICE",
         "certificate" : {
            "self_signed": True,
            "days_until_expire": 3650,
            "subject" : {
                "common_name": "System Default Cert",
                }
             },
         "key_params": {
             "algorithm": "SSL_KEY_ALGORITHM_RSA",
             "rsa_params": {
                 "key_size": "SSL_KEY_2048_BITS"
             }
         },
     }
     },
    {'path': '/api/sslkeyandcertificate',
     'method': 'post',
     'data': {
         "name": "System-Default-Cert-EC",
         "type": "SSL_CERTIFICATE_TYPE_VIRTUALSERVICE",
         "certificate" : {
            "self_signed": True,
            "days_until_expire": 3650,
            "subject" : {
                "common_name": "System Default EC Cert",
                }
             },
         "key_params": {
             "algorithm": "SSL_KEY_ALGORITHM_EC",
             "ec_params": {
                 "curve": "SSL_KEY_EC_CURVE_SECP256R1"
             }
         },
     }
     },
    {'path': '/api/sslkeyandcertificate',
     'method': 'post',
     'data': {
         "name": "System-Default-Portal-Cert",
         "type": "SSL_CERTIFICATE_TYPE_SYSTEM",
         "certificate" : {
            "self_signed": True,
            "days_until_expire": 3650,
            "subject" : {
                "common_name": "Default Portal Cert",
                }
             },
         "key_params": {
             "algorithm": "SSL_KEY_ALGORITHM_RSA",
             "rsa_params": {
                 "key_size": "SSL_KEY_2048_BITS"
             }
         },
     }
     },
    {'path': '/api/sslkeyandcertificate',
    'method': 'post',
    'data': {
        "name": "System-Default-Portal-Cert-EC256",
        "type": "SSL_CERTIFICATE_TYPE_SYSTEM",
         "certificate" : {
            "self_signed": True,
            "days_until_expire": 3650,
            "subject" : {
                "common_name": "Default Portal EC Cert",
                }
             },
        "key_params": {
            "algorithm": "SSL_KEY_ALGORITHM_EC",
            "ec_params": {
                "curve": "SSL_KEY_EC_CURVE_SECP256R1"
            }
        },
    }
    },
    {'path': '/api/sslkeyandcertificate',
     'method': 'post',
     'data': ROOT_CA_DATA
     },
    {'path': '/api/sslkeyandcertificate',
     'method': 'post',
     'data': SECURE_CHANNEL_CERT_DATA
     },
    {'path': '/api/systemconfiguration',
     'method': 'put',
     'data': {
         "ntp_configuration": {
             "ntp_servers": [
                 {'server': {'type': 'DNS', 'addr': '0.us.pool.ntp.org'}},
                 {'server': {'type': 'DNS', 'addr': '1.us.pool.ntp.org'}},
                 {'server': {'type': 'DNS', 'addr': '2.us.pool.ntp.org'}},
                 {'server': {'type': 'DNS', 'addr': '3.us.pool.ntp.org'}}
             ]
         },
         "portal_configuration": {
             "enable_https": True,
             "enable_http": True,
             "redirect_to_https": True,
             "password_strength_check": True,
             "sslkeyandcertificate_refs":
                 ["/api/sslkeyandcertificate?name=System-Default-Portal-Cert",
                  "/api/sslkeyandcertificate?name=System-Default-Portal-Cert-EC256"]
         },
         "secure_channel_configuration": {
             "sslkeyandcertificate_refs": ["/api/sslkeyandcertificate?name=System-Default-Secure-Channel-Cert"]
         },
         "dhcp_enabled": False,
         "email_configuration": {
             "smtp_type": "SMTP_LOCAL_HOST"
         },
         "global_tenant_config": {
             "tenant_vrf": False
         },
         "ssh_ciphers": [
            "aes128-ctr",
            "aes256-ctr",
            "arcfour256",
            "arcfour128"
         ],
         "ssh_hmacs": [
            "hmac-sha2-512-etm@openssh.com",
            "hmac-sha2-256-etm@openssh.com",
            "umac-128-etm@openssh.com",
            "hmac-sha2-512"
         ]
     }
     },
    {'path': '/api/vrfcontext',
     'method': 'post',
     'data': {
         "name": 'global',
         "system_default": True
     }
     },
    {'path': '/api/vrfcontext',
     'method': 'post',
     'data': {
         "name": 'management',
         "system_default": True

     }
     },
    {'path': '/api/applicationpersistenceprofile',
     'method': 'post',
     'data': {
         'name': 'System-Persistence-Client-IP',
         'persistence_type': 'PERSISTENCE_TYPE_CLIENT_IP_ADDRESS',
         'ip_persistence_profile': {
             "ip_persistent_timeout": 5
         }
     }
    },
    {'path': '/api/applicationpersistenceprofile',
     'method': 'post',
     'data': {
         'name': 'System-Persistence-Http-Cookie',
         'persistence_type': 'PERSISTENCE_TYPE_HTTP_COOKIE'
     }
    },
    {'path': '/api/applicationpersistenceprofile',
     'method': 'post',
     'data': {
         'name': 'System-Persistence-Custom-Http-Header',
         'persistence_type': 'PERSISTENCE_TYPE_CUSTOM_HTTP_HEADER',
         'hdr_persistence_profile': {
             'prst_hdr_name': 'customhttphdrname'
         }
     }
    },
    {'path': '/api/applicationpersistenceprofile',
     'method': 'post',
     'data': {
         'name': 'System-Persistence-App-Cookie',
         'persistence_type': 'PERSISTENCE_TYPE_APP_COOKIE',
         'app_cookie_persistence_profile': {
             'prst_hdr_name': 'customhttpcookiename'
         }
     }
    },
    {'path': '/api/applicationpersistenceprofile',
     'method': 'post',
     'data': {
         'name': 'System-Persistence-TLS',
         'persistence_type': 'PERSISTENCE_TYPE_TLS'
     }
    },
    {'path': '/api/seproperties',
     'method': 'put',
     'data': {
        "se_bootup_properties": {
            "se_dp_compression": {
                "level_normal": 1,
            }
        },
        "se_runtime_properties": {
            "app_headers": [
                {
                    "hdr_name": "Server",
                    "hdr_match_case": "SENSITIVE",
                    "hdr_string_op": "EQUALS",
                },
                {
                    "hdr_name": "MicrosoftSharePointTeamServices",
                    "hdr_match_case": "SENSITIVE",
                    "hdr_string_op": "EQUALS",
                }
             ],
            "se_dp_compression": {
                "mobile_str": [
                                "iPhone",
                                "iPod",
                                "Android",
                                "BB10",
                                "BlackBerry",
                                "webOS",
                                "IEMobile",
                                "iPad",
                                "PlayBook",
                                "Xoom",
                                "P160U",
                                "SCH-I800",
                                "Nexus 7",
                                "Touch"
                ],
            },
        },
        "se_agent_properties": {
            "debug_mode": False,
        }
     }
     },
    {'path': '/api/controllerproperties',
     'method': 'put',
     'data': {}
    },
    {'path': '/api/ipaddrgroup',
     'method': 'post',
     'data': {
         "name": "Internal",
         "prefixes": [
             {
                 "ip_addr":{
                        "addr": "10.0.0.0",
                        "type": "V4"
                  },
                 "mask": 8
             },
             {
                 "ip_addr":{
                        "addr": "192.168.0.0",
                        "type": "V4"
                  },
                 "mask": 16
             },
             {
                 "ip_addr":{
                        "addr": "172.16.0.0",
                        "type": "V4"
                  },
                 "mask": 12
             },
         ]
     }
     },
      _data_from_pb(ALERT_SCRIPT_CONFIGS.apiPath(),
                    ALERT_SCRIPT_CONFIGS.configObject(
                        alerts_pb2.ALERT_SCRIPT_CONFIG_SE_GRP_FLV_UPD)),
      _data_from_pb(ALERT_SCRIPT_CONFIGS.apiPath(),
                    ALERT_SCRIPT_CONFIGS.configObject(
                        alerts_pb2.ALERT_SCRIPT_CONFIG_POSTGRESQL_VACUUM)),
      _data_from_pb(ACTION_GROUP_CONFIGS.apiPath(),
                 ACTION_GROUP_CONFIGS.configObject(ACTIONGROUP_HIGH)),
      _data_from_pb(ACTION_GROUP_CONFIGS.apiPath(),
                 ACTION_GROUP_CONFIGS.configObject(ACTIONGROUP_LOW)),
      _data_from_pb(ACTION_GROUP_CONFIGS.apiPath(),
                 ACTION_GROUP_CONFIGS.configObject(ACTIONGROUP_MEDIUM)),
      _data_from_pb(ACTION_GROUP_CONFIGS.apiPath(),
                 ACTION_GROUP_CONFIGS.configObject(ACTIONGROUP_SYSLOG_CONFIG)),
      _data_from_pb(ACTION_GROUP_CONFIGS.apiPath(),
                 ACTION_GROUP_CONFIGS.configObject(ACTIONGROUP_SYSLOG_SYSTEM)),
      _data_from_pb(ACTION_GROUP_CONFIGS.apiPath(),
                 ACTION_GROUP_CONFIGS.configObject(ACTIONGROUP_SE_GRP_FLAVOR_UPDATE)),
    {'path': '/api/cloudproperties',
     'method': 'put',
     'data': {
        "cc_vtypes": [
            "CLOUD_OPENSTACK",
            "CLOUD_AWS",
            "CLOUD_VCA",
            "CLOUD_MESOS",
            "CLOUD_DOCKER_UCP",
            "CLOUD_RANCHER",
            "CLOUD_OSHIFT_K8S",
            "CLOUD_LINUXSERVER",
            "CLOUD_AZURE",
            "CLOUD_GCP"
        ],
        "hyp_props": [
            {
                "htype": "VMWARE_ESX",
                "max_nics": 10
            },
            {
                "htype": "VMWARE_VSAN",
                "max_nics": 10
            },
            {
                "htype": "KVM",
                "max_nics": 24
            },
            {
                "htype": "XEN"
            }
        ],
        "info": [
            {
                "vtype": "CLOUD_VCENTER",
                "htypes": ["VMWARE_ESX"]
            },
            {
                "vtype": "CLOUD_OPENSTACK",
                "htypes": ["KVM", "VMWARE_ESX", "VMWARE_VSAN"],
                "flavor_props": [
                    {
                        "id": "all",
                        "name": "all",
                        "max_ips_per_nic": 11,
                    },
                ]
            },
            {
                "vtype": "CLOUD_AWS",
                "htypes": ["XEN"],
                "flavor_regex_filter": _get_aws_flavor_regex(),
                "flavor_props":
                    _get_aws_flavor_data(),
            },
            {
                "vtype": "CLOUD_MESOS",
            },
            {
                "vtype": "CLOUD_DOCKER_UCP",
            },
            {
                "vtype": "CLOUD_RANCHER",
            },
            {
                "vtype": "CLOUD_OSHIFT_K8S",
            },
            {
                "vtype": "CLOUD_LINUXSERVER",
            },
            {
                "vtype": "CLOUD_VCA",
                "htypes": ["VMWARE_ESX"]
            },
            {
                "vtype": "CLOUD_AZURE",
                "flavor_props": [
                    {
                        "id": "all",
                        "name": "all",
                        "max_nics": 1,
                        "max_ips_per_nic": 150,
                    },
                ]
            },
            {
                "vtype": "CLOUD_GCP"
            },
        ]
     }
    },
    {'path': '/api/autoscalelaunchconfig',
     'method': 'post',
     'data': {
         "name": "default-autoscalelaunchconfig",
         "image_id": "default"
         }
    },
    {'path': '/api/backupconfiguration',
     'method': 'post',
     'data' :  {
         "name": "Backup-Configuration",
         "save_local" : True
         }
    },
    {'path': '/api/scheduler',
     'method': 'post',
     'data' :  {
         "name": "Default-Scheduler",
         "enabled" : True,
         "run_mode" : "RUN_MODE_PERIODIC",
         "frequency" : 1,
         "frequency_unit" : "SCHEDULER_FREQUENCY_UNIT_DAY",
         "backup_config_ref" : "/api/backupconfiguration?name=Backup-Configuration",
         "scheduler_action" : "SCHEDULER_ACTION_BACKUP"
         }
    },
    {'path': '/api/scheduler',
     'method': 'post',
     'data' :  {
         "name": "Postgresql-Vacuum-Scheduler",
         "enabled" : True,
         "run_mode" : "RUN_MODE_PERIODIC",
         "frequency" : 2,
         "frequency_unit" : "SCHEDULER_FREQUENCY_UNIT_WEEK",
         "run_script_ref" : "/api/alertscriptconfig?name=postgres_vacuum",
         "scheduler_action" : "SCHEDULER_ACTION_RUN_A_SCRIPT"
         }
    },
    {'path': '/api/wafprofile',
     'method': 'post',
     'data': {
         'name': 'System-WAF-Profile',
         'config' : {
             'client_request_max_body_size' : 32
          }
     }
    },
    {'path': '/api/wafcrs',
     'method': 'post',
     'waf_crs_name': 'CRS-2017-0',
     'data': {
     }
    },
    {'path': '/api/wafcrs',
     'method': 'post',
     'waf_crs_name': 'CRS-2017-1',
     'data': {
     }
    },
    {'path': '/api/wafpolicy',
     'method': 'post',
     'waf_crs_name': 'CRS-2017-1',
     'data': {
         'name': 'System-WAF-Policy',
         'mode' : 'WAF_MODE_DETECTION_ONLY',
         "waf_profile_ref" : "/api/wafprofile?name=System-WAF-Profile",
         "waf_crs_ref" : "/api/wafcrs?name=CRS-2017-1",
     }
    },
    {'path': '/api/errorpagebody',
     'method': 'post',
     'data': {
         'name': 'Custom-Error-Page',
     }
    },
    {'path': '/api/protocolparser',
     'method': 'post',
     'data': {
         "name": "Default-DHCP",
         "parser_code": "#!/usr/bin/lua5.1\n"
         "\n"
         "package.loaded.bitstring = nil\n"
         "local bitstring = require \"bitstring\"\n"
         "\n"
         "local parse_dhcp = {}\n"
         "local attribute_list = {}\n"
         "local dhcp_params = {}\n"
         "local ip_str = \"\"\n"
         "local dhcp_msg = \"\"\n"
         "\n"
         "local function _num_to_ipv4address(msg, start_pos)\n"
         "   ip_str = \"\"\n"
         "   local ip_len = 4\n"
         "   while (ip_len >0) do\n"
         "      temp = bitstring.unpack(\"8:int\", msg, start_pos)\n"
         "      if (ip_len ~= 4) then\n"
         "         ip_str = ip_str..\".\"\n"
         "      end\n"
         "\n"
         "      ip_str = ip_str..temp\n"
         "      start_pos = start_pos + 1\n"
         "      ip_len = ip_len - 1\n"
         "   end\n"
         "\n"
         "   return ip_str\n"
         "end\n"
         "\n"
         "local function _get_key_value(dhcp_msg, option, attr_len, start_pos,end_pos)\n"
         "   if option == 53 then\n"
         "      temp = bitstring.unpack(\"8:int\", dhcp_msg, start_pos, end_pos)\n"
         "   elseif option == 50 then\n"
         "      temp = _num_to_ipv4address(dhcp_msg, start_pos)\n"
         "   else\n"
         "      if (#dhcp_msg < end_pos) then\n"
         "         temp = bitstring.unpack(\"rest:bin\", dhcp_msg,\n"
         "                                 start_pos, #dhcp_msg)\n"
         "      else\n"
         "         temp = bitstring.unpack((attr_len) .. \":bin, rest:bin\", dhcp_msg,\n"
         "            start_pos, end_pos)\n"
         "      end\n"
         "   end\n"
         "   return temp\n"
         "end\n"
         "\n"
         "\n"
         "function parse_dhcp_pkt(payload)\n"
         "   dhcp_params = {}\n"
         "   dhcp_msg = \"\"\n"
         "   local pos = 1\n"
         "   local result = {}\n"
         "   local data = bitstring.hexstream(payload)\n"
         "   dhcp_msg = bitstring.fromhexstream(data)\n"
         "\n"
         "    -- parse radius message\n"
         "   dhcp_params.msg_type, dhcp_params.hw_type, dhcp_params.hw_address_len, dhcp_params.hops, dhcp_params.txn_id, dhcp_params.elapsed_sec, dhcp_params.bootp_flags, dhcp_params.ciaddr, dhcp_params.yiaddr, dhcp_params.siaddr, dhcp_params.giaddr, dhcp_params.ch_mac, dhcp_params.client_hw_addr_padding,dhcp_params.sname, dhcp_params.boot_file, dhcp_params.dhcp_cookie = bitstring.unpack(\"8:int, 8:int, 8:int, 8:int, 32:int:big, 16:int:big, 2:bin, 4:bin, 4:bin, 4:bin, 4:bin, 6:bin, 10:bin, 64:bin, 128:bin, 4:bin\", dhcp_msg)\n"
         "\n"
         "\n"
         "   if(bitstring.hexstream(dhcp_params.dhcp_cookie) ~= \"63825363\") then\n"
         "      return false, \"DHCP parser (the magic cookie was invalid)\"\n"
         "   end\n"
         "\n"
         "\n"
         "   -- parse dhcp message\n"
         "   attribute_list = {}\n"
         "   local len = #dhcp_msg - 240\n"
         "   local start_pos = 241\n"
         "   local end_pos = 242\n"
         "   dictionary={}\n"
         "\n"
         "   while(len > 0) do\n"
         "      if (len == 1) then\n"
         "         option= bitstring.unpack(\"8:int\", dhcp_msg, start_pos)\n"
         "         -- Check for termination condition\n"
         "         if (option == 0xFF) then\n"
         "            break;\n"
         "         end\n"
         "         break\n"
         "      else\n"
         "         option= bitstring.unpack(\"8:int\", dhcp_msg, start_pos, end_pos)\n"
         "      end\n"
         "\n"
         "      -- Check for termination condition\n"
         "      if (option == 0xFF) then\n"
         "         break;\n"
         "      end\n"
         "\n"
         "      -- Option is of 1 Byte\n"
         "      start_pos = start_pos + 1\n"
         "      end_pos = end_pos + 1\n"
         "\n"
         "      attr_length = bitstring.unpack(\"8:int\", dhcp_msg, start_pos)\n"
         "      start_pos = start_pos + 1\n"
         "      end_pos  = start_pos + attr_length\n"
         "\n"
         "      value = _get_key_value(dhcp_msg, option, attr_length, start_pos, end_pos)\n"
         "\n"
         "      start_pos = end_pos\n"
         "      len = len - attr_length - 2\n"
         "      dictionary[tostring(option)] = value\n"
         "      table.insert(attribute_list, {option = option, length = attr_length, value = value})\n"
         "   end\n"
         "\n"
         "   return dhcp_params, dictionary\n"
         "end\n"
         "\n"
         "function parse_dhcp.getDHCPParamsAndOptions(payload)\n"
         "   dhcp_params, attribute_list =  parse_dhcp_pkt(payload)\n"
         "   return dhcp_params, attribute_list\n"
         "end\n"
         "\n"
         "return parse_dhcp\n"

     }
    },
    {'path': '/api/protocolparser',
     'method': 'post',
     'data': {
         "name": "Default-Radius",
         "parser_code":
         "#!/usr/bin/lua5.1\n"
         "-- parse-radius.lua\n"
         "-- This example demonstrates parsing and creation of RADIUS protocol messages\n"
         "-- using bitstring.pack and bitstring.unpack. It also uses bitstring.hexstream\n"
         "-- and bitstring.fromhexstream utility functions that ease on debugging.\n"
         "-- RADIUS protocol is defined in RFC 2865.\n"
         "-- ---------------------------------------\n"
         "package.loaded.bitstring = nil\n"
         "local bitstring = require \"bitstring\"\n"
         "local s_char = string.char;\n"
         "local parse_radius = {}\n"
         "local attribute_list = {}\n"
         "local code, identifier, message_length, authenticator\n"
         "local ip_str = \"\"\n"
         "--list of integer attributes\n"
         "local attribute_int = {[5] = true, [6] = true, [7] = true, [10] = true, [12] = true,\n"
         "[13] = true, [15] = true, [16] = true, [23] = true, [27] = true, [28] = true,\n"
         "[29] = true, [37] = true, [38] = true, [61] = true, [62] = true}\n"
         "local attribute_addrs = {[4] = true, [8] = true, [9] = true, [14] = true}\n"
         "\n"
         "local function num_to_ipv4address(msg, start_pos)\n"
         "   ip_str = \"\"\n"
         "   for i=1, 4 do\n"
         "      temp = bitstring.unpack(\"8:int\", msg, start_pos)\n"
         "      if (i ~= 1) then\n"
         "         ip_str = ip_str..\".\"\n"
         "      end\n"
         "      ip_str = ip_str..temp\n"
         "      start_pos = start_pos + 1\n"
         "   end\n"
         "   return ip_str\n"
         "end\n"
         "\n"
         "local function get_key_value(radius_msg, option, attr_len, start_pos,end_pos)\n"
         "   --if option ==  then\n"
         "     -- temp = bitstring.unpack(\"8:int\", dhcp_msg, start_pos, end_pos)\n"
         "   if attribute_addrs[option] then\n"
         "      temp = num_to_ipv4address(radius_msg, start_pos)\n"
         "   elseif attribute_int[option] then\n"
         "         temp = bitstring.unpack(\"32:int:big\", radius_msg, start_pos)\n"
         "   else\n"
         "      if (#radius_msg < end_pos) then\n"
         "         temp = bitstring.unpack(\"rest:bin\", radius_msg,\n"
         "                                 start_pos, #radius_msg)\n"
         "      else\n"
         "         temp = bitstring.unpack((attr_len) .. \":bin, rest:bin\", radius_msg,\n"
         "            start_pos, end_pos)\n"
         "      end\n"
         "   end\n"
         "   return temp\n"
         "end\n"
         "\n"
         "function parse_radius.parsepacket(packet)\n"
         "   length=string.len(packet)\n"
         "   packet = bitstring.hexstream(packet)\n"
         "\n"
         "   radius_msg = bitstring.fromhexstream(packet)\n"
         "\n"
         "   -- parse radius message\n"
         "   code, identifier, message_length, authenticator =\n"
         "      bitstring.unpack(\"8:int, 8:int, 16:int:big, 16:bin\", radius_msg)\n"
         "\n"
         "   dictionary = {}\n"
         "   key = {}\n"
         "   attribute_list = {}\n"
         "   len = #radius_msg - 20\n"
         "   local start_pos = 21\n"
         "   local end_pos = 22\n"
         "\n"
         "      dictionary[\"code\"] = code\n"
         "   dictionary[\"identifier\"] = identifier\n"
         "   dictionary[\"message_len\"] = message_length\n"
         "   dictionary[\"authenticator\"] = authenticator\n"
         "\n"
         "   while(len > 0) do\n"
         "      number, attr_length = bitstring.unpack(\"8:int, 8:int\", radius_msg, start_pos, end_pos)\n"
         "      start_pos = start_pos +2\n"
         "\n"
         "      value = get_key_value(radius_msg, number, attr_length-2, start_pos, start_pos+ attr_length - 2)\n"
         "      start_pos = start_pos + attr_length - 2\n"
         "      end_pos = start_pos + 1\n"
         "      len = len - attr_length\n"
         "      dictionary[tostring(number)] = value\n"
         "      table.insert(attribute_list, {number = number, length = attr_length, value = value})\n"
         "   end\n"
         "   return dictionary\n"
         "end\n"
         "\n"
         "function parse_radius.getUserName(s)\n"
         "   --s = s:gsub(\"%s+\", \"\"):gsub(\"%x%x\", function(x) return s_char(tonumber(x, 16)) end);\n"
         "   parse_radius.parsepacket(s)\n"
         "   for i, attribute in ipairs(attribute_list) do\n"
         "      if (attribute.number == 1) then\n"
         "         user_name = attribute.value\n"
         "         break\n"
         "      end\n"
         "   end\n"
         "   return user_name\n"
         "end\n"
         "\n"
         "function parse_radius.getPktIdentifier(s)\n"
         "   dictionary = parse_radius.parsepacket(s)\n"
         "   return dictionary[\"identifier\"]\n"
         "end\n"
         "\n"
         "function parse_radius.is_access_reject(s)\n"
         "   parse_radius.parsepacket(s)\n"
         "   if (code == 3) then\n"
         "      return true\n"
         "   end\n"
         "\n"
         "   return false\n"
         "end\n"
         "\n"
         "return parse_radius"
      }
    },
]

def getConfigData(tenant_uuid=''):
    return _add_system_event_config_objs(DATA_LIST, tenant_uuid)
