# netstat -no | findstr 174 | findstr 22
import subprocess, shlex, time, socket, re
from paramiko import SSHClient, AutoAddPolicy

print ""

HOSTNAME_CONN_TO_VMWARE_VPN = "10.140.16.174"
USER = "root"
PASSWORD = "mad460nash"
SOCKS_PORT = 9090

def test_ping(hostname,count=3,timeout=300):
    cmd = "ping %s -n %s -w %s"%(hostname,count,timeout)
    output = (subprocess.check_output(shlex.split(cmd)))

def check_if_connected_to_avi_vpn(hostname_to_check):
    try:
        test_ping(hostname_to_check)
    except subprocess.CalledProcessError as e:
        print ("\n*************  AVI VPN not connected *****************\n")
        exit(1)

def check_if_connected_to_vmware_vpn(ssh_client):
    response = ssh_client.execute_command("globalprotect show --status")
    if "GlobalProtect status: Connected" in response:
        print "Already Connected"
        return True
    elif ("GlobalProtect status: Disconnected" in response) or ("GlobalProtect status: OnDemand mode" in response):
        return False
    else:
        print "Sth wrong with vmware vpn connection from 10.140.16.174, figure it out"
        exit(1)

def connect_to_vmware_vpn():
    connected_to_vmware_vpn = False
    check_if_connected_to_avi_vpn(HOSTNAME_CONN_TO_VMWARE_VPN)
    try:
        ssh_client = RemoteClient(HOSTNAME_CONN_TO_VMWARE_VPN, USER, PASSWORD)
        connected_to_vmware_vpn = check_if_connected_to_vmware_vpn(ssh_client)
        if not connected_to_vmware_vpn:
            cmd = "globalprotect connect -p gpu.vmware.com -u harshj -g gp-blr3-gw3.vmware.com"
            response = ssh_client.execute_on_shell(cmd)
            if "username" in response:
                response = ssh_client.execute_on_shell("harshj")
            if ("password") in response or ("Enter your tokencode" in response):
                password = raw_input("Enter RSA passsword to connect to vmware vpn: ")
                response = ssh_client.execute_on_shell(password.strip())
            if "Connected" in response:
                print "Connected to VPN"
                connected_to_vmware_vpn = True
            else:
                print "Sth wrong with vmware vpn connection from 10.140.16.174, figure it out"
    finally:
        if ssh_client.client:
            print "SSH Client Disconnecting"
            ssh_client.disconnect()
    return connected_to_vmware_vpn

def check_if_port_is_open(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = False
    try:
        sock.bind(("127.0.0.1", port))
        print ("Port is open")
        result = True
    except:
        print("Port is in use")
    sock.close()
    return result

def close_existing_conn(is_port_open):
    out = subprocess.check_output(shlex.split("netstat -no | findstr %s:22 | findstr ESTAB"%(HOSTNAME_CONN_TO_VMWARE_VPN)),shell=True)
    PIDS = []
    for line in out.splitlines():
        print line
        line_word_list = [word for word in line.strip().split(" ") if word]
        if line_word_list:
            PIDS.append(line_word_list[-1])
    if PIDS:
        for PID in PIDS:
            print "taskkill /F /PID %s"%(PID)
            subprocess.call(shlex.split("taskkill /F /PID %s"%(PID)))
    
def create_ssh_tunnel():
    is_port_open = check_if_port_is_open(SOCKS_PORT)
    if not is_port_open:
        close_existing_conn(is_port_open)
        is_port_open = check_if_port_is_open(SOCKS_PORT)
    cmd = "ssh -i file -D %s -f -C -q -N %s@%s"%(SOCKS_PORT, USER, HOSTNAME_CONN_TO_VMWARE_VPN)
    if is_port_open:
        proc = subprocess.Popen(shlex.split(cmd), stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        print ("SOCK5 Tunnel Created")
    else:
        print ("SOCK5 Tunnel not created")

#connect_to_vmware_vpn()

class RemoteClient:
    """Client to interact with a remote host via SSH """
    def __init__(self, host, user, password):
        self.host = host
        self.user = user
        self.password = password
        self.client = None
        self.channel = None

    def __connect(self):
        """Open connection to remote host."""
        self.client = SSHClient()
        self.client.load_system_host_keys()
        self.client.set_missing_host_key_policy(AutoAddPolicy())
        self.client.connect(self.host,
                                username=self.user,
                                password=self.password)
        return self.client

    def disconnect(self):
        """Close ssh connection."""
        self.client.close()

    def execute_command(self, cmd):
        """Execute command ."""
        if self.client is None:
            self.client = self.__connect()
        stdin, stdout, stderr = self.client.exec_command(cmd)
        stdout.channel.recv_exit_status()
        response = stdout.readlines()
        response = [str(line.strip()) for line in response]
        for line in response:
            print line
        return response

    def execute_on_shell(self,cmd):
        if self.channel is None:
            self.channel = self.client.invoke_shell(term='xterm')
        self.channel.send(cmd+"\n")
        output = self.getBuffer(self.channel)
        return output

    def getBuffer(self,channel):
        buff = ''
        while True:
            if channel.recv_ready():
                output = channel.recv(65536)
                buff += output
            else:
                time.sleep(3)
                if not(channel.recv_ready()):
                    break
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        result = ansi_escape.sub('', buff)
        print result
        return result
'''
if connect_to_vmware_vpn():
    print "Connected to Vmware VPN"
    create_ssh_tunnel()
else:
    print "Not Connected to Vmware VPN"
'''
create_ssh_tunnel()
print ""