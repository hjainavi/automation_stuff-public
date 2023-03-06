import datetime
import re
import os
import subprocess
import shlex
import threading
from concurrent.futures import ThreadPoolExecutor
import threading
import time

main_branch_pattern = re.compile(r"\d+\.\d+\.\d+")
patch_branch_pattern = re.compile(r"\d+\.\d+\.\d+-\d+p\d+")
#all_branches = [i for i in os.listdir("/mnt/builds") if (re.fullmatch(main_branch_pattern, i) or re.fullmatch(patch_branch_pattern, i))]
all_branches = [i for i in os.listdir("/mnt/builds") if re.fullmatch(main_branch_pattern, i)]
all_branches = sorted(all_branches, reverse=True)
all_branches = ["eng"] + all_branches

if os.path.isdir("/home/aviuser/workspace/avi-dev"):
    CWD = "/home/aviuser/workspace/avi-dev"
    FILE_PATH = "/home/aviuser/logfile_git_fetch_cron.txt"
    FILE_PATH_ERROR = "/home/aviuser/logfile_git_fetch_cron_error.txt"

def fetch_branch(CWD_c,branch,file_path,file_path_error, lock, remote_fetch=False):
    ff = []
    ffe = []
    try:
        start = '******** ' + str(datetime.datetime.now()) + '  ********\n'
        ff.append(start)
        ff.append("current dir: %s\n"%(CWD_c))
        if remote_fetch:
            command = "git pull -p origin %s"%(branch)
        else:
            command = "git fetch -v -p -P origin %s:%s"%(branch,branch)
        ff.append(command+"\n")
        #subprocess.run(shlex.split(command), stdout=ff, stderr=ff, cwd=CWD, check=True, timeout=120)
        result = subprocess.run(shlex.split(command), capture_output=True, text=True, cwd=CWD_c, check=True, timeout=120)
        ff.append(str(result.stdout))
        ff.append(str(result.stderr))
        ff.append("\n")
    except Exception as e:
        #raise
        #import ipdb;ipdb.set_trace()
        ffe.append(start)
        ffe.append(command+"\n")
        ffe.append("ERROR !!!  ")
        if not hasattr(e,"stderr"):
            ffe.append(str(e)+"\n")
            if "refusing to fetch into branch" in str(e):
                cwd_c = "/home/aviuser/workspace/avi-dev"
                if "avi-dev" in str(e):
                    cwd_c = "/home/aviuser/workspace/avi-dev"
                if "dev-1" in str(e):
                    cwd_c = "/home/aviuser/workspace/dev-1"
                fetch_branch(cwd_c,branch,file_path,file_path_error, lock, True)
            if "bad object" in str(e) and "tags" in str(e):
                tag = str(e).split("\n")[0].split("/")[-1]
                command_1 = "git tag -d %s"%(tag)
                subprocess.run(shlex.split(command_1), capture_output=True, text=True, cwd=CWD_c, check=True, timeout=120)
                fetch_branch(CWD_c,branch,file_path,file_path_error, lock, False)
        if hasattr(e,"stderr"):
            ffe.append(str(e.stderr))
            
            if "refusing to fetch into branch" in str(e.stderr):
                cwd_c = "/home/aviuser/workspace/avi-dev"
                if "avi-dev" in str(e.stderr):
                    cwd_c = "/home/aviuser/workspace/avi-dev"
                if "dev-1" in str(e.stderr):
                    cwd_c = "/home/aviuser/workspace/dev-1"
                fetch_branch(cwd_c,branch,file_path,file_path_error, lock, True)
            if "bad object" in str(e.stderr) and "tags" in str(e.stderr):
                tag = str(e.stderr).split("\n")[0].split("/")[-1]
                command_1 = "git tag -d %s"%(tag)
                subprocess.run(shlex.split(command_1), capture_output=True, text=True, cwd=CWD_c, check=True, timeout=120)
                fetch_branch(CWD_c,branch,file_path,file_path_error, lock, False)
        #ffe.append(str(result.stdout))
        #ffe.append(str(result.stderr))
        ffe.append("\n")
    if not ffe:
        with lock:
            with open(file_path, "a") as f:
                for i in ff:
                    f.write(i)
    else:
        with lock:
            with open(file_path_error, "a") as f:
                for i in ffe:
                    f.write(i) 

lock = threading.Lock()
fetched_branches = []
for branch in all_branches:
    try:
        if int(branch[:2])<22:
            continue
    except ValueError:
        pass
    print(branch)
    fetched_branches.append(branch)

for branch in fetched_branches:
    fetch_branch(CWD, branch, FILE_PATH,FILE_PATH_ERROR, lock)


# crontab -e has : 0 */8 * * * /usr/bin/python3 /home/aviuser/automation_stuff/scripts/git_fetch_cron_job.py
