#!/usr/bin/env python3
try:
    import pyVim,sys
except ImportError:
    print ("do -->> pip3 install --upgrade pyvmomi")
    sys.exit(1)
try:
    from tabulate import tabulate
except ImportError:
    print ("do -->> pip3 install tabulate")
    sys.exit(1)
from pyVim.connect import Disconnect,SmartConnectNoSSL
from pyVmomi import vim
from socket import inet_aton, inet_ntoa
import random,time,atexit
from concurrent.futures import ThreadPoolExecutor
#import tarfile
#import xmltodict
import subprocess
import shlex
#import argparse
import os
import requests
import time
import json
import re
import urllib3
import ipaddress
import random
urllib3.disable_warnings()
from fabric.api import env, put, sudo, cd
from tabulate import tabulate

ALL_RESERVED_IPS = ["10.102.96.175","10.102.96.176", "100.65.9.177", "100.65.9.178", "100.65.9.179", "100.65.9.180", "100.65.9.181", "100.65.9.182", "100.65.9.183"]
VCENTER_IP = "blr-01-vc13.oc.vmware.com"
VCENTER_USER = "aviuser1"
VCENTER_PASSWORD = "AviUser1234!."
VCENTER_DATACENTER_NAME = "blr-01-vc13"
VCENTER_CLUSTER_NAME = "blr-01-vc13c01"
VCENTER_DATASTORE_NAME = "blr-01-vc13c01-vsan"
VCENTER_FOLDER_NAME = "harshjain"
DEV_VM_IP = "10.102.96.175"
VCENTER_MANAGEMENT_MAP = {
                            "blr-01-avi-dev-IntMgmt":{
                                "name":"blr-01-avi-dev-IntMgmt",
                                "subnet":"100.65.0.0/20",
                                "mask":"20",
                                "gateway":"100.65.15.254"
                            },
                            "blr-01-nsxt02-avi-mgmt":{
                                "name":"blr-01-nsxt02-avi-mgmt",
                                "subnet":"10.102.96.0/22",
                                "mask":"22",
                                "gateway":"10.102.99.254"
                            }
                        }
VCENTER_DNS_SERVERS = ["10.102.0.193", "10.102.0.195"]
VCENTER_NTP = "time.vmware.com"
VCENTER_PORT_GROUP = "blr-01-avi-66-66"
VCENTER_SERVER_IP = "100.66.66.3"


DEFAULT_SETUP_PASSWORD = "58NFaGDJm(PJH0G"
DEFAULT_PASSWORD = "avi123"

def connect(vcenter_ip=VCENTER_IP, user=VCENTER_USER, pwd=VCENTER_PASSWORD ,exit_on_error=True):
    try:
        si= SmartConnectNoSSL(host=vcenter_ip, user=user, pwd=pwd)#, sslContext=s)
        atexit.register(Disconnect,si)
        return si
    except:
        print("Unable to connect to %s" % vcenter_ip)
        raise
        if exit_on_error:
            sys.exit(1)
        else:
            return False

def fill_vms_table(vms_table,virtual_m):
    try:
        folder_name = virtual_m.parent.name
        if virtual_m.config and not virtual_m.config.template:
            if virtual_m.runtime.powerState == 'poweredOff':
                vms_table[(folder_name,virtual_m.name)] = {'state':'POWER OFF','ip_network':[["",""]]}
            else:
                vms_table[(folder_name,virtual_m.name)] = {'state':'POWER ON','ip_network':[]}
                if len(virtual_m.guest.net)>0:
                    for ip_net in virtual_m.guest.net:
                        for ip_addr in ip_net.ipAddress:
                            if not ip_addr or ":" in ip_addr:
                                continue
                            else:
                                vms_table[(folder_name,virtual_m.name)]['ip_network'].append([ip_addr, ip_net.network])
                                
        elif virtual_m.config and virtual_m.config.template:
            vms_table[(folder_name,virtual_m.name)] = {'state':'TEMPLATE','ip_network':[["",""]]}
        else:
            vms_table[(folder_name,virtual_m.name)] = {'state':'UNKNOWN','ip_network':[["",""]]}

    except:
        raise


if len(sys.argv)==1:
    

    folder_name = VCENTER_FOLDER_NAME
    datacenter_name = VCENTER_DATACENTER_NAME
   
    si = connect()
    vms_table = {} # vms_table[(folder,name)] = {state :template/on/off , ip_network: [[ip,network],]}

    for dc in si.content.rootFolder.childEntity:
        if dc.name == datacenter_name:
            datacenter = dc
    vms = datacenter.vmFolder.childEntity
    for vm in vms:
        '''
        if vm.name == "AviSeFolder" and type(vm) == vim.Folder:
            pass
            # vm.config.vAppConfig.property[1].value, id
        '''
        if vm.name == folder_name and type(vm) == vim.Folder:
            for virtual_m in vm.childEntity:
                if vim.Folder == type(virtual_m):
                    continue
                fill_vms_table(vms_table, virtual_m)
            break
    
    reserved_ips_not_found_in_folder = []
    for val_ip in ALL_RESERVED_IPS:
        found = False
        for folder_name,value in vms_table.items():
            for ip_network_val in value['ip_network']:
                if val_ip == ip_network_val[0]:
                    found = True
        if not found:
            reserved_ips_not_found_in_folder.append(val_ip)

    search = si.RetrieveContent().searchIndex
    for val_ip in reserved_ips_not_found_in_folder:
        vms = list(set(search.FindAllByIp(ip=val_ip,vmSearch=True)))
        for virtual_m in vms:
            fill_vms_table(vms_table, virtual_m)

    ################# FORMING PRINT STRUCTURE #####################

    final_print_vals = [("**VM NAME**", "*STATE*", "**IP**", "*NETWORK*")]
    final_print_vals.append(("","","",""))
    for val_ip in ALL_RESERVED_IPS:
        found = False
        for folder_name,value in vms_table.items():
            for ip_network_val in value['ip_network']:
                if val_ip == ip_network_val[0]:
                    found = True
                    final_print_vals.append((folder_name[1], value['state'], val_ip, ip_network_val[1]))
        if not found:
            final_print_vals.append(("--Free IP--", "-------", val_ip, "------"))

    final_print_vals.append(("","","",""))
    final_print_vals.append(("","","",""))

    for folder_name,value in vms_table.items():
        for ip_network_val in value['ip_network']:
            if ip_network_val[0] not in ALL_RESERVED_IPS:
                final_print_vals.append((folder_name[1], value['state'], ip_network_val[0], ip_network_val[1]))    
    final_print_vals.append(("","","",""))
    print(tabulate(final_print_vals, headers="firstrow", tablefmt="psql"))
        

