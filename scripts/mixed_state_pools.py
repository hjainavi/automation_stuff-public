#!/usr/bin/python3
import json
import argparse

# Create an ArgumentParser object
parser = argparse.ArgumentParser(description="Process Avi Networks configuration to find mixed state pools.")
# Add an argument for the filename
parser.add_argument("filename", help="Path to the Avi Networks configuration file (avi_config).")
# Parse the command-line arguments
args = parser.parse_args()

with open(args.filename, "r") as f:
    config = json.loads(f.read())
print("\n\n",args.filename)
pool_hostname_port_state = {}

for pool in config.get("Pool",[]):
    for server in pool.get("servers",[]):
        if server.get("resolve_server_by_dns",False):
            if not pool_hostname_port_state.get(pool["uuid"],False):
                pool_hostname_port_state[pool["uuid"]] = {}
            if not pool_hostname_port_state[pool["uuid"]].get("%s_%s"%(server["hostname"],server.get("port","None")), False):
                pool_hostname_port_state[pool["uuid"]]["%s_%s"%(server["hostname"],server.get("port","None"))] = str(server["enabled"])
            elif pool_hostname_port_state[pool["uuid"]].get("%s_%s"%(server["hostname"],server.get("port","None"))) == "False" and str(server["enabled"]) == "True":
                pool_hostname_port_state[pool["uuid"]]["%s_%s"%(server["hostname"],server.get("port","None"))] = "mixed_state"
            elif pool_hostname_port_state[pool["uuid"]].get("%s_%s"%(server["hostname"],server.get("port","None"))) == "True" and str(server["enabled"]) == "False":
                pool_hostname_port_state[pool["uuid"]]["%s_%s"%(server["hostname"],server.get("port","None"))] = "mixed_state"


mixed_state_pools = {}
if config.get("META",{}).get("version",""):
    mixed_state_pools["version"] = config.get("META",{}).get("version","")
if config.get("META",{}).get("cluster_uuid",""):
    mixed_state_pools["cluster_uuid"] = config.get("META",{}).get("cluster_uuid","")
found = False
for pool_uuid,value in pool_hostname_port_state.items():
    for hostname_port,state in value.items():
        if state == "mixed_state":
            if not mixed_state_pools.get(pool_uuid,False):
                mixed_state_pools[pool_uuid] = []
            mixed_state_pools[pool_uuid].append({"hostname":str(hostname_port.split("_")[0]), "port":str(hostname_port.split("_")[-1]), "state": str(state)})
            found = True
if not found:
    print("NO MIXED STATE POOLS FOUND")
else:
    pretty_json = json.dumps(mixed_state_pools, indent=4)
    print(pretty_json)

found = False
pool_hostname_port_other_mixed_fields = {}
for pool in config.get("Pool",[]):
    hostname_port = {}
    for server in pool.get("servers",[]):
        if not server.get("resolve_server_by_dns",False):
            continue
        server.pop("ip")
        server.pop("enabled")
        server.pop("discovered_networks")
        if not hostname_port.get("%s_%s"%(server["hostname"],server.get("port","None")),False):
            hostname_port["%s_%s"%(server["hostname"],server.get("port","None"))] = server
        elif server != hostname_port["%s_%s"%(server["hostname"],server.get("port","None"))]:
            if not pool_hostname_port_other_mixed_fields.get(pool["uuid"],False):
                pool_hostname_port_other_mixed_fields[pool["uuid"]] = {}
            if not pool_hostname_port_other_mixed_fields[pool["uuid"]].get("%s_%s"%(server["hostname"],server.get("port","None")),False):
                print(server)
                print(hostname_port["%s_%s"%(server["hostname"],server.get("port","None"))])
                pool_hostname_port_other_mixed_fields[pool["uuid"]]["%s_%s"%(server["hostname"],server.get("port","None"))] = "mixed_other_fields"
                found = True
        
if not found:
    print("NO MIXED OTHER FIELDS POOLS FOUND")
else:
    pretty_json = json.dumps(pool_hostname_port_other_mixed_fields, indent=4)
    print(pretty_json)        
            

        