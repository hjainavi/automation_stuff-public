from avi.sdk.avi_api import ApiSession
import ipdb
VCENTER_IP = "wdc-02-vc20.oc.vmware.com"
VCENTER_USER = "aviuser1"
VCENTER_PASSWORD = "AviUser1234!."
VCENTER_DATACENTER_NAME = "blr-01-vc13"
VCENTER_MANAGEMENT_NETWORK = "/api/vimgrnwruntime/?name=vxw-dvs-34-virtualwire-3-sid-2200002-wdc-02-vc20-avi-mgmt"

api = ApiSession.get_session("100.65.9.180", "admin", "avi123", tenant="admin", api_version="30.1.2")
cloud_new_data = {
    "name": "test1",
    "tenant_ref": "/api/tenant/admin",
    "dhcp_enabled":True,
        "vtype":"CLOUD_VCENTER",
        "vcenter_configuration":{
            "privilege": "WRITE_ACCESS",
            "username": VCENTER_USER,
            "vcenter_url": VCENTER_IP,
            "password": VCENTER_PASSWORD,
            "datacenter": VCENTER_DATACENTER_NAME,
            "use_content_lib": False
        }
}
resp = api.post("cloud",cloud_new_data)
if resp.status_code != 201:
    print(resp.content)
    raise Exception()

resp = api.get("cloud?name=test1")
if resp.status_code != 200:
    print(resp.content)
    raise Exception()

resp_j = resp.json()
cloud_data = resp_j['results'][0]
cloud_data["vcenter_configuration"]["management_network"] = VCENTER_MANAGEMENT_NETWORK

resp = api.put("cloud/%s"%(cloud_data['uuid']),cloud_data)
if resp.status_code != 200:
    print(resp.content)
    raise Exception()





