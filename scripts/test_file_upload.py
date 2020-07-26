import json
from requests_toolbelt import MultipartEncoder
from avi.sdk.avi_api import (ApiSession, ObjectNotFound, APIError, ApiResponse,
                             avi_timedelta, sessionDict,
                             AviMultipartUploadError)
from requests.packages import urllib3
import os, sys

login_info = {
        "controller_ip":"10.140.16.180",
        "username":"admin",
        "password":"avi123",
        "tenant":"admin",
        "api_version":"20.1.1"
        }

urllib3.disable_warnings()
gapi_version = '17.2.6'

file_path = sys.argv[1]
file_uri = "controller://hsmpackages"
controller_ip = login_info["controller_ip"]
username = login_info.get("username", "admin")
uri = "fileservice/hsmpackages?hsmtype=safenet"

print("Creating ne session")
api_session = ApiSession.get_session(controller_ip, username,
                login_info.get("password", "fr3sca$%^"),
                tenant=login_info.get("tenant", "admin"),
                tenant_uuid=login_info.get("tenant_uuid", None),
                api_version=login_info.get("api_version", gapi_version),
                verify=False)
api_session.timeout = 1000
api_session.retry_wait_time = 1
filename = os.path.basename(file_path)
with open(file_path, 'rb') as fd:
    file_dict = {
        "file" : (filename, fd, 'application/octet-stream'),
        "uri"  : file_uri
    }
    data = MultipartEncoder(file_dict)
    headers = {}
    headers['Content-Type'] = data.content_type
    headers['Connection'] = 'keep-alive'
    print('Upload file with valid session')
    resp = api_session.post(uri, headers=headers, data=data)
    assert resp.status_code < 300
    print("File upload successfull")



