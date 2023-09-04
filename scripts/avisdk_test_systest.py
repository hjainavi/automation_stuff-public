from avi.sdk.avi_api import ApiSession
import ipdb,json,requests
from concurrent.futures import ThreadPoolExecutor
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


api = ApiSession.get_session("localhost", "admin", "avi123", tenant="admin")

data_wafcrs = api.get("wafcrs?page_size=-1")
#data_pool = api.get("pool")
for d in data_wafcrs.json()['results']:
    print(d)


#api.delete("pool")

'''
fqdn_ip ={
        "10.140.19.101": "avi01.abc",
        "10.140.19.102": "avi02.abc",
        "10.140.19.103": "avi03.abc",
        "10.140.19.104": "avi04.abc",
        "10.140.19.105": "avi05.abc",
        "10.140.19.106": "avi06.abc",
        "10.140.19.107": "avi07.abc",
        "10.140.19.108": "avi08.abc",
        "10.140.19.109": "avi09.abc",
        "10.140.19.110": "avi10.abc",
        "10.140.19.111": "avi11.abc",
        "10.140.19.112": "avi12.abc",
        "10.140.19.113": "avi13.abc",
        "10.140.19.114": "avi14.abc",
        "10.140.19.115": "avi15.abc",
        "10.140.19.116": "avi16.abc",
        "10.140.19.117": "avi17.abc",
        "10.140.19.118": "avi18.abc",
        "10.140.19.119": "avi19.abc",
        "10.140.19.120": "avi20.abc",
}

def put_pool(data_pool,uuid):
    print("uuid ",uuid)
    api.put("pool/%s"%(uuid),data=data_pool)

config = json.loads(data_pool.text)

with ThreadPoolExecutor(max_workers=20) as executor:
    for data_pool in config['results']:
        uuid = data_pool['uuid']
        new_servers = []
        all_fqdns = True
        if not data_pool.get('servers',False):
            print("no servers ====== ",data_pool['uuid'])
            continue
        for server in data_pool['servers']:
            fqdn = fqdn_ip[server['ip']['addr']]
            new_servers.append({"hostname":fqdn,"resolve_server_by_dns":True})
            if not server['resolve_server_by_dns']:
                all_fqdns=False
        if not all_fqdns:
            print(uuid)
        #data_pool['servers']=new_servers
        #executor.submit(put_pool,data_pool,uuid)


'''