#!/usr/bin/env python
try:
    import pyVim,sys
except ImportError:
    print ("do -->> pip install --upgrade pyvmomi")
    sys.exit(1)
from pyVim.connect import SmartConnect,Disconnect,SmartConnectNoSSL
from pyVmomi import vim
from socket import inet_aton, inet_ntoa
import random,time,atexit
from concurrent.futures import ThreadPoolExecutor
import tarfile
#import xmltodict
import subprocess
import shlex
import argparse

def connect(vcenter_ip=None, user=None, pwd=None ,exit_on_error=True):
    if not vcenter_ip:
        vcenter_ip = "blr-01-vc06.oc.vmware.com"
    if not user:
        user = "aviuser1"
    if not pwd:
        pwd = "AviUser1234!."
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

if len(sys.argv)==1 or (len(sys.argv)==2 and sys.argv[1]=='with_host_datastore'):
    with_host_datastore = True if (len(sys.argv)==2 and sys.argv[1]=='with_host_datastore') else False
    all_reserved_ips = ["10.102.65.175", "10.102.65.176", "10.102.65.177", "10.102.65.178", "10.102.65.179", "10.102.65.180", "10.102.65.181"]

    folder_name = "harshjain"
    datacenter_name = "blr-01-vc06"
    vmware_host = "blr-01-vc06.oc.vmware.com"
   
    si = connect()

    for dc in si.content.rootFolder.childEntity:
        if dc.name == datacenter_name:
            datacenter = dc

    #print (datacenter,datacenter.name)
    vms = datacenter.vmFolder.childEntity
    ip_name_state = {}
    ip_host_datastore = {}
    templates = []
    for vm in vms:
        if vm.name == folder_name:
            for virtual_m in vm.childEntity:
                if vim.Folder == type(virtual_m):
                    continue
                if virtual_m.config and not virtual_m.config.template:
                    if virtual_m.runtime.powerState == 'poweredOff':
                        ip_r = "xx NO_IP " + str(random.randint(1000,9999))
                        ip_name_state[ip_r]=(str(virtual_m.name),"POWER OFF")
                        ip_host_datastore[ip_r] = (str(virtual_m.runtime.host.name),str(virtual_m.datastore[0].name))
                    else:
                        if len(virtual_m.guest.net)>1:
                            for ip_net in virtual_m.guest.net:
                                for ip_addr in ip_net.ipAddress:
                                    try:
                                        inet_aton(ip_addr)
                                        if not ip_addr:
                                            ip_addr = "xx NO_IP " + str(random.randint(1000,9999))
                                        ip_name_state[ip_addr]=(str(virtual_m.name),"Power On")
                                        if "blr" in ip_net.network:
                                            ip_host_datastore[ip_addr] = (str(virtual_m.runtime.host.name),str(virtual_m.datastore[0].name),"blr"+str(ip_net.network).split("blr")[1])
                                        else:
                                            ip_host_datastore[ip_addr] = (str(virtual_m.runtime.host.name),str(virtual_m.datastore[0].name),ip_net.network)

                                        
                                    except:
                                        continue
                        else:
                            if not virtual_m.guest.ipAddress:
                                ip_addr = "xx NO_IP " + str(random.randint(1000,9999))
                            else:
                                ip_addr = virtual_m.guest.ipAddress
                            ip_name_state[ip_addr]=(str(virtual_m.name),"Power On")
                            ip_host_datastore[ip_addr] = (str(virtual_m.runtime.host.name),str(virtual_m.datastore[0].name),"blr"+str(virtual_m.guest.net[0].network).split("blr")[1])
                else:
                    templates.append(virtual_m.name)
            break

    no_ips = []
    for key,items in ip_name_state.iteritems():
        if 'NO_IP' not in key:
            continue
        else:
            no_ips.append(key)
    ips = all_reserved_ips
    lot = map(inet_aton, ips)
    lot.sort()
    iplist1 = map(inet_ntoa, lot)
    
    def search_by_ip(ip):
        search = si.RetrieveContent().searchIndex
        #import ipdb;ipdb.set_trace()
        vms = list(set(search.FindAllByIp(ip=ip,vmSearch=True)))
        line = False
        for vm in vms:
            line = " " + vm.name.ljust(25,'-') + "Power On".ljust(12) + ip
            if len(vms)>1:line = line + '\n'
        return line
    print ("\n\n")
    line_header = " " + "**VM NAME**".ljust(25,' ') + "*STATE*".ljust(12) + "   **IP**".ljust(15)
    if with_host_datastore:
        line_header += " " + " **HOST**".ljust(15) + "**DATASTORE**".ljust(12)

    print (line_header)
    for ip in iplist1:
        if ip_name_state.get(ip,False):
            line = " " + ip_name_state[ip][0].ljust(25,'-') + ip_name_state[ip][1].ljust(12) + str(ip).ljust(15)
            if with_host_datastore:
                line += " "  + ip_host_datastore[ip][0].ljust(15) + ip_host_datastore[ip][1].ljust(12)
            ip_name_state.pop(ip)
        else:
            line = search_by_ip(ip)
            if not line:
                line = " " + "----Free IP ----".ljust(25,'-') + "---------".ljust(12) + str(ip).ljust(15) 
        print (line)
    
    for ip in no_ips:
        line = " " + ip_name_state[ip][0].ljust(25) + ip_name_state[ip][1].ljust(12) + "".ljust(15,' ')
        if with_host_datastore:
            line += " "  + ip_host_datastore[ip][0].ljust(15) + ip_host_datastore[ip][1].ljust(12)

        ip_name_state.pop(ip)
        print (line)

    for name in templates:
        line = " " + name.ljust(25) + "=Template=".ljust(12)
        print (line)
    
    print ("\n\n")
    for key in ip_name_state:
        line = " " + ip_name_state[key][0].ljust(25,'-') + ip_name_state[key][1].ljust(12) + key.ljust(16)
        line += " "+ ip_host_datastore[key][2]
        print (line)

    print ("\n")
    #for nic in my_vm.guest.net:
    #    addresses = nic.ipConfig.ipAddress
    #    print(macAddress)
    #    for adr in addresses:
    #        print(adr.ipAddress)
    #        print(adr.prefixLength)

    print ("\n")
