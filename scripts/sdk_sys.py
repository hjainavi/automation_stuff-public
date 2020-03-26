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
    data = {'name':'abcd111'}
    post_data = api.post('pool',data=data)
    uuid_abcd111 = json.loads(post_data.text)['uuid']
    #data = {'model_name':'virtualservice','data':{'uuid':uuid}}
    data = {'data':[
            {'model_name':'pool', 'data':{'name':'abc222'}, 'method':'post'}, 
            {'model_name':'pool', 'data':{'uuid':uuid_abcd111}, 'method':'delete'},
            {'model_name':'poolgroup', 'data':{'name':'poolgroup111','members':[{'ratio':1, 'pool_ref':'/api/pool?name=abc222'}]}, 'method':'post'}
            ]}
    try:
        post_data = api.post('macrostack', data=data)
        if post_data.status_code == 201:
            uuid_poolgroup111 = api.get_object_by_name('poolgroup', 'poolgroup111', 'admin')['uuid']
            uuid_poolabc222 = api.get_object_by_name('pool', 'abc222', 'admin')['uuid']
            api.delete('poolgroup/%s'%(uuid_poolgroup111))
            api.delete('pool/%s'%(uuid_poolabc222))
    finally:
        api.delete('pool/%s'%(uuid_abcd111))


    #api.delete('sslkeyandcertificate/%s'%(obj['uuid']))
