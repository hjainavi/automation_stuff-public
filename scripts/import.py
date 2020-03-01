from avi.rest.view_utils import process_view_request
from permission.models import User
user = User.objects.get(name='admin')

imp_data =  {'configuration' :{"User": [
        {
            "access": [
                {
                "role_ref": "/api/role/?tenant=admin&name=Application-Operator",    
                "tenant_ref":"/api/tenant/?name=admin"
                }
            ],
            "is_superuser": True,
            "name": "token_normal_user_1",
            "password": "token_normal_user_1",
            "username": "token_normal_user_1"
        },
        {   
            "access": [
                {
                "role_ref": "/api/role/?tenant=admin&name=System-Admin",
                "tenant_ref":"/api/tenant/?name=admin"
                }
            ],
            "is_superuser": True,
            "name": "token_super_user_1",
            "password": "token_super_user_1",
            "username": "token_super_user_1"
        }

]
}
}


import_config = process_view_request('/api/configuration/import','POST',imp_data , user)
import pdb;pdb.set_trace()
names = ["token_normal_user_1","token_super_user_1"]
for name in names:

    import_config = process_view_request('/api/user?name=%s'%(name),'GET',{} , user).data['results'][0]
    uuid = import_config['uuid']
    import_config = process_view_request('/api/user/%s'%(uuid),'DELETE',{} , user)




