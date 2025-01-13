#!/usr/bin/env python3
import sys
try:
    import pyVim
except ImportError:
    print ("do -->> pip3 install --upgrade pyvmomi")
    sys.exit(1)
try:
    from tabulate import tabulate
except ImportError:
    print ("do -->> pip3 install tabulate")
    sys.exit(1)
from pyVim.connect import Disconnect,Connect
from pyVmomi import vim
from socket import inet_aton, inet_ntoa
import random,time,atexit
from concurrent.futures import ThreadPoolExecutor
#import tarfile
#import xmltodict
import subprocess, multiprocessing
import shlex
#import argparse
import os
import requests
from requests.auth import HTTPBasicAuth
import time
from datetime import timedelta
import json
import re
import datetime
import urllib3
import ipaddress
import random
urllib3.disable_warnings()
import fabric
from tabulate import tabulate
import jinja2
from retry import retry


with open(os.path.dirname(os.path.abspath(__file__))+"/vals.json", "r") as f:
    config = json.loads(f.read())

VCENTER = config["VCENTER"]
VCENTER_CHOICES = list(VCENTER.keys())
CURRENT_VCENTER = ""

vcenter_str = ""
if len(VCENTER_CHOICES) != 1:
    for index,val in enumerate(VCENTER_CHOICES):
        vcenter_str +="%s:%s, "%(index,val)
    action_confirm = input("Choose the vcenter to operate on [[%s]] [Enter Index] ?: "%(vcenter_str))
    if int(action_confirm.lower()) < len(VCENTER_CHOICES):
        CURRENT_VCENTER = VCENTER_CHOICES[int(action_confirm.lower())]
    else:
        raise Exception("Invalid Choice")
else:
    CURRENT_VCENTER = VCENTER_CHOICES[0]

ALL_MGMT_RESERVED_IPS = VCENTER[CURRENT_VCENTER]["ALL_MGMT_RESERVED_IPS"]
ALL_RESERVED_IPS = VCENTER[CURRENT_VCENTER]["ALL_RESERVED_IPS"]
SE_IPS = VCENTER[CURRENT_VCENTER]["SE_IPS"]
VCENTER_IP = VCENTER[CURRENT_VCENTER]["VCENTER_IP"]
VCENTER_USER = VCENTER[CURRENT_VCENTER]["VCENTER_USER"]
VCENTER_PASSWORD = VCENTER[CURRENT_VCENTER]["VCENTER_PASSWORD"]
VCENTER_DATACENTER_NAME = VCENTER[CURRENT_VCENTER]["VCENTER_DATACENTER_NAME"]
VCENTER_CLUSTER_NAME = VCENTER[CURRENT_VCENTER]["VCENTER_CLUSTER_NAME"]
VCENTER_DATASTORE_NAME = VCENTER[CURRENT_VCENTER]["VCENTER_DATASTORE_NAME"]
VCENTER_FOLDER_NAME = VCENTER[CURRENT_VCENTER]["VCENTER_FOLDER_NAME"]
DEV_VM_IP = VCENTER[CURRENT_VCENTER]["DEV_VM_IP"]
VCENTER_MANAGEMENT_MAP = VCENTER[CURRENT_VCENTER]["VCENTER_MANAGEMENT_MAP"]
VCENTER_DNS_SERVERS = VCENTER[CURRENT_VCENTER]["VCENTER_DNS_SERVERS"]
VCENTER_NTP = VCENTER[CURRENT_VCENTER]["VCENTER_NTP"]
VCENTER_PORT_GROUP = VCENTER[CURRENT_VCENTER]["VCENTER_PORT_GROUP"]
VCENTER_SERVER_IP = VCENTER[CURRENT_VCENTER]["VCENTER_SERVER_IP"]
VCENTER_SERVER_SUBNET = VCENTER[CURRENT_VCENTER]["VCENTER_SERVER_SUBNET"]

SYSADMIN_KEYPATH = "/home/aviuser/.ssh/id_rsa.pub"
DEFAULT_SETUP_PASSWORD = "58NFaGDJm(PJH0G"
DEFAULT_PASSWORD = "avi123"
DHCP = False
GLOBAL_LOGIN_HEADERS = {}
GLOBAL_LOGIN_COOKIES = {}
GLOBAL_CURRENT_PASSWORD = {}
GLOBAL_BUILD_NO = {}

SE_IPS_TO_USE_FOR_CURRENT_CTLR = []

POWER_OFF_STATE = 'POWER OFF'
POWER_ON_STATE = 'POWER ON'
TEMPLATE_STATE = 'TEMPLATE'
UNKNOWN_STATE = 'UNKNOWN'
NIL_PRINT_VAL = "------"
FREE_IP = "--Free IP--"

if 'help' in sys.argv:
    print ("options --> with_se_ips")
    print ("options --> free_ip")
    print ("options --> delete_ctlr_se")
    print ("options --> delete 'ip'")
    print ("options --> delete_name 'name'")
    print ("options --> poweroff 'ip'")
    print ("options --> rename 'ip' 'newname'")
    print ("options --> poweron")
    print ("options --> poweron 'name'")
    print ("options --> reimage_ctlr")
    print ("options --> latest_builds")
    print ("options --> generate_controller_from_ova")
    print ("options --> configure_raw_controller")
    print ("options --> configure_raw_controller_wo_tmux")
    print ("options --> configure_password_only")
    print ("options --> configure_cloud_vs_se")
    print ("options --> configure_vs")
    print ("options --> flush_db_configure_raw_controller_wo_tmux")
    print ("options --> setup_tmux")
    print ("options --> setup_tmux_install_only")
    
START_TIME = time.time()

def connect(vcenter_ip=VCENTER_IP, user=VCENTER_USER, pwd=VCENTER_PASSWORD ,exit_on_error=True):
    try:
        si= Connect(host=vcenter_ip, user=user, pwd=pwd, disableSslCertValidation=True)
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
                vms_table[(folder_name,virtual_m.name)] = {'state':POWER_OFF_STATE,'ip_network':[[NIL_PRINT_VAL,NIL_PRINT_VAL]]}
            else:
                vms_table[(folder_name,virtual_m.name)] = {'state':POWER_ON_STATE,'ip_network':[]}
                if len(virtual_m.guest.net)>0:
                    for ip_net in virtual_m.guest.net:
                        for ip_addr in ip_net.ipAddress:
                            if not ip_addr or ":" in ip_addr:
                                continue
                            else:
                                vms_table[(folder_name,virtual_m.name)]['ip_network'].append([ip_addr, ip_net.network])
                                
        elif virtual_m.config and virtual_m.config.template:
            vms_table[(folder_name,virtual_m.name)] = {'state':TEMPLATE_STATE,'ip_network':[[NIL_PRINT_VAL,NIL_PRINT_VAL]]}
        else:
            vms_table[(folder_name,virtual_m.name)] = {'state':UNKNOWN_STATE,'ip_network':[[NIL_PRINT_VAL,NIL_PRINT_VAL]]}

    except:
        raise

def power_on_vm(virtual_machine_obj):
    vm = virtual_machine_obj
    task = vm.PowerOn()
    while task.info.state not in [vim.TaskInfo.State.success,vim.TaskInfo.State.error]:
        time.sleep(1)
    print ("power on task for vm %s = %s"%(vm.name,task.info.state))





