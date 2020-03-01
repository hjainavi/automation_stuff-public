#!/usr/bin/env python

#simplejson.dumps(authtoken_data, indent=4, sort_keys=True)
try:
    import pyVim
except ImportError:
    print "do -->> pip install pyvmomi"
    exit(1)
from pyVim.connect import SmartConnect,Disconnect,SmartConnectNoSSL
from pyVmomi import vim
import socket, struct
import random,sys,time,atexit
from concurrent.futures import ThreadPoolExecutor
import argparse, os, simplejson, ipaddress

home_folder = os.getenv("HOME")
FILE_PATH = os.path.join(home_folder,".config","vsphere_config.txt")

def is_valid_ip_address(ip):
    # Need to change if we need to detect an IPv6 address.
    try:
        socket.inet_pton(socket.AF_INET, ip)
        return True
    except socket.error:
        return False

def get_ip_list(ip_range):
    if not ip_range:
        return []
    vals = map(str.strip, ip_range.strip().split(","))
    range_vals = [i for i in vals if "-" in i]
    ips = [i for i in vals if "-" not in i]
    if False in map(is_valid_ip_address, ips):
        print "Invalid IP"
        return False
    for range_i in range_vals:
        if len(range_i.split("-")) != 2:
            print "invalid Range %s"%(range_i)
            return False

        start = range_i.strip().split("-")[0].strip()
        end = range_i.strip().split("-")[1].strip()
        start = struct.unpack('>I', socket.inet_aton(start))[0]
        end = struct.unpack('>I', socket.inet_aton(end))[0]+1
        range_ips = [socket.inet_ntoa(struct.pack('>I', i)) for i in range(start, end)]
        if False in map(is_valid_ip_address, range_ips):
            print "invalid IP in range"
            return False
        ips += range_ips
    return ips

def reconfigure():
    vsphere_config_values = [] # vmware_host_ip, user, password , datacenter , folder , ip range
    while True:
        host_ip = raw_input("Enter Vsphere Host IP : ").strip()
        if not is_valid_ip_address(host_ip):
            print "not a valid ip"
            continue
        user = raw_input("Enter the username : ").strip()
        password = raw_input("Enter the password : ").strip()
        datacenter_name = raw_input("Enter the datacenter name : ").strip()
        folder_name = raw_input("Enter your folder name : ").strip()
        while True:
            ip_range = raw_input("Enter your reserved static ips or range (comma separated values) : \n eg: 10.10.3.23, 10.20.30.40 - 10.20.30.50 ,10.10.2.23, 10.10.2.26 \n")
            ip_list = get_ip_list(ip_range)
            if ip_list==False:continue
            if ip_list:
                print ip_list 
                consent = raw_input("Is the above ip list acceptable ? (y/n) ")
                if consent.lower() in ['yes','y']:
                    break
            break
         
        vsphere_dict = {"host_ip":host_ip, "user":user, "password":password, "datacenter_name":datacenter_name, 
                "ip_list":ip_list, "folder_name":folder_name if folder_name else ""}
        vsphere_config_values.append(vsphere_dict)
        more_values = raw_input("Do you have more configurations (y/n) ? ")
        if more_values.lower() not in ['yes','y']:
            break
    with open(FILE_PATH, "w") as f:
        f.write(simplejson.dumps(vsphere_config_values, indent=4, sort_keys=True))
    
    display_config()


def display_config():
    with open(FILE_PATH, "r") as f:
        for line in f:
            print line,
        print '\n'

def load_config():
    with open(FILE_PATH, "r") as f:
        config_dict = simplejson.load(f)
    print config_dict

def connect_to_host_and_get_values(host_ip,user,password,datacenter,folder=None,ip_list=[]):
    # return list of vms
    try:
        si= SmartConnectNoSSL(host=host_ip, user=user, pwd=password)#, sslContext=s)
        atexit.register(Disconnect,si)
    except:
        print("Unable to connect to %s" % vmware_host)
        return []

    for dc in si.content.rootFolder.childEntity:
        if dc.name == datacenter:
            datacenter_obj = dc
    
        

def get_all_vm_values():
    pass

def display_all_vm_values():
    pass


parser = argparse.ArgumentParser()
parser.add_argument('--reconfigure', help="Configure new vsphere ips and folder", action='store_true')
parser.add_argument('--display_config', help="Display the vsphere ips and folder configuration", action='store_true')
parser.add_argument('-dip','--delete_ip', help="IP of the vm to be deleted")
parser.add_argument('-dn','--delete_name', help="Name of the vm to be deleted")
parser.add_argument('-pfip','--poweroff_ip', help="IP of the vm to be powered off")
parser.add_argument('-pon','--poweron_all', help="Power On all the vm in the configured folder", action='store_true')
parser.add_argument('-poname','--poweron_name', help="Power On the vm with name in the configured folder")
parser.add_argument('-r','--rename', help="rename the vm with IP to a new name", nargs=2, metavar=('IP','new_name'))
args = parser.parse_args()

if not os.path.isfile(FILE_PATH) or args.reconfigure:
    reconfigure()

if not len(sys.argv) > 1:
    get_all_vm_values()

if args.display_config:
    display_config()










print "Config File Path '%s'"%(FILE_PATH)


        


