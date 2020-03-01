from avi.rest.view_utils import process_view_request
from permission.models import User
user = User.objects.get(name='admin')

imp_data = {'configuration' :{
                "IpamDnsProviderProfile": [
                    {
                      "name": "internal-test-ipam",
                      "internal_profile": {
                            "usable_network_refs": [
                                "/api/network/?name=test-network"
                        ]
                      },
                      "type": "IPAMDNS_TYPE_INTERNAL"
                    }
                ],
                "Network":[{
                  "name": "test-network",
                  "tenant_ref":"/api/tenant/?name=t1"
                  }]
            }
        }


try:
    import_config = process_view_request('/api/configuration/import','POST',imp_data , user)
except:
    pass
import pdb;pdb.set_trace()
objects = [['ipamdnsproviderprofile','internal-test-ipam'],['network','test-network']]
for obj in objects:
    for name in obj[1:]:
        del_obj = process_view_request('/api/%s?name=%s'%(obj[0],name),'GET',{} , user).data['results']
        if not del_obj:continue
        else:del_obj=del_obj[0]
        uuid = del_obj['uuid']
        del_obj_action = process_view_request('/api/%s/%s'%(obj[0],uuid),'DELETE',{} , user)

