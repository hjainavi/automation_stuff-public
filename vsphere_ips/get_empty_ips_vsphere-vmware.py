#!/usr/bin/env python3
"""
VMware vSphere IP Management and Controller Automation Script

This script provides functionality for managing VMware vSphere VMs, IPs, and 
Avi Networks controllers including deployment, configuration, and monitoring.
"""

# Standard library imports
import atexit
import datetime
import json
import logging
import multiprocessing
import os
import random
import re
import shlex
import ssl
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from socket import inet_aton, inet_ntoa

# Third-party imports
import ipaddress
import urllib3

# VMware/vSphere imports
try:
    import pyVim
    from pyVim.connect import Disconnect, Connect, SoapStubAdapter
    from pyVmomi import vim
except ImportError:
    print("do -->> pip3 install --upgrade pyvmomi")
    sys.exit(1)

# Network and API imports
import requests
from requests.auth import HTTPBasicAuth

# Utility imports
try:
    from tabulate import tabulate
except ImportError:
    print("do -->> pip3 install tabulate")
    sys.exit(1)

try:
    import click
except ImportError:
    print("do -->> pip3 install click")
    sys.exit(1)

import fabric
import jinja2
from retry import retry
from packaging.version import Version

# Disable SSL warnings
urllib3.disable_warnings()


# =============================================================================
# CONFIGURATION AND CONSTANTS
# =============================================================================

# VM State Constants
POWER_OFF_STATE = 'POWER OFF'
POWER_ON_STATE = 'POWER ON'
TEMPLATE_STATE = 'TEMPLATE'
UNKNOWN_STATE = 'UNKNOWN'
NIL_PRINT_VAL = "------"
FREE_IP = "--Free IP--"

# Default Configuration Values
DEFAULT_SETUP_PASSWORD = "58NFaGDJm(PJH0G"
DEFAULT_PASSWORD = "avi123"
DEFAULT_PASSWORD_32_1_1 = "VMwareAvilb123!"
FT_PASSWORD_32_1_1 = "VMwareAvilb123!"
FT_PASSWORD = "avi123"
SYSADMIN_KEYPATH = "/home/aviuser/.ssh/id_rsa.pub"
DHCP = False
SE_DHCP = False
CTLR_MGMT_NETWORK = ""

# Global State Variables (consider refactoring these to a class)
GLOBAL_LOGIN_HEADERS = {}
GLOBAL_LOGIN_COOKIES = {}
GLOBAL_CURRENT_PASSWORD = {}
GLOBAL_BUILD_NO = {}
SE_IPS_TO_USE_FOR_CURRENT_CTLR = []
CONTROLLER_NAME = ""

# Load Configuration from vals.json
def load_configuration():
    """
    Load and validate configuration from vals.json file.
    
    Returns:
        dict: Parsed configuration data
        
    Raises:
        SystemExit: If configuration cannot be loaded or parsed
    """
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vals.json")
    
    try:
        with open(config_path, "r") as f:
            config_data = json.loads(f.read())
        
        # Validate required configuration keys
        required_keys = ["VCENTER"]
        for key in required_keys:
            if key not in config_data:
                raise ValueError(f"Missing required configuration key: {key}")
        
        return config_data
        
    except Exception as e:
        error_msg = f"Error loading configuration: {e}"
        print(f"ERROR: {error_msg}")
        sys.exit(1)


config = load_configuration()

# vCenter Configuration Selection
VCENTER = config["VCENTER"]
VCENTER_CHOICES = list(VCENTER.keys())
CURRENT_VCENTER = ""


def select_vcenter():
    """
    Select vCenter configuration interactively if multiple options exist.
    
    Raises:
        SystemExit: If vCenter selection fails
    """
    global CURRENT_VCENTER
    
    try:
        if len(VCENTER_CHOICES) == 1:
            CURRENT_VCENTER = VCENTER_CHOICES[0]
            logger.info(f"Auto-selected single vCenter: {CURRENT_VCENTER}")
            return
        
        # Multiple vCenter options available
        vcenter_options = []
        for index, vcenter_name in enumerate(VCENTER_CHOICES):
            vcenter_options.append(f"{index}:{vcenter_name}")
        
        vcenter_str = ", ".join(vcenter_options)
        logger.info(f"Multiple vCenter options available: {vcenter_str}")
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                action_confirm = input(
                    f"Choose the vcenter to operate on [[{vcenter_str}]] [Enter Index] ?: "
                )
                selected_index = int(action_confirm.strip())
                
                if 0 <= selected_index < len(VCENTER_CHOICES):
                    CURRENT_VCENTER = VCENTER_CHOICES[selected_index]
                    logger.info(f"Selected vCenter: {CURRENT_VCENTER}")
                    return
                else:
                    print(
                        f"Invalid index. Please enter a number between 0 and {len(VCENTER_CHOICES)-1}"
                    )
                    
            except Exception as e:
                if "KeyboardInterrupt" in str(type(e)):
                    print("\nOperation cancelled by user")
                    sys.exit(1)
                print("Invalid input. Please enter a numeric index.")
            
            if attempt == max_retries - 1:
                logger.error(f"Failed to select vCenter after {max_retries} attempts")
                print("Too many invalid attempts. Exiting.")
                sys.exit(1)
                
    except Exception as e:
        logger.error(f"Unexpected error in vCenter selection: {e}")
        print(f"Error selecting vCenter: {e}")
        sys.exit(1)


# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

def setup_logging(log_level=logging.INFO):
    """
    Setup logging configuration for the application.
    
    Args:
        log_level: Logging level (default: INFO)
    """
    # Create logs directory if it doesn't exist
    # Get home directory location
    logs_dir = os.path.join(os.path.expanduser("~"), "vsphereips_logs")
    
    # Ensure logs directory exists at home location
    if not os.path.exists(logs_dir):
        print(f"Creating logs directory at: {logs_dir}")
    os.makedirs(logs_dir, exist_ok=True)
    
    # Configure logging
    log_file = os.path.join(logs_dir, "vsphere_automation.log")
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    
    # Setup file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)
    
    # Setup console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.WARNING)  # Only warnings and errors to console
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    return logging.getLogger(__name__)


# Initialize logging
logger = setup_logging()

# Check if we're in shell completion mode - skip heavy initialization
_COMPLETION_MODE = any(
    os.environ.get(var) 
    for var in ['_VSPHERE_COMPLETE', 'COMP_WORDS', 'COMP_CWORD', '_GET_EMPTY_IPS_COMPLETE']
)

# Initialize vCenter selection (skip in completion mode)
if not _COMPLETION_MODE:
    select_vcenter()
else:
    # In completion mode, use first vCenter as default
    CURRENT_VCENTER = VCENTER_CHOICES[0] if VCENTER_CHOICES else ""

# Current vCenter Configuration
current_config = VCENTER.get(CURRENT_VCENTER, {}) if CURRENT_VCENTER else {}
ALL_MGMT_RESERVED_IPS = current_config.get("ALL_MGMT_RESERVED_IPS", [])
ALL_RESERVED_IPS = current_config.get("ALL_RESERVED_IPS", [])
SE_IPS = current_config.get("SE_IPS", [])
VCENTER_IP = current_config.get("VCENTER_IP", "")
VCENTER_USERS = current_config.get("VCENTER_USERS", [""])
VCENTER_USER = VCENTER_USERS[0] if VCENTER_USERS else ""
VCENTER_PASSWORD = current_config.get("VCENTER_PASSWORD", "")
VCENTER_DATACENTER_NAME = current_config.get("VCENTER_DATACENTER_NAME", "")
VCENTER_CLUSTER_NAME = current_config.get("VCENTER_CLUSTER_NAME", "")
VCENTER_DATASTORE_NAME = current_config.get("VCENTER_DATASTORE_NAME", "")
VCENTER_FOLDER_NAME = current_config.get("VCENTER_FOLDER_NAME", "")
DEV_VM_IP = current_config.get("DEV_VM_IP", "")
VCENTER_MANAGEMENT_MAP = current_config.get("VCENTER_MANAGEMENT_MAP", {})
VCENTER_DNS_SERVERS = current_config.get("VCENTER_DNS_SERVERS", [])
VCENTER_NTP = current_config.get("VCENTER_NTP", "")
VCENTER_PORT_GROUP = current_config.get("VCENTER_PORT_GROUP", "")
VCENTER_SERVER_IP = current_config.get("VCENTER_SERVER_IP", "")
VCENTER_SERVER_SUBNET = current_config.get("VCENTER_SERVER_SUBNET", "")


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

# Track execution time
START_TIME = time.time()


