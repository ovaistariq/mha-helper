#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import os
from mha_helper.config_helper import ConfigHelper
from mha_helper.mysql_helper import MySQLHelper
from mha_helper.vip_metal_helper import VIPMetalHelper
from mha_helper.mha_helper import MHAHelper

__author__ = 'ovais.tariq'
__project__ = 'mha_helper'


class TestMHAHelper(unittest.TestCase):
    def setUp(self):
        self.root_directory = os.path.dirname(os.path.realpath(__file__))
        mha_helper_config_dir = os.path.join(self.root_directory, 'conf', 'good')
        if not mha_helper_config_dir:
            self.fail(msg='mha-helper configuration dir not set')

        ConfigHelper.MHA_HELPER_CONFIG_DIR = mha_helper_config_dir

        self.mha_helper = MHAHelper(MHAHelper.FAILOVER_TYPE_ONLINE)

        # Setting the necessary variables here needed by the tests
        self.orig_master_host = "master"
        self.orig_master_ip = "192.168.30.11"
        self.orig_master_port = 3306
        self.orig_master_user = "msandbox"
        self.orig_master_password = "msandbox"
        self.orig_master_ssh_host = "manager"
        self.orig_master_ssh_ip = "192.168.30.11"
        self.orig_master_ssh_port = 22
        self.orig_master_ssh_user = "root"
        self.new_master_host = "node1"
        self.new_master_ip = "192.168.30.12"
        self.new_master_port = 3306
        self.new_master_user = "msandbox"
        self.new_master_password = "msandbox"
        self.new_master_ssh_user = "root"
        self.new_master_ssh_host = "node1"
        self.new_master_ssh_ip = "192.168.30.12"
        self.new_master_ssh_port = 22
        self.ssh_options = None

    def tearDown(self):
        self.mha_helper = None

    def test_execute_stop_command_with_all_params(self):
        # We setup the VIP first on the original master as it is assumed that the master already has the VIP attached
        # to it before we enter the stop command
        VIPMetalHelper(self.orig_master_host, self.orig_master_ip, self.orig_master_ssh_user,
                       self.orig_master_ssh_port).assign_vip()

        # First we test by passing in all the parameters that MHA would pass to mha_helper
        ret_val = self.mha_helper.execute_command(command=MHAHelper.FAILOVER_STOP_CMD,
                                                  orig_master_host=self.orig_master_host,
                                                  orig_master_ip=self.orig_master_ip,
                                                  orig_master_port=self.orig_master_port,
                                                  orig_master_user=self.orig_master_user,
                                                  orig_master_password=self.orig_master_password,
                                                  orig_master_ssh_host=self.orig_master_ssh_host,
                                                  orig_master_ssh_ip=self.orig_master_ssh_ip,
                                                  orig_master_ssh_port=self.orig_master_ssh_port,
                                                  orig_master_ssh_user=self.orig_master_ssh_user,
                                                  new_master_host=self.new_master_host,
                                                  new_master_ip=self.new_master_ip,
                                                  new_master_port=self.new_master_port,
                                                  new_master_user=self.new_master_user,
                                                  new_master_password=self.new_master_password,
                                                  new_master_ssh_user=self.new_master_ssh_user,
                                                  new_master_ssh_host=self.new_master_ssh_host,
                                                  new_master_ssh_ip=self.new_master_ssh_ip,
                                                  new_master_ssh_port=self.new_master_ssh_port,
                                                  ssh_options=self.ssh_options)

        self.assertTrue(ret_val)

        # Once the STOP command completes successfully, we would have read_only enabled on both new and original master
        # and we would have the VIP removed from the original master, so we are going to confirm that separately here
        orig_mysql = MySQLHelper(self.orig_master_ip, self.orig_master_port, self.orig_master_user,
                                 self.orig_master_password)
        new_mysql = MySQLHelper(self.new_master_ip, self.new_master_port, self.new_master_user,
                                self.new_master_password)

        orig_mysql.connect()
        self.assertTrue(orig_mysql.is_read_only())

        new_mysql.connect()
        self.assertTrue(new_mysql.is_read_only())

        # We remove the VIP again just to have a clean slate at the end of the test
        VIPMetalHelper(self.orig_master_host, self.orig_master_ip, self.orig_master_ssh_user,
                       self.orig_master_ssh_port).remove_vip()

    def test_execute_stop_command_with_some_params(self):
        # We setup the VIP first on the original master as it is assumed that the master already has the VIP attached
        # to it before we enter the stop command
        VIPMetalHelper(self.orig_master_host, self.orig_master_ip).assign_vip()

        # First we test by passing in all the parameters that MHA would pass to mha_helper
        ret_val = self.mha_helper.execute_command(command=MHAHelper.FAILOVER_STOP_CMD,
                                                  orig_master_host=self.orig_master_host,
                                                  orig_master_ip=self.orig_master_ip,
                                                  orig_master_user=self.orig_master_user,
                                                  orig_master_password=self.orig_master_password,
                                                  new_master_host=self.new_master_host,
                                                  new_master_ip=self.new_master_ip,
                                                  new_master_user=self.new_master_user,
                                                  new_master_password=self.new_master_password)

        self.assertTrue(ret_val)

        # Once the STOP command completes successfully, we would have read_only enabled on both new and original master
        # and we would have the VIP removed from the original master, so we are going to confirm that separately here
        orig_mysql = MySQLHelper(self.orig_master_ip, None, self.orig_master_user, self.orig_master_password)
        new_mysql = MySQLHelper(self.new_master_ip, None, self.new_master_user, self.new_master_password)

        orig_mysql.connect()
        self.assertTrue(orig_mysql.is_read_only())

        new_mysql.connect()
        self.assertTrue(new_mysql.is_read_only())

        self.assertFalse(VIPMetalHelper(self.orig_master_host, self.orig_master_ip, self.orig_master_ssh_user,
                                        self.orig_master_ssh_port).has_vip())

        # We remove the VIP again just to have a clean slate at the end of the test
        VIPMetalHelper(self.orig_master_host, self.orig_master_ip, self.orig_master_ssh_user,
                       self.orig_master_ssh_port).remove_vip()

    def test_execute_start_command_with_all_params(self):
        # We remove the VIP first from the original master as it is assumed that the master already has the VIP removed
        # from it before we enter the start command
        VIPMetalHelper(self.orig_master_host, self.orig_master_ip, self.orig_master_ssh_user,
                       self.orig_master_ssh_port).remove_vip()

        # First we test by passing in all the parameters that MHA would pass to mha_helper
        self.assertTrue(self.mha_helper.execute_command(command=MHAHelper.FAILOVER_START_CMD,
                                                        orig_master_host=self.orig_master_host,
                                                        orig_master_ip=self.orig_master_ip,
                                                        orig_master_port=self.orig_master_port,
                                                        orig_master_user=self.orig_master_user,
                                                        orig_master_password=self.orig_master_password,
                                                        orig_master_ssh_host=self.orig_master_ssh_host,
                                                        orig_master_ssh_ip=self.orig_master_ssh_ip,
                                                        orig_master_ssh_port=self.orig_master_ssh_port,
                                                        orig_master_ssh_user=self.orig_master_ssh_user,
                                                        new_master_host=self.new_master_host,
                                                        new_master_ip=self.new_master_ip,
                                                        new_master_port=self.new_master_port,
                                                        new_master_user=self.new_master_user,
                                                        new_master_password=self.new_master_password,
                                                        new_master_ssh_user=self.new_master_ssh_user,
                                                        new_master_ssh_host=self.new_master_ssh_host,
                                                        new_master_ssh_ip=self.new_master_ssh_ip,
                                                        new_master_ssh_port=self.new_master_ssh_port,
                                                        ssh_options=self.ssh_options))

        # Once the START command completes successfully, we would have read_only disabled on the new master and we
        # would have the VIP assigned to the new master, so we are going to confirm that separately here
        new_mysql = MySQLHelper(self.new_master_ip, self.new_master_port, self.new_master_user,
                                self.new_master_password)

        new_mysql.connect()
        self.assertFalse(new_mysql.is_read_only())

        self.assertTrue(VIPMetalHelper(self.new_master_host, self.new_master_ip, self.new_master_ssh_user,
                                       self.new_master_ssh_port).has_vip())

        # We remove the VIP again just to have a clean slate at the end of the test
        VIPMetalHelper(self.new_master_host, self.new_master_ip, self.new_master_ssh_user,
                       self.new_master_ssh_port).remove_vip()

    def test_execute_start_command_with_some_params(self):
        # We remove the VIP first from the original master as it is assumed that the master already has the VIP removed
        # from it before we enter the start command
        VIPMetalHelper(self.orig_master_host, self.orig_master_ip, self.orig_master_ssh_user,
                       self.orig_master_ssh_port).remove_vip()

        # First we test by passing in all the parameters that MHA would pass to mha_helper
        self.assertTrue(self.mha_helper.execute_command(command=MHAHelper.FAILOVER_START_CMD,
                                                        orig_master_host=self.orig_master_host,
                                                        orig_master_ip=self.orig_master_ip,
                                                        orig_master_user=self.orig_master_user,
                                                        orig_master_password=self.orig_master_password,
                                                        new_master_host=self.new_master_host,
                                                        new_master_ip=self.new_master_ip,
                                                        new_master_user=self.new_master_user,
                                                        new_master_password=self.new_master_password))

        # Once the START command completes successfully, we would have read_only disabled on the new master and we
        # would have the VIP assigned to the new master, so we are going to confirm that separately here
        new_mysql = MySQLHelper(self.new_master_ip, self.new_master_port, self.new_master_user,
                                self.new_master_password)

        new_mysql.connect()
        self.assertFalse(new_mysql.is_read_only())

        self.assertTrue(VIPMetalHelper(self.new_master_host, self.new_master_ip, self.new_master_ssh_user,
                                       self.new_master_ssh_port).has_vip())

        # We remove the VIP again just to have a clean slate at the end of the test
        VIPMetalHelper(self.new_master_host, self.new_master_ip, self.new_master_ssh_user,
                       self.new_master_ssh_port).remove_vip()


if __name__ == '__main__':
    unittest.main()
