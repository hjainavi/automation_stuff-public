from avi.rest.view_utils import process_view_request
from permission.models import User
from avi.util.cluster_info import get_controller_version
import os, subprocess, sys, shlex

import ipdb;ipdb.set_trace()

path1 = "/root/controller_customization_new/aviportal-pdb-django-full/change-conf.py"
if os.path.exists(path1):
    cmd = "python3 %s change_path_only"%(path1)
    print("run below command and re execute manage.py shell")
    print(cmd)


os.environ["AVI_PDB_FLAG"]="ipdb"
os.environ["AVI_PDB_KEY"]="gslb"

user = User.objects.get(name='test1')
custom_view_kwargs = {'version': get_controller_version()}
api = "/api/gslbservice/gslbservice-c8bc4e69-de04-442b-bee8-657a1f876da8"

response = process_view_request(api, "GET", None, user, custom_view_kwargs=custom_view_kwargs)

data = response.data


print(response.data)