if 'help' in sys.argv:
    print ("options --> delete 'ip'")
    print ("options --> delete_name 'name'")
    print ("options --> poweroff 'ip'")
    print ("options --> rename 'ip' 'newname'")
    print ("options --> poweron")
    print ("options --> poweron 'name'")
    print ("options --> generate_controller_from_ova")
    print ("options --> with_host_datastore")


if len(sys.argv)==3 and sys.argv[1] in ('delete','poweroff'):

    if sys.argv[2]:
        ip=sys.argv[2]
        si = connect()
        search = si.RetrieveContent().searchIndex
        vms = list(set(search.FindAllByIp(ip=ip,vmSearch=True)))
        if vms:
            for vm in vms:
                action_confirm = raw_input("Are you sure you want to %s '%s' with ip = %s ?[Y/N] \n"%(sys.argv[1],vm.name,ip))
                if action_confirm.lower() == "n":continue
                if vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOn:
                    print "powering off ",vm.name," ",ip
                    task = vm.PowerOff()
                    while task.info.state not in [vim.TaskInfo.State.success,vim.TaskInfo.State.error]:
                        time.sleep(1)
                    print "power is off.",task.info.state
                
                if vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOff and sys.argv[1]=='delete':
                    print "deleteing ",vm.name," ",ip
                    task = vm.Destroy()
                    while task.info.state not in [vim.TaskInfo.State.success,vim.TaskInfo.State.error]:
                        time.sleep(1)
                    print "vm is deleted.",task.info.state

