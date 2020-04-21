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
    api = ApiSession.get_session(args.controller_ip, args.user, args.password, tenant=args.tenant,api_version=args.version)
    
    imp_data =  {'configuration' :{"Pool": [
        {
            "server":[{'ip':{'type':'V8'}}]
        }
    ]}}
    
    post_data = api.post('configuration/import', data=imp_data)
    import ipdb;ipdb.set_trace()
    a=1







