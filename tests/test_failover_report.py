#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import os
import subprocess
from mha_helper.config_helper import ConfigHelper

__author__ = 'ovais.tariq'
__project__ = 'mha_helper'


class TestFailoverReport(unittest.TestCase):
    def setUp(self):
        self.root_directory = os.path.dirname(os.path.realpath(__file__))
        self.failover_report_script_path = os.path.realpath(
            "{0}/../scripts/master_failover_report".format(self.root_directory))

        self.mha_helper_config_dir = os.path.join(self.root_directory, 'conf', 'good')
        if not self.mha_helper_config_dir:
            self.fail(msg='mha-helper configuration dir not set')

        ConfigHelper.MHA_HELPER_CONFIG_DIR = self.mha_helper_config_dir
        if not ConfigHelper.load_config():
            self.fail(msg='Could not load mha-helper configuration from %s' % self.mha_helper_config_dir)

        self.orig_master_host = os.getenv('ORIG_MASTER_HOST')
        self.new_master_host = os.getenv('NEW_MASTER_HOST')

    def test_main(self):
        mha_config_path = os.path.join(self.mha_helper_config_dir, 'test_cluster.conf')
        email_subject = "Testing Emails via %s" % self.__class__.__name__
        email_body = "Test message sent through %s" % self.__class__.__name__

        print("\n- Testing sending the failover report")
        cmd = """{0} --conf={1} --orig_master_host={2} --new_master_host={3} --subject="{4}" --body="{5}" \
        --test_config_path={6}""".format(self.failover_report_script_path, mha_config_path, self.orig_master_host,
                                         self.new_master_host, email_subject, email_body, self.mha_helper_config_dir)

        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        print("STDOUT: \n%s" % stdout)
        print("STDERR: \n%s" % stderr)

        self.assertEqual(proc.returncode, 0)

if __name__ == '__main__':
    unittest.main()