def get_vms_ips_network(with_se_ips=False,free_ips=False,with_mgmt_reserved_ips=False):
    if with_se_ips:
        all_reserved_ips = ALL_RESERVED_IPS + SE_IPS
    else:
        all_reserved_ips = ALL_RESERVED_IPS
    if with_mgmt_reserved_ips:
        all_reserved_ips = ALL_MGMT_RESERVED_IPS + all_reserved_ips
    folder_name = VCENTER_FOLDER_NAME
    datacenter_name = VCENTER_DATACENTER_NAME
    datacenter = None
    si = connect()
    vms_table = {} # vms_table[(folder,name)] = {state :template/on/off , ip_network: [[ip,network],]}

    for dc in si.content.rootFolder.childEntity:
        if dc.name == datacenter_name:
            datacenter = dc
    if datacenter is None:
        print("datacenter %s not found"%(datacenter_name))
        sys.exit(1)
    search_text = "%s/vm/%s"%(datacenter_name,folder_name)
    search_folder = si.RetrieveContent().searchIndex.FindByInventoryPath(search_text)
    if not search_folder:
        print("folder %s not found"%(folder_name))
        print("search text = %s"%(search_text))
        sys.exit(1)
    for virtual_m in search_folder.childEntity:
        if vim.Folder == type(virtual_m):
            continue
        fill_vms_table(vms_table, virtual_m)
    """
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
    """

    reserved_ips_not_found_in_folder = []
    for val_ip in all_reserved_ips:
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
    for val_ip in all_reserved_ips:
        found = False
        for folder_name,value in vms_table.items():
            for ip_network_val in value['ip_network']:
                if val_ip == ip_network_val[0]:
                    found = True
                    final_print_vals.append((folder_name[1], value['state'], val_ip, ip_network_val[1]))
        if not found:
            final_print_vals.append((FREE_IP, NIL_PRINT_VAL, val_ip, NIL_PRINT_VAL))

    final_print_vals.append(("","","",""))

    for folder_name,value in vms_table.items():
        for ip_network_val in value['ip_network']:
            if ip_network_val[0] not in all_reserved_ips:
                final_print_vals.append((folder_name[1], value['state'], ip_network_val[0], ip_network_val[1]))
    final_print_vals = remove_se_non_reserved_ips(final_print_vals)
    if not free_ips: final_print_vals = remove_free_ips(final_print_vals)
    return final_print_vals

def remove_free_ips(final_print_vals):
    new_final_print_vals = []
    for val in final_print_vals:
        val_name = val[0]
        if FREE_IP != val_name:
            new_final_print_vals.append(val)
    return new_final_print_vals    

def remove_se_non_reserved_ips(final_print_vals):
    #print(final_print_vals)
    reserved_se_names = []
    new_final_print_vals = []
    for val in final_print_vals:
        val_name = val[0]
        val_ip = val[2]
        if val_ip in SE_IPS and FREE_IP != val_name:
            reserved_se_names.append(val_name)
    for val in final_print_vals:
        val_name = val[0]
        val_ip = val[2]
        if val_name in reserved_se_names and val_ip not in SE_IPS:
            continue
        new_final_print_vals.append(val)
    return new_final_print_vals    

def poweroff_and_delete_vm(ips,delete=False,si=None):
    cmd = 'delete' if delete else 'poweroff'
    if not si:
        si = connect()
    search = si.RetrieveContent().searchIndex
    vms_to_operate_on = []
    for ip in ips:
        vms = list(set(search.FindAllByIp(ip=ip,vmSearch=True)))
        if vms:
            for vm in vms:
                action_confirm = input("Are you sure you want to %s '%s' with ip = %s ?[Y/N] \n"%(cmd,vm.name,ip))
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
        
        if vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOff and cmd=='delete':
            print ("deleteing ",vm.name," ",ip)
            task = vm.Destroy()
            while task.info.state not in [vim.TaskInfo.State.success,vim.TaskInfo.State.error]:
                time.sleep(1)
            print ("vm is deleted.",task.info.state)

if len(sys.argv)>=3 and sys.argv[1] in ('delete','poweroff'):
    if sys.argv[2]:
        if sys.argv[1] == 'delete':
            poweroff_and_delete_vm(sys.argv[2:],True)
        else:
            poweroff_and_delete_vm(sys.argv[2:],False)



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

if len(sys.argv)==1:
    final_print_vals = get_vms_ips_network(with_se_ips=True, with_mgmt_reserved_ips=True)
    print(tabulate(final_print_vals, headers="firstrow", tablefmt="psql"))

if len(sys.argv)==2 and sys.argv[1]=='with_se_ips':
    final_print_vals = get_vms_ips_network(with_se_ips=True, with_mgmt_reserved_ips=True)
    print(tabulate(final_print_vals, headers="firstrow", tablefmt="psql"))

if len(sys.argv)==2 and sys.argv[1] in ['free_ip','free_ips']:
    final_print_vals = get_vms_ips_network(with_se_ips=True,free_ips=True, with_mgmt_reserved_ips=True)
    print(tabulate(final_print_vals, headers="firstrow", tablefmt="psql"))


##################################################################################
##################################################################################
##################################################################################


def get_headers(tenant='admin'):
    headers = {
        "Content-Type": "application/json",
    }
    # headers["X-Avi-Version"] = "%s" % version
    return headers


def wait_until_cluster_ready(c_ip,  timeout=1800):
    uri = 'https://' + c_ip + '/api/cluster/runtime'

    sleep_time = 10
    iters = int(timeout / sleep_time)
    rsp = ''
    for i in range(iters):
        try:
            rsp = requests.get(uri, verify=False)
            print('controller %s' % c_ip)
            print('rsp_code %s' % rsp.status_code)
            #print('rsp_data %s' % rsp.json())
        except:
            print('Get for %s fails. Controller %s' % (uri, c_ip))
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
                    'is still not active. controller %s' % (timeout, c_ip))

def change_to_default_password(c_ip):
    uri_base = 'https://' + c_ip + '/'
    print("changing password to avi123")
    r = requests.get(uri_base+'api/useraccount',verify=False, headers=GLOBAL_LOGIN_HEADERS[c_ip], cookies=GLOBAL_LOGIN_COOKIES[c_ip])
    data = r.json()
    data.update({'username':'admin','password':DEFAULT_PASSWORD ,'old_password':GLOBAL_CURRENT_PASSWORD[c_ip]})
    time.sleep(1) 
    #auth = HTTPBasicAuth('admin', GLOBAL_CURRENT_PASSWORD[c_ip])
    resp = requests.put(uri_base+'api/useraccount', data=json.dumps(data) ,verify=False, headers=GLOBAL_LOGIN_HEADERS[c_ip], cookies=GLOBAL_LOGIN_COOKIES[c_ip])
    if resp.status_code not in [200,201]:
        raise Exception(resp.text)
    print("changing password to avi123 -- done")
    

def login_and_set_global_variables(c_ip,password_arg=None):

    global GLOBAL_LOGIN_HEADERS
    global GLOBAL_LOGIN_COOKIES
    global GLOBAL_CURRENT_PASSWORD
    if GLOBAL_LOGIN_HEADERS.get(c_ip,False) and GLOBAL_LOGIN_COOKIES.get(c_ip,False):
        #resp = requests.get(uri_base+'api/useraccount',verify=False, headers=GLOBAL_LOGIN_HEADERS, cookies=GLOBAL_LOGIN_COOKIES)
        #if resp.status_code == 401:
        #    pass
        return
    uri_base = 'https://' + c_ip + '/'
    headers = get_headers()
    logged_in = False
    password_list = [password_arg,"avi123","avi123$%","admin"] if password_arg else ["avi123","avi123$%","admin"]
    for password in password_list:
        data = {'username':'admin', 'password':password}
        login = requests.post(uri_base+'login', data=json.dumps(data), headers=headers, verify=False)
        if login.status_code in [200, 201]:
            logged_in = True
            headers['X-CSRFToken'] = login.cookies['csrftoken']
            headers['Referer'] = uri_base
            GLOBAL_LOGIN_HEADERS[c_ip] = headers
            GLOBAL_LOGIN_COOKIES[c_ip] = login.cookies
            GLOBAL_CURRENT_PASSWORD[c_ip] = password
            break
    if not logged_in:
        print("not able to login using various passwords")
        exit(1)
    
    set_version_controller(c_ip)

def reset_login(c_ip):
    global GLOBAL_LOGIN_COOKIES
    global GLOBAL_LOGIN_HEADERS
    global GLOBAL_CURRENT_PASSWORD
    GLOBAL_LOGIN_HEADERS.pop(c_ip,None)
    GLOBAL_LOGIN_COOKIES.pop(c_ip,None)
    GLOBAL_CURRENT_PASSWORD.pop(c_ip,None)