if len(sys.argv)==3 and sys.argv[1] == 'delete_name':

    si = connect()
    vm_name = sys.argv[2]
    folder_name = "harshjain"
    datacenter_name = "blr-01-vc06"
    for dc in si.content.rootFolder.childEntity:
        if dc.name == datacenter_name:
            datacenter = dc
    #print (datacenter,datacenter.name)
    vmfolders = datacenter.vmFolder.childEntity
    ip_name_state = {}
    templates = []
    for folder in vmfolders:
        if folder.name == folder_name:
            for virtual_m in folder.childEntity:
                if virtual_m.name != vm_name:
                    continue
                action_confirm = raw_input("Are you sure you want to delete '%s'  ?[Y/N] \n"%(vm_name))
                if action_confirm.lower() == "n":continue
                if virtual_m.runtime.powerState == vim.VirtualMachinePowerState.poweredOff:
                    print "deleteing ",virtual_m.name
                    task = virtual_m.Destroy()
                    while task.info.state not in [vim.TaskInfo.State.success,vim.TaskInfo.State.error]:
                        time.sleep(1)
                    print "vm is deleted.",task.info.state
                else:
                    print "delete the vm using ip"


if len(sys.argv)==4 and sys.argv[1]=='rename':
    ip = sys.argv[2]
    newname = sys.argv[3]
    si = connect()
    search = si.RetrieveContent().searchIndex
    vms = list(set(search.FindAllByIp(ip=ip,vmSearch=True)))

    for vm in vms:
        rename_confirm = raw_input("Are you sure you want to rename '%s', (%s) with '%s'  ?[Y/N] \n"%(vm.name,ip,newname))
        if rename_confirm.lower() == "n":continue
        print "renaming  ",vm.name," ",ip," to ",newname
        task = vm.Rename(newname)
        while task.info.state not in [vim.TaskInfo.State.success,vim.TaskInfo.State.error]:
            time.sleep(1)
        print "renaming done.",task.info.state
       
def power_on_vm(virtual_machine_obj):
    vm = virtual_machine_obj
    task = vm.PowerOn()
    while task.info.state not in [vim.TaskInfo.State.success,vim.TaskInfo.State.error]:
        time.sleep(1)
    print "power on task for vm %s = %s"%(vm.name,task.info.state)


if len(sys.argv) in (2,3) and sys.argv[1]=='poweron':
    if len(sys.argv) == 3:
        vm_name = sys.argv[2]
    else:
        vm_name = ''
    all_reserved_ips = [("10.140.16."+str(num)) for num in range(171,190)]
    folder_name = "harshjain"
    datacenter_name = "blr-01-vc06"
    si = connect()
    print "powering on vm in folder %s , datacenter %s "%(folder_name,datacenter_name)
    
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
                            print "vm %s is already ON"%(virtual_m.name)

##################################################################################
##################################################################################
##################################################################################

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

def pretty_print(vals,ljust_vals=[],filler=" "):
    line = " "
    for val,ljust_val in zip(vals,ljust_vals):
        line += str(val).ljust(ljust_val,filler)
    print line

def get_datastores_from_host(cluster_obj,host_ip):

    datastore_obj_list = []
    for host in cluster_obj.host:
        if host.name == host_ip:
            host_obj = host

            for datastore in host_obj.datastore:
                datastore_obj_list.append(datastore)
            break
    return datastore_obj_list

def assist_in_datastore_value(cluster_obj,host_ip):
    print "\nlist of available datastore in host:%s\n"%(host_ip)
    datastore_list = []
    pretty_print(['Index ','Datastore '],ljust_vals=[7,30]) # printing header
    for index,datastore in enumerate(get_datastores_from_host(cluster_obj,host_ip)):
        val = [index,datastore.name]
        pretty_print(val,ljust_vals=[7,30])
        datastore_list.append(val)
    print ""
    if datastore_list:
        datastore_index = raw_input("Enter the index value of the datastore :")
        return datastore_list[int(datastore_index)][1]
    else:
        return raw_input("Enter the name of the datastore :")