# =============================================================================
# VSPHERE CONNECTION AND SESSION MANAGEMENT
# =============================================================================

def connect(vcenter_ip=VCENTER_IP, users=VCENTER_USERS, pwd=VCENTER_PASSWORD):
    """
    Connect to vCenter server with session management.
    
    Args:
        vcenter_ip (str): vCenter IP address
        users (list): List of usernames to try for authentication
        pwd (str): Password for authentication
        
    Returns:
        vim.ServiceInstance: Connected vCenter service instance
        
    Raises:
        SystemExit: If connection fails for all users
    """
    logger.info(f"Attempting to connect to vCenter: {vcenter_ip}")
    
    try:
        context = ssl._create_unverified_context()
        filename = ".vcenter_session_info"
        session_file = os.path.join(os.path.expanduser("~"), filename)
        
        # Load existing session data
        session_data = None
        if os.path.exists(session_file):
            try:
                with open(session_file, "r") as f:
                    session_data = f.read().strip()
                    session_data = json.loads(session_data) if session_data else None
                logger.debug("Loaded existing session data")
            except Exception as e:
                logger.warning(f"Failed to load session file: {e}")
                session_data = None

        def new_session(data):
            """Create a new vCenter session."""
            logger.info("Creating new vCenter session")
            conn = None
            last_error = None
            
            for user in users:
                try:
                    logger.info(f"Connecting with user: {user}")
                    conn = Connect(
                        host=vcenter_ip, 
                        user=user, 
                        pwd=pwd, 
                        disableSslCertValidation=True
                    )
                    logger.info(f"Successfully connected with user: {user}")
                    break
                except Exception as e:
                    last_error = e
                    logger.warning(f"Connection failed for user {user}: {e}")
                    
            if not conn:
                logger.error(f"Failed to connect to vCenter {vcenter_ip} with any user")
                if last_error:
                    raise ConnectionError(f"Unable to connect to {vcenter_ip}: {last_error}")
                
            
            # Save session data
            try:
                if data is None:
                    data = {}
                data.update({
                    str(vcenter_ip): {
                        'cookie': conn._stub.cookie, 
                        'time': time.strftime("%Y-%m-%d %H:%M:%S"), 
                        'version': conn._stub.version, 
                        'user': user
                    }
                })
                
                with open(session_file, "w") as f:
                    f.write(json.dumps(data))
                logger.debug("Saved session data to file")
            except Exception as e:
                logger.warning(f"Failed to save session data: {e}")
                
            return conn

        # Try to reuse existing session
        host_session = session_data.get(str(vcenter_ip)) if session_data else None
        if host_session:
            try:
                logger.debug("Attempting to reuse existing session")
                cookie = host_session['cookie']
                version = host_session['version']
                user = host_session['user']
                
                soapStub = SoapStubAdapter(host=str(vcenter_ip), sslContext=context, version=version)
                conn = vim.ServiceInstance("ServiceInstance", soapStub)
                conn._stub.cookie = cookie
                
                if conn.content.sessionManager.currentSession:
                    logger.info("Successfully reused existing session")
                    return conn
                else:
                    logger.info("Existing session invalid, creating new session")
                    return new_session(session_data)
                    
            except Exception as e:
                logger.warning(f"Failed to reuse session: {e}")
                return new_session(session_data)
        else:
            return new_session(session_data)
            
    except Exception as e:
        logger.error(f"Error during vCenter connection: {e}")
        raise


# =============================================================================
# VM INFORMATION AND MANAGEMENT FUNCTIONS
# =============================================================================

def fill_vms_table(vms_table, virtual_m):
    """
    Fill VM table with VM information including state and IP addresses.
    
    Args:
        vms_table (dict): Dictionary to store VM information
        virtual_m: VMware virtual machine object
    """
    folder_name = virtual_m.parent.name
    
    # Handle VMs without configuration
    if not virtual_m.config:
        vms_table[(folder_name, virtual_m.name)] = {
            'state': UNKNOWN_STATE, 
            'ip_network': [[NIL_PRINT_VAL, NIL_PRINT_VAL]]
        }
        return

    # Handle template VMs
    if virtual_m.config.template:
        vms_table[(folder_name, virtual_m.name)] = {
            'state': TEMPLATE_STATE, 
            'ip_network': [[NIL_PRINT_VAL, NIL_PRINT_VAL]]
        }
        return

    # Handle powered off VMs
    if virtual_m.runtime.powerState == 'poweredOff':
        vms_table[(folder_name, virtual_m.name)] = {
            'state': POWER_OFF_STATE, 
            'ip_network': [[NIL_PRINT_VAL, NIL_PRINT_VAL]]
        }
    else:
        # Handle powered on VMs
        vms_table[(folder_name, virtual_m.name)] = {
            'state': POWER_ON_STATE, 
            'ip_network': []
        }
        
        # Extract IP addresses (IPv4 only)
        if virtual_m.guest and virtual_m.guest.net:
            for ip_net in virtual_m.guest.net:
                if not ip_net.ipAddress:
                    continue
                for ip_addr in ip_net.ipAddress:
                    # Filter out IPv6 and empty addresses
                    if (ip_addr and ":" not in ip_addr) or ("v6" in str(ip_net.network) and "fe80" not in ip_addr):
                        vms_table[(folder_name, virtual_m.name)]['ip_network'].append(
                            [ip_addr, ip_net.network]
                        )
        
        # Set placeholder if no IP addresses found
        if not vms_table[(folder_name, virtual_m.name)]['ip_network']:
            vms_table[(folder_name, virtual_m.name)]['ip_network'].append(
                [NIL_PRINT_VAL, NIL_PRINT_VAL]
            )

def power_on_vm(virtual_machine_obj):
    """
    Power on a virtual machine and wait for completion.
    
    Args:
        virtual_machine_obj: VMware virtual machine object to power on
        
    Raises:
        Exception: If power on operation fails
    """
    try:
        logger.info(f"Powering on VM: {virtual_machine_obj.name}")
        task = virtual_machine_obj.PowerOn()
        
        # Wait for task completion with timeout
        timeout_seconds = 300  # 5 minutes
        start_time = time.time()
        
        while task.info.state not in [vim.TaskInfo.State.success, vim.TaskInfo.State.error]:
            if time.time() - start_time > timeout_seconds:
                logger.error(f"Timeout waiting for VM {virtual_machine_obj.name} to power on")
                raise TimeoutError(f"Timeout powering on VM {virtual_machine_obj.name}")
        time.sleep(1)
        
        if task.info.state == vim.TaskInfo.State.success:
            logger.info(f"Successfully powered on VM: {virtual_machine_obj.name}")
            print(f"Power on task for VM {virtual_machine_obj.name} = SUCCESS")
        else:
            error_msg = f"Failed to power on VM {virtual_machine_obj.name}: {task.info.error}"
            logger.error(error_msg)
            print(f"Power on task for VM {virtual_machine_obj.name} = ERROR")
            raise Exception(error_msg)
            
    except Exception as e:
        logger.error(f"Error powering on VM {virtual_machine_obj.name}: {e}")
        raise





def get_vms_ips_network(with_se_ips=False, free_ips=False, with_mgmt_reserved_ips=False):
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
    # vms_table[(folder,name)] = {state: template/on/off, ip_network: [[ip,network]]}
    vms_table = {}

    for dc in si.content.rootFolder.childEntity:
        if dc.name == datacenter_name:
            datacenter = dc
    if datacenter is None:
        print(f"datacenter {datacenter_name} not found")
        sys.exit(1)
    search_text = f"{datacenter_name}/vm/{folder_name}"
    search_folder = si.RetrieveContent().searchIndex.FindByInventoryPath(search_text)
    if not search_folder:
        print(f"folder {folder_name} not found")
        print(f"search text = {search_text}")
        sys.exit(1)
    for virtual_m in search_folder.childEntity:
        if vim.Folder == type(virtual_m):
            continue
        #import ipdb;ipdb.set_trace()
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
    gap_index = len(final_print_vals)
    final_print_vals.append(("","","",""))

    for folder_name,value in vms_table.items():
        if not value['ip_network']:
            final_print_vals.append((folder_name[1], value['state'], NIL_PRINT_VAL, NIL_PRINT_VAL))
            continue
        for ip_network_val in value['ip_network']:
            if ip_network_val[0] not in all_reserved_ips:
                if ("se" in folder_name[1] or "ctlr" in folder_name[1]) and "10.80" in ip_network_val[0]:
                    final_print_vals.insert(gap_index, (folder_name[1], value['state'], ip_network_val[0], ip_network_val[1]))
                else:
                    final_print_vals.append((folder_name[1], value['state'], ip_network_val[0], ip_network_val[1]))
    final_print_vals = remove_se_non_reserved_ips(final_print_vals)
    if not free_ips:
        final_print_vals = remove_free_ips(final_print_vals)
    return final_print_vals

