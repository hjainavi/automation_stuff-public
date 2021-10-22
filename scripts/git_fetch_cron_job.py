import pexpect,datetime
logs = []

import os

if os.path.isdir("/home/aviuser/workspace/avi-dev"):
    CWD = "/home/aviuser/workspace/avi-dev"
    FILE_PATH = "/home/aviuser/logfile_git_fetch_cron.txt"
elif os.path.isdir("/root/workspace/avi-dev"):
    CWD = "/root/workspace/avi-dev"
    FILE_PATH = "/root/logfile_git_fetch_cron.txt"


def print_logs(val):
    with open(FILE_PATH,'a') as ff:
        ff.write(val)
        ff.write('\n')
try:
    print_logs('******** ' + str(datetime.datetime.now()) + '  ********' + '\n')
    print_logs('git fetch -p -P --force , %s'%(CWD))
    c = pexpect.spawn('git fetch -p -P --force',cwd=CWD)
    c.expect("Enter passphrase for key '/home/aviuser/.ssh/id_rsa':")
    print_logs(c.after)
    c.sendline('maddy')
    c.expect(pexpect.EOF, timeout=3000)
    print_logs(c.before)
except Exception as e:
    print_logs("ERROR !!!")
    print_logs(str(e))

# crontab -e has : 0 */8 * * * /usr/bin/python /root/automation_stuff/scripts/git_fetch_cron_job.py
