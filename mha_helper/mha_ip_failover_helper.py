# (c) 2013, Ovais Tariq <ovaistariq@gmail.com>
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

import time
from datetime import datetime
import subprocess
from mysql_helper import MySQL_helper
from config_helper import MHA_config_helper
from mha_vip_helper import MHA_VIP_helper

class MHA_IP_failover_helper(object):
    CODE_SUCCESS = 0
    CODE_ERR_GENERAL = 1
    CODE_ERR_NO_SSH = 10

    def debug_message(self, message):
	current_datetime = datetime.now().strftime("%Y-%m-%-d %H:%M:%S")
	print "[%s] %s" % (current_datetime, message)

    def execute_stop_command(self, orig_master_host, orig_master_ip,
                                ssh_user, ssh_options, ssh_port):
	# We do not really need to do anything here because there is no SSH access
	return MHA_IP_failover_helper.CODE_ERR_NO_SSH

    def execute_stopssh_command(self, orig_master_host, orig_master_ip,
                                ssh_user, ssh_options, ssh_port):
        config_helper = MHA_config_helper(host=orig_master_host)

        orig_master = MySQL_helper(host=orig_master_ip,
                                    user=config_helper.get_mysql_user(),
                                    password=config_helper.get_mysql_password())

        if ssh_port is None:
            ssh_port = 22

        # If we have to manage the VIP, then remove the VIP from the original master
        if config_helper.get_manage_vip() == True:
            return_val = MHA_VIP_helper.remove_vip(config_helper=config_helper,
                                                host_ip=orig_master_ip,
                                                ssh_user=ssh_user,
                                                ssh_port=ssh_port,
                                                ssh_options=ssh_options)
        if return_val == True:
            exit_code = MHA_IP_failover_helper.CODE_SUCCESS
        else:
            exit_code = MHA_IP_failover_helper.CODE_ERR_GENERAL

        return exit_code

    def execute_start_command(self, orig_master_host, orig_master_ip,
                                new_master_host, new_master_ip,
                                ssh_user, ssh_options, ssh_port):
        config_helper = MHA_config_helper(host=new_master_host)

        new_master = MySQL_helper(host=new_master_ip,
                                    user=config_helper.get_mysql_user(),
                                    password=config_helper.get_mysql_password())

        if ssh_port is None:
            ssh_port = 22

        # Connect to the new master
        if new_master.connect() == False:
            return MHA_IP_failover_helper.CODE_ERR_GENERAL

        # If we have to manage the VIP, then assign the VIP to the new master
        if config_helper.get_manage_vip() == True:
            return_val = MHA_VIP_helper.assign_vip(config_helper=config_helper,
                                                host_ip=new_master_ip,
                                                ssh_user=ssh_user,
                                                ssh_port=ssh_port,
                                                ssh_options=ssh_options)

        if return_val == False:
            new_master.disconnect()
            return MHA_IP_failover_helper.CODE_ERR_GENERAL

        # Remove the read_only flag
        self.debug_message("Removing the read_only flag from the new master")
        new_master.unset_read_only()

        # Disconnect from the new master
        new_master.disconnect()

        return MHA_IP_failover_helper.CODE_SUCCESS

    def execute_status_command(self, orig_master_host, orig_master_ip,
                                ssh_user, ssh_options, ssh_port):
        config_helper = MHA_config_helper(host=orig_master_host)

        if ssh_port is None:
            ssh_port = 22

        self.debug_message("Doing sanity checks")

        mysql_user = config_helper.get_mysql_user()
        mysql_password = config_helper.get_mysql_password()

        if mysql_user == False or mysql_password == False:
            self.debug_message("Error accessing MySQL credentials from config")
            return MHA_IP_failover_helper.CODE_ERR_GENERAL

        if config_helper.get_manage_vip() == True:
            cluster_interface = config_helper.get_cluster_interface()
            writer_vip_cidr = config_helper.get_writer_vip_cidr()

            if cluster_interface == False or writer_vip_cidr == False:
                self.debug_message("Error fetching cluster_interface and "
                    "writer_vip_cidr from config")
                return MHA_IP_failover_helper.CODE_ERR_GENERAL

        return MHA_IP_failover_helper.CODE_SUCCESS
