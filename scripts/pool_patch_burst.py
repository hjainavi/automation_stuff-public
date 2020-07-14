import json, time, requests
import random
import threading
from avi.util.login import login
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import multiprocessing
import tempfile, datetime

class server_addtion_pool:
    def __init__(self,*args,**kwargs):
        self.lock = threading.Lock()
        self.ctrl = kwargs['ctrl']
        self.poolid = kwargs['poolid']
        self.ctrluser = kwargs.get('ctrluser','admin')
        self.ctrlpasswd = kwargs.get('ctrlpasswd','avi123')
        self.cloud = kwargs.get('cloud','Default-Cloud')
        self.tenant_name = kwargs.get('tenant_name','admin')
        self.delete_percent = kwargs.get('delete_percent',20) # % delete of burst size
        self.burst_size = kwargs.get('burst_size',10) # num req
        self.cool_down_interval = kwargs.get('cool_down_interval_secs',1) # secs
        self.total_servers_to_add = kwargs.get('total_servers_to_add',100) # total servers to add
        self.time_sleep = kwargs.get('time_sleep',0)
        self.wait_until_prev_burst_req_completes = kwargs.get('wait_until_prev_burst_req_completes',False) # Flag to wait until all the req from prev burst completes, then only proceed.
        self.log_file_path = kwargs['log_file_path']
        self.final_server_list_json = kwargs['final_server_list_json']
        self.aysnc_list = self.generate_server_ip_port()
        self.cookies , self.headers , _ = login('https://%s'%self.ctrl, user=self.ctrluser, password= self.ctrlpasswd)
        self.headers['X-Avi-Cloud'] = self.cloud
        self.headers['timeout'] = '181'
        self.net_servers_added = []
        self.delete_count = 0
        self.delete_dummy_counter = 0
        self.delete_ratio = self.burst_size*self.delete_percent/100.0
        self.total_added = 0
        self.threads = []
        self.thread_safe_print("================= STARTING =========================")
        self.thread_safe_print(str(datetime.datetime.now()))
        self.thread_safe_print(self.headers)
    

    def generate_server_ip_port(self):
        ip2 = "10.160.91"
        backend_ip_start = 101
        num_backend_vs = 100
        list_of_port_http = []
        for i in range(1010,2001):
            list_of_port_http.append(str(i))
        server_dict = []
        count = 0
        for k in list_of_port_http:
            for i in [ip2]:
                for j in range(backend_ip_start,backend_ip_start + num_backend_vs):
                    server_dict.append([i+"."+str(j),k,count])
                    count += 1
        return server_dict


    def thread_safe_print(self, *args, **kwargs):
        with self.lock:
            with open(self.log_file_path,'a') as f:
                if args and kwargs:
                    f.write(str(args))
                    f.write("\n")
                    f.write(str(kwargs))
                    f.write("\n")
                elif args:
                    f.write(str(args))
                    f.write("\n")
                elif kwargs:
                    f.write(str(kwargs))
                    f.write("\n")
                else:
                    f.write("\n")
                    f.write("\n")

    def do_pool_del_patch_thread(self,ip_addr,port,count,time_sleep):
        data = {'delete':
                    {'servers': []}
        }
        data['delete']['servers'] = ({'enabled': 'true','ip': {'addr': ip_addr, 'type': 'V4'},'port': int(port),'ratio': 1})

        time.sleep(time_sleep)
        #start_time = time.time()
        #self.thread_safe_print("===delete=== do_pool_patch_thread =====",ip_addr,port,count,time_sleep)

        #self.thread_safe_print("IP: %s PORT:%s"%(ip_addr, port))
        i = 0
        while True:
            patch_call = requests.patch('https://%s/api/pool/%s' % (self.ctrl, self.poolid),
                            json.dumps(data), cookies=self.cookies, headers=self.headers, verify= False)
            if patch_call.status_code in [200, 202]:
                break
            i += 1
            time.sleep(10*6 + random.randint(1, 90))
        #end_time = time.time()
        #self.thread_safe_print("TOTAL TIME %s"%str(round(end_time-start_time)))
        if patch_call.status_code in [200, 202]:
            self.thread_safe_print("=== DELETE PASS . SERVER IP %s PORT %s TRY %s COUNT %s STATUS %s"%(ip_addr, port, str(i + 1), str(count), patch_call.status_code))
        else:
            
            self.thread_safe_print("=== DELETE FAIL. SERVER IP %s PORT %s\nPATCH CALL status %s TRY %s COUNT %s"%(ip_addr, port, patch_call.status_code,str(i+1), str(count)))


    def do_pool_patch_thread(self,ip_addr,port,count,time_sleep, **kwargs):
        data = {'add':
                    {'servers': []}
        }
        for i in range(len(ip_addr)):
            data['add']['servers'] = ({'enabled': 'true','ip': {'addr': ip_addr[i], 'type': 'V4'},'port': int(port[i]),'ratio': 1})
            self.net_servers_added.append([ip_addr[i], port[i]])

        time.sleep(time_sleep)
        #start_time = time.time()
        #self.thread_safe_print("START TIME %s\t\t IP: %s PORT:%s"%(str(start_time), ip_addr, port))
        i = 0
        while True:
            patch_call = requests.patch('https://%s/api/pool/%s' % (self.ctrl, self.poolid),
                            json.dumps(data), cookies=self.cookies, headers=self.headers, verify= False)
            if patch_call.status_code in [200, 202]:
                break
            i += 1
            time.sleep(10*6 + random.randint(1, 90))
        #end_time = time.time()
        #self.thread_safe_print("TOTAL TIME %s"%str(round(end_time-start_time)))
        if patch_call.status_code in [200, 202]:
            self.thread_safe_print("ADD PASS . SERVER IP %s PORT %s TRY %s COUNT %s STATUS %s"%(ip_addr, port, str(i + 1), str(count), patch_call.status_code))
        else:
            
            self.thread_safe_print("ADD FAIL. SERVER IP %s PORT %s\nPATCH CALL status %s TRY %s COUNT %s"%(ip_addr, port, patch_call.status_code,str(i+1), str(count)))


    def burst_send_patches(self,total_burst_list):
        burst_threads = []
        for single_req in total_burst_list:
            # Setting thread name as burst_{count} 
            burst_threads.append(threading.Thread(name= 'burst_'+ str(single_req[2]), target=self.do_pool_patch_thread, args=(single_req)))
        #self.thread_safe_print("=====",net_servers_added,delete_count,burst_size,delete_dummy_counter)
        if self.net_servers_added:
            self.delete_dummy_counter += self.delete_ratio
            if self.delete_dummy_counter>=1.0:
                delete_servers = []
                while True:
                    delete_servers.append(self.net_servers_added.pop(0))
                    if len(delete_servers)>=int(self.delete_dummy_counter):
                        break
                    delete_servers.append(self.net_servers_added.pop(-1))
                    if len(delete_servers)>=int(self.delete_dummy_counter):
                        break
                for single_req in delete_servers:
                    self.delete_count+=1
                    burst_threads.append(threading.Thread(name= 'burst_delete_'+ str(self.delete_count), target=self.do_pool_del_patch_thread, args=(single_req+ [self.delete_count, self.time_sleep])))
                self.thread_safe_print("total_deleted = %s "%self.delete_count)
                self.delete_dummy_counter = 0
        for t in burst_threads:
            t.start()
        self.thread_safe_print("All patch bursts thread created.")
        if self.wait_until_prev_burst_req_completes:
            for t in burst_threads:
                t.join()

    def start_work(self):
        while self.total_added < self.total_servers_to_add:
            # These many threads need to be created.
            self.threads = []
            total_burst_list = [[]]
            data_list = self.aysnc_list[self.total_added:(self.total_added + self.burst_size)]
            # Construct burst data
            for burst_req in range(self.burst_size):
                final_list = [[data_list[burst_req][0]], [data_list[burst_req][1]], self.total_added +burst_req +1, self.time_sleep]
                total_burst_list[0].append(final_list)
            new_thread = threading.Thread(target=self.burst_send_patches, args=(total_burst_list))
            self.threads.append(new_thread)
            for t in self.threads:
                t.start()
            for t in self.threads:
                t.join()

            self.total_added += self.burst_size
            self.thread_safe_print("total_added = %s "%self.total_added, "total_servers_to_add = %s "%self.total_servers_to_add)
            # Sleep for cooldown time
            self.thread_safe_print("Sleeping for cooldown time: %s "%self.cool_down_interval)
            time.sleep(self.cool_down_interval)
            self.thread_safe_print()

        self.thread_safe_print("All burst threads completed. Checking to see if there are single patch req threads")
        # Wait until all the single req threads completes
        for single_req_threads in threading.enumerate():
            t_name = single_req_threads.getName()
            if 'burst' in t_name:
                self.thread_safe_print("Found one thread. %s."%t_name)
                single_req_threads.join()
        self.thread_safe_print("All single thread jobs completed.")
        self.thread_safe_print("=============== ENDING ==========================")
        self.thread_safe_print()

        with open(self.final_server_list_json,"w") as f:
            final_dict = {self.poolid:[]}
            for i in self.net_servers_added:
                final_dict[self.poolid].append({'ip':i[0],'port':int(i[1])})    
            json.dump(final_dict,f,indent=4)

