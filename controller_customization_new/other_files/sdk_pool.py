from avi.sdk.avi_api import ApiSession
import argparse, json
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib3

urllib3.disable_warnings()


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--user', help='controller user',
                        default='admin')
    parser.add_argument('-p', '--password', help='controller user password',
                        default='avi123$%')
    parser.add_argument('-t', '--tenant', help='tenant name',
                        default='admin')
    parser.add_argument('-c', '--controller_ip', help='controller ip')
    parser.add_argument('-v', '--version', help='controller ip')

    args = parser.parse_args()
    api = ApiSession.get_session(args.controller_ip, args.user, args.password,
                                 tenant=args.tenant,api_version=args.version)
    

    get_all_vs = api.get('virtualservice?fields=uuid&page_size=-1')
    all_vs_uuids = [str(rec['uuid']) for rec in json.loads(get_all_vs.content)['results']]
    
    def update_vs(key_str_add, uuid):
        '''Update a single virtual service with markers'''
        try:
            vs_data = api.get('virtualservice/%s'%(uuid))
            vs_data_json = json.loads(vs_data.content)
            vs_data_json["markers"] = [{"key":"cluster_%s"%(key_str_add), "value":["cluster_%s"%(key_str_add)]}]
            vs_put_resp = api.put('virtualservice/%s'%(uuid), data=vs_data_json)
            if vs_put_resp.status_code != 200:
                print("error updating vs %s"%(uuid))
                return False
            print(f"cluster id == cluster_%s"%(key_str_add))
            return True
        except Exception as e:
            print(f"Exception updating vs {uuid}: {e}")
            return False

    key_str_add = 1
    # Use ThreadPoolExecutor for concurrent updates
    with ThreadPoolExecutor(max_workers=25) as executor:
        futures = {}
        for i, uuid in enumerate(all_vs_uuids):
            if i % 10 == 0:
                key_str_add += 1
            futures[executor.submit(update_vs, key_str_add, uuid)] = uuid
        for future in as_completed(futures):
            uuid = futures[future]
            try:
                result = future.result()
                if result:
                    pass
            except Exception as e:
                print(f"Exception occurred for vs {uuid}: {e}")