def set_password_only_and_set_systemconfiguration(c_ip,current_password=DEFAULT_SETUP_PASSWORD):
    wait_until_cluster_ready(c_ip)
    login_and_set_global_variables(c_ip,current_password)
    
    uri_base = 'https://' + c_ip + '/'
    time.sleep(1)    
    print("change systemconfiguration settings")
    #import ipdb;ipdb.set_trace()
    r = requests.get(uri_base+'api/systemconfiguration', verify=False, headers=GLOBAL_LOGIN_HEADERS[c_ip] ,cookies=GLOBAL_LOGIN_COOKIES[c_ip])
    if r.status_code not in [200,201]:
        raise Exception(r.text)
    data = r.json()
    data['portal_configuration']['password_strength_check'] = False
    data['portal_configuration']['allow_basic_authentication'] = True
    data['dns_configuration']['server_list'] = [{'addr':val , 'type':'V4'} for val in VCENTER_DNS_SERVERS]
    data['ntp_configuration']['ntp_servers'] = [{'server': {'addr': VCENTER_NTP, 'type': "DNS"}}]
    r = requests.put(uri_base+'api/systemconfiguration', data=json.dumps(data) ,verify=False, headers=GLOBAL_LOGIN_HEADERS[c_ip], cookies=GLOBAL_LOGIN_COOKIES[c_ip])
    if r.status_code not in [200,201]:
        raise Exception(r.text)
    r = requests.get(uri_base+'api/systemconfiguration', verify=False, headers=GLOBAL_LOGIN_HEADERS[c_ip] ,cookies=GLOBAL_LOGIN_COOKIES[c_ip])
    if r.status_code not in [200,201]:
        raise Exception(r.text)
    data = r.json()
    data['default_license_tier']='ENTERPRISE'
    r = requests.put(uri_base+'api/systemconfiguration', data=json.dumps(data) ,verify=False, headers=GLOBAL_LOGIN_HEADERS[c_ip], cookies=GLOBAL_LOGIN_COOKIES[c_ip])
    if r.status_code not in [200,201]:
        print(r.text)
        print("license tier ENTERPRISE failed")
    print("change systemconfiguration settings -- done")

    change_to_default_password(c_ip)
    reset_login(c_ip)
    login_and_set_global_variables(c_ip)
    print("setting complete")


def set_welcome_password_and_set_systemconfiguration(c_ip,current_password=DEFAULT_SETUP_PASSWORD):
    wait_until_cluster_ready(c_ip)
    login_and_set_global_variables(c_ip,current_password)
    
    uri_base = 'https://' + c_ip + '/'
    time.sleep(1)    
    print("change systemconfiguration settings")
    #import ipdb;ipdb.set_trace()
    r = requests.get(uri_base+'api/systemconfiguration', verify=False, headers=GLOBAL_LOGIN_HEADERS[c_ip] ,cookies=GLOBAL_LOGIN_COOKIES[c_ip])
    if r.status_code not in [200,201]:
        raise Exception(r.text)
    data = r.json()
    data['portal_configuration']['password_strength_check'] = False
    data['portal_configuration']['allow_basic_authentication'] = True
    data['dns_configuration']['server_list'] = [{'addr':val , 'type':'V4'} for val in VCENTER_DNS_SERVERS]
    data['ntp_configuration']['ntp_servers'] = [{'server': {'addr': VCENTER_NTP, 'type': "DNS"}}]
    data['welcome_workflow_complete']=True
    r = requests.put(uri_base+'api/systemconfiguration', data=json.dumps(data) ,verify=False, headers=GLOBAL_LOGIN_HEADERS[c_ip], cookies=GLOBAL_LOGIN_COOKIES[c_ip])
    if r.status_code not in [200,201]:
        raise Exception(r.text)
    r = requests.get(uri_base+'api/systemconfiguration', verify=False, headers=GLOBAL_LOGIN_HEADERS[c_ip] ,cookies=GLOBAL_LOGIN_COOKIES[c_ip])
    if r.status_code not in [200,201]:
        raise Exception(r.text)
    data = r.json()
    data['default_license_tier']='ENTERPRISE'
    r = requests.put(uri_base+'api/systemconfiguration', data=json.dumps(data) ,verify=False, headers=GLOBAL_LOGIN_HEADERS[c_ip], cookies=GLOBAL_LOGIN_COOKIES[c_ip])
    if r.status_code not in [200,201]:
        print(r.text)
        print("license tier ENTERPRISE failed")
    print("change systemconfiguration settings -- done")

    print("setting backup default passphrase")
    r = requests.get(uri_base+'api/backupconfiguration',verify=False, headers=GLOBAL_LOGIN_HEADERS[c_ip], cookies=GLOBAL_LOGIN_COOKIES[c_ip])
    if r.status_code not in [200,201]:
        raise Exception(r.text)
    data = r.json()
    uuid = data['results'][0]['uuid']

    time.sleep(1) 
    r = requests.get(uri_base+'api/backupconfiguration'+'/'+uuid,verify=False, headers=GLOBAL_LOGIN_HEADERS[c_ip], cookies=GLOBAL_LOGIN_COOKIES[c_ip])
    if r.status_code not in [200,201]:
        raise Exception(r.text)
    data = r.json()
    data['backup_passphrase']='avi123'
    
    time.sleep(1) 
    r = requests.put(uri_base+'api/backupconfiguration'+'/'+uuid, data=json.dumps(data) ,verify=False, headers=GLOBAL_LOGIN_HEADERS[c_ip], cookies=GLOBAL_LOGIN_COOKIES[c_ip])
    if r.status_code not in [200,201]:
        raise Exception(r.text)

    r = requests.get(uri_base+'api/controllerproperties',verify=False, headers=GLOBAL_LOGIN_HEADERS[c_ip], cookies=GLOBAL_LOGIN_COOKIES[c_ip])
    if r.status_code not in [200,201]:
        raise Exception(r.text)
    data = r.json()
    data['api_idle_timeout']=1400
    
    time.sleep(1) 
    r = requests.put(uri_base+'api/controllerproperties', data=json.dumps(data) ,verify=False, headers=GLOBAL_LOGIN_HEADERS[c_ip], cookies=GLOBAL_LOGIN_COOKIES[c_ip])
    if r.status_code not in [200,201]:
        raise Exception(r.text)
    print("setting backup default passphrase -- done")

    change_to_default_password(c_ip)
    reset_login(c_ip)
    login_and_set_global_variables(c_ip)
    print("setting complete")
   
def setup_tmux_install_only(c_ip):
    login_and_set_global_variables(c_ip,None)
    print("Setting Controller with tmux install only and other packages")
    env_sudo = fabric.Config(overrides={'sudo': {'password': GLOBAL_CURRENT_PASSWORD[c_ip]}})
    conn = fabric.Connection(c_ip, "admin", connect_kwargs={'password':GLOBAL_CURRENT_PASSWORD[c_ip]}, config=env_sudo)
    conn.put("/var/www/html/ctlr_new.tar.gz","/tmp/")
    conn.sudo("mv /tmp/ctlr_new.tar.gz /root/")
    conn.sudo("bash -c 'cd /root/ && tar -xf ctlr_new.tar.gz'")
    conn.sudo("bash -c 'cd /root/controller_customization_new/ && ./controller_cust_install_only.sh'")
    conn.sudo("bash -c 'cd /opt/avi/python/ && ls'")

def setup_tmux(c_ip):
    login_and_set_global_variables(c_ip,None)
    print("Setting Controller with tmux and other packages")
    env_sudo = fabric.Config(overrides={'sudo': {'password': GLOBAL_CURRENT_PASSWORD[c_ip]}})
    conn = fabric.Connection(c_ip, "admin", connect_kwargs={'password':GLOBAL_CURRENT_PASSWORD[c_ip]}, config=env_sudo)
    conn.put("/var/www/html/ctlr_new.tar.gz","/tmp/")
    conn.sudo("mv /tmp/ctlr_new.tar.gz /root/")
    conn.sudo("bash -c 'cd /root/ && tar -xf ctlr_new.tar.gz'")
    conn.sudo("bash -c 'cd /root/controller_customization_new/ && ./controller_cust.sh'")
    conn.sudo("bash -c 'cd /opt/avi/python/ && ls'")


