from avi.sdk.avi_api import ApiSession
import argparse, json


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--user', help='controller user',
                        default='admin')
    parser.add_argument('-p', '--password', help='controller user password',
                        default='avi123')
    parser.add_argument('-t', '--tenant', help='tenant name',
                        default='admin')
    parser.add_argument('-c', '--controller_ip', help='controller ip')
    parser.add_argument('-v', '--version', help='controller ip')

    args = parser.parse_args()
    api = ApiSession.get_session(args.controller_ip, args.user, args.password,
                                 tenant=args.tenant,api_version=args.version)
    post_data = {
            'name':'test123',
            'servers':[{'ip':{'addr':'0.0.0.0', 'type':'V4'} ,'enabled':True, 'hostname':'abc.def', 'resolve_server_by_dns':True}]
        }
    import ipdb;ipdb.set_trace()    
    post_resp = api.post('pool', data=post_data)
    print ("post = %s "%post_resp.status_code)
    uuid = json.loads(post_resp.text)['uuid']
    delete_resp = api.delete('pool/%s'%(uuid)) 
    print ("delete = %s "%delete_resp.status_code)
