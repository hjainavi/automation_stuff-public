if __name__ != "__main__":
    sys.exit(0)

import sys, os
import django
from django.conf import settings
from django.apps import apps

print ("# Script to delete alerts causing upgrade issues")
    
os.environ['PYTHONPATH'] = '/opt/avi/python/lib:/opt/avi/python/bin/portal'
os.environ['DJANGO_SETTINGS_MODULE'] = 'portal.settings_local'
sys.path.append("/opt/avi/python/bin/portal")
if not apps.ready and not settings.configured:
    django.setup()

obj_type_list = ["BACKUP",
        "CONTROLLERLICENSE",
        "CONTROLLERPORTALREGISTRATION",
        "FLOATINGIPSUBNET",
        "GSLBSITE",
        "GSLBTHIRDPARTYSITE",
        "JOBENTRY",
        "LICENSEINFO",
        "LICENSELEDGERDETAILS",
        "LICENSESTATUS",
        "LOGCONTROLLERMAPPING",
        "OBJECTACCESSPOLICY",
        "SCPOOLSERVERSTATEINFO",
        "SCVSSTATEINFO",
        "SECURECHANNELAVAILABLELOCALIPS",
        "SECURECHANNELTOKEN",
        "SECURITYMANAGERDATA",
        "STATEDIFFSNAPSHOT",
        "SYSTEMDEFAULTOBJECT",
        "UPGRADESTATUSSUMMARY",
        "VIDCINFO",
        "VIPGNAMEINFO"]



from api.models import Alert
from avi.infrastructure.db_transaction import db_transaction

all_alerts = Alert.objects.all()
delete_uuids = []
for alert in all_alerts:
    json_data = alert.json_data
    if len(json_data.get("events",[])) == 0:
        continue
    for event in json_data["events"]:
        if event.get("obj_type","None") in obj_type_list:
            delete_uuids.append(alert.uuid)

delete_uuids = list(set(delete_uuids))

@db_transaction
def delete_alerts(delete_uuids=[]):
    for uuid in delete_uuids:
        try:
            Alert.objects.get(uuid=uuid).delete()
            print("Deleted Alert %s"%(uuid))
        except Exception as e:
            print("Error while delete Alert %s"%(uuid))
            print(str(e))

delete_alerts(delete_uuids)
sys.exit(0)