def flush_db(c_ip):
    login_and_set_global_variables(c_ip)
    env_sudo = fabric.Config(overrides={'sudo': {'password': GLOBAL_CURRENT_PASSWORD[c_ip]}})
    conn = fabric.Connection(c_ip, "admin", connect_kwargs={'password':GLOBAL_CURRENT_PASSWORD[c_ip]}, config=env_sudo)
    conn.sudo("bash -c 'cd /root/ && sudo systemctl stop process-supervisor.service && rm /var/lib/avi/etc/flushdb.done && /opt/avi/scripts/flushdb.sh && sudo systemctl start process-supervisor.service'")

def set_version_controller(c_ip):
    global GLOBAL_LOGIN_HEADERS
    global GLOBAL_BUILD_NO
    if GLOBAL_LOGIN_HEADERS.get("X-Avi-Version",False):
        return
    uri_base = 'https://' + c_ip + '/'
    build_no = ""
    resp = requests.get(uri_base+'api/initial-data',verify=False, headers=GLOBAL_LOGIN_HEADERS[c_ip], cookies=GLOBAL_LOGIN_COOKIES[c_ip])
    if resp.status_code == 200:
        data = resp.json()
        version = data['version']['Version']
        build_no = data['version']['build']
    else:
        version = input("Please Enter Controller Version ? :")
    GLOBAL_LOGIN_HEADERS[c_ip]["X-Avi-Version"] = "%s" % version
    GLOBAL_BUILD_NO[c_ip] = build_no
    print("Controller Version: %s-%s"%(version,build_no))

def get_version_controller_from_ova(ova_path):
    print("Getting Controller Version from OVA %s"%(ova_path))
    cmd_ova_spec = '/usr/bin/ovftool --schemaValidate %s'%(ova_path)
    ova_specs = subprocess.check_output(shlex.split(cmd_ova_spec),text=True)
    pattern = re.compile(r'\nVersion:\s*(\d+\.\d+\.\d+)\n')
    res = re.findall(pattern,ova_specs)
    if res:
        return res[0]
    else:
        print("Unable to get Controller Version from OVA %s"%(ova_path))
        version = input("Please Enter Controller Version ? :")
        return version


def wait_until_cloud_ready(c_ip, cookies, headers, cloud_uuid, timeout=850):
    uri_base = 'https://' + c_ip + '/'

    sleep_time = 10
    iters = int(timeout / sleep_time)
    rsp = ''
    uri = uri_base+'api/cloud/%s/runtime'%(cloud_uuid)
    for i in range(iters):
        try:
            rsp = requests.get(uri,verify=False, headers=headers, cookies=cookies)
        except:
            print('Get for %s fails. Controller %s' % (uri, c_ip))
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

def setup_vs(c_ip, version="" ,timeout=60):
    uri_base = 'https://' + c_ip + '/'
    login_and_set_global_variables(c_ip)
    r = requests.get(uri_base+'api/cloud',verify=False, headers=GLOBAL_LOGIN_HEADERS[c_ip], cookies=GLOBAL_LOGIN_COOKIES[c_ip])
    data = {}
    for val in r.json()['results']:
        if val['name'] == 'Default-Cloud':
            data = val
            break
    default_cloud_uuid = data.get('uuid',"")
    print("creating a vs")
    count = 0
    port_group_subnet = ""
    port_group_uuid = ""
    occupied_ips = []
    while True:
        try:
            # getting dev020 network uuid
            r = requests.get(uri_base+'api/networksubnetlist/?discovered_only=true&page_size=-1&cloud_uuid=%s'%(default_cloud_uuid),verify=False, headers=GLOBAL_LOGIN_HEADERS[c_ip], cookies=GLOBAL_LOGIN_COOKIES[c_ip])
            res = r.json()['results']
            exclude_subnet = []
            port_data = {}
            for val in res:
                for subnet in val.get("subnet",[]):
                    if str(subnet.get("prefix").get("ip_addr").get("addr")) == "100.0.0.0" and str(subnet.get("prefix").get("mask")) == "8":
                        exclude_subnet.append(val)
                if VCENTER_PORT_GROUP in val['name']:
                    port_data = val

            for val in exclude_subnet:
                r1 = requests.get(uri_base+'api/network/%s'%(val["uuid"]),verify=False, headers=GLOBAL_LOGIN_HEADERS[c_ip], cookies=GLOBAL_LOGIN_COOKIES[c_ip])
                data1 = r1.json()
                data1["exclude_discovered_subnets"] = True
                r2 = requests.put(uri_base+'api/network/%s'%(val["uuid"]), data=json.dumps(data1) ,verify=False, headers=GLOBAL_LOGIN_HEADERS[c_ip], cookies=GLOBAL_LOGIN_COOKIES[c_ip])
                if r2.status_code not in [200,201]:
                    raise Exception(r.text)
                print("Excluding Subnets %s\n%s\n%s"%(val["uuid"],val["name"],val["subnet"]))

            port_group_uuid = port_data['uuid']
            port_group_subnet = port_data["subnet"][0]["prefix"]["ip_addr"]["addr"] + "/" + str(port_data["subnet"][0]["prefix"]["mask"])
            "https://10.102.65.176/api/cloud/cloud-a1746f89-2f84-4255-9061-8a024d89ca5f/serversbynetwork/?network_uuid=dvportgroup-123-cloud-a1746f89-2f84-4255-9061-8a024d89ca5f&page_size=-1"
            break
        except Exception as e:
            print("Error: %s"%(str(e)))
            time.sleep(10)
            count += 1
            if count == 5: break
    count = 0
    while True and port_group_uuid:
        r = requests.get(uri_base+'api/cloud/%s/serversbynetwork/?network_uuid=%s&page_size=-1'%(default_cloud_uuid,port_group_uuid),verify=False, headers=GLOBAL_LOGIN_HEADERS[c_ip], cookies=GLOBAL_LOGIN_COOKIES[c_ip])
        try:
            for val in r.json()['results']:
                for guest_nic in val['guest_nic']:
                    for guest_ip in guest_nic['guest_ip']:
                        occupied_ips.append(guest_ip["prefix"]["ip_addr"]["addr"])
            break
        except:
            print("Error: ",r.json())
            time.sleep(10)
            count += 1
            if count == 5: break
    if not port_group_subnet:
        port_group_subnet = VCENTER_SERVER_SUBNET
    ip_list = list(set([str(ip) for ip in ipaddress.IPv4Network(port_group_subnet)]) - set([str(ip) for ip in ipaddress.IPv4Network(port_group_subnet.replace("/24","/26"))]))
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
                        "vip_id":1,
                        "ip_address":{
                            "type":"V4",
                            "addr":vsvip_ip
                        }
                    }
                ]
            }

        }
    }

    r = requests.post(uri_base+'api/macro', data=json.dumps(data_macro), verify=False, headers=GLOBAL_LOGIN_HEADERS[c_ip], cookies=GLOBAL_LOGIN_COOKIES[c_ip])
    if r.status_code not in [200,201]:
        raise Exception(r.text)
    print("VS 'test_vs' Created")

@retry(Exception,tries=30,delay=10)
def wait_until_cloud_put(c_ip, uri_base):
    data = {}
    r = requests.get(uri_base+'api/cloud',verify=False, headers=GLOBAL_LOGIN_HEADERS[c_ip], cookies=GLOBAL_LOGIN_COOKIES[c_ip])
    for val in r.json()['results']:
        if val['name'] == 'Default-Cloud':
            data = val
            break
    default_cloud_uuid = data['uuid']
    data.update({
        "dhcp_enabled":True,
        "mgmt_ip_v4_enabled":True,
        "mgmt_ip_v6_enabled":False,
        "vtype":"CLOUD_VCENTER",
        "vcenter_configuration":{
            "privilege": "WRITE_ACCESS",
            "username": VCENTER_USER,
            "vcenter_url": VCENTER_IP,
            "password": VCENTER_PASSWORD,
            "datacenter": VCENTER_DATACENTER_NAME,
            "use_content_lib": False
        }
    })
    r = requests.put(uri_base+'api/cloud/%s'%(default_cloud_uuid), data=json.dumps(data) ,verify=False, headers=GLOBAL_LOGIN_HEADERS[c_ip], cookies=GLOBAL_LOGIN_COOKIES[c_ip])
    if r.status_code not in [200,201]:
        raise Exception(r.text)
    return data