if 'help' in sys.argv:
    print ("options --> delete 'ip'")
    print ("options --> delete_name 'name'")
    print ("options --> poweroff 'ip'")
    print ("options --> rename 'ip' 'newname'")
    print ("options --> poweron")
    print ("options --> poweron 'name'")
    print ("options --> generate_controller_from_ova")
    print ("options --> configure_raw_controller")
    print ("options --> configure_raw_controller_wo_tmux")
    print ("options --> configure_cloud_vs_se")
    print ("options --> configure_vs")
    print ("options --> flush_db_configure_raw_controller_wo_tmux")
    print ("options --> setup_tmux")


if len(sys.argv)>=3 and sys.argv[1] in ('delete','poweroff'):

    if sys.argv[2]:
        ips = sys.argv[2:]
        si = connect()
        search = si.RetrieveContent().searchIndex
        vms_to_operate_on = []
        for ip in ips:
            vms = list(set(search.FindAllByIp(ip=ip,vmSearch=True)))
            if vms:
                for vm in vms:
                    action_confirm = input("Are you sure you want to %s '%s' with ip = %s ?[Y/N] \n"%(sys.argv[1],vm.name,ip))
                    if action_confirm.lower() == "n":continue
                    if DEV_VM_IP in ip:
                        while True:
                            action_confirm = input("Are you sure you want to delete '%s'  ?[confirm/deny] \n"%(ip))
                            if action_confirm.lower() not in ['confirm','deny']:
                                continue
                            break
                        if action_confirm == 'deny':
                            continue
                    vms_to_operate_on.append((vm,ip))
        for vm,ip in vms_to_operate_on:
            if vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOn:
                print ("powering off ",vm.name," ",ip)
                task = vm.PowerOff()
                while task.info.state not in [vim.TaskInfo.State.success,vim.TaskInfo.State.error]:
                    time.sleep(1)
                print ("power is off.",task.info.state)
            
            if vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOff and sys.argv[1]=='delete':
                print ("deleteing ",vm.name," ",ip)
                task = vm.Destroy()
                while task.info.state not in [vim.TaskInfo.State.success,vim.TaskInfo.State.error]:
                    time.sleep(1)
                print ("vm is deleted.",task.info.state)

if len(sys.argv)==3 and sys.argv[1] == 'delete_name':

    si = connect()
    vm_name = sys.argv[2]
    folder_name = VCENTER_FOLDER_NAME
    datacenter_name = VCENTER_DATACENTER_NAME
    for dc in si.content.rootFolder.childEntity:
        if dc.name == datacenter_name:
            datacenter = dc
    #print (datacenter,datacenter.name)
    vmfolders = datacenter.vmFolder.childEntity
    for folder in vmfolders:
        if folder.name == folder_name:
            for virtual_m in folder.childEntity:
                if virtual_m.name != vm_name:
                    continue
                action_confirm = input("Are you sure you want to delete '%s'  ?[Y/N] \n"%(vm_name))
                if action_confirm.lower() == "n":continue
                if "harsh" in vm_name and "dev" in vm_name:
                    while True:
                        action_confirm = input("Are you sure you want to delete '%s'  ?[confirm/deny] \n"%(vm_name))
                        if action_confirm.lower() not in ['confirm','deny']:
                            continue
                        break
                    if action_confirm == 'deny':
                        continue
                if virtual_m.runtime.powerState == vim.VirtualMachinePowerState.poweredOff:
                    print ("deleteing ",virtual_m.name)
                    task = virtual_m.Destroy()
                    while task.info.state not in [vim.TaskInfo.State.success,vim.TaskInfo.State.error]:
                        time.sleep(1)
                    print ("vm is deleted.",task.info.state)
                else:
                    print ("delete the vm using ip")


if len(sys.argv)==4 and sys.argv[1]=='rename':
    ip = sys.argv[2]
    newname = sys.argv[3]
    si = connect()
    search = si.RetrieveContent().searchIndex
    vms = list(set(search.FindAllByIp(ip=ip,vmSearch=True)))

    for vm in vms:
        rename_confirm = input("Are you sure you want to rename '%s', (%s) with '%s'  ?[Y/N] \n"%(vm.name,ip,newname))
        if rename_confirm.lower() == "n":continue
        print ("renaming  ",vm.name," ",ip," to ",newname)
        task = vm.Rename(newname)
        while task.info.state not in [vim.TaskInfo.State.success,vim.TaskInfo.State.error]:
            time.sleep(1)
        print ("renaming done.",task.info.state)
       
def power_on_vm(virtual_machine_obj):
    vm = virtual_machine_obj
    task = vm.PowerOn()
    while task.info.state not in [vim.TaskInfo.State.success,vim.TaskInfo.State.error]:
        time.sleep(1)
    print ("power on task for vm %s = %s"%(vm.name,task.info.state))


if len(sys.argv) in (2,3) and sys.argv[1]=='poweron':
    if len(sys.argv) == 3:
        vm_name = sys.argv[2]
    else:
        vm_name = ''
    folder_name = VCENTER_FOLDER_NAME
    datacenter_name = VCENTER_DATACENTER_NAME
    si = connect()
    print ("powering on vm in folder %s , datacenter %s "%(folder_name,datacenter_name))
    
    for dc in si.content.rootFolder.childEntity:
        if dc.name == datacenter_name:
            datacenter = dc
    #print (datacenter,datacenter.name)
    vms = datacenter.vmFolder.childEntity
    ip_name_state = {}
    templates = []
    for vm in vms:
        if vm.name == folder_name:
            with ThreadPoolExecutor(max_workers=10) as executor:
                for virtual_m in vm.childEntity:
                    if not virtual_m.config.template:
                        if vm_name:
                            if virtual_m.name != vm_name:
                                continue
                        if virtual_m.runtime.powerState == 'poweredOff':
                            executor.submit(power_on_vm,virtual_m)
                        else:
                            print ("vm %s is already ON"%(virtual_m.name))

