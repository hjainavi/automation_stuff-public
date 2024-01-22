#!/bin/bash

cd /home/aviuser/workspace/avi-dev
git gc -q
git prune

# 0 */3 * * * /usr/bin/python3 /home/aviuser/automation_stuff/scripts/git_fetch_cron_job.py
# 0 */23 * * * /home/aviuser/automation_stuff/scripts/git_gc_cron_job.sh