#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import os
from mha_helper.ssh_helper import SSHHelper

__author__ = 'ovais.tariq'
__project__ = 'mha_helper'


class TestSSHHelper(unittest.TestCase):
    def setUp(self):
        self.ssh_host = os.getenv('SSH_TEST_HOST')
        self.ssh_host_ip = os.getenv('SSH_TEST_IP')
        self.ssh_user = os.getenv('SSH_TEST_USER')
        self.ssh_port = os.getenv('SSH_TEST_PORT')

        if not self.ssh_host or not self.ssh_host_ip or not self.ssh_user or not self.ssh_port:
            self.fail(msg='SSH connection information not set')

        self.ssh_client = SSHHelper(host=self.ssh_host, host_ip=self.ssh_host_ip, ssh_user=self.ssh_user,
                                    ssh_port=self.ssh_port, ssh_options=None)

    def test_make_ssh_connection(self):
        self.assertTrue(self.ssh_client.make_ssh_connection())

    def test_execute_ssh_command(self):
        # Setup the SSH connection
        self.ssh_client.make_ssh_connection()

        # Execute a known good command
        cmd = "/sbin/ip addr show"
        cmd_exec_status, cmd_exec_output = self.ssh_client.execute_ssh_command(cmd)
        self.assertTrue(cmd_exec_status)
        self.assertTrue(len(cmd_exec_output) > 0)

        # Execute a known misspelled command
        err_cmd = "/sbin/ifconfig -c"
        cmd_exec_status, cmd_exec_output = self.ssh_client.execute_ssh_command(err_cmd)
        self.assertFalse(cmd_exec_status)

if __name__ == '__main__':
    unittest.main()
