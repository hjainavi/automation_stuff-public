from __future__ import unicode_literals
from prompt_toolkit import prompt
import os

home_folder = os.getenv("HOME")
FILE_DIR = os.path.join(home_folder,".config")
FILE_PATH = os.path.join(home_folder,".config","vsphere_profiles.json")

class Profiles_Vcenter():
    #Profiles_Vcenter.create_profile_dir_and_file()
    def __init__(self):
        self.create_profile_dir_and_file()
    
    def create_profile_dir_and_file(self):
        try:
            os.makedir(FILE_DIR)
        except Exception as e:
            pass

        if not os.path.exists(FILE_PATH):
            with open(FILE_PATH,'w') as ff:
                pass


