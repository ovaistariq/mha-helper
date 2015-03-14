#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import os
import subprocess
from mha_helper.config_helper import ConfigHelper
from mha_helper.mysql_helper import MySQLHelper
from mha_helper.vip_metal_helper import VIPMetalHelper

__author__ = 'ovais.tariq'
__project__ = 'mha_helper'


class TestMasterIPOnlineFailoverHelper(unittest.TestCase):
    def setUp(self):
        self.root_directory = os.path.dirname(os.path.realpath(__file__))
        self.failover_script_path = os.path.realpath(
            "{0}/../scripts/master_ip_online_failover_helper".format(self.root_directory))

        self.mha_helper_config_dir = os.path.join(self.root_directory, 'conf', 'good')
        if not self.mha_helper_config_dir:
            self.fail(msg='mha-helper configuration dir not set')

        ConfigHelper.MHA_HELPER_CONFIG_DIR = self.mha_helper_config_dir
        if not ConfigHelper.load_config():
            self.fail(msg='Could not load mha-helper configuration from %s' % self.mha_helper_config_dir)

        self.orig_master_host = os.getenv('ORIG_MASTER_HOST')
        self.orig_master_ip = os.getenv('ORIG_MASTER_IP')
        self.orig_master_port = os.getenv('ORIG_MASTER_PORT')
        self.orig_master_user = os.getenv('ORIG_MASTER_USER')
        self.orig_master_password = os.getenv('ORIG_MASTER_PASSWORD')
        self.orig_master_ssh_host = os.getenv('ORIG_MASTER_SSH_HOST')
        self.orig_master_ssh_ip = os.getenv('ORIG_MASTER_SSH_IP')
        self.orig_master_ssh_port = os.getenv('ORIG_MASTER_SSH_PORT')
        self.orig_master_ssh_user = os.getenv('ORIG_MASTER_SSH_USER')
        self.new_master_host = os.getenv('NEW_MASTER_HOST')
        self.new_master_ip = os.getenv('NEW_MASTER_IP')
        self.new_master_port = os.getenv('NEW_MASTER_PORT')
        self.new_master_user = os.getenv('NEW_MASTER_USER')
        self.new_master_password = os.getenv('NEW_MASTER_PASSWORD')
        self.new_master_ssh_user = os.getenv('NEW_MASTER_SSH_USER')
        self.new_master_ssh_host = os.getenv('NEW_MASTER_SSH_HOST')
        self.new_master_ssh_ip = os.getenv('NEW_MASTER_SSH_IP')
        self.new_master_ssh_port = os.getenv('NEW_MASTER_SSH_PORT')

        # We setup the VIP first on the original master as it is assumed that the master already has the VIP attached
        # to it before we enter the stop command
        VIPMetalHelper(self.orig_master_host, self.orig_master_ip, self.orig_master_ssh_user,
                       self.orig_master_ssh_port).assign_vip()

    def tearDown(self):
        # We remove the VIP just to have a clean slate at the end of the test
        VIPMetalHelper(self.orig_master_host, self.orig_master_ip, self.orig_master_ssh_user,
                       self.orig_master_ssh_port).remove_vip()

    def test_main(self):
        print("\n- Testing rejects_update stage by executing stop command")
        cmd = """{0} --command=stop --orig_master_host={1} --orig_master_ip={2} --orig_master_port={3} \
        --orig_master_user={4} --orig_master_password={5} --orig_master_ssh_host={6} --orig_master_ssh_ip={7} \
        --orig_master_ssh_port={8} --orig_master_ssh_user={9} --new_master_host={10} --new_master_ip={11} \
        --new_master_port={12} --new_master_user={13} --new_master_password={14} --new_master_ssh_user={15} \
        --new_master_ssh_host={16} --new_master_ssh_ip={17} --new_master_ssh_port={18} \
        --test_config_path={19}""".format(self.failover_script_path, self.orig_master_host, self.orig_master_ip,
                                          self.orig_master_port, self.orig_master_user, self.orig_master_password,
                                          self.orig_master_ssh_host, self.orig_master_ssh_ip,
                                          self.orig_master_ssh_port, self.orig_master_ssh_user, self.new_master_host,
                                          self.new_master_ip, self.new_master_port, self.new_master_user,
                                          self.new_master_password, self.new_master_ssh_user,
                                          self.new_master_ssh_host, self.new_master_ssh_ip, self.new_master_ssh_port,
                                          self.mha_helper_config_dir)

        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        print("STDOUT: \n%s" % stdout)
        print("STDERR: \n%s" % stderr)

        self.assertEqual(proc.returncode, 0)

        # Once the STOP command completes successfully, we would have read_only enabled on both new and original master
        # and we would have the VIP removed from the original master, so we are going to confirm that separately here
        orig_mysql = MySQLHelper(self.orig_master_ip, self.orig_master_port, self.orig_master_user,
                                 self.orig_master_password)
        orig_mysql.connect()
        self.assertTrue(orig_mysql.is_read_only())

        self.assertFalse(VIPMetalHelper(self.orig_master_host, self.orig_master_ip, self.orig_master_ssh_user,
                                        self.orig_master_ssh_port).has_vip())

        print("\n- Testing 'Allow write access on the new master' stage by executing start command")
        cmd = """{0} --command=start --orig_master_host={1} --orig_master_ip={2} --orig_master_port={3} \
        --orig_master_user={4} --orig_master_password={5} --orig_master_ssh_host={6} --orig_master_ssh_ip={7} \
        --orig_master_ssh_port={8} --orig_master_ssh_user={9} --new_master_host={10} --new_master_ip={11} \
        --new_master_port={12} --new_master_user={13} --new_master_password={14} --new_master_ssh_user={15} \
        --new_master_ssh_host={16} --new_master_ssh_ip={17} --new_master_ssh_port={18} \
        --test_config_path={19}""".format(self.failover_script_path, self.orig_master_host, self.orig_master_ip,
                                          self.orig_master_port, self.orig_master_user, self.orig_master_password,
                                          self.orig_master_ssh_host, self.orig_master_ssh_ip,
                                          self.orig_master_ssh_port, self.orig_master_ssh_user, self.new_master_host,
                                          self.new_master_ip, self.new_master_port, self.new_master_user,
                                          self.new_master_password, self.new_master_ssh_user,
                                          self.new_master_ssh_host, self.new_master_ssh_ip, self.new_master_ssh_port,
                                          self.mha_helper_config_dir)

        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        print("STDOUT: \n%s" % stdout)
        print("STDERR: \n%s" % stderr)

        self.assertEqual(proc.returncode, 0)

        # Once the START command completes successfully, we would have read_only disabled on the new master and we
        # would have the VIP assigned to the new master, so we are going to confirm that separately here
        new_mysql = MySQLHelper(self.new_master_ip, self.new_master_port, self.new_master_user,
                                self.new_master_password)

        new_mysql.connect()
        self.assertFalse(new_mysql.is_read_only())

        self.assertTrue(VIPMetalHelper(self.new_master_host, self.new_master_ip, self.new_master_ssh_user,
                                       self.new_master_ssh_port).has_vip())

if __name__ == '__main__':
    unittest.main()
