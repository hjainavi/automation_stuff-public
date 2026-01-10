from avi.rest.view_utils import process_view_request
from permission.models import User
user = User.objects.get(name='admin')
from concurrent.futures import ThreadPoolExecutor
post_data =  {'name':'pool-test',
            'server_auto_scale':True}

y = 'y'
n = 'n'

create_p = input('create pools (y/n) ?\n')
delete_p = input('delete all pools (y/n) ?\n')

if create_p=='y':
    list_of_servers = []
    for i in range(1,101):
        for j in range(1,201):
            list_of_servers.append('20.20.%s.%s'%(i,j))
    error_list = []
    print list_of_servers
    with ThreadPoolExecutor(max_workers=20) as executor:
        for i in range(100):
            post_data = {'name':'pool-test-%s'%(i)}
            post_data['servers']=[]        
            for j in range(201):
                addr = list_of_servers.pop()
                server_data = {'ip':{'type':'V4','addr':addr},'hostname':addr}
                post_data['servers'].append(server_data)
            process_view_request('/api/pool','POST',post_data , user)
            #executor.submit(process_view_request,'/api/pool','POST',post_data , user)

if delete_p=='y':
    pools = process_view_request('/api/pool/?page_size=-1&fields=uuid',"GET",{},user)

    pool_uuids = [str(rec['uuid']) for rec in pools.data.get('results',[]) ]

    with ThreadPoolExecutor(max_workers=20) as executor:
        for uuid in pool_uuids:
            executor.submit(process_view_request,'/api/pool/%s'%(uuid),'DELETE',{} , user)



#import_config = process_view_request('/api/pool','POST',post_data , user)
#import pdb;pdb.set_trace()
#names = ["token_normal_user_1","token_super_user_1"]
#objects = [['pool','pool-test']]
#for obj in objects:
#    for name in obj[1:]:
#        del_obj = process_view_request('/api/%s?name=%s'%(obj[0],name),'GET',{} , user).data['results'][0]
#       uuid = del_obj['uuid']
#        del_obj_action = process_view_request('/api/%s/%s'%(obj[0],uuid),'DELETE',{} , user)




