#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import os
from mha_helper.config_helper import ConfigHelper

__author__ = 'ovais.tariq'
__project__ = 'mha_helper'


class TestConfigHelper(unittest.TestCase):
    def setUp(self):
        self.root_directory = os.path.dirname(os.path.realpath(__file__))

    def test_load_config_with_good_config(self):
        # Test with the correct config
        mha_helper_config_dir = os.path.join(self.root_directory, 'conf', 'good')
        if not mha_helper_config_dir:
            self.fail(msg='mha-helper configuration dir not set')

        ConfigHelper.MHA_HELPER_CONFIG_DIR = mha_helper_config_dir
        self.assertTrue(ConfigHelper.load_config())

    def test_load_config_with_bad_config(self):
        # Test with bad config
        mha_helper_config_dir = os.path.join(self.root_directory, 'conf', 'bad')
        if not mha_helper_config_dir:
            self.fail(msg='mha-helper configuration dir not set')

        ConfigHelper.MHA_HELPER_CONFIG_DIR = mha_helper_config_dir
        self.assertFalse(ConfigHelper.load_config())

    def test_validate_config_value(self):
        # Validate valid values
        self.assertTrue(ConfigHelper.validate_config_value('writer_vip_cidr', '192.168.10.1/22'))
        self.assertTrue(ConfigHelper.validate_config_value('vip_type', 'aws'))
        self.assertTrue(ConfigHelper.validate_config_value('report_email', 'me@ovaistariq.net'))
        self.assertTrue(ConfigHelper.validate_config_value('requires_sudo', 'no'))
        self.assertTrue(ConfigHelper.validate_config_value('cluster_interface', 'eth0'))

        # Validate invalid values
        self.assertFalse(ConfigHelper.validate_config_value('writer_vip_cidr', '192.168.1/22'))
        self.assertFalse(ConfigHelper.validate_config_value('vip_type', 'foo'))
        self.assertFalse(ConfigHelper.validate_config_value('report_email', 'foo@bar'))
        self.assertFalse(ConfigHelper.validate_config_value('requires_sudo', 'bar'))
        self.assertFalse(ConfigHelper.validate_config_value('cluster_interface', ''))

    def test_get_writer_vip(self):
        self.test_load_config_with_good_config()

        host_config = ConfigHelper('master')
        self.assertEqual(host_config.get_writer_vip(), '192.168.30.100')

        host_config = ConfigHelper('db13')
        self.assertEqual(host_config.get_writer_vip(), '192.168.10.155')

    def test_get_writer_vip_cidr(self):
        self.test_load_config_with_good_config()

        host_config = ConfigHelper('master')
        self.assertEqual(host_config.get_writer_vip_cidr(), '192.168.30.100/24')

        host_config = ConfigHelper('db13')
        self.assertEqual(host_config.get_writer_vip_cidr(), '192.168.10.155/24')

    def test_get_vip_type(self):
        self.test_load_config_with_good_config()

        host_config = ConfigHelper('node1')
        self.assertEqual(host_config.get_vip_type(), 'metal')

        host_config = ConfigHelper('db11')
        self.assertEqual(host_config.get_vip_type(), 'aws')

    def test_get_manage_vip(self):
        self.test_load_config_with_good_config()

        host_config = ConfigHelper('node1')
        self.assertTrue(host_config.get_manage_vip())

        host_config = ConfigHelper('db12')
        self.assertFalse(host_config.get_manage_vip())

    def test_get_report_email(self):
        self.test_load_config_with_good_config()

        host_config = ConfigHelper('node2')
        self.assertEqual(host_config.get_report_email(), 'notify@test-cluster.com')

        host_config = ConfigHelper('db12')
        self.assertEqual(host_config.get_report_email(), 'notify@host-db12.com')

    def test_get_requires_sudo(self):
        self.test_load_config_with_good_config()

        host_config = ConfigHelper('master')
        self.assertEqual(host_config.get_requires_sudo(), True)

        host_config = ConfigHelper('db12')
        self.assertEqual(host_config.get_requires_sudo(), False)

    def test_get_cluster_interface(self):
        self.test_load_config_with_good_config()

        host_config = ConfigHelper('node2')
        self.assertEqual(host_config.get_cluster_interface(), 'eth1')

        host_config = ConfigHelper('db10')
        self.assertEqual(host_config.get_cluster_interface(), 'eth10')

if __name__ == '__main__':
    unittest.main()
