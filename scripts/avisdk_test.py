from avi.sdk.avi_api import ApiSession
import ipdb

api = ApiSession.get_session("10.102.65.176", "admin", "avi123", tenant="admin")

data_pool = {"name":"pool-test"}

data = { "name":"abc",
    "trap_servers":[
        {
            "community":"12345",
            "ip_addr":{"addr":"1.1.1.1","type":"V4"}
        }
    ]
}

try:
    resp = api.post("pool",data=data_pool)
except:
    pass
ipdb.set_trace()
resp = api.delete_by_name("pool",data_pool["name"])
