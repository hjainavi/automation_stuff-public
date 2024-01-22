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
CWD = "/home/aviuser/workspace/avi-dev"

logging.basicConfig(filename=LOG_FILE_PATH,
                    filemode='a',
                    format='%(asctime)s.%(msecs)d %(name)s line.%(lineno)d %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.DEBUG)

log = logging.getLogger("gitFetch")
log.info("--------------- Starting Fetch -------------")
if not os.path.isdir(CWD):
    log.error("No such directory %s"%(CWD))
    exit(1)
main_branch_pattern = re.compile(r"\d+\.\d+\.\d+")
patch_branch_pattern = re.compile(r"\d+\.\d+\.\d+-\d+p\d+")
#all_branches = [i for i in os.listdir("/mnt/builds") if (re.fullmatch(main_branch_pattern, i) or re.fullmatch(patch_branch_pattern, i))]
all_branches = [i for i in os.listdir("/mnt/builds") if re.fullmatch(main_branch_pattern, i)]
all_branches = sorted(all_branches, reverse=True)


    
def fetch_branch(CWD_c, branch, remote=True):
    if remote:
        command = "git fetch -v origin %s"%(branch)
    else:
        command = "git fetch -v origin %s:%s"%(branch,branch)        
    log.info("Directory: %s"%(CWD_c))
    log.info("command : %s"%(command))
    try:
        result = subprocess.run(shlex.split(command), capture_output=True, text=True, cwd=CWD_c, check=True, timeout=600)
        if str(result.stdout) != "": log.info(str(result.stdout))
        if str(result.stderr) != "": log.info(str(result.stderr))
    except Exception as e:
        log.error(str(e))

def pull_branch_ff(CWD_c, branch):
    command = "git pull origin %s --ff-only"%(branch)
    log.info("Directory: %s"%(CWD_c))
    log.info("command : %s"%(command))
    try:
        result = subprocess.run(shlex.split(command), capture_output=True, text=True, cwd=CWD_c, check=True, timeout=600)
        if str(result.stdout) != "": log.info(str(result.stdout))
        if str(result.stderr) != "": log.info(str(result.stderr))
    except Exception as e:
        log.error(str(e))

def get_checked_out_branches(CWD_c):
    command = "git worktree list --porcelain"
    log.info("Directory: %s"%(CWD_c))
    log.info("command : %s"%(command))
    datas = {} # {'branch':dir}
    try:
        result = subprocess.run(shlex.split(command), capture_output=True, text=True, cwd=CWD_c, check=True, timeout=10)
        if str(result.stderr) != "":
            log.info("error")
            log.error(str(result.stderr))
            return datas
        res_out = result.stdout
        if str(res_out) != "":
            output_str = str(res_out)
            worktree = branch = ""
            for line in output_str.split("\n"):
                if 'worktree' in line:
                    worktree = line.split(" ")[-1]
                if 'branch' in line:
                    branch = line.split("/")[-1]
                if worktree != "" and branch != "":
                    datas[branch] = worktree
                    worktree = branch = ""
            log.info("Checked Out Branches %s"%(datas))
        
    except Exception as e:
        log.error(str(e))
    return datas

def pull_fetch_or_remote_fetch(checkout_datas, fetched_branches):
    remote_fetch_only = []
    pull_ff_only = {}
    direct_fetch_branches = [branch for branch in fetched_branches if str(branch) not in checkout_datas.keys()]
    pull_remote_fetch_branches = [branch for branch in fetched_branches if str(branch) in checkout_datas.keys()]
    if not pull_remote_fetch_branches:
        return pull_ff_only,direct_fetch_branches,remote_fetch_only
    command = "git status --porcelain"
    for branch,dir in checkout_datas.items():
        if branch not in fetched_branches:
            continue
        log.info("Directory: %s"%(dir))
        log.info("command : %s"%(command))
        try:
            result = subprocess.run(shlex.split(command), capture_output=True, text=True, cwd=dir, check=True, timeout=600)
            if str(result.stderr) != "":
                log.info(str(result.stderr))
                continue
            res_out = result.stdout
            if str(res_out) != "":
                if " M " in res_out or " D " in res_out:
                    remote_fetch_only.append(branch)
                else:
                    pull_ff_only[branch] = dir
            else:
                pull_ff_only[branch] = dir
        except Exception as e:
            log.error(str(e))
    log.info("Remote Fetch only %s"%(remote_fetch_only))
    log.info("Pull only branches %s"%(pull_ff_only.keys()))
    log.info("Direct fetch branches %s"%(direct_fetch_branches))
    return pull_ff_only,direct_fetch_branches,remote_fetch_only



#lock = threading.Lock()
fetched_branches = []
for branch in all_branches:
    try:
        if int(branch[:2])<23:
            continue
    except ValueError:
        pass
    fetched_branches.append(branch)

fetched_branches = ["eng","22.1.4","22.1.5","avi-photon-alb"] + fetched_branches
log.info("Fetching Branches: %s"%(fetched_branches))
checkout_datas = get_checked_out_branches(CWD)
#if not checkout_datas: exit(1)
pull_ff_only,direct_fetch_branches,remote_fetch_only = pull_fetch_or_remote_fetch(checkout_datas, fetched_branches)
if not pull_ff_only and not direct_fetch_branches and not remote_fetch_only: exit(1)
for branch in remote_fetch_only:
    fetch_branch(CWD, branch)
for branch,dir in pull_ff_only.items():
    pull_branch_ff(dir, branch)
for branch in direct_fetch_branches:
    fetch_branch(CWD, branch, remote=False)

log.info("--------------- Ending Fetch -------------\n\n\n")


# crontab -e has : 0 */3 * * * /usr/bin/python3 /home/aviuser/automation_stuff/scripts/git_fetch_cron_job.py


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