##################################################################################
##################################################################################
##################################################################################


def get_headers(controller_ip=None, version="",query_version=False, tenant='admin'):
    headers = {
        "Content-Type": "application/json",
        "X-Avi-Tenant": tenant,
    }
    if query_version:
        # Query the controller version if 'version' is set
        resp = requests.get('https://%s/api/initial-data' % controller_ip,
                            headers={
                                'Content-Type': 'application/json',
                                'X-Avi-Tenant': 'admin'
                            },
                            verify=False)
        if resp.status_code == 200:
            version = resp.json()['version']['Version']
            headers["X-Avi-Version"] = "%s" % version
    else:
        if not version:
            raise Exception("Need controller version")
        headers["X-Avi-Version"] = "%s" % version
    return headers


def wait_until_cluster_ready(c_ip, c_port=None, timeout=1800):
    c_uri = c_ip + ':' + str(c_port) if c_port else c_ip
    uri = 'https://' + c_uri + '/api/cluster/runtime'

    sleep_time = 10
    iters = int(timeout / sleep_time)
    rsp = ''
    for i in range(iters):
        try:
            rsp = requests.get(uri, verify=False)
            print('controller %s' % c_uri)
            print('rsp_code %s' % rsp.status_code)
            #print('rsp_data %s' % rsp.json())
        except:
            print('Get for %s fails. Controller %s' % (uri, c_uri))
            pass

        if rsp and rsp.status_code == 200:
            cluster_state = rsp.json().get('cluster_state', {})
            if cluster_state.get('state') in ['CLUSTER_UP_HA_ACTIVE', 'CLUSTER_UP_NO_HA']:
                print('Found cluster state ACTIVE')
                return True
            else:
                print('cluster state INACTIVE')
        time.sleep(sleep_time)
    raise Exception('Timeout: waited approximately %s sec. and the cluster '
                    'is still not active. controller %s' % (timeout, c_uri))

def set_welcome_password_and_set_systemconfiguration(c_ip, c_port=None,version="" ,timeout=60, current_password=DEFAULT_SETUP_PASSWORD):
    wait_until_cluster_ready(c_ip,c_port)
    c_uri = c_ip + ':' + str(c_port) if c_port else c_ip
    uri_base = 'https://' + c_uri + '/'
    headers = get_headers(controller_ip=c_ip,version=version, tenant='admin')
    print ("login and change password to avi123$%")
    for password in [current_password,"avi123","avi123$%","admin"]:
        data = {'username':'admin', 'password':password}
        login = requests.post(uri_base+'login', data=json.dumps(data), headers=headers, verify=False)
        if login.status_code in [200, 201]:
            current_password = password
            break
        
    time.sleep(1) 
    r = requests.get(uri_base+'api/useraccount', data=json.dumps(data) ,verify=False, headers=headers, cookies=login.cookies)
    data = r.json()
    data.update({'username':'admin','password':"avi123$%" ,'old_password':current_password})
    headers['X-CSRFToken'] = login.cookies['csrftoken']
    headers['Referer'] = uri_base
    r = requests.put(uri_base+'api/useraccount', data=json.dumps(data) ,verify=False, headers=headers, cookies=login.cookies)
    if r.status_code not in [200,201]:
        raise Exception(r.text)
    current_password = "avi123$%"
    time.sleep(1) 
    print ("login and change password to avi123$% -- done")
    print("change systemconfiguration settings")
    r = requests.get(uri_base+'api/systemconfiguration', verify=False, headers=headers ,cookies=login.cookies)
    data = r.json()
    data['portal_configuration']['password_strength_check'] = False
    data['portal_configuration']['allow_basic_authentication'] = True
    data['dns_configuration']['server_list'] = [{'addr':val , 'type':'V4'} for val in VCENTER_DNS_SERVERS]
    data['ntp_configuration']['ntp_servers'] = [{'server': {'addr': VCENTER_NTP, 'type': "DNS"}}]
    data['welcome_workflow_complete']=True
    data['default_license_tier']='ENTERPRISE'

    time.sleep(1) 
    r = requests.put(uri_base+'api/systemconfiguration', data=json.dumps(data) ,verify=False, headers=headers, cookies=login.cookies)
    if r.status_code not in [200,201]:
        raise Exception(r.text)

    print("change systemconfiguration settings -- done")
    print("changing password to avi123")
    time.sleep(1)
    
    r = requests.get(uri_base+'api/useraccount',verify=False, headers=headers, cookies=login.cookies)
    data = r.json()
    data.update({'username':'admin','password':'avi123' ,'old_password':current_password})
    time.sleep(1) 
    r = requests.put(uri_base+'api/useraccount', data=json.dumps(data) ,verify=False, headers=headers, cookies=login.cookies)
    if r.status_code not in [200,201]:
        raise Exception(r.text)

    print("changing password to avi123 -- done")
    print("setting backup default passphrase")
    time.sleep(1) 
    r = requests.get(uri_base+'api/backupconfiguration',verify=False, headers=headers, cookies=login.cookies)
    data = r.json()
    uuid = data['results'][0]['uuid']

    time.sleep(1) 
    r = requests.get(uri_base+'api/backupconfiguration'+'/'+uuid,verify=False, headers=headers, cookies=login.cookies)
    if r.status_code not in [200,201]:
        raise Exception(r.text)
    data = r.json()
    data['backup_passphrase']='avi123'
    
    time.sleep(1) 
    r = requests.put(uri_base+'api/backupconfiguration'+'/'+uuid, data=json.dumps(data) ,verify=False, headers=headers, cookies=login.cookies)
    if r.status_code not in [200,201]:
        raise Exception(r.text)

    r = requests.get(uri_base+'api/controllerproperties',verify=False, headers=headers, cookies=login.cookies)
    if r.status_code not in [200,201]:
        raise Exception(r.text)
    data = r.json()
    data['api_idle_timeout']=1400
    
    time.sleep(1) 
    r = requests.put(uri_base+'api/controllerproperties', data=json.dumps(data) ,verify=False, headers=headers, cookies=login.cookies)
    if r.status_code not in [200,201]:
        raise Exception(r.text)
    
    print("setting backup default passphrase -- done")
    print("setting complete")
   
    
