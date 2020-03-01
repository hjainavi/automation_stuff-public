
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

import os
import sys
import logging
import yaml
import json
import copy

from django.test import TestCase
from avi.config_migration.export_import import get_model_and_serializer

logger = logging.getLogger(__name__)
out_hdlr = logging.StreamHandler(sys.stdout)
out_hdlr.setFormatter(logging.Formatter('%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s'))
out_hdlr.setLevel(logging.INFO)
logger.addHandler(out_hdlr)
logger.setLevel(logging.INFO)

cwd = os.path.dirname(__file__)
version = None

class MigrationsTests(TestCase):
    def get_current_version(self):
        local_version_file = '/bootstrap/VERSION'
        migration_routines_path = '/opt/avi/python/lib/avi/upgrade/migration/'
        with open(local_version_file, 'r') as f:
            version_dict = yaml.load(f.read())
            version = version_dict.get('version')
            version = str(version).strip().replace('.', '_')
            if not os.path.isdir(os.path.join(migration_routines_path, version)):
                version = 'current_version'
            return version

    def load_migration_routine(self, version, model_name):
        api_mod_name = 'avi.upgrade.migration.%s.api_migrate' %version
        upgrade_mod_name = 'avi.upgrade.migration.%s.upgrade_migrate' %version

        __import__(upgrade_mod_name)
        upgrade_routine = sys.modules[upgrade_mod_name].UPGRADE_MIGRATIONS[model_name]

        __import__(api_mod_name)
        (api_forward_migration, api_reverse_migration) = sys.modules[api_mod_name].API_MIGRATIONS.get(model_name, (None, None))

        return (upgrade_routine, api_forward_migration, api_reverse_migration)


    def get_file_content(self, filename, config_path):
        with open(os.path.join(config_path, filename)) as f:
            return json.load(f)

    def inflate_test_config(self, config, config_path):
        return [tuple([self.get_file_content(item, config_path) if isinstance(item, basestring) and item.endswith('.json') else item for item in entry]) for entry in config] 
    
    def verify_upgrade(self, module_name, upgrade_config, upgrade_routine):
        (before, config, after, exclude_params) = upgrade_config
        before = before[module_name][0] if type(before[module_name]) is list else before[module_name]

        input_config = copy.deepcopy(before)
        upgrade_routine(input_config, config)
        self.assertTrue(input_config == after[module_name][0] if type(after[module_name]) is list else after[module_name])

        if config:
            for obj_name, _obj in config.items():
                self.assertTrue(_obj, after[obj_name])

        ''' Testing self Migration'''
        upgrade_routine(input_config, config)
        self.assertTrue(input_config ==  after[module_name][0] if type(after[module_name]) is list else after[module_name])
        logger.info(">>> Self Upgrade for %s: Passed" %module_name)

    def verify_api_versioning(self, module_name, upgrade_config, forward_migration, reverse_migration):
        if forward_migration:

            (before, config, after, exclude_params) = upgrade_config
            before = before[module_name][0] if type(before[module_name]) is list else before[module_name]

            input_config = copy.deepcopy(before)

            if config:
                for obj_name, objs in config.items():
                    model, serializer = get_model_and_serializer(obj_name)
                    self.assertTrue(serializer!=None)
                    for obj in objs:
                        ser = serializer(data = obj)
                        if ser.is_valid():
                            ser.save()



            '''  v1  ---------->  v2
                      Forward     |
                                  | Self
                      Reverse     |
                 v1 <----------   v2
            '''

            ''' Testing Forward Migration'''
            forward_migration(input_config, config)
            self.assertTrue(input_config == after[module_name][0] if type(after[module_name]) is list else after[module_name])
            logger.info(">>> Forward Migration for %s: Passed" %module_name)

            ''' Testing self Migration'''
            forward_migration(input_config, config)
            self.assertTrue(input_config == after[module_name][0] if type(after[module_name]) is list else after[module_name])
            logger.info(">>> Self Migration for %s: Passed" %module_name)

            ''' Testing Inverse Migration'''
            if reverse_migration:
                reverse_migration(input_config, config)
                try:
                    self.assertTrue(input_config == before)
                except AssertionError:
                    if 'exclude_fields' in exclude_params and \
                        sorted(exclude_params.get('exclude_fields')) != sorted(set(before.keys()) - set(input_config.keys())):
                        raise
                logger.info(">>> Inverse Migration for %s: Passed" %module_name)
            logger.info("--->>> API Versioning for %s: Passed" %module_name)
    
    def test_migration_completeness(self):
        version = self.get_current_version()
        upgrade_mod_name = 'avi.upgrade.migration.%s.upgrade_migrate' %version
        api_mod_name = 'avi.upgrade.migration.%s.api_migrate' %version

        test_config_path = '/opt/avi/python/lib/avi/upgrade/migration/%s/test_config' %version

        config_map = {}

        for fname in os.listdir(test_config_path):
            if (not fname.endswith('.py') or fname.startswith('__')):
                continue

            mod_name = ('avi.upgrade.migration.%s.test_config.' % version) + fname.rpartition('.')[0]
            __import__(mod_name)

            try:
                module = sys.modules[mod_name]
            except (ImportError, AttributeError, KeyError) as ex:
                logging.error('Unable to import %s "%s"', mod_name, ex)
                continue

            model_name = getattr(module, 'model_name', None)
            if not model_name:
                raise Exception("Missing 'model_name' in %s" %fname)

            test_config = getattr(module, 'config_%s'%model_name, None)
            if not test_config:
                raise Exception("Missing 'config_%s' in %s" %(model_name, fname))
            config_map[model_name] = test_config


        logger.info( "Checking for Upgrade test case completeness")
        __import__(upgrade_mod_name)
        try:
            upgrade_module = sys.modules[upgrade_mod_name]
        except (ImportError, AttributeError, KeyError) as ex:
            logger.error('Unable to import %s "%s"', upgrade_mod_name, ex)

        for obj in upgrade_module.UPGRADE_MIGRATIONS:
            try:
                self.assertTrue(obj in config_map)
            except AssertionError:
                logger.error('Test Cases missing for %s' %obj)
                raise


        logger.info( "Checking for versioning test case completeness")
        __import__(api_mod_name)
        try:
            api_module = sys.modules[api_mod_name]
        except (ImportError, AttributeError, KeyError) as ex:
            logger.error('Unable to import %s "%s"', api_mod_name, ex)

        for obj in api_module.API_MIGRATIONS:
            try:
                self.assertTrue(obj in config_map)
            except AssertionError:
                logger.error('Test Cases missing for %s' %obj)
                raise

    def test_migration(self):
        version = self.get_current_version()
        test_config_path = '/opt/avi/python/lib/avi/upgrade/migration/%s/test_config' %version

        for fname in os.listdir(test_config_path):
            if (not fname.endswith('.py') or fname.startswith('__')):
                continue

            mod_name = ('avi.upgrade.migration.%s.test_config.' % version) + fname.rpartition('.')[0]
            __import__(mod_name)
            try:
                module = sys.modules[mod_name]
            except (ImportError, AttributeError, KeyError) as ex:
                logging.error('Unable to import %s "%s"', mod_name, ex)
                continue

            model_name = getattr(module, 'model_name', None)
            if not model_name:
                raise Exception("Missing 'model_name' in %s" %fname)

            test_config = getattr(module, 'config_%s'%model_name, None)
            if not test_config:
                raise Exception("Missing 'config_%s' in %s" %(model_name, fname))

            upgrade_routine, api_forward_migration, api_reverse_migration = \
                                self.load_migration_routine(version, model_name)

            test_config = self.inflate_test_config(test_config, test_config_path)

            logger.info("UPGRADE MIGRATION:")
            for config in test_config:
                self.verify_upgrade(model_name, config, upgrade_routine)
            logger.info( "--->>> Migration for %s: Passed" %model_name)

            logger.info("API VERSIONING:")
            for config in test_config:
                self.verify_api_versioning(model_name, config, api_forward_migration, api_reverse_migration)
