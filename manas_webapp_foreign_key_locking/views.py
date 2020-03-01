
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

import socket
import dns.resolver
import jinja2
#import json

# django
from django.http import HttpResponse, HttpRequest
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
#from models import *
#from permission.models import *
#from rest_framework.decorators import api_view

# avi
from api.models import Cloud, CloudConnectorUser
#from avi.rest.views import CommonView
from avi.rest.json_io import JSONRenderer
from avi.infrastructure.services import Services

"""
# this function likely has horrendous performance - optimize later
@api_view(['GET'])
def tree_view(request):
    view = CommonView()
    global_objs = globals()
    objs = {'scope':{}}
    if request.user.is_authenticated():

        # for each object type
        for ct in ContentType.objects.filter(app_label='api'):

            # only return referencable objects
            model = ct.model_class()
            model_name = model.__name__
            if ('uuid' not in dir(model()) or
                'tenant_ref' not in dir(model()) or
                model_name+'Serializer' not in global_objs):
                continue

            # for each object instance
            for m in model.objects.all():
                if not view.check_user_tenant_resource(request.user, m.tenant_ref, ct.model, 1):
                    continue

                tenant = m.tenant_ref.slug
                if tenant not in objs['scope']:
                    objs['scope'][tenant] = {}
                if ct not in objs['scope']:
                    objs['scope'][tenant][ct.model] = []
                objs['scope'][tenant][ct.model].append(
                    global_objs[model_name+'Serializer'](m).data['url'])

    return HttpResponse(JSONRenderer().render(objs), content_type='application/json')
"""

def linux_host_install(request, *args, **kwargs):
    env = jinja2.Environment(loader=jinja2.FileSystemLoader('api/templates/'),
                             autoescape=False,
                             trim_blocks=True)
    template = env.get_template('linux_host_install.sh.template')
    username = request.GET.get("username")
    error = ''
    if username:
        try:
            cloud_user_obj = CloudConnectorUser.objects.get(name=username).protobuf()
            key = cloud_user_obj.public_key
            script = template.render({'user': username, 'key': key})
        except ObjectDoesNotExist as e:
            error = "Specified cloud connector user %s does not exist" % username
        except:
            return HttpResponse(status=501)
    else:
        error = "Please specify the cloud connector user"
    if error:
        script = 'echo %s; exit 1' % error
    response = HttpResponse(script, content_type='text')
    response['Content-Disposition'] = 'attachment; filename=linux_host_install.sh'
    return response

def dns_lookup(request, *args, **kwargs):
    if 'server' not in kwargs:
        return HttpResponse(status=400)
    server = kwargs['server']
    try:
        dns_resolver = dns.resolver.Resolver()
        try:
            ips = [ip.address for ip in dns_resolver.query(server, 'A')]
        except:
            ips = []
        try:
            ip6s = [ip.address for ip in dns_resolver.query(server, 'AAAA')]
        except:
            ip6s = []
        return HttpResponse(JSONRenderer().render({
            'server': server,
            'ips': ips,
            'ip6s': ip6s,
        }), content_type='application/json')
    except:
        return HttpResponse(JSONRenderer().render(
            {'server': server}),
            status=200,
            content_type='application/json')
