#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import os
from mha_helper.config_helper import ConfigHelper

__author__ = 'ovais.tariq'
__project__ = 'mha_helper'


class TestConfigHelper(unittest.TestCase):
    def setUp(self):
        mha_helper_config_dir = os.getenv('MHA_HELPER_TEST_CONFIG_DIR')

        if not mha_helper_config_dir:
            self.fail(msg='mha-helper configuration dir not set')

        ConfigHelper.MHA_HELPER_CONFIG_DIR = os.getenv('MHA_HELPER_TEST_CONFIG_DIR')
        if not ConfigHelper.load_config():
            self.fail(msg='Could not load mha-helper configuration')

    def test_load_config(self):
        pass

    def test_get_writer_vip(self):
        pass

    def test_get_writer_vip_cidr(self):
        pass

    def test_get_manage_vip(self):
        pass

    def test_get_report_email(self):
        pass

    def test_get_requires_sudo(self):
        pass

    def test_get_cluster_interface(self):
        pass


