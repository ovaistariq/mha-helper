#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import os
from mha_helper.config_helper import ConfigHelper
from mha_helper.vip_metal_helper import VIPMetalHelper

__author__ = 'ovais.tariq'
__project__ = 'mha_helper'


class TestVIPMetalHelper(unittest.TestCase):
    def setUp(self):
        self.root_directory = os.path.dirname(os.path.realpath(__file__))

        mha_helper_config_dir = os.path.join(self.root_directory, 'conf', 'good')
        if not mha_helper_config_dir:
            self.fail(msg='mha-helper configuration dir not set')

        ConfigHelper.MHA_HELPER_CONFIG_DIR = mha_helper_config_dir
        if not ConfigHelper.load_config():
            self.fail(msg='Could not load mha-helper configuration from %s' % mha_helper_config_dir)

        self.ssh_host = os.getenv('SSH_TEST_HOST')
        self.ssh_host_ip = os.getenv('SSH_TEST_IP')
        self.ssh_user = os.getenv('SSH_TEST_USER')
        self.ssh_port = os.getenv('SSH_TEST_PORT')

        if not self.ssh_host or not self.ssh_host_ip or not self.ssh_user or not self.ssh_port:
            self.fail(msg='SSH connection information not set')

        self.vip_helper = VIPMetalHelper(host=self.ssh_host, host_ip=self.ssh_host_ip, ssh_user=self.ssh_user,
                                         ssh_port=self.ssh_port, ssh_options=None)

    def tearDown(self):
        self.vip_helper.remove_vip()

    def test_assign_vip(self):
        # We test assigning a VIP to a host that already does not have the VIP
        self.assertTrue(self.vip_helper.assign_vip())

        # We then test assigning a VIP to a host that already has the the VIP assigned
        self.assertFalse(self.vip_helper.assign_vip())

    def test_remove_vip(self):
        # We test removing the VIP from the host that already does not have the VIP
        self.assertFalse(self.vip_helper.remove_vip())

        # We then test removing the VIP from the host that already has the the VIP assigned
        self.vip_helper.assign_vip()
        self.assertTrue(self.vip_helper.remove_vip())

    def test_has_vip(self):
        # We test to see that we are able to validate the function against a host without the VIP
        self.assertFalse(self.vip_helper.has_vip())

        # We now test to see that we are able to validate the function against a host that does have the VIP
        self.vip_helper.assign_vip()
        self.assertTrue(self.vip_helper.has_vip())

if __name__ == '__main__':
    unittest.main()

