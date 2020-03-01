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
    parser.add_argument('-v', '--version', help='controller ip')

    args = parser.parse_args()
    api = ApiSession.get_session(args.controller_ip, args.user, args.password,
                                 tenant=args.tenant,api_version=args.version)
    
    obj = api.get('vrfcontext', None)

    import ipdb;ipdb.set_trace()
    put_data = api.put_by_name('systemconfiguration',None, data = obj)

    #api.delete('sslkeyandcertificate/%s'%(obj['uuid']))