def remove_free_ips(final_print_vals):
    new_final_print_vals = []
    for val in final_print_vals:
        val_name = val[0]
        if FREE_IP != val_name:
            new_final_print_vals.append(val)
    return new_final_print_vals

def remove_se_non_reserved_ips(final_print_vals):
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


def poweroff_and_delete_vm(ips, delete=False, si=None):
    cmd = 'delete' if delete else 'poweroff'
    if not si:
        si = connect()
    search = si.RetrieveContent().searchIndex
    vms_to_operate_on = []
    for ip in ips:
        vms = list(set(search.FindAllByIp(ip=ip,vmSearch=True)))
        if vms:
            for vm in vms:
                action_confirm = input(f"Are you sure you want to {cmd} '{vm.name}' with ip = {ip} ?[Y/N] \n")
                if action_confirm.lower() == "n":continue
                if DEV_VM_IP in ip:
                    dev_vm_confirm = ""
                    while dev_vm_confirm not in ['confirm', 'deny']:
                        dev_vm_confirm = input(f"Are you sure you want to delete dev vm '{ip}'? [confirm/deny] \n").lower()
                    if dev_vm_confirm == 'deny':
                        continue
                vms_to_operate_on.append((vm,ip))
    def process_vm_operation(vm_ip_tuple):
        vm, ip = vm_ip_tuple
        if vm.runtime.powerState == 'poweredOn':
            print ("powering off ",vm.name,ip)
            task = vm.PowerOff()
            while task.info.state not in ['success','error']:
                time.sleep(1)
            print ("power is off.",vm.name,ip,task.info.state)
        
        if vm.runtime.powerState == 'poweredOff' and cmd=='delete':
            print ("deleteing ",vm.name,ip)
            task = vm.Destroy()
            while task.info.state not in ['success','error']:
                time.sleep(1)
            print ("vm is deleted.",vm.name,ip,task.info.state)

    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(process_vm_operation, vms_to_operate_on)
# =============================================================================
# MAIN EXECUTION LOGIC
# =============================================================================

def handle_delete_poweroff_commands(ip_list, delete=True):
    """Handle delete and poweroff commands with IP arguments.
    
    Args:
        ip_list: List of IP addresses to operate on
        delete: If True, delete VMs; if False, only power off
    """
    try:
        if not ip_list:
            raise ValueError("No IP addresses provided")
        operation = 'delete' if delete else 'poweroff'
        logger.info(f"Executing {operation} operation on IPs: {ip_list}")
        
        poweroff_and_delete_vm(list(ip_list), delete)
                
        logger.info(f"{operation.capitalize()} operation completed successfully")
    except Exception as e:
        logger.error(f"Error in delete/poweroff command: {e}")
        raise


def handle_delete_by_name(vm_names):
    """Handle delete by VM name command.
    
    Args:
        vm_names: List of VM names to delete
    """
    si = connect()
    vm_names = [item.strip() for item in vm_names]
    print(vm_names)
    datacenter_name = VCENTER_DATACENTER_NAME
    for dc in si.content.rootFolder.childEntity:
        if dc.name == datacenter_name:
            datacenter = dc
    folder_name = VCENTER_FOLDER_NAME
    search_path = f"/{datacenter.name}/vm/{folder_name}"
    folder_obj = si.content.searchIndex.FindByInventoryPath(search_path)
    if not folder_obj:
        print(f"Folder not found at path: {search_path}")
        sys.exit(1)
    for virtual_m in folder_obj.childEntity:
        for vm_name in vm_names:
            if virtual_m.name != vm_name:
                continue
            action_confirm = input(f"Are you sure you want to delete '{vm_name}'? [Y/N] \n")
            if action_confirm.lower() == "n":
                continue
            if "harsh" in vm_name and "dev" in vm_name:
                dev_vm_confirm = ""
                while dev_vm_confirm not in ['confirm', 'deny']:
                    dev_vm_confirm = input(f"Are you sure you want to delete dev vm '{vm_name}'? [confirm/deny] \n").lower()
                if dev_vm_confirm == 'deny':
                    continue
            if virtual_m.runtime.powerState == vim.VirtualMachinePowerState.poweredOff:
                print(f"Deleting {virtual_m.name}")
                task = virtual_m.Destroy()
                while task.info.state not in [vim.TaskInfo.State.success, vim.TaskInfo.State.error]:
                    time.sleep(1)
                print(f"VM is deleted. {task.info.state}")
            elif len(virtual_m.guest.net) == 0:
                if virtual_m.runtime.powerState == vim.VirtualMachinePowerState.poweredOn:
                    print(f"Powering off {virtual_m.name}")
                    task = virtual_m.PowerOff()
                    while task.info.state not in [vim.TaskInfo.State.success, vim.TaskInfo.State.error]:
                        time.sleep(1)
                    print(f"Power is off. {task.info.state}")
                print(f"Deleting {virtual_m.name}")
                task = virtual_m.Destroy()
                while task.info.state not in [vim.TaskInfo.State.success, vim.TaskInfo.State.error]:
                    time.sleep(1)
                print(f"VM is deleted. {task.info.state}")
            else:
                print("Delete the VM using IP")


# Old command handlers removed - now handled by main() function

# Command handling moved to main() function


# =============================================================================
# AVI CONTROLLER API AND AUTHENTICATION FUNCTIONS
# =============================================================================

def get_headers(tenant='admin'):
    """
    Get standard HTTP headers for API requests.
    
    Args:
        tenant (str): Tenant name (default: 'admin')
        
    Returns:
        dict: HTTP headers for API requests
    """
    headers = {
        "Content-Type": "application/json",
    }
    # Note: X-Avi-Version header is set separately when version is known
    return headers


def wait_until_cluster_ready(c_ip, timeout=1800):
    """
    Wait until controller cluster is ready.
    
    Args:
        c_ip (str): Controller IP address
        timeout (int): Timeout in seconds (default: 1800)
        
    Returns:
        bool: True if cluster is ready
        
    Raises:
        TimeoutError: If cluster is not ready within timeout
        ConnectionError: If unable to connect to controller
    """
    uri = f'https://{c_ip}/api/cluster/runtime'
    sleep_time = 10
    iters = int(timeout / sleep_time)
    
    logger.info(f"Waiting for cluster ready on controller {c_ip} (timeout: {timeout}s)")
    
    for i in range(iters):
        try:
            rsp = requests.get(uri, verify=False, timeout=30)
            logger.debug(f"Controller {c_ip} response code: {rsp.status_code}")
            
            if rsp.status_code == 200:
                cluster_state = rsp.json().get('cluster_state', {})
                state = cluster_state.get('state', 'UNKNOWN')
                
                if state in ['CLUSTER_UP_HA_ACTIVE', 'CLUSTER_UP_NO_HA']:
                    logger.info(f"Cluster state ACTIVE on controller {c_ip}")
                    print(f'Found cluster state ACTIVE on {c_ip}')
                    return True
                else:
                    logger.debug(f"Cluster state INACTIVE on controller {c_ip}: {state}")
                    print(f'Cluster state INACTIVE on {c_ip}: {state}')
            else:
                logger.warning(f"Non-200 response from controller {c_ip}: {rsp.status_code}")
                
        except Exception as e:
            logger.warning(f"Request failed for {uri}: {e}")
            print(f'Connection attempt {i+1}/{iters} failed for controller {c_ip}')
            
        if i < iters - 1:  # Don't sleep on the last iteration
            time.sleep(sleep_time)
        if i == 50 and CONTROLLER_NAME:
            si = connect()
            virtual_m = find_vm_by_name(si,CONTROLLER_NAME)
            if virtual_m:
                if len(virtual_m.guest.net) == 0:
                    #change network adapter
                    change_network_adapter(virtual_m)

    error_msg = f'Timeout: waited approximately {timeout} sec. and the cluster is still not active. controller {c_ip}'
    logger.error(error_msg)
    raise TimeoutError(error_msg)

def find_vm_by_name(si,vm_name):
    search_path = f"/{VCENTER_DATACENTER_NAME}/vm/{VCENTER_FOLDER_NAME}"
    folder_obj = si.content.searchIndex.FindByInventoryPath(search_path)
    if not folder_obj:
        print(f"Folder not found at path: {search_path}")
        sys.exit(1)
    for virtual_m in folder_obj.childEntity:
        if virtual_m.name == vm_name:
            return virtual_m
    return None

