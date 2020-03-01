#!/usr/bin/env python
import shlex , subprocess, os

homedir = os.environ['HOME']
cmd = "find " + homedir + " -name .git"
#cmd = "find ./ -name .git"

proc = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE)
output = proc.stdout.read()
git_path = ''
for rec in output.split("\n"):
    if "avi-dev/.git" in rec:
        git_path = rec

file_precommit = os.path.join(git_path,"hooks/pre-commit")

if os.path.isfile(file_precommit):
    os.rename(file_precommit,file_precommit+".other")

repo_path = git_path.replace(".git","")
cmd = "flake8 --install-hook git"
subprocess.call(shlex.split(cmd),cwd=repo_path.encode('string_escape'))

########### install flake8 git hook to avi-dev repo in dev machine
