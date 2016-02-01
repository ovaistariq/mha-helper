#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import os
from mha_helper.mysql_helper import MySQLHelper

__author__ = 'ovais.tariq'
__project__ = 'mha_helper'


class TestMySQLHelper(unittest.TestCase):
    def setUp(self):
        mysql_host = os.getenv('MYSQL_TEST_IP')
        mysql_user = os.getenv('MYSQL_TEST_USER')
        mysql_password = os.getenv('MYSQL_TEST_PASSWORD')
        mysql_port = os.getenv('MYSQL_TEST_PORT')

        if not mysql_host or not mysql_user or not mysql_password or not mysql_port:
            self.fail(msg='MySQL database connection information not set')

        self.mysql_conn = MySQLHelper(host=mysql_host, port=mysql_port, user=mysql_user, password=mysql_password)
        if not self.mysql_conn.connect():
            self.fail(msg='Could not connect to the MySQL database')

        self.mysql_version = os.getenv('MYSQL_TEST_VERSION')

    def tearDown(self):
        self.mysql_conn.disconnect()

    def test_is_read_only_query(self):
        self.assertEqual(MySQLHelper.is_read_only_query('SELECT 1'), True)
        self.assertEqual(MySQLHelper.is_read_only_query('INSERT INTO foo VALUES ("bar")'), False)

    def test_get_version(self):
        self.assertEqual(self.mysql_conn.get_version(), self.mysql_version)

    def test_get_connection_id(self):
        self.assertNotEqual(self.mysql_conn.get_connection_id(), None)

    def test_get_current_user(self):
        self.assertNotEqual(self.mysql_conn.get_current_user(), None)

    def test_set_read_only(self):
        self.mysql_conn.set_read_only()
        self.assertEqual(self.mysql_conn.is_read_only(), True)

    def test_unset_read_only(self):
        self.mysql_conn.unset_read_only()
        self.assertEqual(self.mysql_conn.is_read_only(), False)

    def test_get_processlist(self):
        processlist = self.mysql_conn.get_processlist()
        self.assertTrue(len(processlist) >= 1)

    def test_kill_connection(self):
        mysql_host = os.getenv('MYSQL_TEST_IP')
        mysql_user = os.getenv('MYSQL_TEST_USER')
        mysql_password = os.getenv('MYSQL_TEST_PASSWORD')
        mysql_port = int(os.getenv('MYSQL_TEST_PORT'))

        mysql_conn = MySQLHelper(host=mysql_host, port=mysql_port, user=mysql_user, password=mysql_password)
        if not mysql_conn.connect():
            self.fail(msg='Could not connect to the MySQL database')

        mysql_conn_id = mysql_conn.get_connection_id()
        self.assertTrue(self.mysql_conn.kill_connection(mysql_conn_id))

        del mysql_conn

if __name__ == '__main__':
    unittest.main()
