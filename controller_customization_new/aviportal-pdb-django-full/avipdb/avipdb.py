import os, sys
import ipdb, inspect
import pdb

def set_trace(key=None):
    pdbtype = os.environ.get('AVI_PDB_FLAG')
    pdbkey = os.environ.get('AVI_PDB_KEY')
    if pdbkey == "-1":
        key = "-1" 
    if pdbtype == "pdb" and pdbkey == key:
        return pdb.Pdb().set_trace(sys._getframe().f_back)
    elif pdbtype == "ipdb" and pdbkey == key:
        return ipdb.set_trace(inspect.currentframe().f_back)
    else:
        print "IN AVIPDB PASS"