def setup_tmux(c_ip):
    print("Setting Controller with tmux and other packages")
    env.host_string = c_ip
    env.user = "admin"
    env.password = DEFAULT_PASSWORD
    env.sudo_password = DEFAULT_PASSWORD
    env.disable_known_hosts = True
    put("/var/www/html/ctlr_new.tar.gz","/root/",use_sudo=True)
    with cd("/root/"):
        sudo("tar -xvf ctlr_new.tar.gz")
    with cd("/root/controller_customization_new/"):
        sudo("./controller_cust.sh")
    with cd("/root/controller_customization_new/other_files"):
        sudo("./tmux_start_script.sh")
    with cd("/opt/avi/python"):
        sudo("ls")


def flush_db(c_ip,password=DEFAULT_PASSWORD):

    env.host_string = c_ip
    env.user = "admin"
    env.password = password
    env.sudo_password = password
    env.disable_known_hosts = True
    with cd("/root/"):
        sudo("sudo systemctl stop process-supervisor.service && rm /var/lib/avi/etc/flushdb.done && /opt/avi/scripts/flushdb.sh && sudo systemctl start process-supervisor.service")


def get_version_controller_from_ova(ova_path=None):
    if not ova_path:
        version = input("Please Enter Controller Version ? :")
        return version
    
    print("Getting Controller Version from OVA %s"%(ova_path))
    cmd_ova_spec = '/usr/bin/ovftool --schemaValidate %s'%(ova_path)
    ova_specs = subprocess.check_output(shlex.split(cmd_ova_spec),text=True)
    pattern = re.compile('\\nVersion:\s*(\d+\.\d+\.\d+)\\n')
    res = re.findall(pattern,ova_specs)
    if res:
        return res[0]
    else:
        print("Unable to get Controller Version from OVA %s"%(ova_path))
        version = input("Please Enter Controller Version ? :")
        return version


def wait_until_cloud_ready(c_ip, cookies, headers, cloud_uuid, timeout=450):
    c_uri = c_ip
    uri_base = 'https://' + c_uri + '/'

    sleep_time = 10
    iters = int(timeout / sleep_time)
    rsp = ''
    for i in range(iters):
        try:
            uri = uri_base+'api/cloud/%s/runtime'%(cloud_uuid)
            rsp = requests.get(uri,verify=False, headers=headers, cookies=cookies)
        except:
            print('Get for %s fails. Controller %s' % (uri, c_uri))
            pass

        if rsp and rsp.status_code == 200:
            cloud_state = rsp.json().get("network_sync_complete")
            if cloud_state:
                print('Cloud Network Sync Complete')
                return True
            else:
                print('Cloud Network Sync Incomplete')
        time.sleep(sleep_time)
    raise Exception('Timeout: waited approximately %s sec. and the cloud '
                    'is still not active. controller %s' % (timeout, uri))

def setup_vs(c_ip, c_port=None,version="" ,timeout=60, current_password=DEFAULT_PASSWORD):
    c_uri = c_ip
    uri_base = 'https://' + c_uri + '/'
    data = {'username':'admin', 'password':current_password}
    headers = get_headers(controller_ip=c_ip,version=version, tenant='admin')
    login = requests.post(uri_base+'login', data=json.dumps(data), headers=headers, verify=False)
    headers['X-CSRFToken'] = login.cookies['csrftoken']
    headers['Referer'] = uri_base
    r = requests.get(uri_base+'api/cloud',verify=False, headers=headers, cookies=login.cookies)
    for val in r.json()['results']:
        if val['name'] == 'Default-Cloud':
            data = val
            break
    default_cloud_uuid = data['uuid']
    cookies=login.cookies
    print("creating a vs")
    # getting dev020 network uuid
    r = requests.get(uri_base+'api/networksubnetlist/?discovered_only=true&page_size=-1&cloud_uuid=%s'%(default_cloud_uuid),verify=False, headers=headers, cookies=cookies)
    for val in r.json()['results']:
        if VCENTER_PORT_GROUP in val['name']:
            data = val
            break
    network_dev020_uuid = data['uuid']
    network_dev020_subnet = data["subnet"][0]["prefix"]["ip_addr"]["addr"] + "/" + str(data["subnet"][0]["prefix"]["mask"])
    occupied_ips = []
    "https://10.102.65.176/api/cloud/cloud-a1746f89-2f84-4255-9061-8a024d89ca5f/serversbynetwork/?network_uuid=dvportgroup-123-cloud-a1746f89-2f84-4255-9061-8a024d89ca5f&page_size=-1"
    while True:
        r = requests.get(uri_base+'api/cloud/%s/serversbynetwork/?network_uuid=%s&page_size=-1'%(default_cloud_uuid,network_dev020_uuid),verify=False, headers=headers, cookies=cookies)
        try:
            for val in r.json()['results']:
                for guest_nic in val['guest_nic']:
                    for guest_ip in guest_nic['guest_ip']:
                        occupied_ips.append(guest_ip["prefix"]["ip_addr"]["addr"])
            break
        except:
            print("Error: ",r.json())
            time.sleep(10)

    ip_list = list(set([str(ip) for ip in ipaddress.IPv4Network(network_dev020_subnet)]) - set([str(ip) for ip in ipaddress.IPv4Network(network_dev020_subnet.replace("/24","/26"))]))
    ip_list = sorted(ip_list ,  key=lambda x:int(x.split(".")[-1]))[:-1]
    while True:
        vsvip_ip = random.choice(ip_list)
        if vsvip_ip not in occupied_ips:
            break
    data_macro = {
        "model_name": "VirtualService",
        "data": {
            "name":"test_vs",
            "services": [{"port":80}],
            "pool_ref_data":{
                "name":"test_pool",
                "servers": [
                    {
                        "ip": {
                            "type": "V4",
                            "addr": VCENTER_SERVER_IP
                        }
                    }
                ]
            },
            "vsvip_ref_data":{
                "name":"test_vsvip",
                "vip":[
                    {
                        "ip_address":{
                            "type":"V4",
                            "addr":vsvip_ip
                        }
                    }
                ]
            }

        }
    }

    r = requests.post(uri_base+'api/macro', data=json.dumps(data_macro), verify=False, headers=headers, cookies=cookies)
    if r.status_code not in [200,201]:
        raise Exception(r.text)