def setup_cloud_se(c_ip,version=""):
    login_and_set_global_variables(c_ip, None)
    print("setting up vmware write access cloud")
    put_to_cloud(c_ip)
    setup_cloud_se_wo_put_to_cloud(c_ip,version)

def put_to_cloud(c_ip):
    print("setting up vmware write access cloud")
    uri_base = 'https://' + c_ip + '/'
    login_and_set_global_variables(c_ip, None)
    print("setting up vmware write access cloud")
    wait_until_cloud_put(c_ip,uri_base)

def setup_cloud_se_wo_put_to_cloud(c_ip,version=""):
    uri_base = 'https://' + c_ip + '/'
    data = {}
    r = requests.get(uri_base+'api/cloud',verify=False, headers=GLOBAL_LOGIN_HEADERS[c_ip], cookies=GLOBAL_LOGIN_COOKIES[c_ip])
    for val in r.json()['results']:
        if val['name'] == 'Default-Cloud':
            data = val
            break
    default_cloud_uuid = data['uuid']
    wait_until_cloud_ready(c_ip, GLOBAL_LOGIN_COOKIES[c_ip], GLOBAL_LOGIN_HEADERS[c_ip], default_cloud_uuid, timeout=850)
    management_network = "/api/vimgrnwruntime/?name=%s"%(VCENTER_MANAGEMENT_MAP["Internal_Management"]["name"])
    r = requests.get(uri_base+'api/cloud',verify=False, headers=GLOBAL_LOGIN_HEADERS[c_ip], cookies=GLOBAL_LOGIN_COOKIES[c_ip])
    data = r.json()['results'][0]
    data["vcenter_configuration"]["management_network"] = management_network
    r = requests.put(uri_base+'api/cloud/%s'%(default_cloud_uuid), data=json.dumps(data) ,verify=False, headers=GLOBAL_LOGIN_HEADERS[c_ip], cookies=GLOBAL_LOGIN_COOKIES[c_ip])
    if r.status_code not in [200,201]:
        raise Exception(r.text)
    print("changing service engine group settings")
    r = requests.get(uri_base+'api/serviceenginegroup',verify=False, headers=GLOBAL_LOGIN_HEADERS[c_ip], cookies=GLOBAL_LOGIN_COOKIES[c_ip])
    for val in r.json()['results']:
        if default_cloud_uuid in val['cloud_ref']:
            data = val
            break
    se_name_prefix = c_ip.split(".")[-1]+"_"+GLOBAL_LOGIN_HEADERS[c_ip]["X-Avi-Version"].replace(".","")
    data.update({
        "se_name_prefix":se_name_prefix,
        "se_deprovision_delay":0,
        "vcenter_folder":VCENTER_FOLDER_NAME,
        "max_se":"1" if not SE_IPS_TO_USE_FOR_CURRENT_CTLR else str(len(SE_IPS_TO_USE_FOR_CURRENT_CTLR))
    })
    r = requests.put(uri_base+'api/serviceenginegroup/%s'%(data['uuid']), data=json.dumps(data), verify=False, headers=GLOBAL_LOGIN_HEADERS[c_ip], cookies=GLOBAL_LOGIN_COOKIES[c_ip])
    if r.status_code not in [200,201]:
        raise Exception(r.text)
    
    if SE_IPS_TO_USE_FOR_CURRENT_CTLR:
        mgmt_network = {}
        print("Set Static IPs for SE")
        # set static ips for se
        @retry(ValueError, 240, 10)
        def retry_get():
            return_network = {}
            r = requests.get(uri_base+"/api/network/?name=%s"%(VCENTER_MANAGEMENT_MAP["Internal_Management"]["name"]),verify=False, headers=GLOBAL_LOGIN_HEADERS[c_ip], cookies=GLOBAL_LOGIN_COOKIES[c_ip])
            mgmt_networks = r.json()["results"]
            for n in mgmt_networks:
                if default_cloud_uuid in n["cloud_ref"]:
                    print(n)
                    return_network = n
                    return return_network
                print("%s not found"%(VCENTER_MANAGEMENT_MAP["Internal_Management"]["name"]))
                raise ValueError("not found")
            if not return_network: 
                print("%s not found"%(VCENTER_MANAGEMENT_MAP["Internal_Management"]["name"]))
                raise ValueError("not found")
            return return_network
        mgmt_network = retry_get()

        static_ip_ranges = []
        for se_ip in SE_IPS_TO_USE_FOR_CURRENT_CTLR:
            data = {
                "range": {
                    "begin": {
                        "addr": se_ip,
                        "type": "V4"
                    },
                    "end": {
                        "addr": se_ip,
                        "type": "V4"
                    }
                },
                "type": "STATIC_IPS_FOR_SE"
            }
            static_ip_ranges.append(data)
        data_configured_subnets = [
            {
                "prefix":{
                    "mask":VCENTER_MANAGEMENT_MAP["Internal_Management"]["mask"],
                    "ip_addr":{
                            "addr":VCENTER_MANAGEMENT_MAP["Internal_Management"]["subnet"].split("/")[0],
                            "type":"V4"
                    }
                },
                "static_ip_ranges":static_ip_ranges
            }
        ]
        mgmt_network["configured_subnets"] = data_configured_subnets
        mgmt_network["dhcp_enabled"] = False
        r = requests.put(uri_base+"/api/network/%s"%(mgmt_network["uuid"]),data=json.dumps(mgmt_network), verify=False, headers=GLOBAL_LOGIN_HEADERS[c_ip], cookies=GLOBAL_LOGIN_COOKIES[c_ip])
        if r.status_code not in [200,201]:
            raise Exception(r.text)
        
        vrf_context = {}
        print("setting default gateway")
        r = requests.get(uri_base+"/api/vrfcontext",verify=False, headers=GLOBAL_LOGIN_HEADERS[c_ip], cookies=GLOBAL_LOGIN_COOKIES[c_ip])
        vrf_contexts = r.json()["results"]
        for i in vrf_contexts:
            if default_cloud_uuid in i["cloud_ref"] and i["name"] == "management":
                vrf_context = i
        static_routes = [
            {
                "next_hop":{
                    "addr": VCENTER_MANAGEMENT_MAP["Internal_Management"]["gateway"],
                    "type": "V4"
                },
                "prefix":{
                    "mask":0,
                    "ip_addr":{
                            "addr":"0.0.0.0",
                            "type":"V4"
                    }
                },
                "route_id":1
            }
        ]
        vrf_context["static_routes"] = static_routes
        r = requests.put(uri_base+"/api/vrfcontext/%s"%(vrf_context["uuid"]),data=json.dumps(vrf_context), verify=False, headers=GLOBAL_LOGIN_HEADERS[c_ip], cookies=GLOBAL_LOGIN_COOKIES[c_ip])
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
            return dc

def get_cluster_obj(datacenter_obj,cluster_name):
    
    for cluster in datacenter_obj.hostFolder.childEntity:
        if cluster.name == cluster_name:
            cluster_obj = cluster
            return cluster_obj
    return None

def get_folder_obj(si,datacenter_name, folder_name):
    search_text = "%s/vm/%s"%(datacenter_name,folder_name)
    search_folder = si.RetrieveContent().searchIndex.FindByInventoryPath(search_text)
    if not search_folder:
        print("folder %s not found"%(folder_name))
        print("search text = %s"%(search_text))
        return False
    return search_folder


def get_index_format_ips_excluding_dev_ip(si,free=True,ips_to_check=[]):
    if not ips_to_check:
        ips_to_check = ALL_RESERVED_IPS
    if free:
        free_ips = {str(index):val for index,val in enumerate([ip for ip in ips_to_check if (check_if_ip_is_valid_and_free(si,ip,True) and ip!=DEV_VM_IP)]) }
        return free_ips
    else:
        used_ips = {str(index):val for index,val in enumerate([ip for ip in ips_to_check if (not check_if_ip_is_valid_and_free(si,ip,True) and ip!=DEV_VM_IP)]) }
        return used_ips

