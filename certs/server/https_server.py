'''
PROTOCOL_SSLv23
PROTOCOL_TLSv1
PROTOCOL_TLSv1_1
PROTOCOL_TLSv1_2
'''
import BaseHTTPServer, SimpleHTTPServer
import ssl
from ssl import SSLContext
import threading
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--protocol", help="protocol to use. default = SSLv23, tls1, tls1_1 , tls1_2")
parser.add_argument("--ciphers", help="ciphers to use. default = ALL, eg: 'ECDH:!ECDHE' ", default="ALL")
parser.add_argument("--certfile", help="Path of the certificate pem file")
parser.add_argument("--keyfile", help="Path of the certificate private key file")
args = parser.parse_args()


if args.protocol:
    if args.protocol == 'tls1':protocol=ssl.PROTOCOL_TLSv1
    elif args.protocol == 'tls1_1':protocol=ssl.PROTOCOL_TLSv1_1
    elif args.protocol == 'tls1_2':protocol=ssl.PROTOCOL_TLSv1_2
    else:
        raise Exception("no such protocol")
else:
    protocol = ssl.PROTOCOL_SSLv23

ciphers = args.ciphers
context = SSLContext(protocol)
context.load_dh_params("/root/certs/dh/dhparam.pem")
print args
context.load_cert_chain(certfile=args.certfile,keyfile=args.keyfile)
if ciphers:
    context.set_ciphers(ciphers)

httpd = BaseHTTPServer.HTTPServer(('', 13443),
        SimpleHTTPServer.SimpleHTTPRequestHandler)
httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
httpd.serve_forever()


