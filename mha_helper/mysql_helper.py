# (c) 2015, Ovais Tariq <me@ovaistariq.net>
#
# This file is part of mha_helper
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function
import pymysql
import re


class MySQLHelper(object):
    @staticmethod
    def is_read_only_query(sql):
        if re.match('^select', sql, re.I) is not None:
            return True

        if re.match('^show', sql, re.I) is not None:
            return True

        return False

    def __init__(self, host, port, user, password):
        if port is None or port < 1:
            port = 3306

        self._host = host
        self._port = int(port)
        self._user = user
        self._password = password
        self._connection = None

    def connect(self):
        try:
            self._connection = pymysql.connect(host=self._host, port=self._port, user=self._user, passwd=self._password)
        except pymysql.Error as e:
            print("Error %d: %s" % (e.args[0], e.args[1]))
            return False

        return True

    def disconnect(self):
        if self._connection is not None:
            self._connection.close()

    def get_version(self):
        cursor = self._connection.cursor()
        try:
            cursor.execute("SELECT VERSION()")
            row = cursor.fetchone()
        except pymysql.Error as e:
            print("Error %d: %s" % (e.args[0], e.args[1]))
            return False
        finally:
            cursor.close()

        return row[0]

    def get_connection_id(self):
        return self._connection.thread_id()

    def get_current_user(self):
        return self._user

    def set_read_only(self):
        cursor = self._connection.cursor()
        try:
            cursor.execute("SET GLOBAL read_only = 1")
        except pymysql.Error as e:
            print("Error %d: %s" % (e.args[0], e.args[1]))
            return False
        finally:
            cursor.close()

        return True

    def unset_read_only(self):
        cursor = self._connection.cursor()
        try:
            cursor.execute("SET GLOBAL read_only = 0")
        except pymysql.Error as e:
            print("Error %d: %s" % (e.args[0], e.args[1]))
            return False
        finally:
            cursor.close()

        return True

    def is_read_only(self):
        cursor = self._connection.cursor()
        cursor.execute("SELECT @@read_only")
        row = cursor.fetchone()
        cursor.close()

        if row[0] == 1:
            return True

        return False

    def set_super_read_only(self):
        cursor = self._connection.cursor()
        try:
            cursor.execute("SET GLOBAL super_read_only = 1")
        except pymysql.Error as e:
            print("Error %d: %s" % (e.args[0], e.args[1]))
            return False
        finally:
            cursor.close()

        return True

    def unset_super_read_only(self):
        cursor = self._connection.cursor()
        try:
            cursor.execute("SET GLOBAL super_read_only = 0")
        except pymysql.Error as e:
            print("Error %d: %s" % (e.args[0], e.args[1]))
            return False
        finally:
            cursor.close()

        return True

    def is_super_read_only(self):
        cursor = self._connection.cursor()
        cursor.execute("SELECT @@super_read_only")
        row = cursor.fetchone()
        cursor.close()

        if row[0] == 1:
            return True

        return False

    def disable_log_bin(self):
        cursor = self._connection.cursor()
        try:
                cursor.execute("SET SQL_LOG_BIN = 0")
        except pymysql.Error as e:
            print("Error %d: %s" % (e.args[0], e.args[1]))
            return False
        finally:
            cursor.close()

        return True

    def enable_log_bin(self):
        cursor = self._connection.cursor()
        try:
            cursor.execute("SET SQL_LOG_BIN = 1")
        except pymysql.Error as e:
            print("Error %d: %s" % (e.args[0], e.args[1]))
            return False
        finally:
            cursor.close()

        return True

    def get_processlist(self):
        cursor = self._connection.cursor(pymysql.cursors.DictCursor)
        try:
            cursor.execute("SHOW PROCESSLIST")
            threads = cursor.fetchall()
        except pymysql.Error as e:
            print("Error %d: %s" % (e.args[0], e.args[1]))
            return False
        finally:
            cursor.close()

        return threads

    def get_all_users(self):
        cursor = self._connection.cursor(pymysql.cursors.DictCursor)
        try:
            cursor.execute("SELECT * from mysql.user")
            users = cursor.fetchall()
        except pymysql.Error as e:
            print("Error %d: %s" % (e.args[0], e.args[1]))
            return False
        finally:
            cursor.close()

        return users

    def get_user_grants(self, username, hostname):
        cursor = self._connection.cursor()
        grants = []
        try:
            cursor.execute("SHOW GRANTS FOR '%s'@'%s'" % (username, hostname))
            for row in cursor.fetchall():
                grants.append(row[0])
        except pymysql.Error as e:
            print("Error %d: %s" % (e.args[0], e.args[1]))
            return False
        finally:
            cursor.close()

        return grants

    def revoke_all_privileges(self, user, hostname):
        cursor = self._connection.cursor()
        try:
            cursor.execute(print("REVOKE ALL PRIVILEGES, GRANT OPTION FROM '%s'@'%s'" % (user, hostname)))
        except pymysql.Error as e:
            print("Error %d: %s" % (e.args[0], e.args[1]))
            return False
        finally:
            cursor.close()

        return True

    def get_slave_status(self):
        cursor = self._connection.cursor(pymysql.cursors.DictCursor)
        try:
            cursor.execute("SHOW SLAVE STATUS")
            row = cursor.fetchone()
        except pymysql.Error as e:
            print("Error %d: %s" % (e.args[0], e.args[1]))
            return False
        finally:
            cursor.close()

        return row

    def kill_connection(self, connection_id):
        cursor = self._connection.cursor()
        try:
            cursor.execute("KILL CONNECTION %d" % connection_id)
        except pymysql.Error as e:
            print("Error %d: %s" % (e.args[0], e.args[1]))
            return False
        finally:
            cursor.close()

        return True

    def execute_admin_query(self, sql):
        cursor = self._connection.cursor()
        try:
            cursor.execute(sql)
        except pymysql.Error as e:
            print("Error %d: %s" % (e.args[0], e.args[1]))
            return False
        finally:
            cursor.close()

        return True