def get_free_controller_ips(si):
    while True:
        get_again = False
        free_ips_1 = get_index_format_ips_excluding_dev_ip(si,free=True)
        print ("Free IP's : %s"%(free_ips_1))
        mgmt_ips = get_ips_from_index(free_ips_1)
        for mgmt_ip in mgmt_ips:
            if not check_if_ip_is_valid_and_free(si,mgmt_ip,print_not_free=True):
                get_again = True
                continue
        if not get_again:
            return mgmt_ips


def get_used_controller_ips(si):
    used_ips_1 = get_index_format_ips_excluding_dev_ip(si,free=False)
    print ("Configured IP's : %s"%(used_ips_1))
    return get_ips_from_index(used_ips_1)


def get_ips_from_index(index_format_ips):
    mgmt_indexes = input("Controller IP ? [Enter comma separated Indexes] :")
    mgmt_indexes = [i.strip() for i in mgmt_indexes.split(",") if (int(i.strip()) or i.strip()=="0")]
    mgmt_ips = []
    for mgmt_index in mgmt_indexes:
        if mgmt_index not in index_format_ips.keys():
            print("not a valid index ")
            mgmt_ips_str = input("Controller IP ? [Enter comma separated IPs] :")
            print("Controller IPs: %s"%(mgmt_ips_str))
            mgmt_ips.extend([i.strip() for i in mgmt_ips_str.split(",")])
        else:
            mgmt_ips.append(index_format_ips[mgmt_index])
    print("Controller IPs: %s"%(mgmt_ips))
    return mgmt_ips

def get_leader_ip_from_index(index_format_ips):
    input_str = input("Controller IP ? [Enter Index] :")
    mgmt_index = input_str.strip()
    mgmt_ip = ""
    while True:
        if mgmt_index not in index_format_ips.keys():
            print("not a valid index ")
            continue
        else:
            mgmt_ip = index_format_ips[mgmt_index]
            break
    print("Controller Leader IP: %s"%(mgmt_ip))
    return mgmt_ip

def get_used_controller_ip(si):
    used_ips_1 = get_index_format_ips_excluding_dev_ip(si,free=False)
    print ("Configured IP's : %s"%(used_ips_1))
    mgmt_index = input("Controller IP ? [Enter Index] :")
    if mgmt_index not in used_ips_1.keys():
        print("not a valid index ")
        mgmt_ip = input("Controller IP ? [Enter IP] :")
    else:
        mgmt_ip = used_ips_1[mgmt_index]
    print("Controller IP: %s"%(mgmt_ip))
    return mgmt_ip

def check_if_ip_is_valid_and_free(si,ip,only_check=False,print_not_free=False):
    try:
        mgmt_ip = inet_ntoa(inet_aton(ip))
    except Exception as e:
        print(str(e))
        print("Ip %s is not valid"%(ip))
        return False
    search = si.RetrieveContent().searchIndex
    vms = list(set(search.FindAllByIp(ip=ip,vmSearch=True)))
    if not vms:
        return True
    if vms and only_check:
        if print_not_free: print("IP %s is not free"%(ip))
        return False
    delete_vm = False
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
    keypath = SYSADMIN_KEYPATH
    if os.path.exists(keypath):
        with open(keypath, 'r') as keyfile:
            data = keyfile.read().rstrip('\n')
            return data
    raise Exception('Failed to find sysadmin public key file at %s\n' % (keypath))

def configure_cluster_details(mgmt_leader_ip, mgmt_ips):
    wait_until_cluster_ready(mgmt_leader_ip)
    login_and_set_global_variables(mgmt_leader_ip)
    
    uri_base = 'https://' + mgmt_leader_ip + '/'
    time.sleep(1)    
    print("change cluster settings")
    #import ipdb;ipdb.set_trace()
    r = requests.get(uri_base+'api/cluster', verify=False, headers=GLOBAL_LOGIN_HEADERS[mgmt_leader_ip] ,cookies=GLOBAL_LOGIN_COOKIES[mgmt_leader_ip])
    if r.status_code not in [200,201]:
        raise Exception(r.text)
    data = r.json()
    for ip in mgmt_ips:
        if ip != mgmt_leader_ip:
            node_data = {"name":ip, "ip": {"addr": ip, "type": "V4"}, "password": GLOBAL_CURRENT_PASSWORD[mgmt_leader_ip]}
            data["nodes"].append(node_data)
    r = requests.put(uri_base+'api/cluster', data=json.dumps(data) ,verify=False, headers=GLOBAL_LOGIN_HEADERS[mgmt_leader_ip], cookies=GLOBAL_LOGIN_COOKIES[mgmt_leader_ip])
    if r.status_code not in [200,201]:
        raise Exception(r.text)
    

def configure_raw_controller_cluster(si, mgmt_leader_ip, mgmt_ips):
    for ip in mgmt_ips:
        try:
            configure_password_only(ip)
        except Exception as e:
            print("----------------------",str(e))


    if len(mgmt_ips)>1:
        try:
            se_ips_to_use_for_ctlr(si,mgmt_leader_ip)
            set_welcome_password_and_set_systemconfiguration(mgmt_leader_ip)
            put_to_cloud(mgmt_leader_ip)
            configure_cluster_details(mgmt_leader_ip, mgmt_ips)
        except Exception as e:
            print("----------------------",str(e))
    
    for ip in mgmt_ips:
        try:
            setup_tmux(ip)
        except Exception as e:
            print("----------------------",str(e))
    
    if len(mgmt_ips)>1:
        try:
            wait_until_cluster_ready(mgmt_leader_ip)
            setup_cloud_se_wo_put_to_cloud(mgmt_leader_ip)
            setup_vs(mgmt_leader_ip)
        except Exception as e:
            print("----------------------",str(e))

def configure_raw_controller(si,mgmt_ip):
    se_ips_to_use_for_ctlr(si,mgmt_ip)
    set_welcome_password_and_set_systemconfiguration(mgmt_ip)
    put_to_cloud(mgmt_ip)
    setup_tmux(mgmt_ip)
    setup_cloud_se_wo_put_to_cloud(mgmt_ip)
    setup_vs(mgmt_ip)

def configure_password_only(mgmt_ip):
    set_password_only_and_set_systemconfiguration(mgmt_ip)

def configure_raw_controller_wo_tmux(si,mgmt_ip):
    se_ips_to_use_for_ctlr(si,mgmt_ip)
    set_welcome_password_and_set_systemconfiguration(mgmt_ip)
    setup_cloud_se(mgmt_ip)
    setup_vs(mgmt_ip)


def upload_pkg_to_ctlr(c_ip,source_pkg_path):
    login_and_set_global_variables(c_ip,None)
    cmd = 'sshpass -p %s scp %s admin@%s:~/'%(GLOBAL_CURRENT_PASSWORD[c_ip],source_pkg_path,c_ip)
    print("Running Upload Command::: %s"%(cmd))
    subprocess.run(shlex.split(cmd), check=True)
    print("Upload Done")


def reimage_controller(c_ip):
    print("Starting reimage...")
    env_sudo = fabric.Config(overrides={'sudo': {'password': GLOBAL_CURRENT_PASSWORD[c_ip]}})
    conn = fabric.Connection(c_ip, "admin", connect_kwargs={'password':GLOBAL_CURRENT_PASSWORD[c_ip]}, config=env_sudo)
    conn.sudo("/opt/avi/scripts/reimage_system.py --base /home/admin/controller.pkg")
    print("reimage started")