def change_network_adapter(virtual_m, network_identifier=None):
    #power off vm
    task = virtual_m.PowerOff()
    while task.info.state not in [vim.TaskInfo.State.success, vim.TaskInfo.State.error]:
        time.sleep(1)
    print(f"Power is off. {task.info.state}")

    
    # Find the network adapter device
    network_adapter = None
    for device in virtual_m.config.hardware.device:
        if isinstance(device, vim.vm.device.VirtualEthernetCard):
            network_adapter = device
            break
    # Remove the current network adapter first
    if network_adapter:
        remove_device_change = vim.vm.device.VirtualDeviceSpec()
        remove_device_change.operation = vim.vm.device.VirtualDeviceSpec.Operation.remove
        remove_device_change.device = network_adapter
        
        remove_config_spec = vim.vm.ConfigSpec()
        remove_config_spec.deviceChange = [remove_device_change]
        
        # Remove the current adapter
        remove_task = virtual_m.ReconfigVM_Task(remove_config_spec)
        while remove_task.info.state not in [vim.TaskInfo.State.success, vim.TaskInfo.State.error]:
            time.sleep(1)
        
        if remove_task.info.state == vim.TaskInfo.State.success:
            print(f"Successfully removed existing network adapter")
        else:
            print(f"Failed to remove network adapter: {remove_task.info.error}")
            return
    
    # Add a new E1000 network adapter
    new_network_adapter = vim.vm.device.VirtualE1000()
    new_network_adapter.key = -1  # Temporary key for new device
    new_network_adapter.deviceInfo = vim.Description()
    new_network_adapter.deviceInfo.label = "Network adapter 1"
    new_network_adapter.deviceInfo.summary = "E1000 ethernet adapter"
    
    # Configure the network backing (connect to the same network as before)
    backing = vim.vm.device.VirtualEthernetCard.NetworkBackingInfo()
    new_network_name = "ibn5-avi-dev-IntMgmt"  if not network_identifier else network_identifier
    backing.deviceName = new_network_name
    new_network_adapter.backing = backing
    
    # Configure connection settings
    new_network_adapter.connectable = vim.vm.device.VirtualDevice.ConnectInfo()
    new_network_adapter.connectable.startConnected = True
    new_network_adapter.connectable.allowGuestControl = True
    new_network_adapter.connectable.connected = True
    
    # Create device change spec for adding the new adapter
    add_device_change = vim.vm.device.VirtualDeviceSpec()
    add_device_change.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
    add_device_change.device = new_network_adapter
    
    add_config_spec = vim.vm.ConfigSpec()
    add_config_spec.deviceChange = [add_device_change]
    
    # Add the new E1000 adapter
    add_task = virtual_m.ReconfigVM_Task(add_config_spec)
    while add_task.info.state not in [vim.TaskInfo.State.success, vim.TaskInfo.State.error]:
        time.sleep(1)
    
    if add_task.info.state == vim.TaskInfo.State.success:
        print(f"Successfully added new E1000 network adapter to {new_network_name} network")
    else:
        print(f"Failed to add E1000 network adapter to {new_network_name} network: {add_task.info.error}")
        return
    #power on vm
    task = virtual_m.PowerOn()
    while task.info.state not in [vim.TaskInfo.State.success, vim.TaskInfo.State.error]:
        time.sleep(1)
    print(f"Power is on. {task.info.state}")

def change_to_default_password(c_ip, uri_base):
    change_password = ""
    version = GLOBAL_LOGIN_HEADERS[c_ip].get('X-Avi-Version',None)
    if version:
        version = Version(version)
        if version >= Version('32.1.1'):
            change_password = DEFAULT_PASSWORD_32_1_1
            if GLOBAL_CURRENT_PASSWORD[c_ip] == DEFAULT_PASSWORD_32_1_1:
                print("password is already set to VMwareAvilb123!")
                return
            data = {}
            r = requests.get(uri_base+'api/useraccountprofile',verify=False, headers=GLOBAL_LOGIN_HEADERS[c_ip], cookies=GLOBAL_LOGIN_COOKIES[c_ip])
            for val in r.json()['results']:
                if val['name'] == 'Default-User-Account-Profile':
                    data = val
                    break
            data['complexity_constraint']['min_length'] = 8
            data['complexity_constraint']['min_lowercase'] = 1
            data['complexity_constraint']['min_numeric'] = 1
            data['complexity_constraint']['min_special'] = 0
            data['complexity_constraint']['min_uppercase'] = 0
            data['complexity_constraint']['password_history'] = 1
            data['lockout_constraint']['lockout_max_auth_failures'] = 0
            r = requests.put(uri_base+'api/useraccountprofile/%s'%(data['uuid']), data=json.dumps(data) ,verify=False, headers=GLOBAL_LOGIN_HEADERS[c_ip], cookies=GLOBAL_LOGIN_COOKIES[c_ip])
            if r.status_code not in [200,201]:
                raise Exception(r.text)
        else:
            change_password = DEFAULT_PASSWORD
            if GLOBAL_CURRENT_PASSWORD[c_ip] == DEFAULT_PASSWORD:
                print("password is already set to avi123")
                return
    uri_base = 'https://' + c_ip + '/'
    print(f"changing password to {change_password}")
    r = requests.get(uri_base+'api/useraccount',verify=False, headers=GLOBAL_LOGIN_HEADERS[c_ip], cookies=GLOBAL_LOGIN_COOKIES[c_ip])
    data = r.json()
    data.update({'username':'admin','password':change_password ,'old_password':GLOBAL_CURRENT_PASSWORD[c_ip]})
    time.sleep(1) 
    #auth = HTTPBasicAuth('admin', GLOBAL_CURRENT_PASSWORD[c_ip])
    resp = requests.put(uri_base+'api/useraccount', data=json.dumps(data) ,verify=False, headers=GLOBAL_LOGIN_HEADERS[c_ip], cookies=GLOBAL_LOGIN_COOKIES[c_ip])
    if resp.status_code not in [200,201]:
        raise Exception(resp.text)
    print(f"changing password to {change_password} -- done")
    

def change_password_for_ft(c_ip):
    """Change controller password to VMwareAvilb123! for FT testing."""
    login_and_set_global_variables(c_ip)
    # Check version to determine which password to use
    version = GLOBAL_LOGIN_HEADERS[c_ip].get('X-Avi-Version', None)
    if version:
        version = Version(version)
        if version >= Version('32.1.1'):
            target_password = FT_PASSWORD_32_1_1
        else:
            target_password = FT_PASSWORD
    else:
        target_password = FT_PASSWORD  # Default to FT_PASSWORD if version not available
    
    if GLOBAL_CURRENT_PASSWORD[c_ip] == target_password:
        print(f"Password is already set to {target_password}")
        return
    
    uri_base = 'https://' + c_ip + '/'
    
    print(f"Changing password to: {target_password} since version is {version}")
    r = requests.get(uri_base+'api/useraccount', verify=False, headers=GLOBAL_LOGIN_HEADERS[c_ip], cookies=GLOBAL_LOGIN_COOKIES[c_ip])
    data = r.json()
    data.update({'username': 'admin', 'password': target_password, 'old_password': GLOBAL_CURRENT_PASSWORD[c_ip]})
    time.sleep(1)
    resp = requests.put(uri_base+'api/useraccount', data=json.dumps(data), verify=False, headers=GLOBAL_LOGIN_HEADERS[c_ip], cookies=GLOBAL_LOGIN_COOKIES[c_ip])
    if resp.status_code not in [200, 201]:
        raise Exception(resp.text)
    print(f"Changing password to {target_password} -- done for version {version}")
    reset_login(c_ip)

def _try_login_for_controller(c_ip):
    """Try to login to a controller with various passwords. Returns (c_ip, password)."""
    uri_base = 'https://' + c_ip + '/'
    headers = get_headers()
    password_list = ["avi123", "VMwareAvilb123!","admin","avi12345", "avi123$%", "Avi123", "Avi123456789#$%"]
    for password in password_list:
        data = {'username': 'admin', 'password': password}
        try:
            login = requests.post(uri_base + 'login', data=json.dumps(data), headers=headers, verify=False, timeout=30)
            if login.status_code in [200, 201]:
                return (c_ip, password)
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to {c_ip}: {e}")
            continue
    return (c_ip, "not able to login using various passwords")