def sample_host_obj():
    si = connect()
    cluster_obj = get_cluster_obj(si,"Bangalore","Netgear")
    return cluster_obj.host[0]

def sample_datastore_obj():
    return sample_host_obj().datastore[0] 

def get_hosts_from_cluster(cluster_obj):
    host_obj_list = []
    for host in cluster_obj.host:
        host_obj_list.append(host)
    return host_obj_list

def get_host_info(host):
    memory_capacity_in_MB = convert_units(int(host.hardware.memorySize), base_unit='byte', return_unit='MB')
    memory_usage_in_MB = int(host.summary.quickStats.overallMemoryUsage)
    free_memory_in_MB = memory_capacity_in_MB - memory_usage_in_MB    
    return free_memory_in_MB

def get_datastore_info(datastore):
    free_space_in_MB = datastore.summary.freeSpace/float(1<<20)
    return free_space_in_MB

def assist_in_host_value(cluster_obj):
    print "\nList of available hosts in cluster:%s\n"%(cluster_obj.name)
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
    print ""
    if host_list:
        host_index = raw_input("Enter the index value of the host :")
        return host_list[int(host_index)][1]
    else:
        return raw_input("Enter the name of the host :")

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
        print "*** No compatible host, datastore options available. The ova may not get deployed succesfully on the incompatible options ***"
    else:
        final_list = compatible_list

    for rec in final_list:
        pretty_print(rec, ljust_vals=ljust_vals)
    #for rec in incompatible_list:
    #    pretty_print(rec, ljust_vals=ljust_vals)
    print ""
    index_input = int(raw_input("Enter the index value of the host datastore combination to use :"))
    host_ip , datastore = final_list[index_input][1], final_list[index_input][3]
    return host_ip,datastore


def filter_host_and_datastore_based_on_specs(cluster_obj, ova_memory_spec_in_MB=False, ova_disk_spec_in_MB=False, display_all=False):
    if not ova_memory_spec_in_MB: ova_memory_spec_in_MB = 0
    if not ova_disk_spec_in_MB: ova_disk_spec_in_MB = 0
    print "\nMemory Specs from OVA",convert_units(ova_memory_spec_in_MB,base_unit='MB',return_unit='GB'),"GB"
    print "Disk Specs from OVA  ",convert_units(ova_disk_spec_in_MB,base_unit='MB',return_unit='GB'),"GB"
    print "Swap Space Needed    ",convert_units(ova_memory_spec_in_MB/float(2.0),base_unit='MB',return_unit='GB'),"GB"
    print ""
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
    
    '''
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
    '''
    
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

def get_folder_obj(datacenter_obj,folder_name):
    
    for folder in datacenter_obj.vmFolder.childEntity:
        if vim.Folder._wsdlName == folder._wsdlName and folder.name == folder_name:
            return folder
    print "Folder: %s does not exist"%(folder_name)
    return False

def check_if_ip_is_free(si,datacenter_obj,ip):
    vm =  si.content.searchIndex.FindByIp(ip=ip,datacenter=datacenter_obj,vmSearch=True)
    if vm:
        print "Ip = %s is already being used by %s"%(ip,vm.name)
        return False
    else:
        return True

def check_if_vm_name_exists_in_folder(folder_obj,vm_name):
    for vm in folder_obj.childEntity:
        if vim.VirtualMachine._wsdlName == vm._wsdlName and vm.name == vm_name:
            print "Name already exists"
            return True
    return False

