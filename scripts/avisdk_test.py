from avi.sdk.avi_api import ApiSession
import ipdb

api = ApiSession.get_session("100.65.9.177", "admin", "admin", tenant="admin")

resp = api.get("cloud")
api.