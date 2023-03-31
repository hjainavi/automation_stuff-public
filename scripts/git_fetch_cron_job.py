import datetime
import re
import os
import subprocess
import shlex
import threading
from concurrent.futures import ThreadPoolExecutor
import threading
import time
import logging

LOG_FILE_PATH = "/home/aviuser/logfile_git_fetch_cron.txt"
logging.basicConfig(filename=LOG_FILE_PATH,
                    filemode='a',
                    format='%(asctime)s.%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.DEBUG)

log = logging.getLogger("gitFetch")
log.info("--------------- Starting Fetch -------------")
main_branch_pattern = re.compile(r"\d+\.\d+\.\d+")
patch_branch_pattern = re.compile(r"\d+\.\d+\.\d+-\d+p\d+")
#all_branches = [i for i in os.listdir("/mnt/builds") if (re.fullmatch(main_branch_pattern, i) or re.fullmatch(patch_branch_pattern, i))]
all_branches = [i for i in os.listdir("/mnt/builds") if re.fullmatch(main_branch_pattern, i)]
all_branches = sorted(all_branches, reverse=True)

if os.path.isdir("/home/aviuser/workspace/avi-dev"):
    CWD = "/home/aviuser/workspace/avi-dev"
    
def fetch_to_remote(CWD_c, branch):
    #command = "git fetch -v -p -P origin %s"%(branch)
    command = "git fetch -v origin %s"%(branch)
    log.info("Directory: %s"%(CWD_c))
    log.info("command : %s"%(command))
    try:
        result = subprocess.run(shlex.split(command), capture_output=True, text=True, cwd=CWD_c, check=True, timeout=600)
        if str(result.stdout) != "": log.info(str(result.stdout))
        if str(result.stderr) != "": log.info(str(result.stderr))
    except Exception as e:
        log.error(str(e))

#lock = threading.Lock()
fetched_branches = []
for branch in all_branches:
    try:
        if int(branch[:2])<22:
            continue
    except ValueError:
        pass
    fetched_branches.append(branch)

fetched_branches = ["AV-173613_21.1.7","AV-173613_22.1.4","AV-173613_30.1.1","AV-173613_eng","eng","21.1.7"] + fetched_branches
log.info("Fetching Branches: %s"%(fetched_branches))
for branch in fetched_branches:
    fetch_to_remote(CWD, branch)
log.info("--------------- Ending Fetch -------------\n\n\n")


# crontab -e has : 0 */8 * * * /usr/bin/python3 /home/aviuser/automation_stuff/scripts/git_fetch_cron_job.py


"""
def fetch_branch(CWD_c,branch, remote_fetch=False):
    try:
        start = '******** ' + str(datetime.datetime.now()) + '  ********\n'
        FF.append(start)
        FF.append("current dir: %s\n"%(CWD_c))
        if remote_fetch:
            command = "git pull -p origin %s"%(branch)
        else:
            command = "git fetch -v -p -P origin %s:%s"%(branch,branch)
        FF.append(command+"\n")
        #subprocess.run(shlex.split(command), stdout=FF, stderr=FF, cwd=CWD, check=True, timeout=120)
        result = subprocess.run(shlex.split(command), capture_output=True, text=True, cwd=CWD_c, check=True, timeout=120)
        FF.append(str(result.stdout))
        FF.append(str(result.stderr))
        FF.append("\n")
    except Exception as e:
        #raise
        #import ipdb;ipdb.set_trace()
        FF.append("ERROR !!! start ---- ")
        FF.append(start)
        FF.append(command+"\n")
        if not hasattr(e,"stderr"):
            FF.append(str(e)+"\n")
            if "refusing to fetch into branch" in str(e):
                cwd_c = "/home/aviuser/workspace/avi-dev"
                if "avi-dev" in str(e):
                    cwd_c = "/home/aviuser/workspace/avi-dev"
                if "dev-1" in str(e):
                    cwd_c = "/home/aviuser/workspace/dev-1"
                fetch_branch(cwd_c,branch, True)
            if "bad object" in str(e) and "tags" in str(e):
                tag = str(e).split("\n")[0].split("/")[-1]
                command_1 = "git tag -d %s"%(tag)
                subprocess.run(shlex.split(command_1), capture_output=True, text=True, cwd=CWD_c, check=True, timeout=120)
                fetch_branch(CWD_c,branch, False)
        if hasattr(e,"stderr"):
            FF.append(str(e.stderr))
            
            if "refusing to fetch into branch" in str(e.stderr):
                cwd_c = False
                if "avi-dev" in str(e.stderr):
                    cwd_c = "/home/aviuser/workspace/avi-dev"
                if "dev-1" in str(e.stderr):
                    cwd_c = "/home/aviuser/workspace/dev-1"
                if "dev-2" in str(e.stderr):
                    cwd_c = "/home/aviuser/workspace/dev-2"
                if cwd_c:
                    fetch_branch(cwd_c,branch, True)
            if "bad object" in str(e.stderr) and "tags" in str(e.stderr):
                tag = str(e.stderr).split("\n")[0].split("/")[-1]
                command_1 = "git tag -d %s"%(tag)
                subprocess.run(shlex.split(command_1), capture_output=True, text=True, cwd=CWD_c, check=True, timeout=120)
                fetch_branch(CWD_c,branch, False)
        #FF.append(str(result.stdout))
        #FF.append(str(result.stderr))
        FF.append("Error End !!! ---- \n")
"""