def setup_cloud_se(c_ip, c_port=None,version="" ,timeout=60, current_password=DEFAULT_PASSWORD):
    c_uri = c_ip + ':' + str(c_port) if c_port else c_ip
    uri_base = 'https://' + c_uri + '/'
    data = {'username':'admin', 'password':current_password}
    headers = get_headers(controller_ip=c_ip,version=version, tenant='admin')
    login = requests.post(uri_base+'login', data=json.dumps(data), headers=headers, verify=False)
    headers['X-CSRFToken'] = login.cookies['csrftoken']
    headers['Referer'] = uri_base
    print("setting up vmware write access cloud")
    r = requests.get(uri_base+'api/cloud',verify=False, headers=headers, cookies=login.cookies)
    for val in r.json()['results']:
        if val['name'] == 'Default-Cloud':
            data = val
            break
    default_cloud_uuid = data['uuid']
    data.update({
        "dhcp_enabled":True,
        "vtype":"CLOUD_VCENTER",
        "vcenter_configuration":{
            "privilege": "WRITE_ACCESS",
            "deactivate_vm_discovery": False,
            "username": VCENTER_USER,
            "vcenter_url": VCENTER_IP,
            "password": VCENTER_PASSWORD,
            "datacenter": VCENTER_DATACENTER_NAME,
            "use_content_lib": False
        }
    })
    r = requests.put(uri_base+'api/cloud/%s'%(default_cloud_uuid), data=json.dumps(data) ,verify=False, headers=headers, cookies=login.cookies)
    if r.status_code not in [200,201]:
        raise Exception(r.text)
    wait_until_cloud_ready(c_ip, login.cookies, headers, default_cloud_uuid, c_port=None, timeout=450)

    management_network = "/api/vimgrnwruntime/?name=%s"%(VCENTER_MANAGEMENT_MAP["blr-01-avi-dev-IntMgmt"]["name"])
    r = requests.get(uri_base+'api/cloud',verify=False, headers=headers, cookies=login.cookies)
    data = r.json()['results'][0]
    data["vcenter_configuration"]["management_network"] = management_network
    r = requests.put(uri_base+'api/cloud/%s'%(default_cloud_uuid), data=json.dumps(data) ,verify=False, headers=headers, cookies=login.cookies)
    if r.status_code not in [200,201]:
        raise Exception(r.text)
    print("changing service engine group settings")
    r = requests.get(uri_base+'api/serviceenginegroup',verify=False, headers=headers, cookies=login.cookies)
    for val in r.json()['results']:
        if default_cloud_uuid in val['cloud_ref']:
            data = val
            break
    se_name_prefix = c_ip.split(".")[-1]+"_"+version.replace(".","")
    data.update({
        "se_name_prefix":se_name_prefix,
        "vcenter_folder":VCENTER_FOLDER_NAME,
        "max_se":"1"
    })
    r = requests.put(uri_base+'api/serviceenginegroup/%s'%(data['uuid']), data=json.dumps(data), verify=False, headers=headers, cookies=login.cookies)
    if r.status_code not in [200,201]:
        raise Exception(r.text)


def pretty_print(vals,ljust_vals=[],filler=" "):
    line = " "
    for val,ljust_val in zip(vals,ljust_vals):
        line += str(val).ljust(ljust_val,filler)
    print (line)


def get_datacenter_obj(si,datacenter_name):

    for dc in si.content.rootFolder.childEntity:
        if dc.name == datacenter_name:
            datacenter_obj = dc
    return datacenter_obj

def get_cluster_obj(datacenter_obj,cluster_name):
    
    for cluster in datacenter_obj.hostFolder.childEntity:
        if cluster.name == cluster_name:
            cluster_obj = cluster
            return cluster_obj
    return None

def get_folder_obj(datacenter_obj,folder_name):
    
    for folder in datacenter_obj.vmFolder.childEntity:
        if vim.Folder._wsdlName == folder._wsdlName and folder.name == folder_name:
            return folder
    print ("Folder: %s does not exist"%(folder_name))
    return False

def check_if_ip_is_free(si,ip,only_check=False):
    search = si.RetrieveContent().searchIndex
    vms = list(set(search.FindAllByIp(ip=ip,vmSearch=True)))
    if not vms:
        return True
    if vms and only_check:
        return False
    if vms: 
        delete_vm = input("Do you want to delete the vm occupying the ip '%s' ?[Y/N] \n"%(ip))
        if delete_vm.lower() == "y":
            delete_vm = True
        else:
            delete_vm = False
            return False

    if vms and delete_vm:
        
        for vm in vms:
            action_confirm = input("Are you sure you want to delete '%s' with ip = %s ?[Y/N] \n"%(vm.name,ip))
            if action_confirm.lower() == "n":continue
            if vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOn:
                print ("powering off ",vm.name," ",ip)
                task = vm.PowerOff()
                while task.info.state not in [vim.TaskInfo.State.success,vim.TaskInfo.State.error]:
                    time.sleep(1)
                print ("power is off.",task.info.state)
    
            if vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOff and sys.argv[1]=='delete':
                print ("deleteing ",vm.name," ",ip)
                task = vm.Destroy()
                while task.info.state not in [vim.TaskInfo.State.success,vim.TaskInfo.State.error]:
                    time.sleep(1)
                print ("vm is deleted.",task.info.state)
    new_vms = list(set(search.FindAllByIp(ip=ip,vmSearch=True)))
    if not vms:
        return True
    else:
        return False

def check_if_vm_name_exists_in_folder(folder_obj,vm_name):
    for vm in folder_obj.childEntity:
        if vim.VirtualMachine._wsdlName == vm._wsdlName and vm.name == vm_name:
            print ("Name already exists")
            return True
    return False

def get_own_sysadmin_key():
    keypath = "/home/aviuser/.ssh/id_rsa.pub"
    if os.path.exists(keypath):
        with open(keypath, 'r') as keyfile:
            data = keyfile.read().rstrip('\n')
            return data
    raise Exception('Failed to find sysadmin public key file at %s\n' % (keypath))

