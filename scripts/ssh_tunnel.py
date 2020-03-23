from pexpect import pxssh
import subprocess, shlex, time
import socket

def test_ping(hostname,count=3,timeout=300):
    cmd = "ping %s -n %s -w %s"%(hostname,count,timeout)
    subprocess.check_output(shlex.split(cmd))


def connect_to_vmware_vpn():
    try:
        test_ping('10.140.16.174')
    except subprocess.CalledProcessError as e:
        print "\n*************  AVI VPN not connected *****************\n"
        exit(1)
    try:
        connected_to_vmware_vpn = False
        ss = pxssh.pxssh(options={
                        "StrictHostKeyChecking": "no",
                        "UserKnownHostsFile": "/dev/null"})
        #hostname = raw_input('hostname: ')
        #username = raw_input('username: ')
        #password = getpass.getpass('password: ')
        ss.login("10.140.16.174", "root", "mad460nash")
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
        elif "GlobalProtect status: Disconnected" in ss.before:
            cmd = "globalprotect connect -p gpu.vmware.com -u harshj -g gp-blr3-gw3.vmware.com"
            ss.sendline(cmd)
            ss.prompt(timeout=10)
            print ss.before
            if "username" in ss.before:
                ss.sendline("harshj")
                ss.prompt(timeout=10)
                print ss.before
            if "username(harshj)" in ss.before:
                ss.sendline("")
                ss.prompt(timeout=10)
                print ss.before
            if "password" in ss.before:
                password = raw_input("Enter RSA passsword to connect to vmware vpn: ")
                ss.sendline(password.strip())
                ss.prompt(timeout=10)
                print ss.before
            if "Connected" in ss.before:
                print "Connected to VPN"
                connected_to_vmware_vpn = True

        elif "Unable to establish a new GlobalProtect connection as a GlobalProtect connection is already established from this Linux system by the same user or another user":
            print ss.before

        else:
            print ss.before
            print "Sth wrong with vmware vpn connection from 10.140.16.174, figure it out"

        #import ipdb;ipdb.set_trace()
        ss.logout()
    except pxssh.ExceptionPxssh as e:
        print("pxssh failed on login.")
        print(e)
    return connected_to_vmware_vpn

def check_if_port_is_open(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = False
    try:
        sock.bind(("0.0.0.0", port))
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
            for pid in line.split(" "):
                if pid:
                    try:
                        print "kill -9 %s"%(pid)
                        subprocess.call(shlex.split('kill -9 %s'%(pid)))
                    except subprocess.CalledProcessError as e:
                        pass
                    break

def create_ssh_tunnel():
    open_port = check_if_port_is_open(9090)
    close_existing_conn(open_port)
    open_port = check_if_port_is_open(9090)
    
    cmd = "sshpass -p 'mad460nash' ssh -f -N -D 9090 root@10.140.16.174"
    if open_port:
        proc = subprocess.Popen(shlex.split(cmd),stderr=subprocess.PIPE,stdout=subprocess.PIPE)
        print "SOCK5 Tunnel Created"
    else:
        print "SOCK5 Tunnel not created"

if connect_to_vmware_vpn():
    create_ssh_tunnel()