def get_current_password_for_all_controllers(si):
    vals = get_index_format_ips_excluding_dev_ip(si, free=False)
    controller_ips = list(vals.values())
    
    # Run login attempts for all controllers in parallel
    store_password = {}
    with ThreadPoolExecutor(max_workers=min(10, len(controller_ips))) as executor:
        results = executor.map(_try_login_for_controller, controller_ips)
        for c_ip, password in results:
            store_password[c_ip] = password
    
    # Print the results in a tabulated format
    table_data = []
    for c_ip, password in store_password.items():
        table_data.append([c_ip, password])
    
    headers = ["Controller IP", "Password"]
    print(tabulate(table_data, headers=headers, tablefmt="psql"))

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
    password_list = [password_arg,"avi123","VMwareAvilb123!","Avi123456789#$%","avi12345","avi123$%","admin","Avi123"] if password_arg else ["avi123","VMwareAvilb123!","Avi123456789#$%","avi12345","avi123$%","admin","Avi123"]
    for password in password_list:
        data = {'username':'admin', 'password':password}
        login = requests.post(uri_base+'login', data=json.dumps(data), headers=headers, verify=False)
        if login.status_code in [200, 201]:
            headers['X-CSRFToken'] = login.cookies['csrftoken']
            headers['Referer'] = uri_base
            GLOBAL_LOGIN_HEADERS[c_ip] = headers
            GLOBAL_LOGIN_COOKIES[c_ip] = login.cookies
            GLOBAL_CURRENT_PASSWORD[c_ip] = password
            break
    else:
        print("not able to login using various passwords")
        sys.exit(1)
    
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

    change_to_default_password(c_ip, uri_base)
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
    version = GLOBAL_LOGIN_HEADERS[c_ip].get('X-Avi-Version',None)
    if version:
        version = Version(version)
        if version < Version('32.1.1'):
            print("password strength check is not supported in this version")
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
    data['backup_passphrase']='Avi123456789#$%'
    
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

    change_to_default_password(c_ip, uri_base)
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
    time.sleep(3)
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

def fetch_network_based_on_ip(c_ip):
    for network in VCENTER_MANAGEMENT_MAP:
        subnet_str = VCENTER_MANAGEMENT_MAP[network]["subnet"]
        try:
            # Create an IP address object
            ip_addr = ipaddress.ip_address(c_ip)
            # Create a network object (handles the CIDR notation)
            subnet_net = ipaddress.ip_network(subnet_str)
            # Use the 'in' operator for membership testing
            if ip_addr in subnet_net:
                return VCENTER_MANAGEMENT_MAP[network]["name"]
        except ValueError as e:
            raise
    print(f"ERROR: IP {c_ip} not found in any network")
    sys.exit(1)
        

def setup_cloud_se_wo_put_to_cloud(c_ip,version=""):
    global CTLR_MGMT_NETWORK
    uri_base = 'https://' + c_ip + '/'
    data = {}
    r = requests.get(uri_base+'api/cloud',verify=False, headers=GLOBAL_LOGIN_HEADERS[c_ip], cookies=GLOBAL_LOGIN_COOKIES[c_ip])
    for val in r.json()['results']:
        if val['name'] == 'Default-Cloud':
            data = val
            break
    default_cloud_uuid = data['uuid']
    wait_until_cloud_ready(c_ip, GLOBAL_LOGIN_COOKIES[c_ip], GLOBAL_LOGIN_HEADERS[c_ip], default_cloud_uuid, timeout=850)
    if not CTLR_MGMT_NETWORK:
        CTLR_MGMT_NETWORK = fetch_network_based_on_ip(c_ip)
    management_network = "/api/vimgrnwruntime/?name=%s"%(CTLR_MGMT_NETWORK)
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
        

        

    
# =============================================================================
# VSPHERE UTILITY AND HELPER FUNCTIONS
# =============================================================================

def pretty_print(vals, ljust_vals=None, filler=" "):
    """
    Print values in a formatted table-like structure.
    
    Args:
        vals (list): Values to print
        ljust_vals (list): Left justification widths for each value
        filler (str): Character to use for padding (default: space)
    """
    if ljust_vals is None:
        ljust_vals = []
    
    line = " "
    for val, ljust_val in zip(vals, ljust_vals):
        line += str(val).ljust(ljust_val, filler)
    print(line)


def get_datacenter_obj(si, datacenter_name):
    """
    Get datacenter object by name.
    
    Args:
        si: vCenter service instance
        datacenter_name (str): Name of the datacenter
        
    Returns:
        Datacenter object or None if not found
    """
    for dc in si.content.rootFolder.childEntity:
        if dc.name == datacenter_name:
            return dc
    return None

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
    
            if vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOff and delete_vm:
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

def fetch_ip_from_vm(si, vm_name):
    vm_name = vm_name if vm_name else CONTROLLER_NAME
    datacenter_name = VCENTER_DATACENTER_NAME
    folder_name = VCENTER_FOLDER_NAME
    search_text = f"{datacenter_name}/vm/{folder_name}"
    search_folder = si.RetrieveContent().searchIndex.FindByInventoryPath(search_text)
    if not search_folder:
        print(f"folder {folder_name} not found")
        print(f"search text = {search_text}")
        sys.exit(1)
    vm_obj = None

    @retry(ValueError,tries=100,delay=5)
    def fetch_vm_obj():
        vm_obj = None
        
        for virtual_m in search_folder.childEntity:
            if vim.Folder == type(virtual_m):
                continue
            if virtual_m.name == vm_name:
                vm_obj = virtual_m
                return vm_obj
        if not vm_obj:
            raise ValueError(f"VM {vm_name} not found in folder {folder_name}")
    
    print(f"Checking for VM {vm_name} in folder {folder_name}")
    vm_obj = fetch_vm_obj()
    if not vm_obj:
        print(f"VM {vm_name} not found in folder {folder_name}")
        sys.exit(1)
    print(f"VM {vm_name} found in folder {folder_name}")

    mgmt_ip = None
    @retry(Exception,tries=30,delay=10)
    def fetch_mgmt_ip(vm_obj):
        
        if vm_obj.guest and vm_obj.guest.net:
            for ip_net in vm_obj.guest.net:
                if not ip_net.ipAddress:
                    continue
                for ip_addr in ip_net.ipAddress:
                    if ip_addr and ":" not in ip_addr:
                        return ip_addr
        # No IPv4 IP found - raise exception to trigger retry
        raise Exception(f"No IPv4 management IP address found for VM {vm_name}")

    print(f"Fetching management IP from VM {vm_name}")
    try:
        mgmt_ip = fetch_mgmt_ip(vm_obj)
    except Exception as e:
        print(f"ERROR: Failed to retrieve management IP from VM {vm_name} after all retries")
        print("The VM may not have been fully initialized or network configuration is incomplete.")
        print("Changing network adapter and retrying...")
        change_network_adapter(vm_obj,network_identifier="ibn-cm1w2-nsx1-avi-mgmt")
        try:
            mgmt_ip = fetch_mgmt_ip(vm_obj)
        except Exception as e2:
            print(f"ERROR: Failed to retrieve management IP from VM {vm_name} after changing network adapter")
            print("The VM may not have been fully initialized or network configuration is incomplete.")
            sys.exit(1)
    
    return mgmt_ip

def configure_raw_controller(si,mgmt_ip,vm_name = "",dhcp=False):
    if dhcp:
        mgmt_ip = fetch_ip_from_vm(si, vm_name)
        if mgmt_ip is None:
            print(f"ERROR: Failed to retrieve management IP from VM {CONTROLLER_NAME}")
            print("The VM may not have been fully initialized or network configuration is incomplete.")
            sys.exit(1)
    se_ips_to_use_for_ctlr(si,mgmt_ip)
    set_welcome_password_and_set_systemconfiguration(mgmt_ip)
    put_to_cloud(mgmt_ip)
    try:
        setup_tmux(mgmt_ip)
    except Exception as e:
        print("----------------------",str(e))
    setup_cloud_se_wo_put_to_cloud(mgmt_ip)
    setup_vs(mgmt_ip)

def configure_raw_controller_dhcp(si,vm_name):
    mgmt_ip = fetch_ip_from_vm(si, vm_name)
    if mgmt_ip is None:
        print(f"ERROR: Failed to retrieve management IP from VM {vm_name}")
        print("The VM may not have been fully initialized or network configuration is incomplete.")
        sys.exit(1)
    se_ips_to_use_for_ctlr(si,mgmt_ip)
    set_welcome_password_and_set_systemconfiguration(mgmt_ip)
    put_to_cloud(mgmt_ip)
    try:
        setup_tmux(mgmt_ip)
    except Exception as e:
        print("----------------------",str(e))
    setup_cloud_se_wo_put_to_cloud(mgmt_ip)
    setup_vs(mgmt_ip)