def generate_controller_from_ova():
    vm_type = "controller"
    vcenter_ip = raw_input("Vcenter IP ? [Default: blr-01-vc06.oc.vmware.com] :") or 'blr-01-vc06.oc.vmware.com'
    si = connect()
    datacenter = raw_input("Datacenter Name ? [Default: blr-01-vc06] :") or 'blr-01-vc06'
    datacenter_obj = get_datacenter_obj(si,datacenter)
    cluster_name = raw_input("Cluster ? [Default: wdc-02-vc20c01] :") or 'wdc-02-vc20c01'
    cluster_obj = get_cluster_obj(datacenter_obj,cluster_name)
    source_ova_path = raw_input("Source Ova Path (local/http/ftp) ? :")
    if not source_ova_path:sys.exit(1)
    ova_memory_spec_in_MB , ova_disk_spec_in_MB = get_memory_and_disk_spec_from_ova(source_ova_path)
    filter_options = raw_input("type 'Y' if you want to see host,datastore options based on ova specs ; 'N' for all options; [Y/N] :")
    if filter_options.lower() == 'y' and si:
        host_ip, datastore = filter_host_and_datastore_based_on_specs(cluster_obj, ova_memory_spec_in_MB, ova_disk_spec_in_MB)
    else:
        host_ip, datastore = filter_host_and_datastore_based_on_specs(cluster_obj, ova_memory_spec_in_MB, ova_disk_spec_in_MB, display_all=True)
    management_network = raw_input("Managament Network ? [Default: vxw-dvs-34-virtualwire-3-sid-2200002-wdc-02-vc20-avi-mgmt] :") or "vxw-dvs-34-virtualwire-3-sid-2200002-wdc-02-vc20-avi-mgmt"
    while True:
        mgmt_ip = raw_input("Management IP ? :")
        if mgmt_ip:
            if check_if_ip_is_free(si,datacenter_obj,mgmt_ip):
                break
    mask = raw_input("Network Mask ? [Default: 22] :") or '22'
    gw_ip = raw_input("Gateway IP ? [Default: 10.79.168.1] :") or '10.79.168.1'
    while True:
        folder_name = raw_input("Folder Name ? [Default: harshjain] :") or 'harshjain'
        if folder_name:
            folder_obj = get_folder_obj(datacenter_obj,folder_name)
            if folder_obj:
                break
    while True:
        vm_name = raw_input("VM Name ? :")
        if not check_if_vm_name_exists_in_folder(folder_obj,vm_name):
            break
    power_on = raw_input("Power On VM [Y/N]? [Y] :")
    if power_on.lower() not in ['y','n']:power_on = 'y'
    
    vi = 'vi://aviuser1:AviUser1234!.@' + vcenter_ip
    vi = vi + '/' + datacenter + '/host/'
    vi = vi + cluster_name + '/'
    vi = vi + host_ip + '/'

    prop = ''
    if vm_type == 'controller':
        prop = '--prop:avi.mgmt-ip.CONTROLLER=' + mgmt_ip + \
            ' --prop:avi.default-gw.CONTROLLER=' + gw_ip + ' '
        prop = prop + ' --prop:avi.mgmt-mask.CONTROLLER=' + str(mask) + ' '
        prop += '--name="' + vm_name + '" '
        if power_on.lower() == 'y':
            prop += '--powerOn '
        prop += '"--vmFolder='+folder_name+'" ' 

        cmd = '/usr/bin/ovftool --noSSLVerify "--datastore=' + datastore + \
            '" --net:Management="' + management_network + \
            '" ' + prop + source_ova_path + ' ' + vi + ' --X:logFile /root/ovftool.log' + ' --X:logLevel info'
    print '\n',cmd,'\n'
    verify = raw_input("Verify the command and agree to proceed [Y/N] ? [N] :") or 'N'
    if verify.lower() == 'y':
        print "\nDeploying OVA"
        subprocess.call(cmd, shell=True)


if len(sys.argv)==2 and sys.argv[1] == 'generate_controller_from_ova':
    generate_controller_from_ova()

# https://gist.github.com/goodjob1114/9ededff0de32c1119cf7


'''
parser = argparse.ArgumentParser()
parser.add_argument('--default_profile', help="Set default profile", action='store_true')
parser.add_argument('--list_profiles', help="Display the Vsphere static ips and folder configuration", action='store_true')
parser.add_argument('--create_profile', help="Create vsphere ips and folder configuration", action='store_true')
args = parser.parse_args()
'''

