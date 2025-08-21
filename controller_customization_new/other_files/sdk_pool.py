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
    name = "test_"
    for i in range(201):
        name_new = name+str(i)
        post_data = {"name":name_new}
        #post_resp = api.post('pool', data=post_data)
        #print ("post = %s "%post_resp.status_code)

    get_resp = api.get('pool?fields=name&page_size=-1')
    #get_resp = api.get('pool?fields=name&page=2')
    print(json.dumps(json.loads(get_resp.content),indent=4))

    for uuid in json.loads(get_resp.content):
        #delete_resp = api.delete('pool', uuid)
        #print ("delete = %s "%delete_resp.status_code)
        pass
