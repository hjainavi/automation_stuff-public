#!/usr/bin/env python
import sys,os
change = "None"
change_path_only = "False"
if len(sys.argv)>1:
    if sys.argv[1]=='change':
        change="True"
    if sys.argv[1]=='changeback':
        change="False"
    if sys.argv[1]=='change_path_only':
        change_path_only="True"
else:
    sys.exit(1)
data=[]
filepath = '/etc/systemd/system/'+sys.argv[2] if not change_path_only else ""
if change=="True" and not change_path_only:
    with open(filepath,'r') as f:
        for line in f.readlines():
            if 'ExecStopPost' in line and '#' not in line:
                data.append('#'+line)
            else:
                data.append(line)
    with open(filepath,'w') as f:
        for line in data:
            f.write(line)

elif change=="False" and not change_path_only:
    with open(filepath,'r') as f:
        for line in f.readlines():
            if 'ExecStopPost' in line and line[0]=='#':
                data.append(line[1:])
            else:
                data.append(line)
    with open(filepath,'w') as f:
        for line in data:
            f.write(line)

else:
    pass

# adding pythonpath of avipdb in aviportal.sh -- when running via init script     
lines = []
current_path = os.path.dirname(sys.argv[0])
print("change_conf ",current_path)
with open('/opt/avi/python/bin/aviportal.sh','r') as f:
    for line in f.readlines():
        add_text = False
        if 'export PYTHONPATH' in line:
            if 'avipdb' not in line:
                add_text = ':' + os.path.join(current_path,'avipdb')
        if add_text:
            lines.append(line.strip('\n')+add_text+'\n')
        else:
            lines.append(line)
with open('/opt/avi/python/bin/aviportal.sh','w') as f:
    for line in lines:
        f.write(line)

# adding pythonpath of avipdb in manage.py shell pythonpath   
lines = []
current_path = os.path.dirname(sys.argv[0])
print("change_conf ",current_path)
bin_portal_index = False
avipdb_present = False
with open('/opt/avi/python/bin/portal/manage.py','r') as f:
    for index,line in enumerate(f.readlines()):
        if '/opt/avi/python/bin/portal' in line:
            bin_portal_index = index
        if 'avipdb' in line:
            avipdb_present = True
        lines.append(line)

with open('/opt/avi/python/bin/portal/manage.py','w') as f:
    for index,line in enumerate(lines):
        f.write(line)
        if not avipdb_present and index == bin_portal_index:
            avipdb_path = os.path.join(current_path,'avipdb')
            add_text = 'sys.path.append("%s")'%(avipdb_path)
            f.write(add_text)
            f.write("\n")