def configure_password_only(mgmt_ip):
    set_password_only_and_set_systemconfiguration(mgmt_ip)

def configure_raw_controller_wo_tmux(si,mgmt_ip):
    se_ips_to_use_for_ctlr(si,mgmt_ip)
    set_welcome_password_and_set_systemconfiguration(mgmt_ip)
    setup_cloud_se(mgmt_ip)
    setup_vs(mgmt_ip)

def setup_cloud_vs_se(si, mgmt_ip):
    se_ips_to_use_for_ctlr(si,mgmt_ip)
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

def get_build_details_from_build_dir(dir,in_dir):
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
        return buildno, time_ago, ova_file
    return None, None, None

def list_all_builds_in_mnt_builds(version):
    "[[index version buildno file date],...]"
    all_builds = []
    dir = os.path.join("/mnt/builds/",version)
    if not os.path.isdir(dir):
        print("Not a valid dir %s"%(dir))
        return {}
    for in_dir in os.listdir(dir):
        if "last" in in_dir:
            buildno, time_ago, ova_file = get_build_details_from_build_dir(dir,in_dir)
            if buildno:
                all_builds.append([0 ,version, int(buildno), ova_file, time_ago])
    if not all_builds:
        for in_dir in os.listdir(dir):
            buildno, time_ago, ova_file = get_build_details_from_build_dir(dir,in_dir)
            if buildno:
                all_builds.append([0 ,version, int(buildno), ova_file, time_ago])
    all_builds.sort(key=lambda x: x[2])
    for i in range(len(all_builds)):
        all_builds[i][0] = i+1
    return all_builds


def se_ips_to_use_for_ctlr(si,c_ip=""):
    global SE_IPS_TO_USE_FOR_CURRENT_CTLR
    global SE_DHCP
    if SE_IPS_TO_USE_FOR_CURRENT_CTLR or SE_DHCP:
        return
    dhcp = input("Do you want to use DHCP for SE management IP [Y/N]? [N]: ")
    if dhcp.lower() == "y":
        SE_DHCP = True
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
        mgmt_ips = input("Management IP ? [Enter Comma Separated IP] [Default: %s]: "%(default_ip))
        if not mgmt_ips:
            if not se_ip: continue
            mgmt_ips = [default_ip]
        else:
            mgmt_ips = mgmt_ips.split(",")
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
    global DHCP
    vm_type = "controller"
    si = connect()
    custom_version = input("Custom Build [Y/N]? [N]: ")
    ctlr_name = ""
    if custom_version.lower() == "y":
        default_path = "/home/aviuser/workspace/avi-dev/build/controller.ova"
        source_ova_path = input(f"Source Ova Path (local/http/ftp) ? [Default: {default_path}] :")
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
        print(f"Source Ova Path = {source_ova_path}")
        ctlr_name = "ctlr_%s-%s"%(builds[build_index-1][1],builds[build_index-1][2])
    global CONTROLLER_NAME
    CONTROLLER_NAME = ctlr_name
    mgmt_leader_ip = ""
    mgmt_ips = []
    while True:
        dhcp = input("Do you want to use DHCP for Controller management IP [Y/N]? [N]: ")
        if dhcp.lower() == "y":
            DHCP = True
            break
        mgmt_ips = get_free_controller_ips(si)
        if len(mgmt_ips)==3:
            print("Creating a 3 node cluster")
            mgmt_ips_leader = {str(index): val for index, val in enumerate(mgmt_ips)}
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

    vcenter_ip = input(f"Vcenter IP ? [Default: {VCENTER_IP}] :") or VCENTER_IP
    datacenter = input(f"Datacenter Name ? [Default: {VCENTER_DATACENTER_NAME}] :") or VCENTER_DATACENTER_NAME
    #datacenter_obj = get_datacenter_obj(si,datacenter)
    cluster_name = input(f"Cluster ? [Default: {VCENTER_CLUSTER_NAME}] :") or VCENTER_CLUSTER_NAME
    datastore = input(f"Datastore ? [Default: {VCENTER_DATASTORE_NAME}] :") or VCENTER_DATASTORE_NAME
    while True:
        folder_name = input(f"Folder Name ? [Default: {VCENTER_FOLDER_NAME}] :") or VCENTER_FOLDER_NAME
        if folder_name:
            folder_obj = get_folder_obj(si, datacenter,folder_name)
            if folder_obj:
                break
    management_network_input = input(f"Management Network ? [Default: {VCENTER_MANAGEMENT_MAP['Internal_Management']['name']}][ or (1) {VCENTER_MANAGEMENT_MAP['Management']['name']} ]:")
    management_network = VCENTER_MANAGEMENT_MAP["Internal_Management"]["name"] if not management_network_input else management_network_input
    if management_network_input == "1":
        management_network = VCENTER_MANAGEMENT_MAP["Management"]["name"]
    global CTLR_MGMT_NETWORK
    CTLR_MGMT_NETWORK = management_network

    if not DHCP:
        mask = input(f"Network Mask ? [Default: {VCENTER_MANAGEMENT_MAP['Internal_Management']['mask']}] :") or VCENTER_MANAGEMENT_MAP["Internal_Management"]["mask"]
        gw_ip = input(f"Gateway IP ? [Default: {VCENTER_MANAGEMENT_MAP['Internal_Management']['gateway']}] :") or VCENTER_MANAGEMENT_MAP["Internal_Management"]["gateway"]

    while True:
        vm_name = input(f"VM Name ? [{ctlr_name}]:")
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
        if not DHCP:
            for ip in mgmt_ips:
                if ip == mgmt_leader_ip:
                    vm_name_str = vm_name
                else:
                    count += 1
                    vm_name_str = str(vm_name)+"-"+str(count)
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

        else:
            prop = ' --prop:avi.sysadmin-public-key.CONTROLLER="' + get_own_sysadmin_key() + '" '
            prop += '--name="' + vm_name + '" '
            if power_on.lower() == 'y':
                prop += '--powerOn '
            prop += '"--vmFolder='+folder_name+'" ' 
            cmd = 'ovftool --noSSLVerify --X:logLevel=warning --X:logToConsole "--datastore=' + datastore + \
                '" --net:Management="' + management_network + \
                '" ' + prop + source_ova_path + ' ' + vi 
            print ('\n',cmd,'\n')
            verify = input("Verify the command and agree to proceed [Y/N] ? [Y] :") or 'Y'
            if verify.lower() == 'y':
                cmds["DHCP"] = cmd
            else:
                print ("Exiting ...")
                exit(0)


        print ("\nDeploying OVA")
        jobs = []
        if not DHCP:
            for ip in mgmt_ips:
                p = multiprocessing.Process(target=deploy_ova, args=(cmds[ip],))
                jobs.append(p)
                p.start()

            for proc in jobs:
                proc.join()
            if set_password_and_sys_config.upper() == "Y":
                if len(mgmt_ips)>1:
                    configure_raw_controller_cluster(si, mgmt_leader_ip, mgmt_ips)
                elif len(mgmt_ips) == 1:
                    configure_raw_controller(si, mgmt_leader_ip)
        else:
            deploy_ova(cmds["DHCP"])   
            if set_password_and_sys_config.upper() == "Y":
                configure_raw_controller(si, mgmt_leader_ip, dhcp=True) 

    print("================== DONE ==============")

# All old command handlers removed - functionality moved to organized handler functions


# All command handling moved to main() function
def handle_rename_vm(ip, newname):
    """Handle VM rename command.
    
    Args:
        ip: IP address of the VM to rename
        newname: New name for the VM
    """
    si = connect()
    search = si.RetrieveContent().searchIndex
    vms = list(set(search.FindAllByIp(ip=ip, vmSearch=True)))

    for vm in vms:
        rename_confirm = input(f"Are you sure you want to rename '{vm.name}', ({ip}) with '{newname}'? [Y/N] \n")
        if rename_confirm.lower() == "n":
            continue
        print(f"Renaming {vm.name} {ip} to {newname}")
        task = vm.Rename(newname)
        while task.info.state not in [vim.TaskInfo.State.success, vim.TaskInfo.State.error]:
            time.sleep(1)
        print(f"Renaming done. {task.info.state}")


