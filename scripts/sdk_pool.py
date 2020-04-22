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
    import ipdb;ipdb.set_trace()    
    get_data = api.get_object_by_name('pool', name='abcde-poo')
    server = {'ip':{'addr':'1.1.1.1/24', 'type':'V4'} ,'enabled':True}
    get_data['servers'].append(server)
    uuid = get_data['uuid']
    put_data = api.put('pool/%s'%(uuid), data=get_data) 

