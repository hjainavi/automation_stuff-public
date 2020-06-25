from avi.sdk.avi_api import ApiSession
import argparse, json
import urllib3
urllib3.disable_warnings()
import ipdb

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--user', help='controller user',
                        default='admin')
    parser.add_argument('-p', '--password', help='controller user password',
                        default='avi123')
    parser.add_argument('-t', '--tenant', help='tenant name',
                        default='admin')
    parser.add_argument('-c', '--controller_ip', help='controller ip')
    parser.add_argument('-v', '--version', help='controller ip')

    args = parser.parse_args()
    api = ApiSession.get_session(args.controller_ip, args.user, args.password,
                                 tenant=args.tenant,api_version=args.version)
    
    #create vrfcontext
    vrf_json = {'name':'shared-vip-vrf','uuid':'shared-vip-vrf'}
    posting = api.post('vrfcontext',data=vrf_json)
    try:
        posting.raise_for_status()
    except:
        print (posting.text)
        ipdb.set_trace()
    
    
    #create network
    network_json =  {'configured_subnets': [
                {'prefix': {
                    'ip_addr': {'addr': '1.1.1.0','type': 'V4'},
                    'mask': 24},
                'static_ranges': [{
                                'begin': {'addr': '1.1.1.100','type': 'V4'},
                                'end': {'addr': '1.1.1.200','type': 'V4'}}]}],
                'name': 'shared_vip_network',
                'uuid': 'shared_vip_network'}
    
    posting = api.post('network',data=network_json)
    try:
        posting.raise_for_status()
    except:
        print (posting.text)
        ipdb.set_trace()


    #create ipam
    ipam_data = {
            "name": "shared_vip_operations_ipam", 
            "type": "IPAMDNS_TYPE_INTERNAL", 
            "internal_profile": {
                "usable_network_refs": ["/api/network/?name=shared_vip_network"], 
                "dns_service_domain": []}
            }
    
    
    posting = api.post('ipamdnsproviderprofile',data=ipam_data)
    try:
        posting.raise_for_status()
    except:
        print (posting.text)
        ipdb.set_trace()
    
    #put ipam in cloud
    cloud_obj = api.get('cloud?name=Default-Cloud')
    cloud_data = json.loads(cloud_obj.text)['results'][0]
    cloud_uuid = cloud_data['uuid']
    cloud_data['ipam_provider_ref'] = '/api/ipamdnsproviderprofile?name=shared_vip_operations_ipam'
    cloud_put = api.put('cloud/%s'%(cloud_uuid), data=cloud_data)
    try:
        cloud_put.raise_for_status()
    except:
        print (cloud_put.text)
        ipdb.set_trace()
    
    #create vsvip
    vsvip_data = {
            "name": "vsvip_auto_allocation-1", 
            "uuid": "vsvip_auto_allocation-1", 
            "dns_info": [{"fqdn": "autoallocate1.avi.local", "type": "DNS_RECORD_A"}], 
            "vrf_context_ref": "/api/vrfcontext/?name=shared-vip-vrf", 
            "vip": [{"auto_allocate_ip": True, "avi_allocated_vip": True}], 
            "ipam_network_subnet": {
                "network_ref": "/api/network/?name=shared_vip_network", 
                "subnet": {
                    "mask": 24, 
                    "ip_addr": {"addr": "1.1.1.0", "type": "V4"}
                    }
                }
            }
    
    posting = api.post('vsvip',data=vsvip_data)
    try:
        posting.raise_for_status()
    except:
        print (posting.text)
        ipdb.set_trace()

    ##############################################################
    '''
    # delete vsvip
    vsvip_obj = api.get('vsvip?name=vsvip_auto_allocation-1')
    vsvip_data = json.loads(vsvip_obj.text)['results'][0]
    vsvip_uuid = vsvip_data['uuid']
    deleting = api.delete('vsvip/%s'%(vsvip_uuid))
    try:
        deleting.raise_for_status()
    except:
        print (deleting.text)
        ipdb.set_trace()
    '''
    
    # remove ipam in cloud
    cloud_obj = api.get('cloud?name=Default-Cloud')
    cloud_data = json.loads(cloud_obj.text)['results'][0]
    cloud_uuid = cloud_data['uuid']
    cloud_data.pop("ipam_provider_ref")
    cloud_put = api.put('cloud/%s'%(cloud_uuid), data=cloud_data)
    try:
        cloud_put.raise_for_status()
    except:
        print (deleting.text)
        ipdb.set_trace()
    
    
    # delete ipam
    ipam_obj = api.get('ipamdnsproviderprofile?name=shared_vip_operations_ipam')
    ipam_data = json.loads(ipam_obj.text)['results'][0]
    ipam_uuid = ipam_data['uuid']
    deleting = api.delete('ipamdnsproviderprofile/%s'%(ipam_uuid))
    try:
        deleting.raise_for_status()
    except:
        print (deleting.text)
        ipdb.set_trace()

    # delete network
    network_obj = api.get('network?name=shared_vip_network')
    network_data = json.loads(network_obj.text)['results'][0]
    network_uuid = network_data['uuid']
    #deleting = api.delete('network/%s?force_delete'%(network_uuid))
    deleting = api.delete('network/%s'%(network_uuid))
    try:
        deleting.raise_for_status()
    except:
        print (deleting.text)
    
    
    # delete vsvip
    vsvip_obj = api.get('vsvip?name=vsvip_auto_allocation-1')
    vsvip_data = json.loads(vsvip_obj.text)['results'][0]
    vsvip_uuid = vsvip_data['uuid']
    deleting = api.delete('vsvip/%s'%(vsvip_uuid))
    try:
        deleting.raise_for_status()
    except:
        print (deleting.text)
        ipdb.set_trace()


    # delete network
    network_obj = api.get('network?name=shared_vip_network')
    network_data = json.loads(network_obj.text)['results'][0]
    network_uuid = network_data['uuid']
    #deleting = api.delete('network/%s?force_delete'%(network_uuid))
    deleting = api.delete('network/%s'%(network_uuid))
    try:
        deleting.raise_for_status()
    except:
        print (deleting.text)
    
    # delete vrf
    vrf_obj = api.get('vrfcontext?name=shared-vip-vrf')
    vrf_data = json.loads(vrf_obj.text)['results'][0]
    vrf_uuid = vrf_data['uuid']
    deleting = api.delete('vrfcontext/%s'%(vrf_uuid))
    try:
        deleting.raise_for_status()
    except:
        print (deleting.text)
        ipdb.set_trace()

    print ("doing a force_delete of the network")
    deleting = api.delete('network/%s?force_delete'%(network_uuid))

