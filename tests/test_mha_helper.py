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
            self.fail(msg='mha_helper configuration dir not set')

        ConfigHelper.MHA_HELPER_CONFIG_DIR = mha_helper_config_dir

        # Setting the necessary variables here needed by the tests
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
        self.ssh_options = None

    def tearDown(self):
        self.mha_helper = None

    def test_execute_stop_command_with_all_params(self):
        # Setup mha_helper object with online failover type
        self.mha_helper = MHAHelper(MHAHelper.FAILOVER_TYPE_ONLINE)

        # We setup the VIP first on the original master as it is assumed that the master already has the VIP attached
        # to it before we enter the stop command
        VIPMetalHelper(self.orig_master_host, self.orig_master_ip, self.orig_master_ssh_user,
                       self.orig_master_ssh_port).assign_vip()

        # First we test by passing in all the parameters that MHA would pass to mha_helper
        self.assertTrue(self.mha_helper.execute_command(command=MHAHelper.FAILOVER_STOP_CMD,
                                                        orig_master_host=self.orig_master_host,
                                                        orig_master_ip=self.orig_master_ip,
                                                        orig_master_port=self.orig_master_port,
                                                        orig_master_user=self.orig_master_user,
                                                        orig_master_password=self.orig_master_password,
                                                        orig_master_ssh_host=self.orig_master_ssh_host,
                                                        orig_master_ssh_ip=self.orig_master_ssh_ip,
                                                        orig_master_ssh_port=self.orig_master_ssh_port,
                                                        orig_master_ssh_user=self.orig_master_ssh_user,
                                                        ssh_options=self.ssh_options))

        # Once the STOP command completes successfully, we would have read_only enabled on both new and original master
        # and we would have the VIP removed from the original master, so we are going to confirm that separately here
        orig_mysql = MySQLHelper(self.orig_master_ip, self.orig_master_port, self.orig_master_user,
                                 self.orig_master_password)
        orig_mysql.connect()
        self.assertTrue(orig_mysql.is_read_only())

        self.assertFalse(VIPMetalHelper(self.orig_master_host, self.orig_master_ip, self.orig_master_ssh_user,
                                        self.orig_master_ssh_port).has_vip())

        # We remove the VIP again just to have a clean slate at the end of the test
        VIPMetalHelper(self.orig_master_host, self.orig_master_ip, self.orig_master_ssh_user,
                       self.orig_master_ssh_port).remove_vip()

    def test_execute_stop_command_with_minimum_params(self):
        # Setup mha_helper object with online failover type
        self.mha_helper = MHAHelper(MHAHelper.FAILOVER_TYPE_ONLINE)

        # We setup the VIP first on the original master as it is assumed that the master already has the VIP attached
        # to it before we enter the stop command
        VIPMetalHelper(self.orig_master_host, self.orig_master_ip).assign_vip()

        # First we test by passing in all the parameters that MHA would pass to mha_helper
        self.assertTrue(self.mha_helper.execute_command(command=MHAHelper.FAILOVER_STOP_CMD,
                                                        orig_master_host=self.orig_master_host,
                                                        orig_master_ip=self.orig_master_ip,
                                                        orig_master_user=self.orig_master_user,
                                                        orig_master_password=self.orig_master_password))

        # Once the STOP command completes successfully, we would have read_only enabled on both new and original master
        # and we would have the VIP removed from the original master, so we are going to confirm that separately here
        orig_mysql = MySQLHelper(self.orig_master_ip, None, self.orig_master_user, self.orig_master_password)
        orig_mysql.connect()
        self.assertTrue(orig_mysql.is_read_only())

        self.assertFalse(VIPMetalHelper(self.orig_master_host, self.orig_master_ip, self.orig_master_ssh_user,
                                        self.orig_master_ssh_port).has_vip())

        # We remove the VIP again just to have a clean slate at the end of the test
        VIPMetalHelper(self.orig_master_host, self.orig_master_ip, self.orig_master_ssh_user,
                       self.orig_master_ssh_port).remove_vip()

    def test_execute_stop_hard_command_with_all_params(self):
        # Setup mha_helper object with hard failover type
        self.mha_helper = MHAHelper(MHAHelper.FAILOVER_TYPE_HARD)

        # First we test by passing in all the parameters that MHA would pass to mha_helper
        self.assertTrue(self.mha_helper.execute_command(command=MHAHelper.FAILOVER_STOP_CMD,
                                                        orig_master_host=self.orig_master_host,
                                                        orig_master_ip=self.orig_master_ip,
                                                        orig_master_ssh_host=self.orig_master_ssh_host,
                                                        orig_master_ssh_ip=self.orig_master_ssh_ip,
                                                        orig_master_ssh_port=self.orig_master_ssh_port,
                                                        ssh_options=self.ssh_options))

        # Once the STOP HARD command completes successfully, there is no change in state on the original master
        # because there is nothing to do as STOP HARD means in bare metal no SSH basically
        self.assertFalse(VIPMetalHelper(self.orig_master_host, self.orig_master_ip, self.orig_master_ssh_user,
                                        self.orig_master_ssh_port).has_vip())

        # We remove the VIP again just to have a clean slate at the end of the test
        VIPMetalHelper(self.orig_master_host, self.orig_master_ip, self.orig_master_ssh_user,
                       self.orig_master_ssh_port).remove_vip()

    def test_execute_stop_hard_command_with_minimum_params(self):
        # Setup mha_helper object with hard failover type
        self.mha_helper = MHAHelper(MHAHelper.FAILOVER_TYPE_HARD)

        # First we test by passing in all the parameters that MHA would pass to mha_helper
        self.assertTrue(self.mha_helper.execute_command(command=MHAHelper.FAILOVER_STOP_CMD,
                                                        orig_master_host=self.orig_master_host,
                                                        orig_master_ip=self.orig_master_ip))

        # Once the STOP HARD command completes successfully, there is no change in state on the original master
        # because there is nothing to do as STOP HARD means in bare metal no SSH basically
        self.assertFalse(VIPMetalHelper(self.orig_master_host, self.orig_master_ip, self.orig_master_ssh_user,
                                        self.orig_master_ssh_port).has_vip())

        # We remove the VIP again just to have a clean slate at the end of the test
        VIPMetalHelper(self.orig_master_host, self.orig_master_ip, self.orig_master_ssh_user,
                       self.orig_master_ssh_port).remove_vip()

    def test_execute_stop_ssh_command_with_all_params(self):
        # Setup mha_helper object with hard failover type
        self.mha_helper = MHAHelper(MHAHelper.FAILOVER_TYPE_HARD)

        # We setup the VIP first on the original master as it is assumed that the master already has the VIP attached
        # to it before we enter the stop_ssh command
        VIPMetalHelper(self.orig_master_host, self.orig_master_ip, self.orig_master_ssh_user,
                       self.orig_master_ssh_port).assign_vip()

        # First we test by passing in all the parameters that MHA would pass to mha_helper
        self.assertTrue(self.mha_helper.execute_command(command=MHAHelper.FAILOVER_STOPSSH_CMD,
                                                        orig_master_host=self.orig_master_host,
                                                        orig_master_ip=self.orig_master_ip,
                                                        orig_master_port=self.orig_master_port,
                                                        orig_master_ssh_host=self.orig_master_ssh_host,
                                                        orig_master_ssh_ip=self.orig_master_ssh_ip,
                                                        orig_master_ssh_port=self.orig_master_ssh_port,
                                                        ssh_options=self.ssh_options))

        # Once the STOP SSH command completes successfully, the VIP should be removed from the original master
        self.assertFalse(VIPMetalHelper(self.orig_master_host, self.orig_master_ip, self.orig_master_ssh_user,
                                        self.orig_master_ssh_port).has_vip())

        # We remove the VIP again just to have a clean slate at the end of the test
        VIPMetalHelper(self.orig_master_host, self.orig_master_ip, self.orig_master_ssh_user,
                       self.orig_master_ssh_port).remove_vip()

    def test_execute_stop_ssh_command_with_minimum_params(self):
        # Setup mha_helper object with hard failover type
        self.mha_helper = MHAHelper(MHAHelper.FAILOVER_TYPE_HARD)

        # We setup the VIP first on the original master as it is assumed that the master already has the VIP attached
        # to it before we enter the stop_ssh command
        VIPMetalHelper(self.orig_master_host, self.orig_master_ip, self.orig_master_ssh_user,
                       self.orig_master_ssh_port).assign_vip()

        # First we test by passing in all the parameters that MHA would pass to mha_helper
        self.assertTrue(self.mha_helper.execute_command(command=MHAHelper.FAILOVER_STOPSSH_CMD,
                                                        orig_master_host=self.orig_master_host,
                                                        orig_master_ip=self.orig_master_ip,
                                                        orig_master_port=self.orig_master_port))

        # Once the STOP SSH command completes successfully, the VIP should be removed from the original master
        self.assertFalse(VIPMetalHelper(self.orig_master_host, self.orig_master_ip, self.orig_master_ssh_user,
                                        self.orig_master_ssh_port).has_vip())

        # We remove the VIP again just to have a clean slate at the end of the test
        VIPMetalHelper(self.orig_master_host, self.orig_master_ip, self.orig_master_ssh_user,
                       self.orig_master_ssh_port).remove_vip()

    def test_execute_start_command_with_all_params(self):
        # Setup mha_helper object with online failover type
        self.mha_helper = MHAHelper(MHAHelper.FAILOVER_TYPE_ONLINE)

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

    def test_execute_start_command_with_minimum_params(self):
        # Setup mha_helper object with online failover type
        self.mha_helper = MHAHelper(MHAHelper.FAILOVER_TYPE_ONLINE)

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

    def test_execute_status_command_with_all_params(self):
        # Setup mha_helper object with online failover type
        self.mha_helper = MHAHelper(MHAHelper.FAILOVER_TYPE_ONLINE)

        # We setup the VIP first on the original master as it is assumed that the master already has the VIP attached
        # to it before we enter the status command
        VIPMetalHelper(self.orig_master_host, self.orig_master_ip, self.orig_master_ssh_user,
                       self.orig_master_ssh_port).assign_vip()

        # First we test by passing in all the parameters that MHA would pass to mha_helper
        self.assertTrue(self.mha_helper.execute_command(command=MHAHelper.FAILOVER_STATUS_CMD,
                                                        orig_master_host=self.orig_master_host,
                                                        orig_master_ip=self.orig_master_ip,
                                                        orig_master_port=self.orig_master_port,
                                                        orig_master_ssh_host=self.orig_master_ssh_host,
                                                        orig_master_ssh_ip=self.orig_master_ssh_ip,
                                                        orig_master_ssh_port=self.orig_master_ssh_port,
                                                        orig_master_ssh_user=self.orig_master_ssh_user,
                                                        ssh_options=self.ssh_options))

        # We remove the VIP again just to have a clean slate at the end of the test
        VIPMetalHelper(self.orig_master_host, self.orig_master_ip, self.orig_master_ssh_user,
                       self.orig_master_ssh_port).remove_vip()

        # And then we test the status command again to make sure that it actually returns false this time
        self.assertFalse(self.mha_helper.execute_command(command=MHAHelper.FAILOVER_STATUS_CMD,
                                                         orig_master_host=self.orig_master_host,
                                                         orig_master_ip=self.orig_master_ip,
                                                         orig_master_port=self.orig_master_port,
                                                         orig_master_ssh_host=self.orig_master_ssh_host,
                                                         orig_master_ssh_ip=self.orig_master_ssh_ip,
                                                         orig_master_ssh_port=self.orig_master_ssh_port,
                                                         orig_master_ssh_user=self.orig_master_ssh_user,
                                                         ssh_options=self.ssh_options))

    def test_execute_status_command_with_minimum_params(self):
        # Setup mha_helper object with online failover type
        self.mha_helper = MHAHelper(MHAHelper.FAILOVER_TYPE_ONLINE)

        # We setup the VIP first on the original master as it is assumed that the master already has the VIP attached
        # to it before we enter the status command
        VIPMetalHelper(self.orig_master_host, self.orig_master_ip).assign_vip()

        # First we test by passing in all the parameters that MHA would pass to mha_helper
        self.assertTrue(self.mha_helper.execute_command(command=MHAHelper.FAILOVER_STATUS_CMD,
                                                        orig_master_host=self.orig_master_host,
                                                        orig_master_ip=self.orig_master_ip))

        # We remove the VIP again just to have a clean slate at the end of the test
        VIPMetalHelper(self.orig_master_host, self.orig_master_ip).remove_vip()

        # And then we test the status command again to make sure that it actually returns false this time
        self.assertFalse(self.mha_helper.execute_command(command=MHAHelper.FAILOVER_STATUS_CMD,
                                                         orig_master_host=self.orig_master_host,
                                                         orig_master_ip=self.orig_master_ip))

    def test_rollback_stop_command_with_all_params(self):
        # Setup mha_helper object with online failover type
        self.mha_helper = MHAHelper(MHAHelper.FAILOVER_TYPE_ONLINE)

        # We setup the VIP first on the original master as it is assumed that the master already has the VIP attached
        # to it before we enter the stop command
        VIPMetalHelper(self.orig_master_host, self.orig_master_ip, self.orig_master_ssh_user,
                       self.orig_master_ssh_port).assign_vip()

        # First we test by passing in all the parameters that MHA would pass to mha_helper
        self.assertFalse(self.mha_helper.execute_command(command=MHAHelper.FAILOVER_STOP_CMD,
                                                         orig_master_host=self.orig_master_host,
                                                         orig_master_ip=self.orig_master_ip,
                                                         orig_master_port=self.orig_master_port,
                                                         orig_master_user=self.orig_master_user,
                                                         orig_master_password=self.orig_master_password,
                                                         orig_master_ssh_host=self.orig_master_ssh_host,
                                                         orig_master_ssh_ip="Incorrect IP on purpose to make it fail",
                                                         orig_master_ssh_port=self.orig_master_ssh_port,
                                                         orig_master_ssh_user=self.orig_master_ssh_user))

        # Once the STOP command is rolled back successfully, we would have read_only disabled on  original master
        # and we would have the VIP assigned to the original master, so we are going to confirm that separately here
        orig_mysql = MySQLHelper(self.orig_master_ip, self.orig_master_port, self.orig_master_user,
                                 self.orig_master_password)
        orig_mysql.connect()
        self.assertFalse(orig_mysql.is_read_only())

        self.assertTrue(VIPMetalHelper(self.orig_master_host, self.orig_master_ip, self.orig_master_ssh_user,
                                       self.orig_master_ssh_port).has_vip())

        # We remove the VIP again just to have a clean slate at the end of the test
        VIPMetalHelper(self.orig_master_host, self.orig_master_ip, self.orig_master_ssh_user,
                       self.orig_master_ssh_port).remove_vip()

    def test_rollback_stop_command_with_minimum_params(self):
        # Setup mha_helper object with online failover type
        self.mha_helper = MHAHelper(MHAHelper.FAILOVER_TYPE_ONLINE)

        # We setup the VIP first on the original master as it is assumed that the master already has the VIP attached
        # to it before we enter the stop command
        VIPMetalHelper(self.orig_master_host, self.orig_master_ip, self.orig_master_ssh_user,
                       self.orig_master_ssh_port).assign_vip()

        # First we test by passing in all the parameters that MHA would pass to mha_helper
        self.assertFalse(self.mha_helper.execute_command(command=MHAHelper.FAILOVER_STOP_CMD,
                                                         orig_master_host=self.orig_master_host,
                                                         orig_master_ip=self.orig_master_ip,
                                                         orig_master_user=self.orig_master_user,
                                                         orig_master_password=self.orig_master_password,
                                                         orig_master_ssh_ip="Incorrect IP on purpose to make it fail"))

        # Once the STOP command is rolled back successfully, we would have read_only disabled on  original master
        # and we would have the VIP assigned to the original master, so we are going to confirm that separately here
        orig_mysql = MySQLHelper(self.orig_master_ip, self.orig_master_port, self.orig_master_user,
                                 self.orig_master_password)
        orig_mysql.connect()
        self.assertFalse(orig_mysql.is_read_only())

        self.assertTrue(VIPMetalHelper(self.orig_master_host, self.orig_master_ip, self.orig_master_ssh_user,
                                       self.orig_master_ssh_port).has_vip())

        # We remove the VIP again just to have a clean slate at the end of the test
        VIPMetalHelper(self.orig_master_host, self.orig_master_ip, self.orig_master_ssh_user,
                       self.orig_master_ssh_port).remove_vip()


if __name__ == '__main__':
    unittest.main()