def check_upgrade_status(c_ip):
    status = False

    @retry(ValueError,tries=100,delay=20)
    def _check_upgrade_state():
        nonlocal status
        uri_base = 'https://' + c_ip + '/'
        try:
            r = requests.get(uri_base+'api/upgradestatusinfo/',verify=False, headers=GLOBAL_LOGIN_HEADERS[c_ip], cookies=GLOBAL_LOGIN_COOKIES[c_ip], timeout=20)
        except Exception as e:
            print("Bad Service")
            raise ValueError("Bad Service")
        if r.status_code == 401:
            reset_login(c_ip)
            login_and_set_global_variables(c_ip,None)
            print("login again ")
            ValueError("login again ")
        if r.status_code != 200:
            err = "Upgrade in Progress"
            print(err)
            raise ValueError(err)
        
        else:
            for res in r.json()['results']:
                if res.get('node_type','') == 'NODE_CONTROLLER_CLUSTER':
                    for check in res.get('upgrade_readiness',{}).get('checks',[]):
                        if 'error' in check.get('state','').lower():
                            print("Upgrade pre check failed !!!")
                            exit(1)
                    if 'completed' in res.get('state',{}).get('state','').lower():
                        print("Controller Upgrade Complete")
                        status = True
                        return
                    elif 'SE_UPGRADE_IN_PROGRESS' in res.get('state',{}).get('state',''):
                        print("Controller Upgrade Complete")
                        status = True
                        return
                    else:
                        err = "Upgrade in progress %s"%(res['progress'])
                        print(err)
                        raise ValueError(err)
    _check_upgrade_state()
    if not status:
        print("Upgrade Failed !!!!!!!!!!! ")
        exit(1)

def get_all_se(c_ip):
    login_and_set_global_variables(c_ip,None)
    uri_base = 'https://' + c_ip + '/'
    resp = requests.get(uri_base+'api/serviceengine/',verify=False, headers=GLOBAL_LOGIN_HEADERS[c_ip], cookies=GLOBAL_LOGIN_COOKIES[c_ip])
    if resp.status_code != 200:
        raise Exception(resp.text)
    se_datas = resp.json()
    mgmt_se_ips = []
    se_uuids = []
    for se in se_datas['results']:
        for i in se.get('mgmt_vnic',{}).get('vnic_networks',[]):
            ip = i.get('ip',{}).get('ip_addr',{}).get('addr','')
            if ip:
                mgmt_se_ips.append(ip)
            se_uuids.append(se.get('uuid'))
    return mgmt_se_ips

def delete_all_se(si,c_ip):
    print("Deleting all SEs vms")
    login_and_set_global_variables(c_ip,None)
    uri_base = 'https://' + c_ip + '/'
    se_uuids = []
    mgmt_se_ips = get_all_se(c_ip)
    if not mgmt_se_ips:
        return
    print("SE IPs %s"%(mgmt_se_ips))
    poweroff_and_delete_vm(mgmt_se_ips,delete=True,si=si)
    print("Deleting SEs from controller")
    for se_uuid in se_uuids:
        resp = requests.delete(uri_base+'api/serviceengine/%s?force_delete=True'%(se_uuid),verify=False, headers=GLOBAL_LOGIN_HEADERS[c_ip], 
        cookies=GLOBAL_LOGIN_COOKIES[c_ip])
        if resp.status_code > 299:
            print("Delete of SE %s from controller failed"%(se_uuid))
        else:
            print("SE %s deleted"%(se_uuid))

def is_version_eng(version,build_dir):
    dir = os.path.join("/mnt/builds/eng",build_dir)
    version_file = os.path.join(dir,'VERSION')
    with open(version_file,"r") as f:
        file_data = f.read()
    pattern = re.compile(r'^Version.*(\d{2}\.\d{1,2}\.\d{1,2})$', re.MULTILINE)
    version_list = re.findall(pattern,file_data)
    if version_list and version in version_list:
        return True
    return False

def list_all_builds_in_mnt_builds(version):
    "[[index version buildno file date],...]"
    all_builds = []
    dir = os.path.join("/mnt/builds/",version)
    if not os.path.isdir(dir):
        print("Not a valid dir %s"%(dir))
        return {}
    for in_dir in os.listdir(dir):
        ova_file = ""
        buildno = ""
        time_ago = ""
        if "last" in in_dir:
            version_file = os.path.join(dir,in_dir,'VERSION')
            ova_file = os.path.join(dir,in_dir,"controller.ova")
            if not os.path.isfile(ova_file):
                ova_file = ""
            if os.path.isfile(version_file):
                with open(version_file,"r") as f:
                    file_data = f.read()
                pattern = re.compile(r'^build.*(\d{4,5})$', re.MULTILINE)
                build_regex = re.findall(pattern,file_data)
                buildno = build_regex[0] if build_regex else ""
                modified_time = os.path.getmtime(version_file)
                time_ago = str(timedelta(seconds=time.time()-modified_time)) + " ago"
                all_builds.append([0 ,version, int(buildno), ova_file, time_ago])
    all_builds.sort(key=lambda x: x[2])
    for i in range(len(all_builds)):
        all_builds[i][0] = i+1
    return all_builds


def se_ips_to_use_for_ctlr(si,c_ip):
    global SE_IPS_TO_USE_FOR_CURRENT_CTLR
    if SE_IPS_TO_USE_FOR_CURRENT_CTLR:
        return
    se_ip = ""
    if ".32." in c_ip:
        se_ip = c_ip.replace(".32.",".33.")
    if ".11." in c_ip:
        se_ip = c_ip.replace(".11.",".12.")
    while True:
        free_ips_1 = get_index_format_ips_excluding_dev_ip(si,True,SE_IPS)
        print("SE IPs Configuration")
        print ("Free SE IP's : %s"%(list(free_ips_1.values())))
        default_ip = se_ip
        mgmt_ips = input("Management IP ? [Enter Comma Separated IP] [Default: %s][or DHCP]: "%(default_ip))
        if not mgmt_ips:
            if not se_ip: continue
            mgmt_ips = [default_ip]
        else:
            mgmt_ips = mgmt_ips.split(",")
        if len(mgmt_ips) == 1 and mgmt_ips[0].upper() == "DHCP":
            SE_IPS_TO_USE_FOR_CURRENT_CTLR = []
            return
        for ip in mgmt_ips:
            mgmt_ip = ip.strip()
            if mgmt_ip:
                if check_if_ip_is_valid_and_free(si,mgmt_ip,print_not_free=True):
                    print(" %s ip is free"%(mgmt_ip))
                    SE_IPS_TO_USE_FOR_CURRENT_CTLR.append(mgmt_ip)
        if SE_IPS_TO_USE_FOR_CURRENT_CTLR:
            return

def deploy_ova(cmd):
    while True:
        try:
            subprocess.run(cmd, shell=True,check=True)
            break
        except subprocess.CalledProcessError as e:
            print(str(e))
            print("======================== Retrying Ova deploy ============================")