def generate_controller_from_ova():
    vm_type = "controller"
    vcenter_ip = input("Vcenter IP ? [Default: %s] :"%(VCENTER_IP)) or VCENTER_IP
    si = connect()
    datacenter = input("Datacenter Name ? [Default: %s] :"%(VCENTER_DATACENTER_NAME)) or VCENTER_DATACENTER_NAME
    datacenter_obj = get_datacenter_obj(si,datacenter)
    cluster_name = input("Cluster ? [Default: %s] :"%(VCENTER_CLUSTER_NAME)) or VCENTER_CLUSTER_NAME
    datastore = input("Datastore ? [Default: %s] :"%(VCENTER_DATASTORE_NAME)) or VCENTER_DATASTORE_NAME
    #cluster_obj = get_cluster_obj(datacenter_obj,cluster_name)
    source_ova_path = input("Source Ova Path (local/http/ftp) ? [Default: /home/aviuser/workspace/avi-dev/build/controller.ova] :")
    if not source_ova_path:
        source_ova_path = "/home/aviuser/workspace/avi-dev/build/controller.ova"
    '''
    ova_memory_spec_in_MB , ova_disk_spec_in_MB = get_memory_and_disk_spec_from_ova(source_ova_path)
    filter_options = input("type 'Y' if you want to see host,datastore options based on ova specs ; 'N' for all options; [Y/N] :")
    if filter_options.lower() == 'y' and si:
        host_ip, datastore = filter_host_and_datastore_based_on_specs(cluster_obj, ova_memory_spec_in_MB, ova_disk_spec_in_MB)
    else:
        host_ip, datastore = filter_host_and_datastore_based_on_specs(cluster_obj, ova_memory_spec_in_MB, ova_disk_spec_in_MB, display_all=True)
    '''
    management_network = input("Management Network ? [Default: %s] :"%(VCENTER_MANAGEMENT_MAP["blr-01-avi-dev-IntMgmt"]["name"])) or VCENTER_MANAGEMENT_MAP["blr-01-avi-dev-IntMgmt"]["name"]

    mask = input("Network Mask ? [Default: %s] :"%(VCENTER_MANAGEMENT_MAP["blr-01-avi-dev-IntMgmt"]["mask"])) or VCENTER_MANAGEMENT_MAP["blr-01-avi-dev-IntMgmt"]["mask"]
    gw_ip = input("Gateway IP ? [Default: %s] :"%(VCENTER_MANAGEMENT_MAP["blr-01-avi-dev-IntMgmt"]["gateway"])) or VCENTER_MANAGEMENT_MAP["blr-01-avi-dev-IntMgmt"]["gateway"]

    while True:
        free_ips_1 = {str(index):val for index,val in enumerate([ip for ip in ALL_RESERVED_IPS if check_if_ip_is_free(si,ip,True)]) }
        print ("Free IP's : %s"%(free_ips_1))

        mgmt_index = input("Management IP ? [Enter Index] :")
        if mgmt_index not in free_ips_1.keys():
            print("not a valid index ")
            mgmt_ip = input("Management IP ? [Enter IP] :")
        else:
            mgmt_ip = free_ips_1[mgmt_index]
        if mgmt_ip:
            if check_if_ip_is_free(si,mgmt_ip):
                try:
                    mgmt_ip = inet_ntoa(inet_aton(mgmt_ip))
                except Exception as e:
                    print(str(e))
                    continue
                print(" %s ip is free"%(mgmt_ip))
                break
    
    while True:
        folder_name = input("Folder Name ? [Default: %s] :"%(VCENTER_FOLDER_NAME)) or VCENTER_FOLDER_NAME
        if folder_name:
            folder_obj = get_folder_obj(datacenter_obj,folder_name)
            if folder_obj:
                break
    while True:
        vm_name = input("VM Name ? :")
        if not check_if_vm_name_exists_in_folder(folder_obj,vm_name):
            break
    power_on = input("Power On VM [Y/N]? [Y] :")
    if power_on.lower() not in ['y','n']:power_on = 'y'
    ctlr_version = get_version_controller_from_ova(source_ova_path)
    print("Controller Version: %s"%(ctlr_version))
    set_password_and_sys_config = input("Do you want to change default password and set systemconfiguration [Y/N] ? [Y] :") or 'Y'


    vi = 'vi://%s:%s@'%(VCENTER_USER, VCENTER_PASSWORD) + vcenter_ip
    vi = vi + '/' + datacenter + '/host/'
    vi = vi + cluster_name + '/'
    #vi = vi + host_ip + '/'

    prop = ''
    if vm_type == 'controller':
        prop = '--prop:avi.mgmt-ip.CONTROLLER=' + mgmt_ip + \
            ' --prop:avi.default-gw.CONTROLLER=' + gw_ip + ' '
        prop = prop + ' --prop:avi.mgmt-mask.CONTROLLER=' + str(mask) + ' '
        prop = prop + ' --prop:avi.sysadmin-public-key.CONTROLLER="' + get_own_sysadmin_key() + '" '
        prop += '--name="' + vm_name + '" '
        if power_on.lower() == 'y':
            prop += '--powerOn '
        prop += '"--vmFolder='+folder_name+'" ' 

        cmd = '/usr/bin/ovftool --noSSLVerify --X:logLevel=warning --X:logToConsole "--datastore=' + datastore + \
            '" --net:Management="' + management_network + \
            '" ' + prop + source_ova_path + ' ' + vi 
    print ('\n',cmd,'\n')

    verify = input("Verify the command and agree to proceed [Y/N] ? [Y] :") or 'Y'
    if verify.lower() == 'y':
        print ("\nDeploying OVA")
        subprocess.call(cmd, shell=True)
    else:
        print ("Exiting ...")
    if set_password_and_sys_config.lower() == 'y':
        set_welcome_password_and_set_systemconfiguration(mgmt_ip, version=ctlr_version)
        setup_cloud_se(mgmt_ip, c_port=None,version=ctlr_version ,timeout=60)
        setup_vs(mgmt_ip, c_port=None,version=ctlr_version ,timeout=60)
        setup_tmux(mgmt_ip)

    print("================== DONE ==============")

if len(sys.argv)==2 and sys.argv[1]=='configure_cloud_vs_se':
    si = connect()
    used_ips_1 = [ip for ip in ALL_RESERVED_IPS if not check_if_ip_is_free(si,ip,True)]
    print ("Configured IP's : %s"%(used_ips_1))
    mgmt_ip = input("Management IP ? :")
    ctlr_version = get_version_controller_from_ova()
    setup_cloud_se(mgmt_ip, c_port=None,version=ctlr_version ,timeout=60)
    setup_vs(mgmt_ip, c_port=None,version=ctlr_version ,timeout=60)

