import datetime
import re
import os
import subprocess
import shlex

main_branch_pattern = re.compile(r"\d+\.\d+\.\d+")
patch_branch_pattern = re.compile(r"\d+\.\d+\.\d+-\d+p\d+")
all_branches = [i for i in os.listdir("/mnt/builds") if (re.fullmatch(main_branch_pattern, i) or re.fullmatch(patch_branch_pattern, i))]
all_branches += ["eng","webapp2-release1","webapp2-release2"]

all_branches = sorted(all_branches, reverse=True)

if os.path.isdir("/home/aviuser/workspace/avi-dev"):
    CWD = "/home/aviuser/workspace/avi-dev"
    FILE_PATH = "/home/aviuser/logfile_git_fetch_cron.txt"
elif os.path.isdir("/root/workspace/avi-dev"):
    CWD = "/root/workspace/avi-dev"
    FILE_PATH = "/root/logfile_git_fetch_cron.txt"


for branch in all_branches:
    
    with open(FILE_PATH, "a") as ff:
        try:
            if int(branch[:2])<20:
                continue
        except ValueError:
            pass
        try:
            ff.write('******** ' + str(datetime.datetime.now()) + '  ********\n')
            ff.write('git fetch -p -P origin %s, %s\n'%(branch,CWD))
            command = "git fetch -p -P origin %s"%(branch)
            #subprocess.run(shlex.split(command), stdout=ff, stderr=ff, cwd=CWD, check=True, timeout=120)
            result = subprocess.run(shlex.split(command), capture_output=True, text=True, cwd=CWD, check=True, timeout=120)
            ff.write(str(result.stdout))
            ff.write(str(result.stderr))
            ff.write("\n")
        except Exception as e:
            ff.write("ERROR !!!")
            ff.write(str(e))
            ff.write("\n")
# crontab -e has : 0 */8 * * * /usr/bin/python /root/automation_stuff/scripts/git_fetch_cron_job.py