def generate_controller_from_ova():
    vm_type = "controller"
    si = connect()
    custom_version = input("Custom Build [Y/N]? [N]: ")
    ctlr_name = ""
    if custom_version.lower() == "y":
        default_path = "/home/aviuser/workspace/avi-dev/build/controller.ova"
        source_ova_path = input("Source Ova Path (local/http/ftp) ? [Default: %s] :"%(default_path))
        if not source_ova_path:
            source_ova_path = default_path
    else:
        while True:
            version = input("Version ?: ")
            if not version:
                continue
            builds = list_all_builds_in_mnt_builds(version)
            if builds:
                break
        final_print_vals = [("Index","Version","Build No", "File", "Date")]
        for value in builds:
            final_print_vals.append((value[0],value[1],value[2],value[3],value[4]))
        print(tabulate(final_print_vals, headers="firstrow", tablefmt="psql"))
        while True:
            build_index = int(input("Build to deploy? [Index]: "))
            if int(build_index) <= len(builds) and int(build_index) > 0:
                break
        source_ova_path = builds[build_index-1][3]
        print("Source Ova Path = %s"%(source_ova_path))
        ctlr_name = "ctlr_%s-%s"%(builds[build_index-1][1],builds[build_index-1][2])

    mgmt_leader_ip = ""
    mgmt_ips = []
    while True:
        mgmt_ips = get_free_controller_ips(si)
        if len(mgmt_ips)==3:
            print("Creating a 3 node cluster")
            mgmt_ips_leader = {str(index):val for index,val in enumerate(mgmt_ips) }
            print ("Choose Leader IP : %s"%(mgmt_ips_leader))
            mgmt_leader_ip = get_leader_ip_from_index(mgmt_ips_leader)
            break
        elif len(mgmt_ips)==1:
            print("Creating a single node cluster")
            mgmt_leader_ip = mgmt_ips[0]
            break
        else:
            print("Invalid no of ips for a single or 3 node cluster")
            continue
    
    se_ips_to_use_for_ctlr(si,mgmt_leader_ip)

    vcenter_ip = input("Vcenter IP ? [Default: %s] :"%(VCENTER_IP)) or VCENTER_IP
    datacenter = input("Datacenter Name ? [Default: %s] :"%(VCENTER_DATACENTER_NAME)) or VCENTER_DATACENTER_NAME
    #datacenter_obj = get_datacenter_obj(si,datacenter)
    cluster_name = input("Cluster ? [Default: %s] :"%(VCENTER_CLUSTER_NAME)) or VCENTER_CLUSTER_NAME
    datastore = input("Datastore ? [Default: %s] :"%(VCENTER_DATASTORE_NAME)) or VCENTER_DATASTORE_NAME
    while True:
        folder_name = input("Folder Name ? [Default: %s] :"%(VCENTER_FOLDER_NAME)) or VCENTER_FOLDER_NAME
        if folder_name:
            folder_obj = get_folder_obj(si, datacenter,folder_name)
            if folder_obj:
                break
    management_network = input("Management Network ? [Default: %s][ or %s ]:"%(VCENTER_MANAGEMENT_MAP["Internal_Management"]["name"], VCENTER_MANAGEMENT_MAP["Management"]["name"])) or VCENTER_MANAGEMENT_MAP["Internal_Management"]["name"]

    if not DHCP:
        mask = input("Network Mask ? [Default: %s] :"%(VCENTER_MANAGEMENT_MAP["Internal_Management"]["mask"])) or VCENTER_MANAGEMENT_MAP["Internal_Management"]["mask"]
        gw_ip = input("Gateway IP ? [Default: %s] :"%(VCENTER_MANAGEMENT_MAP["Internal_Management"]["gateway"])) or VCENTER_MANAGEMENT_MAP["Internal_Management"]["gateway"]

    while True:
        vm_name = input("VM Name ? [%s]:"%(ctlr_name))
        if not vm_name: vm_name = ctlr_name
        if not vm_name: continue
        if not check_if_vm_name_exists_in_folder(folder_obj,vm_name) and vm_name:
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
    cmds = {}
    prop = ''
    count = 0
    verify = ""
    if vm_type == 'controller':
        for ip in mgmt_ips:
            if ip == mgmt_leader_ip:
                vm_name_str = vm_name
            else:
                count += 1
                vm_name_str = str(vm_name)+"-"+str(count)
            if not DHCP:
                prop = '--prop:avi.mgmt-ip.CONTROLLER=' + ip + \
                ' --prop:avi.default-gw.CONTROLLER=' + gw_ip + ' '
                prop = prop + ' --prop:avi.mgmt-mask.CONTROLLER=' + str(mask) + ' '
            prop = prop + ' --prop:avi.sysadmin-public-key.CONTROLLER="' + get_own_sysadmin_key() + '" '
            prop += '--name="' + vm_name_str + '" '
            if power_on.lower() == 'y':
                prop += '--powerOn '
            prop += '"--vmFolder='+folder_name+'" ' 
            cmd = 'ovftool --noSSLVerify --X:logLevel=warning --X:logToConsole "--datastore=' + datastore + \
                '" --net:Management="' + management_network + \
                '" ' + prop + source_ova_path + ' ' + vi 
            print ('\n',cmd,'\n')
            verify = input("Verify the command and agree to proceed [Y/N] ? [Y] :") or 'Y'
            if verify.lower() == 'y':
                if ip == mgmt_leader_ip:
                    cmds[ip] = cmd
                else:
                    cmds[ip] = cmd
            else:
                print ("Exiting ...")
                exit(0)

        print ("\nDeploying OVA")
        jobs = []
        """
        for ip in mgmt_ips:
            p = multiprocessing.Process(target=deploy_ova, args=(cmds[ip],))
            jobs.append(p)
            p.start()

        for proc in jobs:
            proc.join()
        """
        if len(mgmt_ips)>1:
            configure_raw_controller_cluster(si, mgmt_leader_ip, mgmt_ips)
        elif len(mgmt_ips) == 1:
            configure_raw_controller(si, mgmt_leader_ip)
        

    print("================== DONE ==============")

if len(sys.argv)==2 and sys.argv[1]=='delete_ctlr_se':
    si = connect()
    mgmt_ips = get_used_controller_ips(si)
    mgmt_se_ips = set()
    for mgmt_ip in mgmt_ips:
        mgmt_se_ips.update(set(get_all_se(mgmt_ip)))
    poweroff_and_delete_vm(mgmt_ips + list(mgmt_se_ips),delete=True,si=si)

if len(sys.argv)==2 and sys.argv[1]=='latest_builds':
    all_builds = []
    while True:
        versions = input("Versions [comma separated] ?: ")
        if not versions:
            continue
        for version in versions.split(","):
            builds = list_all_builds_in_mnt_builds(version.strip())
            if builds:
                all_builds.append(builds)
        if all_builds:
            break
    final_print_vals = [("Index","Version","Build No", "File", "Date")]
    for build in all_builds:
        for value in build:
            final_print_vals.append((value[0],value[1],value[2],value[3],value[4]))
        final_print_vals.append(("---","---","---","---","---"))

    print(tabulate(final_print_vals, headers="firstrow", tablefmt="psql"))
    

if len(sys.argv)==2 and sys.argv[1]=='configure_cloud_vs_se':
    si = connect()
    mgmt_ip = get_used_controller_ip(si)
    login_and_set_global_variables(mgmt_ip,None)
    mgmt_se_ips = get_all_se(mgmt_ip)
    if not mgmt_se_ips:
        se_ips_to_use_for_ctlr(si,mgmt_ip)
    se_ips_to_use_for_ctlr(si,mgmt_ip)
    setup_cloud_se(mgmt_ip)
    setup_vs(mgmt_ip)

if len(sys.argv)==2 and sys.argv[1]=='configure_vs':
    si = connect()
    mgmt_ip = get_used_controller_ip(si)
    setup_vs(mgmt_ip)


if len(sys.argv)==2 and sys.argv[1]=='setup_tmux':
    si = connect()
    mgmt_ip = get_used_controller_ip(si)
    setup_tmux(mgmt_ip)

if len(sys.argv)==2 and sys.argv[1]=='setup_tmux_install_only':
    si = connect()
    mgmt_ip = get_used_controller_ip(si)
    setup_tmux_install_only(mgmt_ip)


if len(sys.argv)==2 and sys.argv[1]=='flush_db_configure_raw_controller_wo_tmux':
    si = connect()
    mgmt_ip = get_used_controller_ip(si)
    se_ips_to_use_for_ctlr(si,mgmt_ip)
    delete_all_se(si,mgmt_ip)
    flush_db(mgmt_ip)
    set_welcome_password_and_set_systemconfiguration(mgmt_ip)
    setup_cloud_se(mgmt_ip)
    setup_vs(mgmt_ip)


if len(sys.argv)==2 and sys.argv[1] == 'generate_controller_from_ova':
    generate_controller_from_ova()


if len(sys.argv)==2 and (sys.argv[1] == 'configure_raw_controller' or sys.argv[1] == 'configure_raw_controller_wo_tmux' or sys.argv[1] == 'configure_password_only'):
    si = connect()
    mgmt_ips = get_used_controller_ips(si)
    for mgmt_ip in mgmt_ips:
        if sys.argv[1] == 'configure_raw_controller':
            configure_raw_controller(si,mgmt_ip)
        if sys.argv[1] == 'configure_raw_controller_wo_tmux':
            configure_raw_controller_wo_tmux(si,mgmt_ip)
        if sys.argv[1] == 'configure_password_only':
            configure_password_only(mgmt_ip)
    

END_TIME = time.time()
print("Time Elapsed %s,  Current Time = %s"%(str(timedelta(seconds=END_TIME-START_TIME)), datetime.datetime.now()))
   

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
