from avi.rest.view_utils import process_view_request
from permission.models import User
user = User.objects.get(name='admin')


sys1 = process_view_request('/api/systemconfiguration','GET',{},user)
put_data = sys1.data
put_data['snmp_configuration']['community']="abcde"
sys1_put = process_view_request('/api/systemconfiguration','PUT',put_data , user)


