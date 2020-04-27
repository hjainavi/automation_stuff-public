from avi.sdk.avi_api import ApiSession
import argparse,json
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

_APP_KEY = '''
-----BEGIN RSA PRIVATE KEY-----
MIICWwIBAAKBgQCdcL7Kl+gcOo+ckZF6SWUxUKD5fqfwOupkh2Ova4xP6tzWiFOv
WNQx8Km3u7PjUGJ+T6Xw4IiRFf7xcZLcboXi2JbDR3ZNVRMiot5vmazLwiCqHBDc
Tb1uCaokzpjfFOza/HoX17uIRwLdygoZgamj90SurhLVmQ4c0HKvWO/NkwIDAQAB
AoGARgyO5wb1f/HSSeA+sQEM5AcyyC9BO1KLTVUr1jXsxPYDcfRP/5lvOBUS/ium
mwH+AKMheu379UmrF/PnWupV6Oi03akkFu+POOVdLOmRaZCmR0dqztEgKhL1WLeu
xek7T06CfocFqlQFH+BNzuOtT3u3NtkG8K0HvKL3eWRycFkCQQDMj9KJhagi+m2Q
UkmqfCADXDVp6YhfxEI9KQabwMmorShJPMq1He5XYkpVVXiKPyK3TytS20D+cQqp
zVXybIFNAkEAxQeYe2lacRZybmf98jmW8jUkBjLTrhFf0OYwmZ7sm216aGw35uen
JKIze+PTTbdeGMCupUqL9NqZp9WkTrIaXwJAGaN1CdN8rVWh4dLOdNW11XX7I9kn
RIl+m9fGgkL5g3Cgef1qkqS7uKwTEPrzbrBXE46SqYHddYaJhZq8yPOciQJAAr9y
XvY/LqiTe/qzTfeDpWkcUYHP9fOEFJPBRcMzpY9HT8GCnhPI/vfMJAQvZDwUcd/u
D5wUi5uo3PBb1EUjnQJAWWSl9Cj725zRz6PYS0eI6BIoba3AgzeckYCrXFZXNG9C
DIj95DypWiPntyrnVxS3ksBAFWOBePaTlW68xUFGyA==
-----END RSA PRIVATE KEY-----
'''
_APP_CERT = '''
-----BEGIN CERTIFICATE-----
MIID2DCCAsCgAwIBAgICEAAwDQYJKoZIhvcNAQELBQAwXTELMAkGA1UEBhMCSU4x
CzAJBgNVBAgMAktBMRgwFgYDVQQKDA9MT0dTVEFTSCBDQSBMVEQxDjAMBgNVBAsM
BUlOVEVSMRcwFQYDVQQDDA5sb2dzdGFzaC5pbnRlcjAeFw0xOTA3MTExMDE3NTda
Fw0zOTA4MDMxMDE3NTdaMGMxCzAJBgNVBAYTAklOMQswCQYDVQQIDAJLQTEcMBoG
A1UECgwTTE9HU1RBU0ggU0VSVkVSIExURDEPMA0GA1UECwwGU0VSVkVSMRgwFgYD
VQQDDA9sb2dzdGFzaC5zZXJ2ZXIwgZ8wDQYJKoZIhvcNAQEBBQADgY0AMIGJAoGB
AJ1wvsqX6Bw6j5yRkXpJZTFQoPl+p/A66mSHY69rjE/q3NaIU69Y1DHwqbe7s+NQ
Yn5PpfDgiJEV/vFxktxuheLYlsNHdk1VEyKi3m+ZrMvCIKocENxNvW4JqiTOmN8U
7Nr8ehfXu4hHAt3KChmBqaP3RK6uEtWZDhzQcq9Y782TAgMBAAGjggEeMIIBGjAJ
BgNVHRMEAjAAMBEGCWCGSAGG+EIBAQQEAwIGQDAzBglghkgBhvhCAQ0EJhYkT3Bl
blNTTCBHZW5lcmF0ZWQgU2VydmVyIENlcnRpZmljYXRlMB0GA1UdDgQWBBSdqX1o
IxjWvsHPdzwTyDgvsVP4zDCBgAYDVR0jBHkwd4AU1JlDPrmC03/aE603Kuikkx/S
9nqhW6RZMFcxCzAJBgNVBAYTAklOMQswCQYDVQQIDAJLQTEYMBYGA1UECgwPTE9H
U1RBU0ggQ0EgTFREMQswCQYDVQQLDAJDQTEUMBIGA1UEAwwLbG9nc3Rhc2guY2GC
AhAAMA4GA1UdDwEB/wQEAwIFoDATBgNVHSUEDDAKBggrBgEFBQcDATANBgkqhkiG
9w0BAQsFAAOCAQEAgziy/8pL215JYEwYci7NjevUSDGZNywv4F4XLLqQzD7HgijL
sGO0ewzxyioqf445/Epo4hd/JjD2q5uuXRyNjdKr73Cj7pfu4S9GPmrfg+S3r950
6n8gsuXslKda2ZkadcdsewC8pb8IEEtJyR3MpNQj8mt02b65ig0t5ksLbHeA1t9Q
5t/dwoAp9UiO+ua4FqLJJUs+LvqbC/7Zh1N8W6gKMDvYtDjvRSj2OUI3Rwvdl+73
EsrOKsu55vAKOiH0Jsel8qWSLInKRmy76TFAbdtYgA6+pDFifQeTECW+xQ+IqQlz
0RBd5QASagUN8lz3HIVi80jRljHVYCNsV26oFw==
-----END CERTIFICATE-----
'''
_INTERMEDIATE_CERT = '''
-----BEGIN CERTIFICATE-----
MIIDljCCAn6gAwIBAgICEAAwDQYJKoZIhvcNAQELBQAwVzELMAkGA1UEBhMCSU4x
CzAJBgNVBAgMAktBMRgwFgYDVQQKDA9MT0dTVEFTSCBDQSBMVEQxCzAJBgNVBAsM
AkNBMRQwEgYDVQQDDAtsb2dzdGFzaC5jYTAeFw0xOTA3MTExMDE3MzVaFw0zOTA4
MDQxMDE3MzVaMF0xCzAJBgNVBAYTAklOMQswCQYDVQQIDAJLQTEYMBYGA1UECgwP
TE9HU1RBU0ggQ0EgTFREMQ4wDAYDVQQLDAVJTlRFUjEXMBUGA1UEAwwObG9nc3Rh
c2guaW50ZXIwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDPLvuH5W0O
RZH+9bwXAjvF0liB78Yr9/dDvG+o5b0HR3HJIqypXRiNXRbSroxBSmMdnqAcuSwf
kp1YEM0PhYBSMAwsJbET8fNovq7VfN5Dd5NTszVveKPKfXr5r1oAeaNwY+/XGQnp
QZYCpa39av5KL2ikcLNNBjpsl+CSS3yi8PuP71aHaGhFXolfdovmQhcHrFKHQth9
NXVbVPlaHEbENTSL3fMuZxzXWoSmOUqUR0gN9V8GLNSSkPBJOaLMzR/GPcGZNYnA
syBulCBq7BoGDMMiO2klTaz6oWZoDg0d2VXHFbcnzqnmOCuSTYwzNPusVeYdSbNl
w0iT6BTTNjqlAgMBAAGjZjBkMB0GA1UdDgQWBBTUmUM+uYLTf9oTrTcq6KSTH9L2
ejAfBgNVHSMEGDAWgBQMtTxPfBTX26BTmtfbLMGpLy7HszASBgNVHRMBAf8ECDAG
AQH/AgEAMA4GA1UdDwEB/wQEAwIBhjANBgkqhkiG9w0BAQsFAAOCAQEAUsaH7ZMQ
z76ammzLbA8uQV0b1pPHPlAnhBr8irr9ZfazzFNcPhxyRqPIquCMwydM71Y/xYph
Snyc0lXiLZMOIGMf++MiXKSanWi8/tzt683J7TcwIRLrG9lY6KweT10bH5p0L9Ys
prkqvnj67sOOURMgL3vYS6bhI1qmRS7vwb0o3x1s3NeVZbMvl+iq1sEJmFqZKsiV
RfoMhCezcc8QtERBMTR/SJhjmpoxP6K91LHDmxRk9VdkauJGsQ/v7wU1DQfoEzti
GpeyHyGtMYgxZ8rCvUIwomK2DAzcvd6ZSIXMiFgkPE9W1ExRgqsAriq41bV/hFMK
RObiDNer3H5cqQ==
-----END CERTIFICATE-----
'''
_ROOT_CERT = '''
-----BEGIN CERTIFICATE-----
MIIDlDCCAnygAwIBAgIJAMttd5vrbYZPMA0GCSqGSIb3DQEBCwUAMFcxCzAJBgNV
BAYTAklOMQswCQYDVQQIDAJLQTEYMBYGA1UECgwPTE9HU1RBU0ggQ0EgTFREMQsw
CQYDVQQLDAJDQTEUMBIGA1UEAwwLbG9nc3Rhc2guY2EwHhcNMTkwNzExMTAxNzEx
WhcNMzkwNzA2MTAxNzExWjBXMQswCQYDVQQGEwJJTjELMAkGA1UECAwCS0ExGDAW
BgNVBAoMD0xPR1NUQVNIIENBIExURDELMAkGA1UECwwCQ0ExFDASBgNVBAMMC2xv
Z3N0YXNoLmNhMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAvVCyY7OF
e7FOjkBEw4bnbIkfuq0KpQKW2Y3WJNGs+CkSBG+cuK3Hb2ARc/PmWzbG9/CQdoVO
M4Lf2DrjaJ+es5zHd12Mxc/ezsh5+tMMSPCS+DMl3LJGfC56BJXJKZna/Wt8UMQO
QbkUgdFnK8IBDMptflkT6UZeyj46O6nHNO5BiuVHAx4VvEfantCIk1KphfBU1zM3
un6qoG+Ioj0CIa28AD+7M+aw0dNEb1XYKjUySe+771VlD0Js/bfmJ/UK9UYte44z
BOdcenTTP2FtkXPVHjy6T6w6iFGS/S0vv2aRFKevcN1G3GofC2FBapU2U3qPyVDF
krKH9ep9TLdErwIDAQABo2MwYTAdBgNVHQ4EFgQUDLU8T3wU19ugU5rX2yzBqS8u
x7MwHwYDVR0jBBgwFoAUDLU8T3wU19ugU5rX2yzBqS8ux7MwDwYDVR0TAQH/BAUw
AwEB/zAOBgNVHQ8BAf8EBAMCAYYwDQYJKoZIhvcNAQELBQADggEBAKR+GvhxT/Q4
wkx5wK1mfzuc31oKz8jP2jNBrAsATh7LhQr/hkQXmnHMypcR4LfbRMy6N6majNcC
VnWXXUMRToCMHeTelHu5J0kzPCL6Ld14BLUe1iiIktF4s7jUBRMT4YI8PIsNQcf6
KTaFz3byalucXd3GNofW1hsZdmyYZ1JqX/7/ZYNDA3RuwbcpAsYzrmhcZgNGTw8Y
wTU+NqsJUMlbaJwVay8obpEQZZsCbbJPLRonMwLE3zd9eurMyS7tT5aa7sJ/W8FD
1WCgswHGmH/aeqZhg0a3Lvin+bdeDviHSGGDnyGnzgFynIrUsAbF8OT1NHvDlUXe
bFwRY3Yfz7k=
-----END CERTIFICATE-----
'''

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--user', help='controller user',
                        default='admin')
    parser.add_argument('-p', '--password', help='controller user password',
                        default='avi123')
    parser.add_argument('-t', '--tenant', help='tenant name',
                        default='admin')
    parser.add_argument('-c', '--controller_ip', help='controller ip', required=True)
    parser.add_argument('-v', '--version', help='version', required=True)

    args = parser.parse_args()
    api = ApiSession.get_session(args.controller_ip, args.user, args.password,
                                 tenant=args.tenant,api_version=args.version)
    
    ssl_data = {
        "name": "test_app",
        "key": _APP_KEY,
        "certificate":{"certificate":_APP_CERT},
        "type": "SSL_CERTIFICATE_TYPE_VIRTUALSERVICE",
        "key_passphrase": "avi123"
    }
    post = api.post('sslkeyandcertificate', data = ssl_data)
    post_data_app1 =  json.loads(post.text)
    print post_data_app1['name']
    print post_data_app1['uuid']

    ssl_data = {
        "name": "test_intermediate",
        "type": "SSL_CERTIFICATE_TYPE_CA",
        "certificate":{"certificate":_INTERMEDIATE_CERT}
    }
    post = api.post('sslkeyandcertificate', data = ssl_data)
    post_data_int1 =  json.loads(post.text)
    print post_data_int1['name']
    print post_data_int1['uuid']

    ssl_data = {
        "name": "test_root",
        "type": "SSL_CERTIFICATE_TYPE_CA",
        "certificate":{"certificate":_ROOT_CERT}
    }
    post = api.post('sslkeyandcertificate', data = ssl_data)
    post_data_ca =  json.loads(post.text)
    print post_data_ca['name']
    print post_data_ca['uuid']

    import pdb;pdb.set_trace()
    api.delete('sslkeyandcertificate/%s/?force_delete=True'%(post_data_ca['uuid']))
   
    #import ipdb;ipdb.set_trace()
    api.delete('sslkeyandcertificate/%s/?force_delete=True'%(post_data_int1['uuid']))


