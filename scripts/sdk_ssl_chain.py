from avi.sdk.avi_api import ApiSession
import argparse,json
from ssl_certs import _INTERMEDIATE_CERT, _INTERMEDIATE_CERT1, _APP_KEY1, _APP_CERT1
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

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
    
    ssl_data = {
        "name": "app1",
        "key": _APP_KEY1,
        "certificate":{"certificate":_APP_CERT1},
        "type": "SSL_CERTIFICATE_TYPE_VIRTUALSERVICE",
        "key_passphrase": "avi123"
    }
    post_data_app1 = api.post('sslkeyandcertificate', data = ssl_data)
    config =  json.loads(post_data_app1.text)
    print config['name']
    print config['uuid']

    ssl_data = {
        "name": "int1",
        "type": "SSL_CERTIFICATE_TYPE_CA",
        "certificate":{"certificate":_INTERMEDIATE_CERT1}
    }
    post_data_int1 = api.post('sslkeyandcertificate', data = ssl_data)
    config =  json.loads(post_data_int1.text)
    print config['name']
    print config['uuid']

    ssl_data = {
        "name": "ca",
        "type": "SSL_CERTIFICATE_TYPE_CA",
        "certificate":{"certificate":_INTERMEDIATE_CERT}
    }
    post_data_ca = api.post('sslkeyandcertificate', data = ssl_data)
    config =  json.loads(post_data_ca.text)
    print config['name']
    print config['uuid']

    import pdb;pdb.set_trace()
    post_data_ca = json.loads(post_data_ca.text)
    api.delete('sslkeyandcertificate/%s/?force_delete=True'%(post_data_ca['uuid']))
   
    import ipdb;ipdb.set_trace()
    post_data_int1 = json.loads(post_data_int1.text)
    api.delete('sslkeyandcertificate/%s/?force_delete=True'%(post_data_int1['uuid']))


