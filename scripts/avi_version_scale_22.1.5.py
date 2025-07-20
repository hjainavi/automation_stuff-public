import requests
import json
import copy
import sys
import random
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib3



urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
c_uri = '100.65.11.179'
uri_base = 'https://' + c_uri + '/'

def do_login(username, password, tenant=None):
    data = {'username':username, 'password':password}
    headers = {
        "Content-Type": "application/json",
        "X-Avi-Version": "22.1.3"
    }
    headers.update({'X-Avi-Tenant':tenant}) if tenant else None
    login = requests.post(uri_base+'login', data=json.dumps(data), headers=headers, verify=False)
    if login.status_code not in [200,201]:
        print(login.text)
        sys.exit(1)
    headers['X-CSRFToken'] = login.cookies['csrftoken']
    headers['Referer'] = uri_base
    return login, headers

def get_application_profile(Nheaders, cookies, tenant=None):
    headers = copy.deepcopy(Nheaders)
    headers.update({'X-Avi-Tenant':tenant}) if tenant else None
    r = requests.get(uri_base+'api/applicationprofile?name=appl-t1',verify=False, headers=headers, cookies=cookies)
    if r.status_code not in [200,201]:
        print("get APPLI",r.text)
        return
    if len(r.json()['results']) == 0:
        print("no application profile 'appl-t1' found") 

def get_http_policy(Nheaders, cookies, tenant=None):
    headers = copy.deepcopy(Nheaders)
    headers.update({'X-Avi-Tenant':tenant}) if tenant else None
    r = requests.get(uri_base+'api/httppolicyset?name=httppol-t1',verify=False, headers=headers, cookies=cookies)
    if r.status_code not in [200,201]:
        print("get HTTPPOL", r.text)
        return
    if len(r.json()['results']) == 0:
        print("no http policy 'http-t1' found")

def get_ssl_profile(Nheaders, cookies, tenant=None):
    headers = copy.deepcopy(Nheaders)
    headers.update({'X-Avi-Tenant':tenant}) if tenant else None
    r = requests.get(uri_base+'api/sslprofile?name=System-Standard',verify=False, headers=headers, cookies=cookies)
    if r.status_code not in [200,201]:
        print("get sslprofile", r.text)
        return
    if len(r.json()['results']) == 0:
        print("no ssl profile found")

def put_pool(Nheaders, cookies, tenant=None):
    headers = copy.deepcopy(Nheaders)
    headers.update({'X-Avi-Tenant': tenant}) if tenant else None

    r = requests.get(uri_base+'api/pool?name=pool-t1',verify=False, headers=headers, cookies=cookies)
    if r.status_code not in [200,201]:
        print("get Pool", r.text)
        return
    if len(r.json()['results']) == 0:
        print("no pool found")
        return
    data = r.json()['results'][0]
    data['enabled'] = not data['enabled']
    r = requests.put(uri_base+'api/pool/'+data['uuid'], data=json.dumps(data), verify=False, headers=headers, cookies=cookies)
    if r.status_code not in [200,201]:
        print("pool PUT",r.text)

def put_vrfcontext(Nheaders, cookies, tenant=None):
    headers = copy.deepcopy(Nheaders)
    headers.update({'X-Avi-Tenant': tenant}) if tenant else None
    r = requests.get(uri_base+'api/vrfcontext?name=global',verify=False, headers=headers, cookies=cookies)
    if r.status_code not in [200,201]:
        print(r.text)
        return
    if len(r.json()['results']) == 0:
        print("no vrfcontext found")
        return
    data = r.json()['results'][0]
    data['lldp_enable'] = not data['lldp_enable']
    r = requests.put(uri_base+'api/vrfcontext/'+data['uuid'], data=json.dumps(data), verify=False, headers=headers, cookies=cookies)
    if r.status_code not in [200,201]:
        print("vrf PUT", r.text)
    
     

def main():
    
    login, headers = do_login('u1','u1')
    cookies = login.cookies
    list_of_calls = [
        ("get_application_profile (t1)", lambda: get_application_profile(headers, cookies, tenant=None)),
        ("get_http_policy (t1)", lambda: get_http_policy(headers, cookies, tenant=None)),
        ("get_ssl_profile (from t1)", lambda: get_ssl_profile(headers, cookies, tenant=None)),
        ("put_pool (t1)", lambda: put_pool(headers, cookies, tenant=None)),
        ("put_vrfcontext (admin)", lambda: put_vrfcontext(headers, cookies, tenant='admin'))
    ]

    running_tasks = set()
    lock = threading.Lock()

    def worker(func, index, name):
        """Wrapper to execute the function and manage running_tasks set."""
        #print(f"Thread for task '{name}' (index: {index}) started.")
        try:
            func()
        except Exception as e:
            pass
            #print(f"Task '{name}' (index: {index}) failed with error: {e}")
        finally:
            with lock:
                running_tasks.remove(index)
            #print(f"Thread for task '{name}' (index: {index}) finished.")
        return f"Task '{name}' (index: {index}) finished successfully."

    #print("Starting concurrent API calls for 30 seconds...")
    with ThreadPoolExecutor(max_workers=len(list_of_calls)) as executor:
        futures = []
        end_time = time.time() + 30
        while time.time() < end_time:
            with lock:
                available_tasks_indices = [i for i in range(len(list_of_calls)) if i not in running_tasks]

            if not available_tasks_indices:
                time.sleep(0.1)
                continue

            task_index = random.choice(available_tasks_indices)

            with lock:
                if task_index in running_tasks:
                    continue
                running_tasks.add(task_index)

            name, func = list_of_calls[task_index]
            #print(f"Submitting task '{name}' (index: {task_index})")
            future = executor.submit(worker, func, task_index, name)
            futures.append(future)

            time.sleep(random.uniform(0.1, 0.5))

        #print("\n--- Time's up! Waiting for all submitted tasks to complete. ---")
        for future in as_completed(futures):
            try:
                #print(future.result())
                future.result()
            except Exception as e:
                print(f"A task execution resulted in an error: {e}")


    

if __name__ == "__main__":
    main()


"""

try with x-avi-tenant switch with same session , then without any tenant same session , then with different sessions
vrf put admin
get application t1
get httppolicy t1
get admin-sslprofile from t1
pool put t1

""" 