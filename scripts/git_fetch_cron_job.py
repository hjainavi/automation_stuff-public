import pexpect,datetime
logs = []
try:
    c = pexpect.spawn('git fetch -p -P --force',cwd='/root/workspace/avi-dev')
    c.expect("Enter passphrase for key '/root/.ssh/id_rsa':")
    logs.append(c.after)
    c.sendline('maddy')
    c.expect(pexpect.EOF, timeout=120)
    logs.append(c.before)
except Exception as e:
    logs.append(str(e))

with open('/root/logfile_git_fetch_cron.txt','a') as ff:
    ff.write('******** ' + str(datetime.datetime.now()) + '  ********' + '\n')
    for log in logs:
        ff.write(log)
    ff.write('\n')
# crontab -e has : 0 */8 * * * /usr/bin/python /root/automation_stuff/scripts/git_fetch_cron_job.py
