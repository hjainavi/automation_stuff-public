
############################################################################
#
# AVI CONFIDENTIAL
# __________________
#
# [2013] - [2018] Avi Networks Incorporated
# All Rights Reserved.
#
# NOTICE: All information contained herein is, and remains the property
# of Avi Networks Incorporated and its suppliers, if any. The intellectual
# and technical concepts contained herein are proprietary to Avi Networks
# Incorporated, and its suppliers and are covered by U.S. and Foreign
# Patents, patents in process, and are protected by trade secret or
# copyright law, and other laws. Dissemination of this information or
# reproduction of this material is strictly forbidden unless prior written
# permission is obtained from Avi Networks Incorporated.
###

import unittest
import os
import time
import shlex 
import subprocess32 as subprocess

from datetime import datetime, timedelta
from django.db import transaction
from api.models import SchedulerSerializer, BackupConfigurationSerializer
from api.models_scheduler import (Scheduler, BackupConfiguration)
from api.models_backup import Backup
from avi.util.cluster_info import management_ip
from avi.upgrade.upgrade_utils import wait_until_cluster_ready_external

class SchedulerTestCase(unittest.TestCase):
    def setUp(self):
        subprocess.call(shlex.split('service ntp stop'))
        subprocess.call(shlex.split('date -s "+9min"'))
        time.sleep(10)
        current_node = management_ip()
        wait_until_cluster_ready_external(current_node, max_wait=15*60)

    @transaction.atomic
    def create_scheduler_with_backup_config(self, frequency, frequency_unit, run_mode, scheduler_action, **timeargs):
        backup_config = {
            'name' : 'test-backupconfig',
            'save_local': True,
            'maximum_backups_stored': 4,
            'tenant_ref': u'/api/tenant/admin', 
            }
        backupconfig_ser = BackupConfigurationSerializer(data = backup_config)
        if backupconfig_ser.is_valid():
            backupconfig_ser.save()
        if run_mode == 'RUN_MODE_PERIODIC':
            scheduler_data = {
                'enabled': True,
                'backup_config_ref': '/api/backupconfiguration?name=test-backupconfig',
                'frequency': frequency,
                'frequency_unit': frequency_unit,
                'run_mode': run_mode,
                'scheduler_action': scheduler_action,
                'start_date_time': str(datetime.now()),
                'tenant_ref': u'/api/tenant/admin', 
                'name' : 'test-scheduler'
                }
        elif run_mode == 'RUN_MODE_NOW':
            scheduler_data = {
                'enabled': True,
                'backup_config_ref': '/api/backupconfiguration?name=test-backupconfig',
                'run_mode': run_mode,
                'scheduler_action': scheduler_action,
                'start_date_time': str(datetime.now()),
                'tenant_ref': u'/api/tenant/admin', 
                'name' : 'test-scheduler'
                }
        elif run_mode == 'RUN_MODE_AT':
            scheduler_data = {
                'enabled': True,
                'backup_config_ref': '/api/backupconfiguration?name=test-backupconfig',
                'run_mode': run_mode,
                'scheduler_action': scheduler_action,
                'start_date_time': str(datetime.now()+timedelta(**timeargs)),
                'tenant_ref': u'/api/tenant/admin', 
                'name' : 'test-scheduler'
                }
        ser = SchedulerSerializer(data=scheduler_data)
        if ser.is_valid():
            ser.save()

    def check_backups(self, backups):
        print "checking backups"
        for backup in backups:
            backup_pb = backup.protobuf()
            local_file_url = getattr(backup_pb, 'local_file_url', None)
            if local_file_url:
                self.assertTrue(os.path.exists(local_file_url.replace('controller:/', '/var/lib/avi')))

    def cleanup_objs(self, backups):
        print "Cleaning up objects"
        for backup in backups:
            backup_pb = backup.protobuf()
            local_file_url = getattr(backup_pb, 'local_file_url', None)
            if local_file_url:
                os.remove(local_file_url.replace('controller:/', '/var/lib/avi'))
            backup.delete()
        Scheduler.objects.get(name='test-scheduler').delete()
        BackupConfiguration.objects.get(name='test-backupconfig').delete()


    def check_and_delete(self):
        while True:
            backups = Backup.objects.filter(json_data__file_name__contains='backup_test-scheduler')
            if backups:
                self.check_backups(backups)
                self.cleanup_objs(backups)
                break

    def wait_and_check_backup(self, log_rotate = 1):
        while True:
            backups = Backup.objects.filter(json_data__file_name__contains='backup_test-scheduler')
            if backups and backups.count() == log_rotate:
                self.check_backups(backups)
                break

    def test_10min_scheduler(self):
        self.create_scheduler_with_backup_config(10, 'SCHEDULER_FREQUENCY_UNIT_MIN', 'RUN_MODE_PERIODIC', 'SCHEDULER_ACTION_BACKUP')
        subprocess.call(shlex.split('date -s "+9min"'))
        self.check_and_delete()
        subprocess.call(shlex.split('ntpd -gq'))

    def test_1hr_scheduler(self):
        self.create_scheduler_with_backup_config(1, 'SCHEDULER_FREQUENCY_UNIT_HOUR', 'RUN_MODE_PERIODIC', 'SCHEDULER_ACTION_BACKUP')
        subprocess.call(shlex.split('date -s "+59min"'))
        self.check_and_delete()
        subprocess.call(shlex.split('ntpd -gq'))

    def test_1day_scheduler(self):
        self.create_scheduler_with_backup_config(1, 'SCHEDULER_FREQUENCY_UNIT_DAY', 'RUN_MODE_PERIODIC', 'SCHEDULER_ACTION_BACKUP')
        subprocess.call(shlex.split('date -s "+1439min"'))
        self.check_and_delete()
        subprocess.call(shlex.split('ntpd -gq'))

    def test_1week_scheduler(self):
        self.create_scheduler_with_backup_config(1, 'SCHEDULER_FREQUENCY_UNIT_DAY', 'RUN_MODE_PERIODIC', 'SCHEDULER_ACTION_BACKUP')
        subprocess.call(shlex.split('date -s "+10079min"'))
        self.check_and_delete()
        subprocess.call(shlex.split('ntpd -gq'))

    def test_10min_scheduler_multiple_and_rotation(self):
        self.create_scheduler_with_backup_config(10, 'SCHEDULER_FREQUENCY_UNIT_MIN', 'RUN_MODE_PERIODIC', 'SCHEDULER_ACTION_BACKUP')
        subprocess.call(shlex.split('date -s "+9min"'))
        self.wait_and_check_backup(1)
        subprocess.call(shlex.split('date -s "+8min"'))
        self.wait_and_check_backup(2)
        subprocess.call(shlex.split('date -s "+8min"'))
        self.wait_and_check_backup(3)
        subprocess.call(shlex.split('date -s "+8min"'))
        self.wait_and_check_backup(4)
        subprocess.call(shlex.split('date -s "+8min"'))
        self.wait_and_check_backup(4)
        subprocess.call(shlex.split('date -s "+8min"'))
        self.wait_and_check_backup(4)
        self.assertTrue(Backup.objects.filter(json_data__file_name__contains='backup_test-scheduler').count() == 4)
        self.check_and_delete()
        subprocess.call(shlex.split('ntpd -gq'))

    def test_run_now_scheduler(self):
        self.create_scheduler_with_backup_config(0, None, 'RUN_MODE_NOW', 'SCHEDULER_ACTION_BACKUP')
        self.wait_and_check_backup(1)
        self.check_and_delete()

    def test_run_at_scheduler(self):
        self.create_scheduler_with_backup_config(0, None, 'RUN_MODE_AT', 'SCHEDULER_ACTION_BACKUP', minutes=120)
        subprocess.call(shlex.split('date -s "+118min"'))
        self.wait_and_check_backup(1)
        self.check_and_delete()

    def tearDown(self):
        subprocess.call(shlex.split('service ntp start'))

