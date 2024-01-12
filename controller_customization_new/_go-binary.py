#!/usr/bin/env python
import sys,os
if not len(sys.argv)>2:
    sys.exit(1)
data=[]
if not ("change" in sys.argv[1] or "changeback" in sys.argv[1]):
    print("not a valid 1st argument")
    sys.exit(1)
if not ("octavius" in sys.argv[2] or "apiserver" in sys.argv[2]):
    print("not a valid 2nd argument")
    sys.exit(1)
filepath = '/etc/systemd/system/'+sys.argv[2]+'_service_script.sh'
with open(filepath,'r') as f:
    for line in f.readlines():
        if 'ln -sfn /opt/avi/bin/go-controller ' in line and sys.argv[1] == "change":
            line1 = line.replace("go-controller", "go-controller-new")
            data.append(line1)
        elif 'ln -sfn /opt/avi/bin/go-controller-new ' in line and sys.argv[1] == "changeback":
            line1 = line.replace("go-controller-new", "go-controller")
            data.append(line1)
        else:
            data.append(line)
with open(filepath,'w') as f:
    for line in data:
        f.write(line)