def initiate_server_addtion_pool(**kwargs):
    obj = server_addtion_pool(**kwargs)
    obj.start_work()


configurations = [
        {
            "ctrl":"10.79.169.176",
            "poolid":"pool-de844636-685f-4d40-9584-fb186494aa77",
            "ctrluser":"admin",
            "ctrlpasswd":"avi123",
            "cloud":"Default-Cloud",
            "tenant_name":"admin",
            "delete_percent":20,
            "burst_size":10,
            "cool_down_interval_secs":1,
            "total_servers_to_add":30,
            "wait_until_prev_burst_req_completes":False,
            "log_file_path":"/root/test123.log",
            "final_server_list_json":"/root/test123_1.json"
        },
        {
            "ctrl":"10.79.169.176",
            "poolid":"pool-0080f211-e42b-486b-a334-0908758ad6dc",
            "ctrluser":"admin",
            "ctrlpasswd":"avi123",
            "cloud":"Default-Cloud",
            "tenant_name":"admin",
            "delete_percent":20,
            "burst_size":10,
            "cool_down_interval_secs":1,
            "total_servers_to_add":30,
            "wait_until_prev_burst_req_completes":False,
            "log_file_path":"/root/test345.log",
            "final_server_list_json":"/root/test345_1.json"
        }
    ]

proc_list = []
for config in configurations:
    p = multiprocessing.Process(target=initiate_server_addtion_pool,kwargs=config)
    proc_list.append(p)
    p.start()

for proc in proc_list:
    proc.join()
