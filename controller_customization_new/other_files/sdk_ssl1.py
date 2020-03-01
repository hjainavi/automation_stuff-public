from avi.sdk.avi_api import ApiSession
import argparse


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--user', help='controller user',
                        default='admin')
    parser.add_argument('-p', '--password', help='controller user password',
                        default='avi123')
    parser.add_argument('-t', '--tenant', help='tenant name',
                        default='admin')
    parser.add_argument('-c', '--controller_ip', help='controller ip')
    parser.add_argument('-v', '--version', help='version')

    args = parser.parse_args()
    api = ApiSession.get_session(args.controller_ip, args.user, args.password,
                                 tenant=args.tenant,api_version=args.version)
    
    pool_data = {'name':"pool/|;+, ''-_.*()!%?$@&=#b77"}
    sign = '''
-----BEGIN CERTIFICATE REQUEST-----
MIIBiDCB8gIBADBJMQswCQYDVQQGEwJJTjEQMA4GA1UECAwHRW5nbGFuZDETMBEG
A1UECgwKU2VydmVyIEx0ZDETMBEGA1UEAwwKYXZpLnNlcnZlcjCBnzANBgkqhkiG
9w0BAQEFAAOBjQAwgYkCgYEAxmj/mTbaDHjIqyHX/H4V00hev+x4TKzIbk0n6CMq
IycXIUCoocyNjCMfQPmhmWho4fPPYt6Ux7bOfazofKTlMvXJXiPm7OdgjskFWfFK
jWH/aXNN9thutEw52tnKzzbgpg7d4NLBrTgnyzYk1uufwaM+ducftby0NXlnLjle
6XcCAwEAAaAAMA0GCSqGSIb3DQEBCwUAA4GBACCnOkbwKi03tgvGXtBXJaTcp9Ft
wBbLP7ddcz2Hja4Sz1mgtEbqYJRuRmW4TXvGzWwZSQSG6Q34g1FT+65balKsrrkc
HNacfGgDzSTVprElX8b9o8bY/Ed4RcUUu54h/2yBliXTKkUyjJktbP69psiKb6JR
+O73Kanewj6ebvMf
-----END CERTIFICATE REQUEST-----
'''
    ssl_data = {'name':"abcd",'certificate':{'certificate_signing_request':sign}}
    post_data = api.post('sslkeyandcertificate', data = ssl_data)


    #api.delete('sslkeyandcertificate/%s'%(obj['uuid']))
