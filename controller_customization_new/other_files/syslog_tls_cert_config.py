import sys, os, django
import ssl, socket

sys.path.append('/opt/avi/python/bin/portal')
os.environ["DJANGO_SETTINGS_MODULE"] = "portal.settings_full"

from api.models import SSLKeyAndCertificate, PKIProfile
from avi.util.ssl_utils import decrypt_string

django.setup()

def user_input(question):
    '''
    We start with using raw_input and asking the question until the user
    enters something. We can also improve this with default and validation routine
    when needed
    '''
    val = ''
    while not val:
        val = raw_input(question)
    return val

try:
    if not os.path.exists('/etc/ssl/rsyslog'):
        os.makedirs('/etc/ssl/rsyslog')
except OSError:
    print 'Error: Creating directory for rsyslog. Please run this script with root privilege'

sslpb = SSLKeyAndCertificate.objects.get(name='SyslogTLSSSLKeyAndCertificate').protobuf()
pkipb = PKIProfile.objects.get(name='SyslogTLSPKIProfile').protobuf()

if sslpb:
    with open('/etc/ssl/rsyslog/SyslogClient-cert.pem', 'w') as f:
        f.write(sslpb.certificate.certificate)

    with open('/etc/ssl/rsyslog/SyslogClient-key.pem', 'w') as f:
        f.write(decrypt_string(sslpb.key))
else:
    print 'SSL Key and Certificate with name SyslogTLSSSLKeyAndCertificate not found'

if pkipb:
    with open('/etc/ssl/rsyslog/CA.pem', 'w') as f:
        pki_cert = ''
        for cert in pkipb.ca_certs:
            pki_cert += cert.certificate + '\n'
        f.write(pki_cert)
else:
    print 'PKI Profile with name SyslogTLSPKIProfile not found'


# TEST the connection
socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
# context.verify_mode = ssl.CERT_NONE
context.verify_mode = ssl.CERT_REQUIRED
context.load_verify_locations(cafile="/etc/ssl/rsyslog/CA.pem")
context.load_cert_chain(certfile='/etc/ssl/rsyslog/SyslogClient-cert.pem',keyfile='/etc/ssl/rsyslog/SyslogClient-key.pem')
socket1 = context.wrap_socket(socket1)

syslog_server_ip = user_input('Please enter the Syslog Server\'s IP address : ')
syslog_server_port = int(user_input('Please enter the Syslog Server\'s port : '))

try:
    socket1.connect((syslog_server_ip, syslog_server_port))
    print 'Connect to Syslog Server Successful'
except Exception as e:
    print 'Issue connecting to the Syslog Server'
    raise e