def handle_poweron_vm(vm_name=''):
    """Handle power on VM command.
    
    Args:
        vm_name: Optional VM name to power on (empty string for all)
    """
    si = connect()
    datacenter_name = VCENTER_DATACENTER_NAME
    for dc in si.content.rootFolder.childEntity:
        if dc.name == datacenter_name:
            datacenter = dc
    folder_name = VCENTER_FOLDER_NAME
    search_path = f"/{datacenter.name}/vm/{folder_name}"
    folder_obj = si.content.searchIndex.FindByInventoryPath(search_path)
    if not folder_obj:
        print(f"Folder not found at path: {search_path}")
        sys.exit(1)
    with ThreadPoolExecutor(max_workers=10) as executor:
        for virtual_m in folder_obj.childEntity:
            if not virtual_m.config.template:
                if vm_name:
                    if virtual_m.name != vm_name:
                        continue
                if virtual_m.runtime.powerState == 'poweredOff':
                    executor.submit(power_on_vm, virtual_m)
                else:
                    print(f"VM {virtual_m.name} is already ON")


def handle_delete_ctlr_se():
    """Handle delete controller and SE command."""
    si = connect()
    mgmt_ips = get_used_controller_ips(si)
    mgmt_se_ips = set()
    for mgmt_ip in mgmt_ips:
        mgmt_se_ips.update(set(get_all_se(mgmt_ip)))
    poweroff_and_delete_vm(mgmt_ips + list(mgmt_se_ips), delete=True, si=si)


def handle_latest_builds():
    """Handle latest builds command."""
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
    final_print_vals = [("Index", "Version", "Build No", "File", "Date")]
    for build in all_builds:
        for value in build:
            final_print_vals.append((value[0], value[1], value[2], value[3], value[4]))
        final_print_vals.append(("---", "---", "---", "---", "---"))

    print(tabulate(final_print_vals, headers="firstrow", tablefmt="psql"))
    

def handle_configure_vs():
    """Handle configure VS command."""
    si = connect()
    mgmt_ip = get_used_controller_ip(si)
    setup_vs(mgmt_ip)


def handle_configure_cloud_vs_se():
    """Handle configure cloud VS SE command."""
    si = connect()
    mgmt_ip = get_used_controller_ip(si)
    setup_cloud_vs_se(si, mgmt_ip)


def handle_setup_tmux():
    """Handle setup tmux command."""
    si = connect()
    mgmt_ip = get_used_controller_ip(si)
    setup_tmux(mgmt_ip)


def handle_setup_tmux_install_only():
    """Handle setup tmux install only command."""
    si = connect()
    mgmt_ip = get_used_controller_ip(si)
    setup_tmux_install_only(mgmt_ip)


def handle_flush_db_configure():
    """Handle flush DB configure command."""
    si = connect()
    mgmt_ip = get_used_controller_ip(si)
    se_ips_to_use_for_ctlr(si, mgmt_ip)
    delete_all_se(si, mgmt_ip)
    flush_db(mgmt_ip)
    set_welcome_password_and_set_systemconfiguration(mgmt_ip)
    setup_cloud_se(mgmt_ip)
    setup_vs(mgmt_ip)


def handle_configure_controller(command):
    """Handle configure controller commands."""
    si = connect()
    mgmt_ips = get_used_controller_ips(si)
    for mgmt_ip in mgmt_ips:
        if command == 'configure_raw_controller':
            configure_raw_controller(si, mgmt_ip)
        elif command == 'configure_raw_controller_wo_tmux':
            configure_raw_controller_wo_tmux(si, mgmt_ip)
        elif command == 'configure_password_only':
            configure_password_only(mgmt_ip)

def handle_configure_raw_controller_dhcp():
    """Handle configure raw controller DHCP command."""
    si = connect()
    vm_name = input("Enter the VM name: ")
    if not vm_name:
        print("VM name is required")
        sys.exit(1)
    vm_name = vm_name.strip()
    configure_raw_controller_dhcp(si, vm_name)


def handle_change_password_for_ft():
    """Handler for change_password_for_FT command."""
    si = connect()
    mgmt_ips = get_used_controller_ips(si)
    for mgmt_ip in mgmt_ips:
        change_password_for_ft(mgmt_ip)

def handle_show_password_for_all_controllers():
    """Handler for show_password_for_all_controllers command."""
    si = connect()
    get_current_password_for_all_controllers(si)
# =============================================================================
# CLICK CLI COMMANDS
# =============================================================================

def print_execution_time():
    """Print execution time summary."""
    end_time = time.time()
    elapsed_time = str(timedelta(seconds=end_time - START_TIME))
    current_time = datetime.datetime.now()
    execution_summary = f"Time Elapsed {elapsed_time}, Current Time = {current_time}"
    logger.info(execution_summary)
    print(execution_summary)


class WideHelpGroup(click.Group):
    """Custom Group class that provides wider command column in help output."""
    
    # Define preferred command order for help display (matches show_help() order)
    COMMAND_ORDER = [
        'with_se_ips',
        'free_ip',
        'free_ips',
        'delete_ctlr_se',
        'delete',
        'delete_name',
        'poweroff',
        'rename',
        'poweron',
        'reimage_ctlr',
        'latest_builds',
        'generate_controller_from_ova',
        'configure_raw_controller_dhcp',
        'configure_raw_controller',
        'configure_raw_controller_wo_tmux',
        'configure_password_only',
        'configure_cloud_vs_se',
        'configure_vs',
        'flush_db_configure_raw_controller_wo_tmux',
        'setup_tmux',
        'setup_tmux_install_only',
        'change_password_for_FT',
        'show_password_for_all_controllers',
        'install_completion',
    ]
    
    def list_commands(self, ctx):
        """Return commands in custom order."""
        commands = list(self.commands.keys())
        # Sort by custom order, unknown commands go at the end alphabetically
        return sorted(commands, key=lambda x: (
            self.COMMAND_ORDER.index(x) if x in self.COMMAND_ORDER else len(self.COMMAND_ORDER),
            x  # Secondary sort alphabetically for commands not in COMMAND_ORDER
        ))
    
    def format_commands(self, ctx, formatter):
        """Write all the commands with increased column width for long command names."""
        commands = []
        for subcommand in self.list_commands(ctx):
            cmd = self.get_command(ctx, subcommand)
            if cmd is None:
                continue
            help_text = cmd.get_short_help_str(limit=150)
            commands.append((subcommand, help_text))

        if commands:
            # Calculate max command width with minimum of 45 chars for long command names
            max_cmd_len = max(len(cmd[0]) for cmd in commands)
            limit = max(max_cmd_len + 2, 45)

            with formatter.section('Commands'):
                formatter.write_dl(commands, col_max=limit)


@click.group(cls=WideHelpGroup, invoke_without_command=True, context_settings=dict(max_content_width=300, terminal_width=300))
@click.pass_context
def cli(ctx):
    """VMware vSphere IP Management and Controller Automation Tool.
    
    Run without any command to show VMs with SE IPs and management reserved IPs.
    Use --help with any command for more information.
    """
    logger.info("Starting vSphere automation script")
    # Store whether we ran the default command for the result callback
    ctx.ensure_object(dict)
    ctx.obj['ran_default'] = False
    
    if ctx.invoked_subcommand is None:
        # Default behavior: show VMs
        logger.info("Executing default command: showing VM information")
        ctx.obj['ran_default'] = True
        final_print_vals = get_vms_ips_network(with_se_ips=True, with_mgmt_reserved_ips=True)
        print(tabulate(final_print_vals, headers="firstrow", tablefmt="psql"))


@cli.result_callback()
@click.pass_context
def process_result(ctx, result, **kwargs):
    """Called after any command completes to print execution time."""
    print_execution_time()


# --- Simple commands (no arguments) ---

@cli.command('with_se_ips')
def cmd_with_se_ips():
    """Show VMs with SE IPs and management reserved IPs."""
    logger.info("Executing with_se_ips command")
    final_print_vals = get_vms_ips_network(with_se_ips=True, with_mgmt_reserved_ips=True)
    print(tabulate(final_print_vals, headers="firstrow", tablefmt="psql"))


@cli.command('free_ips')
def cmd_free_ips():
    """Show available free IPs."""
    logger.info("Executing free_ips command")
    final_print_vals = get_vms_ips_network(with_se_ips=True, free_ips=True, with_mgmt_reserved_ips=True)
    print(tabulate(final_print_vals, headers="firstrow", tablefmt="psql"))


# Alias for free_ips
@cli.command('free_ip')
def cmd_free_ip():
    """Show available free IPs (alias for free_ips)."""
    logger.info("Executing free_ip command")
    final_print_vals = get_vms_ips_network(with_se_ips=True, free_ips=True, with_mgmt_reserved_ips=True)
    print(tabulate(final_print_vals, headers="firstrow", tablefmt="psql"))


@cli.command('delete_ctlr_se')
def cmd_delete_ctlr_se():
    """Delete controller and SE VMs."""
    logger.info("Executing delete_ctlr_se command")
    handle_delete_ctlr_se()


