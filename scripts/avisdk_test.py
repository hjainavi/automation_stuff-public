from avi.sdk.avi_api import ApiSession
import ipdb

api = ApiSession.get_session("100.65.9.180", "admin", "avi123", tenant="admin")
vs_name = "test2"
resp = api.get("virtualservice?name=%s"%(vs_name))
resp_j = resp.json()
vs_uuid = resp_j['results'][0]['uuid']
se_uuid = resp_j['results'][0]['vip_runtime'][0]['se_list'][0]['se_ref'].split("/")[-1]
se_group_uuid = resp_j['results'][0]['se_group_ref'].split("/")[-1]
print(vs_uuid,se_uuid,se_group_uuid)
ipdb.set_trace()
resp = api.delete("serviceengine/%s"%(se_uuid))
if resp.status_code != 204:
    ipdb.set_trace()

resp = api.delete("serviceenginegroup/%s"%(se_group_uuid))
if resp.status_code != 204:
    ipdb.set_trace()




