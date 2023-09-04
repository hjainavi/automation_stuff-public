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


CWD = "/home/aviuser/workspace/avi-dev"

    
def fetch_all_branches(CWD_c):
    command = "git branch -l"       
    print("Directory: %s"%(CWD_c))
    print("command : %s"%(command))
    branches = []
    try:
        result = subprocess.run(shlex.split(command), capture_output=True, text=True, cwd=CWD_c, check=True, timeout=600)
        if str(result.stderr) != "": 
            raise Exception(str(result.stderr))
        if str(result.stdout) != "":
            branches_str = str(result.stdout).split("\n")
            branches_str = [i.strip() for i in branches_str if (("HEAD" not in i) and (i != ""))]
            return branches_str
    except Exception as e:
        print(str(e))

def delete_branches(CWD_c, branches):
    final_delete_branches = []
    for branch in branches:
        if "AV" in branch:
            final_delete_branches.append(branch)
        else:
            delete = input("Delete branch %s ? [Y/N] : "%(branch))
            if delete.lower() == "y":
                final_delete_branches.append(branch)


    print("\n\n List of branches to be deleted locally:")
    for i in final_delete_branches:
        print(i)
    final_ask = input("Do you want to delete these branches ? [Y/N]: ")
    if final_ask.lower() != "y":
        return

    for branch in final_delete_branches:
        command_1 = "git branch -D %s"%(branch)
        print("Directory: %s"%(CWD_c))
        print("command : %s"%(command_1))
        try:
            result = subprocess.run(shlex.split(command_1), capture_output=True, text=True, cwd=CWD_c, check=True, timeout=600)
            if str(result.stdout) != "": print(str(result.stdout))
            if str(result.stderr) != "": print(str(result.stderr))
        except Exception as e:
            print(str(e))
        
        command_2 = "git branch -dr origin/%s"%(branch)
        print("Directory: %s"%(CWD_c))
        print("command : %s"%(command_2))
        try:
            result = subprocess.run(shlex.split(command_2), capture_output=True, text=True, cwd=CWD_c, check=True, timeout=600)
            if str(result.stdout) != "": print(str(result.stdout))
            if str(result.stderr) != "": print(str(result.stderr))
        except Exception as e:
            print(str(e))

branches = fetch_all_branches(CWD)
delete_branches(CWD, branches)