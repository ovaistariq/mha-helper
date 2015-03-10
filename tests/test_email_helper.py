#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import os
from mha_helper.config_helper import ConfigHelper
from mha_helper.email_helper import EmailHelper

__author__ = 'ovais.tariq'
__project__ = 'mha_helper'


class TestEmailHelper(unittest.TestCase):
    def setUp(self):
        self.root_directory = os.path.dirname(os.path.realpath(__file__))

        # Test with the correct config
        mha_helper_config_dir = os.path.join(self.root_directory, 'conf', 'good')
        if not mha_helper_config_dir:
            self.fail(msg='mha-helper configuration dir not set')

        ConfigHelper.MHA_HELPER_CONFIG_DIR = mha_helper_config_dir
        if not ConfigHelper.load_config():
            self.fail(msg='Could not load mha-helper configuration from %s' % mha_helper_config_dir)

    def test_send_email(self):
        subject = "Testing Emails via %s" % self.__class__.__name__
        message = "Test message sent through %s" % self.__class__.__name__

        email_sender = EmailHelper('master')
        self.assertTrue(email_sender.send_email(subject, message))

if __name__ == '__main__':
    unittest.main()