if len(sys.argv)==2 and sys.argv[1]=='configure_vs':
    si = connect()
    used_ips_1 = [ip for ip in ALL_RESERVED_IPS if not check_if_ip_is_free(si,ip,True)]
    print ("Configured IP's : %s"%(used_ips_1))
    mgmt_ip = input("Management IP ? :")
    ctlr_version = get_version_controller_from_ova()
    setup_vs(mgmt_ip, c_port=None,version=ctlr_version ,timeout=60)


if len(sys.argv)==2 and sys.argv[1]=='setup_tmux':
    si = connect()
    used_ips_1 = [ip for ip in ALL_RESERVED_IPS if not check_if_ip_is_free(si,ip,True)]
    print ("Configured IP's : %s"%(used_ips_1))
    mgmt_ip = input("Management IP ? :")
    setup_tmux(mgmt_ip)

if len(sys.argv)==2 and sys.argv[1]=='flush_db_configure_raw_controller_wo_tmux':
    si = connect()
    used_ips_1 = [ip for ip in ALL_RESERVED_IPS if not check_if_ip_is_free(si,ip,True)]
    print ("Configured IP's : %s"%(used_ips_1))
    mgmt_ip = input("Management IP ? :")
    ctlr_version = get_version_controller_from_ova()
    flush_db(mgmt_ip)
    set_welcome_password_and_set_systemconfiguration(mgmt_ip, version=ctlr_version)
    setup_cloud_se(mgmt_ip, c_port=None,version=ctlr_version ,timeout=60)
    setup_vs(mgmt_ip, c_port=None,version=ctlr_version ,timeout=60)


if len(sys.argv)==2 and sys.argv[1] == 'generate_controller_from_ova':
    generate_controller_from_ova()

if len(sys.argv)==2 and (sys.argv[1] == 'configure_raw_controller' or sys.argv[1] == 'configure_raw_controller_wo_tmux'):
    si = connect()
    used_ips_1 = [ip for ip in ALL_RESERVED_IPS if not check_if_ip_is_free(si,ip,True)]
    print ("Configured IP's : %s"%(used_ips_1))
    mgmt_ip = input("Management IP ? :")
    ctlr_version = get_version_controller_from_ova()
    set_welcome_password_and_set_systemconfiguration(mgmt_ip, version=ctlr_version)
    setup_cloud_se(mgmt_ip, c_port=None,version=ctlr_version ,timeout=60)
    setup_vs(mgmt_ip, c_port=None,version=ctlr_version ,timeout=60)
    if sys.argv[1] != 'configure_raw_controller_wo_tmux':
        setup_tmux(mgmt_ip)
# https://gist.github.com/goodjob1114/9ededff0de32c1119cf7


'''
parser = argparse.ArgumentParser()
parser.add_argument('--default_profile', help="Set default profile", action='store_true')
parser.add_argument('--list_profiles', help="Display the Vsphere static ips and folder configuration", action='store_true')
parser.add_argument('--create_profile', help="Create vsphere ips and folder configuration", action='store_true')
args = parser.parse_args()
'''

