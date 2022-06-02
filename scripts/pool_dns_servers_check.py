
if __name__ != "__main__":
    sys.exit(0)

import sys, os
import django
from django.conf import settings
from django.apps import apps

print("# Script to check if any two or more hostnames in pool resolve to same ip address")
    
os.environ['PYTHONPATH'] = '/opt/avi/python/lib:/opt/avi/python/bin/portal'
os.environ['DJANGO_SETTINGS_MODULE'] = 'portal.settings_local'
sys.path.append("/opt/avi/python/bin/portal")
if not apps.ready and not settings.configured:
    django.setup()

from avi.rest.view_utils import get_model_from_name
from api.models import Pool
from avi.util.dns_resolver import resolve_host

for pool in Pool.objects.all():
    name = pool.name
    ip_hostname_from_pool = {}
    ip_hostname_actual_resolve = {}
    for server in pool.json_data['servers']:
        ip_hostname_from_pool[server['ip']['addr']] = [server.get('hostname','NA'),server.get('resolve_server_by_dns',False)]
    for _,value in ip_hostname_from_pool.items():
        if value[1]:
            resolved_ips = resolve_host(value[0])
            for ip_val in resolved_ips:
                if ip_hostname_actual_resolve.get(ip_val,False):
                    ip_hostname_actual_resolve[ip_val].add(value[0])
                else:
                    ip_hostname_actual_resolve[ip_val] = {value[0]}
    #print(ip_hostname_from_pool)
    #print(ip_hostname_actual_resolve)
    for ip,val in ip_hostname_from_pool.items():
        if not val[1] and ip in ip_hostname_actual_resolve.keys():
            print("******* issue with ip",ip,"and hostnames",ip_hostname_actual_resolve[ip],"in Pool",name,"*******")
    for ip,val in ip_hostname_actual_resolve.items():
        if len(val) > 1:
            print("******* Hostnames", val,"being resolved to same ip",ip,"in Pool",name,"*******")
sys.exit(0)

