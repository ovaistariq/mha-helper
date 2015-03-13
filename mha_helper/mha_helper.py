# (c) 2015, Ovais Tariq <ovaistariq@gmail.com>
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
import time
import datetime
from mysql_helper import MySQLHelper
from config_helper import ConfigHelper
from vip_metal_helper import VIPMetalHelper


class MHAHelper(object):
    FAILOVER_TYPE_ONLINE = 'online_failover'
    FAILOVER_TYPE_HARD = 'hard_failover'
    FAILOVER_STOP_CMD = 'stop'
    FAILOVER_STOPSSH_CMD = 'stopssh'
    FAILOVER_START_CMD = 'start'
    FAILOVER_STATUS_CMD = 'status'

    def __init__(self, failover_type):
        self.failover_type = failover_type

        if not self.__validate_failover_type():
            raise ValueError

        # Setup configuration
        if not ConfigHelper.load_config():
            raise ValueError

        self.orig_master_host = None
        self.new_master_host = None

        self.orig_master_config = None
        self.new_master_config = None

    def execute_command(self, command, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self, key, value)

        # Delegate the work to other functions
        if command == self.FAILOVER_STOP_CMD:
            return self.__stop_command()
        elif command == self.FAILOVER_STOPSSH_CMD:
            return self.__stop_ssh_command()
        elif command == self.FAILOVER_START_CMD:
            return self.__start_command()
        elif command == self.FAILOVER_STATUS_CMD:
            return self.__status_command()

        # If we reach here that means no valid command was provided so we return an error here
        return False

    def __validate_failover_type(self):
        return (self.failover_type == MHAHelper.FAILOVER_TYPE_ONLINE or
                self.failover_type == MHAHelper.FAILOVER_TYPE_HARD)

    def __stop_command(self):
        if not hasattr(self, "orig_master_host") or not hasattr(self, "new_master_host"):
            return False

        self.orig_master_host = getattr(self, "orig_master_host")
        self.new_master_host = getattr(self, "new_master_host")

        self.orig_master_config = ConfigHelper(self.orig_master_host)
        self.new_master_config = ConfigHelper(self.new_master_host)

        # Original master
        try:
            orig_master_ip = getattr(self, "orig_master_ip", self.orig_master_host)
            orig_master_mysql_port = getattr(self, "orig_master_port", None)
            orig_master_mysql_user = getattr(self, "orig_master_user")
            orig_master_mysql_pass = getattr(self, "orig_master_password")
            orig_master_ssh_ip = getattr(self, "orig_master_ssh_ip", orig_master_ip)
            orig_master_ssh_port = getattr(self, "orig_master_ssh_port", None)
            orig_master_ssh_user = getattr(self, "orig_master_ssh_user", None)
        except AttributeError as e:
            print("Failed to read one or more required original master parameter(s): %s" % str(e))
            return False

        # New master
        try:
            new_master_ip = getattr(self, "new_master_ip", self.new_master_host)
            new_master_mysql_port = getattr(self, "new_master_port", None)
            new_master_mysql_user = getattr(self, "new_master_user")
            new_master_mysql_pass = getattr(self, "new_master_password")
        except AttributeError as e:
            print("Failed to read one or more required new master parameter(s): %s" % str(e))
            return False

        # Setup MySQL connections
        mysql_orig_master = MySQLHelper(orig_master_ip, orig_master_mysql_port, orig_master_mysql_user,
                                        orig_master_mysql_pass)
        mysql_new_master = MySQLHelper(new_master_ip, new_master_mysql_port, new_master_mysql_user,
                                       new_master_mysql_pass)

        try:
            print("Connecting to mysql on the original master '%s'" % self.orig_master_host)
            if not mysql_orig_master.connect():
                return False

            print("Connecting to mysql on the new master '%s'" % self.new_master_host)
            if not mysql_new_master.connect():
                return False

            print("Setting read_only to '1' on the new master '%s'" % self.new_master_host)
            if not mysql_new_master.set_read_only() or not mysql_new_master.is_read_only():
                return False

            print("Setting read_only to '1' on the original master '%s'" % self.orig_master_host)
            if not mysql_orig_master.set_read_only() or not mysql_orig_master.is_read_only():
                return False

            if self.orig_master_config.get_manage_vip():
                vip_type = self.orig_master_config.get_vip_type()
                print("Removing the vip using the '%s' provider from the original master '%s'" %
                      (vip_type, self.orig_master_host))

                if not self.__remove_vip_from_host(vip_type, self.orig_master_host, orig_master_ssh_ip,
                                                   orig_master_ssh_user, orig_master_ssh_port):
                    return False

            if not self.__mysql_kill_threads(self.orig_master_host, mysql_orig_master):
                return False
        except Exception as e:
            print("Unexpected error: %s" % str(e))
        finally:
            print("Disconnecting from mysql on the new master '%s'" % self.new_master_host)
            mysql_new_master.disconnect()

            print("Disconnecting from mysql on the original master '%s'" % self.orig_master_host)
            mysql_orig_master.disconnect()

        return True

    def __stop_ssh_command(self):
        pass

    def __start_command(self):
        if not hasattr(self, "orig_master_host") or not hasattr(self, "new_master_host"):
            return False

        self.orig_master_host = getattr(self, "orig_master_host")
        self.new_master_host = getattr(self, "new_master_host")

        self.orig_master_config = ConfigHelper(self.orig_master_host)
        self.new_master_config = ConfigHelper(self.new_master_host)

        # New master
        try:
            new_master_ip = getattr(self, "new_master_ip", self.new_master_host)
            new_master_mysql_port = getattr(self, "new_master_port", None)
            new_master_mysql_user = getattr(self, "new_master_user")
            new_master_mysql_pass = getattr(self, "new_master_password")
            new_master_ssh_ip = getattr(self, "new_master_ssh_ip", new_master_ip)
            new_master_ssh_port = getattr(self, "new_master_ssh_port", None)
            new_master_ssh_user = getattr(self, "new_master_ssh_user", None)
        except AttributeError as e:
            print("Failed to read one or more required new master parameter(s): %s" % str(e))
            return False

        # Setup MySQL connection
        mysql_new_master = MySQLHelper(new_master_ip, new_master_mysql_port, new_master_mysql_user,
                                       new_master_mysql_pass)

        try:
            print("Connecting to mysql on the new master '%s'" % self.new_master_host)
            if not mysql_new_master.connect():
                return False

            print("Setting read_only to '0' on the new master '%s'" % self.new_master_host)
            if not mysql_new_master.unset_read_only() or mysql_new_master.is_read_only():
                return False

            if self.new_master_config.get_manage_vip():
                vip_type = self.new_master_config.get_vip_type()
                print("Adding the vip using the '%s' provider to the new master '%s'" %
                      (vip_type, self.new_master_host))

                if not self.__add_vip_to_host(vip_type, self.new_master_host, new_master_ssh_ip, new_master_ssh_user,
                                              new_master_ssh_port):
                    return False
        except Exception as e:
            print("Unexpected error: %s" % str(e))
        finally:
            print("Disconnecting from mysql on the new master '%s'" % self.new_master_host)
            mysql_new_master.disconnect()

        return True

    def __status_command(self):
        if not hasattr(self, "orig_master_host"):
            return False

        self.orig_master_host = getattr(self, "orig_master_host")
        self.orig_master_config = ConfigHelper(self.orig_master_host)

        # Original master
        try:
            orig_master_ip = getattr(self, "orig_master_ip", self.orig_master_host)
            orig_master_ssh_ip = getattr(self, "orig_master_ssh_ip", orig_master_ip)
            orig_master_ssh_port = getattr(self, "orig_master_ssh_port", None)
            orig_master_ssh_user = getattr(self, "orig_master_ssh_user", None)
        except AttributeError as e:
            print("Failed to read one or more required original master parameter(s): %s" % str(e))
            return False

        try:
            if self.orig_master_config.get_manage_vip():
                vip_type = self.orig_master_config.get_vip_type()
                print("Checking the vip using the '%s' provider on the original master '%s'" %
                      (vip_type, self.orig_master_host))

                if not self.__check_vip_on_host(vip_type, self.orig_master_host, orig_master_ssh_ip,
                                                orig_master_ssh_user, orig_master_ssh_port):
                    return False
        except Exception as e:
            print("Unexpected error: %s" % str(e))

        return True

    @classmethod
    def __remove_vip_from_host(cls, vip_type, host, host_ip, ssh_user, ssh_port):
        if vip_type == ConfigHelper.VIP_PROVIDER_TYPE_METAL:
            vip_helper = VIPMetalHelper(host, host_ip, ssh_user, ssh_port)
            if not vip_helper.remove_vip():
                return False
        elif vip_type == ConfigHelper.VIP_PROVIDER_TYPE_AWS:
            pass
        elif vip_type == ConfigHelper.VIP_PROVIDER_TYPE_OS:
            pass
        else:
            # There are no other vip providers apart from what we are testing for above. Hence we throw an
            # error here
            return False

        return True

    @classmethod
    def __add_vip_to_host(cls, vip_type, host, host_ip, ssh_user, ssh_port):
        if vip_type == ConfigHelper.VIP_PROVIDER_TYPE_METAL:
            vip_helper = VIPMetalHelper(host, host_ip, ssh_user, ssh_port)
            if not vip_helper.assign_vip():
                return False
        elif vip_type == ConfigHelper.VIP_PROVIDER_TYPE_AWS:
            pass
        elif vip_type == ConfigHelper.VIP_PROVIDER_TYPE_OS:
            pass
        else:
            # There are no other vip providers apart from what we are testing for above. Hence we throw an
            # error here
            return False

        return True

    @classmethod
    def __check_vip_on_host(cls, vip_type, host, host_ip, ssh_user, ssh_port):
        if vip_type == ConfigHelper.VIP_PROVIDER_TYPE_METAL:
            return VIPMetalHelper(host, host_ip, ssh_user, ssh_port).has_vip()
        elif vip_type == ConfigHelper.VIP_PROVIDER_TYPE_AWS:
            pass
        elif vip_type == ConfigHelper.VIP_PROVIDER_TYPE_OS:
            pass
        else:
            # There are no other vip providers apart from what we are testing for above. Hence we throw an
            # error here
            return False

        return True

    @classmethod
    def __mysql_kill_threads(cls, host, mysql_connection):
        timeout = 5
        sleep_interval = 0.1
        start = datetime.datetime.now()

        print("Waiting %d seconds for application threads to disconnect from the MySQL server '%s'" % (timeout, host))
        while True:
            try:
                mysql_threads = cls.__get_mysql_threads_list(mysql_connection)
                if len(mysql_threads) < 1:
                    break
            except Exception as e:
                print("Unexpected error: %s" % str(e))
                return False

            time.sleep(sleep_interval)
            now = datetime.datetime.now()
            if (now - start).seconds > timeout:
                break

        print("Terminating all application threads connected to the MySQL server '%s'" % host)
        try:
            for thread in iter(cls.__get_mysql_threads_list(mysql_connection)):
                print("Terminating thread Id => %s, User => %s, Host => %s" %
                      (thread['Id'], thread['User'], thread['Host']))
                mysql_connection.kill_connection(thread['Id'])
        except Exception as e:
            print("Unexpected error: %s" % str(e))
            return False

        return True

    @classmethod
    def __get_mysql_threads_list(cls, mysql_connection):
        threads = list()
        try:
            for row in mysql_connection.get_processlist():
                if (mysql_connection.get_connection_id() == row['Id'] or row['Command'] == "Binlog Dump" or
                        row['User'] == "system user" or (row['Command'] == "Sleep" and row['Time'] >= 1)):
                    continue
                threads.append(row)
        except Exception as e:
            print("Failed to get list of processes from MySQL: %s" % str(e))
            return False

        return threads