'''

def change_vm_memory(vm,memory):
    if vm.runtime.powerState != 'poweredOff':
        return False
    cspec = vim.vm.ConfigSpec()
    cspec.memoryMB = memory
    task = vm.ReconfigVM_Task(cspec)
    while task.info.state not in [vim.TaskInfo.State.success,vim.TaskInfo.State.error]:
        time.sleep(1)
    if task.info.state == vim.TaskInfo.State.success:
        return True
    else:
        return False

def get_datastores_from_host(cluster_obj,host_ip):

    datastore_obj_list = []
    for host in cluster_obj.host:
        if host.name == host_ip:
            host_obj = host

            for datastore in host_obj.datastore:
                datastore_obj_list.append(datastore)
            break
    return datastore_obj_list

def assist_in_host_value(cluster_obj):
    print ("\nList of available hosts in cluster:%s\n"%(cluster_obj.name))
    host_list = []
    tmp = []
    for host in get_hosts_from_cluster(cluster_obj):
        tmp.append(host.name)
    tmp = sorted(tmp, key = lambda ip: (int(ip.split(".")[0]), 
                                        int(ip.split(".")[1]),
                                        int(ip.split(".")[2]),
                                        int(ip.split(".")[3])))
    
    pretty_print(['Index ','Host Name '],ljust_vals=[7,15]) # printing header
    for index,host in enumerate(tmp):
        val = [index,host]
        pretty_print(val,ljust_vals=[7,15]) # printing vals
        host_list.append(val)
    print ("")
    if host_list:
        host_index = input("Enter the index value of the host :")
        return host_list[int(host_index)][1]
    else:
        return input("Enter the name of the host :")

def get_hosts_from_cluster(cluster_obj):
    host_obj_list = []
    for host in cluster_obj.host:
        host_obj_list.append(host)
    return host_obj_list

def filter_host_and_datastore_based_on_specs(cluster_obj, ova_memory_spec_in_MB=False, ova_disk_spec_in_MB=False, display_all=False):
    if not ova_memory_spec_in_MB: ova_memory_spec_in_MB = 0
    if not ova_disk_spec_in_MB: ova_disk_spec_in_MB = 0
    print ("\nMemory Specs from OVA",convert_units(ova_memory_spec_in_MB,base_unit='MB',return_unit='GB'),"GB")
    print ("Disk Specs from OVA  ",convert_units(ova_disk_spec_in_MB,base_unit='MB',return_unit='GB'),"GB")
    print ("Swap Space Needed    ",convert_units(ova_memory_spec_in_MB/float(2.0),base_unit='MB',return_unit='GB'),"GB")
    print ("")
    host_datastore_compatible = []
    for host in cluster_obj.host:
        free_memory_in_host_in_MB = get_host_info(host)
        free_memory_in_host_in_GB = round(convert_units(free_memory_in_host_in_MB, base_unit='MB', return_unit='GB'),2)
        for datastore in host.datastore:
            free_disk_space_in_datastore_in_MB = get_datastore_info(datastore)
            free_disk_space_in_datastore_in_GB = round(convert_units(free_disk_space_in_datastore_in_MB, base_unit='MB', return_unit='GB'),2)

            #print free_memory_in_host_in_MB,"  ",(ova_memory_spec_in_MB + 1024),"  ",free_disk_space_in_datastore_in_MB,"  ",(ova_disk_spec_in_MB + ova_memory_spec_in_MB/2.0 + 1024),"  ",free_memory_in_host_in_GB,"  ",free_disk_space_in_datastore_in_GB
            if (free_memory_in_host_in_MB > (ova_memory_spec_in_MB + 1024)) and (free_disk_space_in_datastore_in_MB > (ova_disk_spec_in_MB + ova_memory_spec_in_MB/2.0 + 1024)):
                host_datastore_compatible.append([host.name.replace('.oc.vmware.com',''),str(free_memory_in_host_in_GB)+'GB',datastore.name,str(free_disk_space_in_datastore_in_GB)+'GB','COMPATIBLE'])
            else:
                host_datastore_compatible.append([host.name.replace('.oc.vmware.com',''),str(free_memory_in_host_in_GB)+'GB',datastore.name,str(free_disk_space_in_datastore_in_GB)+'GB','NOT COMPATIBLE'])
            #print host_datastore_compatible[-1]
    return filter_question_based_on_specs(host_datastore_compatible, display_all=display_all)




def get_host_info(host):
    memory_capacity_in_MB = convert_units(int(host.hardware.memorySize), base_unit='byte', return_unit='MB')
    memory_usage_in_MB = int(host.summary.quickStats.overallMemoryUsage)
    free_memory_in_MB = memory_capacity_in_MB - memory_usage_in_MB    
    return free_memory_in_MB

def get_datastore_info(datastore):
    free_space_in_MB = datastore.summary.freeSpace/float(1<<20)
    return free_space_in_MB



def filter_question_based_on_specs(host_datastore_compatible_list, display_all=False):
    compatible_list = []
    incompatible_list = []
    final_list = []
    count = 0
    for rec in host_datastore_compatible_list:
        if rec[4] == 'COMPATIBLE':
            rec.insert(0,count)
            compatible_list.append(rec)
            count += 1
    for rec in host_datastore_compatible_list:
        if rec[4] == 'NOT COMPATIBLE':
            rec.insert(0,count)
            incompatible_list.append(rec)
            count += 1

    ljust_vals = [8,17,15,20,15,15] 
    pretty_print(['Index','Host Name','Free Memory','Datastore','Free Space','Compatiblity'], ljust_vals=ljust_vals,filler="-")
    if display_all:
        final_list = compatible_list + incompatible_list
    elif len(compatible_list) == 0:
        final_list = incompatible_list
        print ("*** No compatible host, datastore options available. The ova may not get deployed succesfully on the incompatible options ***")
    else:
        final_list = compatible_list

    for rec in final_list:
        pretty_print(rec, ljust_vals=ljust_vals)
    #for rec in incompatible_list:
    #    pretty_print(rec, ljust_vals=ljust_vals)
    print ("")
    index_input = int(input("Enter the index value of the host datastore combination to use :"))
    host_ip , datastore = final_list[index_input][1], final_list[index_input][3]
    return host_ip,datastore


    


UNITS_MAPPING = {
        'byte':1,
        'bytes':1,
        'KB':1<<10,
        'MB':1<<20,
        'GB':1<<30,
        'TB':1<<40
        }

def convert_units(units, base_unit='byte', return_unit='MB'):
    return units*UNITS_MAPPING[base_unit]/float(UNITS_MAPPING[return_unit])

def get_memory_and_disk_spec_from_ova(path_to_ova):
    
    """
    try:
        disk_total_in_MB = False
        memory_total_in_MB = False
        
        tar_file = tarfile.open(path_to_ova)
        ovffile_obj = tar_file.extractfile(tar_file.getmember('controller.ovf'))
        xml_string = ovffile_obj.read()
        xml_obj = xmltodict.parse(xml_string)
        
        disk_total_units = xml_obj.get('Envelope',{}).get('DiskSection',{}).get('Disk',{}).get('@ovf:capacity',False)
        disk_unit = xml_obj.get('Envelope',{}).get('DiskSection',{}).get('Disk',{}).get('@ovf:capacityAllocationUnits',False)
        if disk_total_units and disk_unit:
            vals = disk_unit.split("*")[1].strip().split("^")
            base_byte_unit = int(vals[0])**int(vals[1])
            disk_total_in_MB = int(disk_total_units) * convert_units(base_byte_unit, base_unit='byte', return_unit='MB')
        
        memory_unit = False
        memory_total_units = False
        for item in xml_obj.get('Envelope',{}).get('VirtualSystem',{}).get('VirtualHardwareSection',{}).get('Item',[]):
            if item.get('rasd:Description',False) == 'Memory Size':
                memory_unit = item.get('rasd:AllocationUnits',False)
                memory_total_units = item.get('rasd:VirtualQuantity',False)
                break
        if memory_unit and memory_total_units:
            vals = memory_unit.split("*")[1].strip().split("^")
            base_byte_unit = int(vals[0])**int(vals[1])
            memory_total_in_MB = int(memory_total_units) * convert_units(base_byte_unit, base_unit='byte', return_unit='MB')

    finally:
        tar_file.close()
    return memory_total_in_MB, disk_total_in_MB
    """
    
    disk_total_in_MB = False
    memory_total_in_MB = False
    cmd_ova_spec = '/usr/bin/ovftool --schemaValidate %s'%(path_to_ova)
    ova_specs = subprocess.check_output(shlex.split(cmd_ova_spec))
    memory_specs = ''
    disk_specs = ''
    for line in ova_specs.split('\n'):
        if 'Memory:' in line and not memory_specs:
            memory_specs = line.split('Memory:')[1].strip()
        if 'Flat disks:' in line and not disk_specs:
            disk_specs = line.split('Flat disks:')[1].strip()
    memory_total_in_MB = convert_units(float(memory_specs.split(' ')[0]), base_unit=memory_specs.split(' ')[1], return_unit='MB')
    disk_total_in_MB = convert_units(float(disk_specs.split(' ')[0]), base_unit=disk_specs.split(' ')[1], return_unit='MB') + memory_total_in_MB/2.0
    return memory_total_in_MB, disk_total_in_MB



'''
