# -*- coding: utf-8 -*-
from avi.sdk.avi_api import ApiSession
import argparse, urllib, json

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
    
    #import ipdb; ipdb.set_trace()
    #name = "popoolgroupa|;+, ''-_.*()!%?$@&=#b77ol77AlmaWeb_St\xf6rung".decode('utf-8')
    name = ['popoo|;+, -_.*()!%?$@&=#lgroeb_Störung', 'pool|;+, -_.*()!%?$@&=#lgroeb', 'lgroeb_Störung',
            "ab|;+,-_.*()!%?$@&=#98pool_ÜNICöDE"]
    for i in name:
        #name_encoded = urllib.quote(name)
        pool_data = {'name':i}
        post_data = api.post('pool', data = pool_data)
        print post_data.text
    
    name1 = urllib.quote(name[3])
    print name1
    get_name_data = api.get('pool?name=%s'%(name1))
    print get_name_data.text
    ##json_get_name_data = json.loads(get_name_data.text)['results'][0]
    #uuid = json_get_name_data['uuid']
    #put_res = api.put('pool/%s'%(uuid), data = json_get_name_data)
    #pass
    #api.delete('sslkeyandcertificate/%s'%(obj['uuid']))    
