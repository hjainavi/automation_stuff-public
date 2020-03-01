
if __name__ != "__main__":
    sys.exit(0)

import sys, os
import django
from django.conf import settings
from django.apps import apps
import simplejson
import argparse
from django.utils.crypto import get_random_string

parser = argparse.ArgumentParser()
parser.add_argument('-p','--passphrase', help="Encrypt token key passphrase", required=True)
args = parser.parse_args()
passphrase = args.passphrase
TEST_STRING = "thisisencrypted"

print "# Script to copy user tokens from a previous version of the controller to newer version "
question = "Is the script being run before an upgrade ? (Y/N) "
before_upgrade = raw_input(question)

if str.lower(before_upgrade) in ['y','yes']:
    
    os.environ['PYTHONPATH'] = '/opt/avi/python/lib:/opt/avi/python/bin/portal'
    os.environ['DJANGO_SETTINGS_MODULE'] = 'portal.settings_local'
    sys.path.append("/opt/avi/python/bin/portal")
    if not apps.ready and not settings.configured:
        django.setup()

    from permission.models import AuthToken
    from api.models import SystemConfiguration
    from rest_framework.serializers import DateTimeField
    from avi.util.ssl_utils import encrypt_string
    from django.contrib.auth.hashers import PBKDF2PasswordHasher as pbkdf2
    
    salt = get_random_string(16)
    if passphrase:
        hasher = pbkdf2()
        _, _, _, passkey = hasher.encode(passphrase, salt, iterations=100000).split('$', 3)
    else:
        passkey = None

    docker_mode = SystemConfiguration.objects.all()[0].json_data['docker_mode']
    authtoken_data = {'AuthToken':[]}
    for obj in AuthToken.objects.all():
        authtoken_data['AuthToken'].append({
            'key':encrypt_string(obj.key,passkey),
            'user':str('/api/user/%s'%(obj.user.uuid)),
            'expires_at':DateTimeField().to_native(obj.expires_at),
            'created':DateTimeField().to_native(obj.created)
            })
    authtoken_data['salt'] = salt
    authtoken_data['encrypted_string'] = encrypt_string(TEST_STRING, passkey)
    authtoken_json = simplejson.dumps(authtoken_data, indent=4, sort_keys=True)
    authtoken_file_path = "/vol/authtoken_data.json" if docker_mode else "/host/authtoken_data.json"
    with open(authtoken_file_path,'w') as f:
        f.write(authtoken_json)

    print "Copied AuthToken data to file %s"%(authtoken_file_path)
    print "Run this script after upgrade to populate the Database with the token values"
    sys.exit(0)

question = "Is the script being run 'after' an upgrade ? (Y/N) "
after_upgrade = raw_input(question)
if str.lower(after_upgrade) in ['y','yes']:
    

    os.environ['PYTHONPATH'] = '/opt/avi/python/lib:/opt/avi/python/bin/portal'
    os.environ['DJANGO_SETTINGS_MODULE'] = 'portal.settings_local'
    sys.path.append("/opt/avi/python/bin/portal")
    if not apps.ready and not settings.configured:
        django.setup()

    from permission.models import AuthToken
    from api.models import SystemConfiguration 
    from permission.models import AuthTokenSerializer
    from avi.util.ssl_utils import decrypt_string
    from django.contrib.auth.hashers import PBKDF2PasswordHasher as pbkdf2
    
    docker_mode = SystemConfiguration.objects.all()[0].json_data['docker_mode']
    authtoken_file_path = "/vol/authtoken_data.json" if docker_mode else "/host/authtoken_data.json"
    if not os.path.isfile(authtoken_file_path):
        print "ERROR : Please run this file before upgrade to extract the token values"
        sys.exit(1)
    with open(authtoken_file_path, "r") as f:
        authtoken_data = simplejson.load(f)
    errors = []
    
    if passphrase:
        salt = authtoken_data['salt']
        hasher = pbkdf2()
        _, _, _, passkey = hasher.encode(passphrase, salt, iterations=100000).split('$', 3)
    else:
        passkey = None
    try:
        if decrypt_string(authtoken_data['encrypted_string'], passkey) != TEST_STRING:
            print "ERROR : wrong passphrase. Please enter correct passphrase (--passphrase option)"
    except Exception as e:
        if "wrong key" in str(e):
            print "ERROR : wrong passphrase. Please enter correct passphrase (--passphrase option)"
        sys.exit(1)

        

    for val in authtoken_data['AuthToken']:
        val['key'] = decrypt_string(val['key'],passkey)
        if not val.get('expires_at', None):
            # Import long lived auth tokens only.
            continue
        objs = AuthToken.objects.filter(key=val['key'])
        if objs:
            #Ignore if the same key exists on the controller.
            continue
        serializer = AuthTokenSerializer(data=val)
        if serializer.is_valid():
            saved_obj = serializer.save(update_time=True)
        else:
            errors.append('Serializing error %s for %s with data: %s'%
                    (serializer.errors, "AuthTokenSerializer", str(val)))
    print "************** Tokens Imported **************"
    if errors:
        for er in errors:
            print er
    
    
