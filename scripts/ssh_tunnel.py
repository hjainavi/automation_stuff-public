from pexpect import pxssh
import subprocess, shlex, time
import socket

print ""

HOSTNAME_CONN_TO_VMWARE_VPN = "10.140.16.174"
USER = "root"
PASSWORD = "mad460nash"
SOCKS_PORT = 9090


def test_ping(hostname,count=3,timeout=300):
    cmd = "ping %s -n %s -w %s"%(hostname,count,timeout)
    subprocess.check_output(shlex.split(cmd))

def check_if_connected_to_avi_vpn(hostname_to_check):
    try:
        test_ping(hostname_to_check)
    except subprocess.CalledProcessError as e:
        print ("\n*************  AVI VPN not connected *****************\n")
        exit(1)

def connect_to_vmware_vpn():
    connected_to_vmware_vpn = False
    check_if_connected_to_avi_vpn(HOSTNAME_CONN_TO_VMWARE_VPN)
    try:
        ss = pxssh.pxssh(options={
                        "StrictHostKeyChecking": "no",
                        "UserKnownHostsFile": "/dev/null"})
        ss.login(HOSTNAME_CONN_TO_VMWARE_VPN , USER, PASSWORD)
        ss.sendline('uptime')   # run a command
        ss.prompt()             # match the prompt
        print ss.before        # print everything before the prompt.
        cmd = "globalprotect show --status"
        ss.sendline(cmd)
        ss.prompt(timeout=10)
        print ss.before
        if "GlobalProtect status: Connected" in ss.before:
            print "Already Connected"
            connected_to_vmware_vpn = True
        elif ("GlobalProtect status: Disconnected" in ss.before) or ("GlobalProtect status: OnDemand mode" in ss.before) or ("GlobalProtect status: Connecting..." in ss.before):
            cmd = "globalprotect connect -p gpu.vmware.com -u harshj -g gp-blr3-gw3.vmware.com"
            ss.sendline(cmd)
            ss.prompt(timeout=10)
            print ss.before
            if "username" in ss.before:
                ss.sendline("harshj")
                ss.prompt(timeout=10)
                print ss.before
            if ("Password" in ss.before) or ("Enter your tokencode" in ss.before):
                password = raw_input("Enter RSA passsword to connect to vmware vpn: ")
                ss.sendline(password.strip())
                ss.prompt(timeout=10)
                print ss.before
            if "Connected" in ss.before:
                print "Connected to VPN"
                connected_to_vmware_vpn = True

        elif "Unable to establish a new GlobalProtect connection as a GlobalProtect connection is already established from this Linux system by the same user or another user" in ss.before:
            ss.sendline("ps -ef | grep globalprotect")
            ss.prompt(timeout=10)
            print ss.before
            kill_pid = raw_input("Enter Kill PID :")
            kill_cmd = "kill -9 %s"%(kill_pid.strip())
            ss.sendline(kill_cmd)
            ss.prompt(timeout=10)
            print ss.before

        else:
            print ss.before
            print "Sth wrong with vmware vpn connection from 10.140.16.174, figure it out"

        ss.logout()
    except pxssh.ExceptionPxssh as e:
        print("pxssh failed on login.")
        print(e)
        ss.logout()
        raise
    return connected_to_vmware_vpn

def check_if_port_is_open(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = False
    try:
        sock.bind(("127.0.0.1", port))
        print "Port is open"
        result = True
    except:
        print("Port is in use")
    sock.close()
    return result

def close_existing_conn(is_port_open):
    out = subprocess.check_output(shlex.split("ps -s | grep _ssh"))
    for line in out.split('\n'):
        if "_ssh" in line:
            pid = line.strip().split(" ")[0]
            if pid:
                try:
                    print "kill -9 %s"%(pid)
                    subprocess.call(shlex.split('kill -9 %s'%(pid)))
                except subprocess.CalledProcessError as e:
                    pass
                break


def create_ssh_tunnel():
    open_port = check_if_port_is_open(SOCKS_PORT)
    if not open_port:
        close_existing_conn(SOCKS_PORT)
        open_port = check_if_port_is_open(SOCKS_PORT)
    cmd = "sshpass -p '%s' ssh -D %s -f -C -q -N %s@%s"%(PASSWORD, SOCKS_PORT, USER, HOSTNAME_CONN_TO_VMWARE_VPN)
    if open_port:
        proc = subprocess.Popen(shlex.split(cmd),stderr=subprocess.PIPE,stdout=subprocess.PIPE)
        print "SOCK5 Tunnel Created"
    else:
        print "SOCK5 Tunnel not created"

if connect_to_vmware_vpn():
    create_ssh_tunnel()