@cli.command('latest_builds')
def cmd_latest_builds():
    """Show latest builds available."""
    logger.info("Executing latest_builds command")
    handle_latest_builds()


@cli.command('configure_vs')
def cmd_configure_vs():
    """Configure virtual service."""
    logger.info("Executing configure_vs command")
    handle_configure_vs()


@cli.command('configure_cloud_vs_se')
def cmd_configure_cloud_vs_se():
    """Configure cloud, VS, and SE."""
    logger.info("Executing configure_cloud_vs_se command")
    handle_configure_cloud_vs_se()


@cli.command('setup_tmux')
def cmd_setup_tmux():
    """Setup tmux on controller."""
    logger.info("Executing setup_tmux command")
    handle_setup_tmux()


@cli.command('setup_tmux_install_only')
def cmd_setup_tmux_install_only():
    """Setup tmux install only (no configuration)."""
    logger.info("Executing setup_tmux_install_only command")
    handle_setup_tmux_install_only()


@cli.command('flush_db_configure_raw_controller_wo_tmux')
def cmd_flush_db_configure():
    """Flush DB and configure controller without tmux."""
    logger.info("Executing flush_db_configure_raw_controller_wo_tmux command")
    handle_flush_db_configure()


@cli.command('generate_controller_from_ova')
def cmd_generate_controller_from_ova():
    """Generate controller from OVA file."""
    logger.info("Executing generate_controller_from_ova command")
    generate_controller_from_ova()


@cli.command('configure_raw_controller')
def cmd_configure_raw_controller():
    """Configure raw controller with full setup."""
    logger.info("Executing configure_raw_controller command")
    handle_configure_controller('configure_raw_controller')


@cli.command('configure_raw_controller_wo_tmux')
def cmd_configure_raw_controller_wo_tmux():
    """Configure raw controller without tmux."""
    logger.info("Executing configure_raw_controller_wo_tmux command")
    handle_configure_controller('configure_raw_controller_wo_tmux')


@cli.command('configure_password_only')
def cmd_configure_password_only():
    """Configure password only on controller."""
    logger.info("Executing configure_password_only command")
    handle_configure_controller('configure_password_only')


@cli.command('configure_raw_controller_dhcp')
def cmd_configure_raw_controller_dhcp():
    """Configure raw controller with DHCP."""
    logger.info("Executing configure_raw_controller_dhcp command")
    handle_configure_raw_controller_dhcp()


@cli.command('change_password_for_FT')
def cmd_change_password_for_ft():
    """Change password to VMwareAvilb123!/avi123 for FT."""
    logger.info("Executing change_password_for_FT command")
    handle_change_password_for_ft()

@cli.command('show_password_for_all_controllers')
def cmd_show_password_for_all_controllers():
    """Show password for all controllers."""
    logger.info("Executing show_password_for_all_controllers command")
    handle_show_password_for_all_controllers()


@cli.command('reimage_ctlr')
def cmd_reimage_ctlr():
    """Reimage controller."""
    logger.info("Executing reimage_ctlr command")
    # Placeholder - implement if function exists
    print("Reimage controller command - not yet implemented")


# --- Commands with arguments ---

@cli.command('delete')
@click.argument('ips', nargs=-1, required=True)
def cmd_delete(ips):
    """Delete VMs by IP address.
    
    IPS: One or more IP addresses of VMs to delete.
    """
    logger.info(f"Executing delete command with IPs: {ips}")
    handle_delete_poweroff_commands(ips, delete=True)


@cli.command('poweroff')
@click.argument('ips', nargs=-1, required=True)
def cmd_poweroff(ips):
    """Power off VMs by IP address.
    
    IPS: One or more IP addresses of VMs to power off.
    """
    logger.info(f"Executing poweroff command with IPs: {ips}")
    handle_delete_poweroff_commands(ips, delete=False)


@cli.command('delete_name')
@click.argument('names', nargs=-1, required=True)
def cmd_delete_name(names):
    """Delete VMs by name.
    
    NAMES: One or more VM names to delete.
    """
    logger.info(f"Executing delete_name command with names: {names}")
    handle_delete_by_name(names)


@cli.command('rename')
@click.argument('ip')
@click.argument('newname')
def cmd_rename(ip, newname):
    """Rename a VM.
    
    IP: IP address of the VM to rename.
    NEWNAME: New name for the VM.
    """
    logger.info(f"Executing rename command: {ip} -> {newname}")
    handle_rename_vm(ip, newname)


@cli.command('poweron')
@click.argument('name', required=False, default='')
def cmd_poweron(name):
    """Power on VMs.
    
    NAME: Optional VM name to power on. If not provided, powers on all VMs.
    """
    logger.info(f"Executing poweron command with name: {name or 'all'}")
    handle_poweron_vm(name)


# =============================================================================
# SHELL COMPLETION SUPPORT
# =============================================================================

# Get all available commands for completion
def _get_all_commands():
    """Return list of all available CLI commands."""
    return WideHelpGroup.COMMAND_ORDER


def _generate_bash_completion_script(script_path, alias_name='vsphere'):
    """Generate bash completion script content."""
    commands = ' '.join(_get_all_commands())
    var_name = f"_{alias_name.upper()}_COMMANDS"
    return f'''# Bash completion for vSphere automation script
# Generated by get_empty_ips_vsphere-vmware.py

{var_name}="{commands}"

_vsphere_completions() {{
    local cur
    COMPREPLY=()
    cur="${{COMP_WORDS[COMP_CWORD]}}"
    
    # Complete commands on first argument
    if [[ ${{COMP_CWORD}} -eq 1 ]]; then
        COMPREPLY=( $(compgen -W "${var_name}" -- "${{cur}}") )
    fi
}}

# Completion for the alias
complete -F _vsphere_completions {alias_name}
'''


def install_shell_completion():
    """
    Install bash shell completion.
    
    Creates completion script and optionally adds alias to ~/.bashrc.
    """
    script_path = os.path.abspath(__file__)
    alias_name = 'vsphere_ips'
    
    rc_file = os.path.expanduser('~/.bashrc')
    completion_dir = os.path.expanduser('~/.bash_completion.d')
    completion_file = os.path.join(completion_dir, f'{alias_name}_completion.bash')
    completion_content = _generate_bash_completion_script(script_path, alias_name)
    
    # Create completion directory if it doesn't exist
    os.makedirs(completion_dir, exist_ok=True)
    
    # Write completion script
    try:
        with open(completion_file, 'w') as f:
            f.write(completion_content)
        print(f"✓ Completion script written to: {completion_file}")
    except Exception as e:
        print(f"✗ Error writing completion script: {e}")
        return
    
    # Create alias line
    alias_line = f"alias {alias_name}='python3 {script_path}'"
    
    # Source line for completion
    source_lines = f'''
# vSphere automation script completion and alias
if [ -f {completion_file} ]; then
    source {completion_file}
fi
{alias_line}
'''
    
    # Check if already installed
    try:
        with open(rc_file, 'r') as f:
            content = f.read()
            if 'vSphere automation script completion' in content:
                print(f"✓ Shell completion already configured in {rc_file}")
                print(f"\n  To refresh, run: source {rc_file}")
                print(f"  Then use '{alias_name}' followed by TAB TAB to see commands")
                return
    except FileNotFoundError:
        pass
    
    # Ask user if they want to add to rc file
    print(f"\nTo enable completion, add the following to {rc_file}:")
    print("-" * 60)
    print(source_lines)
    print("-" * 60)
    
    try:
        add_to_rc = input(f"\nAdd to {rc_file} now? [Y/n]: ").strip().lower()
        if add_to_rc in ('', 'y', 'yes'):
            with open(rc_file, 'a') as f:
                f.write(source_lines)
            print(f"\n✓ Added to {rc_file}")
            print(f"\nTo activate now:")
            print(f"  source {rc_file}")
            print(f"\nThen type '{alias_name}' and press TAB TAB to see available commands.")
        else:
            print(f"\nYou can manually add the lines above to {rc_file}")
    except Exception as e:
        print(f"\nCould not modify {rc_file}: {e}")
        print(f"Please manually add the lines above to {rc_file}")


@cli.command('install_completion')
def cmd_install_completion():
    """Install shell tab completion (type 'vsphere_ips' + TAB TAB for commands)."""
    install_shell_completion()


# Execute CLI if script is run directly
if __name__ == "__main__":
    # Check for special completion installation flag
    if len(sys.argv) > 1 and sys.argv[1] == '--install-completion':
        install_shell_completion()
    else:
        cli()
   

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
