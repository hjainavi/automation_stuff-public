# -*- coding: utf-8 -*-
from avi.sdk.avi_api import ApiSession
import argparse, urllib, json, sys, time, requests
from concurrent.futures import ThreadPoolExecutor
requests.packages.urllib3.disable_warnings()

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--reset', action="store_true", default=False, help='reset pool to default 500 server')
    args = parser.parse_args()
    pool_url = 'pool/pool-e45c7b89-937d-4349-8528-909da440b57f/' 
    ip = '10.50.58.177'
    user='admin'
    password='admin'
    tenant='admin'
    version='18.2.7'
   
    if args.reset:
        api = ApiSession.get_session(ip, user, password, tenant=tenant, api_version=version)
        config = json.loads(api.get(pool_url).text)
        print len(config['servers'])
        new_servers = []
        for server in config['servers']:
            if server['port'] < 1010:
                new_servers.append(server)
        config['servers'] = new_servers
        resp = api.put(pool_url, data=config, params={'resetting':True})
        print len(json.loads(resp.text)['servers'])
        sys.exit(0)
    
    
    ip1 = "10.160.90"
    ip2 = "10.160.91"
    backend_ip_start = 101
    num_backend_vs = 100
    list_of_port_http = []
    for i in range(1010,2001):
        list_of_port_http.append(str(i))

    def generate_server_ip_port():
        server_dict = []
        count = 0
        for k in list_of_port_http:
            for i in [ip1, ip2]:
                for j in range(backend_ip_start,backend_ip_start + num_backend_vs):
                    count += 1
                    yield (i+"."+str(j),k,count)


    newheaders = {'Content-Type': 'application/json',
             'X-AVI-TENANT': 'admin',
              'X-AVI-VERSION': '18.2.7'}

    url_pool = "https://10.50.58.177/api/pool/pool-e45c7b89-937d-4349-8528-909da440b57f/" 

    ip_generator = generate_server_ip_port()

    def call_patch_thread(full_url,data):
        print full_url
        print data
        requests.patch(full_url, data=data, auth=('admin','admin'), verify=False, headers=newheaders, timeout=2)

    TOTAL_PATCH_REQUESTS_PER_MIN = 40
    TOTAL_TIME_IN_MIN = 20
    # requests spread out evenly
    #40/60  2 req every 3 secs

    executor = ThreadPoolExecutor(20)
    curr_time = time.time()
    for i in range(TOTAL_PATCH_REQUESTS_PER_MIN*TOTAL_TIME_IN_MIN):
        ip , port , number = ip_generator.next()
        data = json.dumps({"add": {"servers":[{"ip":{"type":"V4", "addr":ip},"port":port}]}})
        #print data
        number = "22-05-20_17:28" + str(number)
        full_url = url_pool + "?number=" + str(number)
        #print full_url
        try:
            executor.submit(call_patch_thread,full_url,data)
        except:
            pass
        if (i+1) % 2 == 0:
            pass
            time.sleep(3)
        
    print "total time %s"%(time.time()-curr_time)



