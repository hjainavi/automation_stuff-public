#!/usr/bin/env python
import subprocess,pexpect,shlex,sys
ctlr_ip = ''
username = ''
password = ''

if len(sys.argv)>1:
    ctlr_ip = sys.argv[1]
else:
    ctlr_ip = raw_input("controller ip ? \n")

if len(sys.argv)>2:
    username = sys.argv[2]
else:
    username = raw_input("username ? \n")

if len(sys.argv)>3:
    password = sys.argv[3]
else:
    password = raw_input("password ? \n")

print ctlr_ip,username,password

var_cmd = "sudo ./prepare_controller_customizations.sh"
var_child = pexpect.spawn([
