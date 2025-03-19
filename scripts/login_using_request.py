import requests
import json
import ipaddress

def generate_ips_in_range(start_ip, num_ips):
    
    try:
        start = ipaddress.ip_address(start_ip)
    except ValueError:
        print(f"Invalid start IP address: {start_ip}")
        return []

    ips = []
    for i in range(num_ips):
        ips.append(str(start + i))
    return ips

# Generate 2000 IP addresses starting from 192.168.1.1
start_ip = "192.168.1.1"
num_ips_to_generate = 1990
ip_addresses = generate_ips_in_range(start_ip, num_ips_to_generate)
servers = []
for ip in ip_addresses:
    servers.append(
        {
            "enabled":True,
            "hostname": str(ip),
            "ip": {
                "addr": str(ip),
                "type": "V4"
            }
        }
    )

print(ip_addresses)

url = "https://100.65.11.178/api/pool/pool-59d81884-8d6a-43e8-be97-696ccc06b2f5"

payload = ""
headers = {
  'X-AVI-VERSION': '22.1.5',
  'Content-Type': 'application/json',
  'X-CSRFToken': 'YhUQJt09CAqzDQ4apxpfZslD789aPnXW',
  'Referer': 'https://100.65.11.178/',
  'X-AVI-TENANT': 'admin',
  'Authorization': 'Basic YWRtaW46YXZpMTIz',
  'Cookie': 'avi-sessionid=p0lqt5ivwgxkf5by4z3grmgdmf2wfapu; csrftoken=YhUQJt09CAqzDQ4apxpfZslD789aPnXW; sessionid=p0lqt5ivwgxkf5by4z3grmgdmf2wfapu'
}

response = requests.request("GET", url, headers=headers, data=payload, verify=False)

payload = json.loads(response.text)
#payload["servers"] = payload["servers"] + servers
for server in payload["servers"]:
    if "192.168" in server["ip"]["addr"]:
        server["enabled"] = False

payload = json.dumps(payload)
response = requests.request("PUT", url, headers=headers, data=payload, verify=False)

print(response.text)



