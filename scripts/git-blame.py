#!/usr/bin/env python3

import subprocess
import os
import shlex
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
 

PATH = "/home/aviuser/workspace/dev-2/go/src/avi/"
EXCLUDE_TEST_DIRS = ["controller/cloudconnector", "controller/octavius/checks"]
AUTHOR_LIST = ['Satyajit Panda', 'lngeorge', 'Santosh Sharma',  'satyajitvmw',  'Anjali Raj',  'Adi',  'obineeta', 'Nikhil Kumar Yadav',  'chitr',  'Gregory Cox', 'Niveditha M', 'Sooraj Tom','Priya Koshta', 'Harsh Jain',   'Tilak Bisht', 'Suraj S Sawant',  'Bineeta Oram',  'Abhishek Kumar', 'Libin N George',  'Mohit Singh Panwar', 'Sushrut Deshpande',  'harsh jain', 'Satvik Jagannath']
AUTHOR_LIST = ["b1zantine"]

def get_all_go_test_files(path=PATH, only_test=True):
    go_test_files_full_path = []
    for (root,dirs,files) in os.walk(path, topdown=True):
        for filename in files:
            if only_test:
                if "_test.go" in filename:
                    full_path = (root,filename)
                    exclude = False
                    for i in EXCLUDE_TEST_DIRS:
                        if i in full_path[0]:
                            exclude=True
                            break
                    if not exclude:
                        go_test_files_full_path.append(full_path)
            else:
                go_test_files_full_path.append((root,filename))

    return go_test_files_full_path

def get_git_blame_author(dir,filename):
    cmd = "/home/aviuser/automation_stuff/scripts/git_blame.sh %s %s"%(dir,filename)
    try:
        output = subprocess.check_output(shlex.split(cmd),text=True)
        return output,dir,filename
    except subprocess.CalledProcessError as e:
        print(e.output)
        raise
    
def get_test_files_with_authors():
    go_test_files_full_path = get_all_go_test_files()
    test_files_to_add = []
    test_files_excluded = []
    with ThreadPoolExecutor(20) as executor:
        # submit tasks and collect futures
        futures = [executor.submit(get_git_blame_author, dir, filename) for dir,filename in go_test_files_full_path]
        # process task results as they are available
        for future in as_completed(futures):
            # retrieve the result
            unique_author = set()
            value,dir,filename = future.result()
            if "\n" in value:
                for l in value.split("\n"):
                    author = l.strip().split("author ")[-1]
                    unique_author.add(author)
            else:
                author = value.strip().split("author ")[-1]
                unique_author.add(author)
            found = False
            for aa in AUTHOR_LIST:
                if aa in list(unique_author):
                    test_files_to_add.append((os.path.join(dir,filename),list(unique_author)))
                    found = True
                    break
            if not found:
                test_files_excluded.append((os.path.join(dir,filename),list(unique_author)))
        
    return test_files_to_add, test_files_excluded

added,excluded = get_test_files_with_authors()
print("files added ============= ")
for i in added:
    print(i[0])
    print(i[1])

'''
print("files excluded ====================== ")
for i in excluded:
    print(i[0])
    print(i[1])
'''