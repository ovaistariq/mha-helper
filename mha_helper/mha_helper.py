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
import time
import datetime
import re
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

    def execute_command(self, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self, key, value)

        try:
            command = getattr(self, "command")
        except Exception as e:
            print("No command supplied: %s" % str(e))
            return False

        # Delegate the work to other functions
        if command == self.FAILOVER_STOP_CMD:
            if self.failover_type == self.FAILOVER_TYPE_ONLINE:
                if not self.__stop_command():
                    self.__rollback_stop_command()
                    return False
            elif self.failover_type == self.FAILOVER_TYPE_HARD:
                return self.__stop_hard_command()

            return True
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
        try:
            self.orig_master_host = getattr(self, "orig_master_host")
            self.orig_master_config = ConfigHelper(self.orig_master_host)
        except Exception as e:
            print("Failed to read configuration for original master: %s" % str(e))
            return False

        # Original master
        try:
            orig_master_ip = getattr(self, "orig_master_ip", self.orig_master_host)
            orig_master_mysql_port = getattr(self, "orig_master_port", None)
            orig_master_ssh_ip = getattr(self, "orig_master_ssh_ip", orig_master_ip)
            orig_master_ssh_port = getattr(self, "orig_master_ssh_port", None)
            orig_master_ssh_user = getattr(self, "orig_master_ssh_user", None)
            orig_master_mysql_user = self.__unescape_from_shell(getattr(self, "orig_master_user"))
            orig_master_mysql_pass = self.__unescape_from_shell(getattr(self, "orig_master_password"))
        except AttributeError as e:
            print("Failed to read one or more required original master parameter(s): %s" % str(e))
            return False

        # Setup MySQL connections
        mysql_orig_master = MySQLHelper(orig_master_ip, orig_master_mysql_port, orig_master_mysql_user,
                                        orig_master_mysql_pass)

        try:
            print("Connecting to mysql on the original master '%s'" % self.orig_master_host)
            if not mysql_orig_master.connect():
                return False

            if self.orig_master_config.get_manage_vip():
                vip_type = self.orig_master_config.get_vip_type()
                print("Removing the vip using the '%s' provider from the original master '%s'" %
                      (vip_type, self.orig_master_host))

                if not self.__remove_vip_from_host(vip_type, self.orig_master_host, orig_master_ssh_ip,
                                                   orig_master_ssh_user, orig_master_ssh_port,
                                                   self.FAILOVER_TYPE_ONLINE):
                    return False

            if self.orig_master_config.get_super_read_only() and mysql_orig_master.super_read_only_supported():
                print("Setting super_read_only to '1' on the original master '%s'" % self.orig_master_host)
                if not mysql_orig_master.set_super_read_only() or not mysql_orig_master.is_super_read_only():
                    return False
            else:
                print("Setting read_only to '1' on the original master '%s'" % self.orig_master_host)
                if not mysql_orig_master.set_read_only() or not mysql_orig_master.is_read_only():
                    return False

            if not self.__mysql_kill_threads(self.orig_master_host, mysql_orig_master):
                return False
        except Exception as e:
            print("Unexpected error: %s" % str(e))
            return False
        finally:
            print("Disconnecting from mysql on the original master '%s'" % self.orig_master_host)
            mysql_orig_master.disconnect()

        return True

    def __stop_hard_command(self):
        try:
            self.orig_master_host = getattr(self, "orig_master_host")
            self.orig_master_config = ConfigHelper(self.orig_master_host)
        except Exception as e:
            print("Failed to read configuration for original master: %s" % str(e))
            return False

        # Original master
        try:
            orig_master_ip = getattr(self, "orig_master_ip", self.orig_master_host)
            orig_master_ssh_ip = getattr(self, "orig_master_ssh_ip", orig_master_ip)
            orig_master_ssh_port = getattr(self, "orig_master_ssh_port", None)
        except AttributeError as e:
            print("Failed to read one or more required original master parameter(s): %s" % str(e))
            return False

        try:
            if self.orig_master_config.get_manage_vip():
                vip_type = self.orig_master_config.get_vip_type()
                print("Removing the vip using the '%s' provider from the original master '%s'" %
                      (vip_type, self.orig_master_host))

                if not self.__remove_vip_from_host(vip_type, self.orig_master_host, orig_master_ssh_ip, None,
                                                   orig_master_ssh_port, self.FAILOVER_TYPE_HARD):
                    return False
        except Exception as e:
            print("Unexpected error: %s" % str(e))
            return False

        return True

    def __stop_ssh_command(self):
        try:
            self.orig_master_host = getattr(self, "orig_master_host")
            self.orig_master_config = ConfigHelper(self.orig_master_host)
        except Exception as e:
            print("Failed to read configuration for original master: %s" % str(e))
            return False

        # Original master
        try:
            orig_master_ip = getattr(self, "orig_master_ip", self.orig_master_host)
            orig_master_ssh_ip = getattr(self, "orig_master_ssh_ip", orig_master_ip)
            orig_master_ssh_port = getattr(self, "orig_master_ssh_port", None)
            orig_master_ssh_user = getattr(self, "ssh_user", None)
        except AttributeError as e:
            print("Failed to read one or more required original master parameter(s): %s" % str(e))
            return False

        try:
            if self.orig_master_config.get_manage_vip():
                vip_type = self.orig_master_config.get_vip_type()
                print("Removing the vip using the '%s' provider from the original master '%s'" %
                      (vip_type, self.orig_master_host))

                if not self.__remove_vip_from_host(vip_type, self.orig_master_host, orig_master_ssh_ip,
                                                   orig_master_ssh_user, orig_master_ssh_port,
                                                   self.FAILOVER_TYPE_ONLINE):
                    return False
        except Exception as e:
            print("Unexpected error: %s" % str(e))
            return False

        return True

    def __start_command(self):
        try:
            self.orig_master_host = getattr(self, "orig_master_host")
            self.orig_master_config = ConfigHelper(self.orig_master_host)
        except Exception as e:
            print("Failed to read configuration for original master: %s" % str(e))
            return False

        try:
            self.new_master_host = getattr(self, "new_master_host")
            self.new_master_config = ConfigHelper(self.new_master_host)
        except Exception as e:
            print("Failed to read configuration for new master: %s" % str(e))
            return False

        # New master
        try:
            new_master_ip = getattr(self, "new_master_ip", self.new_master_host)
            new_master_mysql_port = getattr(self, "new_master_port", None)
            new_master_mysql_user = self.__unescape_from_shell(getattr(self, "new_master_user"))
            new_master_mysql_pass = self.__unescape_from_shell(getattr(self, "new_master_password"))
            new_master_ssh_ip = getattr(self, "new_master_ssh_ip", new_master_ip)
            new_master_ssh_port = getattr(self, "new_master_ssh_port", None)

            if self.failover_type == self.FAILOVER_TYPE_HARD:
                new_master_ssh_user = getattr(self, "ssh_user", None)
            else:
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
            return False
        finally:
            print("Disconnecting from mysql on the new master '%s'" % self.new_master_host)
            mysql_new_master.disconnect()

        return True

    def __status_command(self):
        try:
            self.orig_master_host = getattr(self, "orig_master_host")
            self.orig_master_config = ConfigHelper(self.orig_master_host)
        except Exception as e:
            print("Failed to read configuration for original master: %s" % str(e))
            return False

        # Original master
        try:
            orig_master_ip = getattr(self, "orig_master_ip", self.orig_master_host)
            orig_master_ssh_ip = getattr(self, "orig_master_ssh_ip", orig_master_ip)
            orig_master_ssh_port = getattr(self, "orig_master_ssh_port", None)
            orig_master_ssh_user = getattr(self, "ssh_user", None)
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
            return False

        return True

    def __rollback_stop_command(self):
        try:
            self.orig_master_host = getattr(self, "orig_master_host")
            self.orig_master_config = ConfigHelper(self.orig_master_host)
        except Exception as e:
            print("Failed to read configuration for original master: %s" % str(e))
            return False

        # Original master
        try:
            orig_master_ip = getattr(self, "orig_master_ip", self.orig_master_host)
            orig_master_mysql_port = getattr(self, "orig_master_port", None)
            orig_master_mysql_user = self.__unescape_from_shell(getattr(self, "orig_master_user"))
            orig_master_mysql_pass = self.__unescape_from_shell(getattr(self, "orig_master_password"))
            orig_master_ssh_ip = getattr(self, "orig_master_ssh_ip", orig_master_ip)
            orig_master_ssh_port = getattr(self, "orig_master_ssh_port", None)
            orig_master_ssh_user = getattr(self, "orig_master_ssh_user", None)
        except AttributeError as e:
            print("Failed to read one or more required original master parameter(s): %s" % str(e))
            return False

        # Setup MySQL connections
        mysql_orig_master = MySQLHelper(orig_master_ip, orig_master_mysql_port, orig_master_mysql_user,
                                        orig_master_mysql_pass)

        print("Rolling back the failover changes on the original master '%s'" % self.orig_master_host)
        try:
            if not mysql_orig_master.connect():
                print("Failed to connect to mysql on the original master '%s'" % self.orig_master_host)
                return False

            if not mysql_orig_master.unset_read_only() or mysql_orig_master.is_read_only():
                print("Failed to reset read_only to '0' on the original master '%s'" % self.orig_master_host)
                return False

            print("Set read_only back to '0' on the original master '%s'" % self.orig_master_host)

            if self.orig_master_config.get_manage_vip():
                vip_type = self.orig_master_config.get_vip_type()
                if not self.__add_vip_to_host(vip_type, self.orig_master_host, orig_master_ssh_ip, orig_master_ssh_user,
                                              orig_master_ssh_port):
                    print("Failed to add back the vip using the '%s' provider to the original master '%s'" %
                          (vip_type, self.orig_master_host))
                    return False

                print("Added back the vip to the original master '%s'" % self.orig_master_host)
        except Exception as e:
            print("Unexpected error: %s" % str(e))
            return False
        finally:
            mysql_orig_master.disconnect()

        return True

    @classmethod
    def __remove_vip_from_host(cls, vip_type, host, host_ip, ssh_user, ssh_port, failover_type):
        if vip_type == ConfigHelper.VIP_PROVIDER_TYPE_METAL:
            vip_helper = VIPMetalHelper(host, host_ip, ssh_user, ssh_port)

            # If this is a hard failover and we cannot connect to the original master over SSH then we cannot really do
            # anything here at the moment.
            # TODO: At the moment we are not doing anything here but we would probably want to do something here
            if failover_type == cls.FAILOVER_TYPE_HARD:
                return True

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
                        row['User'] == "system user"):
                    continue
                threads.append(row)
        except Exception as e:
            print("Failed to get list of processes from MySQL: %s" % str(e))
            return False

        return threads

    @classmethod
    def __unescape_from_shell(cls, escaped):
        # This matches with mha4mysql-node::NodeUtil.pm::@shell_escape_chars
        # username and password provided by MHA are escaped like this
        unescaped = re.sub(r'\\(?!\\)', '', escaped)

        return unescaped
