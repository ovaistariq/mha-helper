import time
from datetime import datetime
import subprocess
from mysql_helper import MySQL_helper
from mha_config_helper import MHA_config_helper

class MHA_IP_failover_helper(object):
    def debug_message(self, message):
	current_datetime = datetime.now().strftime("%Y-%m-%-d %H:%M:%S")
	print "[%s] %s" % (current_datetime, message)

    def execute_stop_command(self, orig_master_host, orig_master_ip, 
                                ssh_user, ssh_options):
        orig_master = MySQL_helper(host=orig_master_ip, user=self._user,
                                    password=self._password)

	# We do not really need to do anything here because there is no SSH access
	return True

    def execute_stopssh_command(self, orig_master_host, orig_master_ip, 
                                ssh_user, ssh_options):
        config_helper = MHA_config_helper(host=orig_master_host)

        orig_master = MySQL_helper(host=orig_master_ip, 
                                    user=config_helper.get_mysql_user(),
                                    password=config_helper.get_mysql_password())

        # If we have to manage the VIP, then remove the VIP from the original master
        if config_helper.get_manage_vip() == 'yes':
            ifconfig_cmd = "/sbin/ifconfig %s %s down" % (config_helper.get_cluster_interface(),
                                                            config_helper.get_writer_vip())

            cmd = ["ssh", "%s@%s" % (ssh_user, orig_master_ip), ssh_options, ifconfig_cmd]
            cmd_return_code = subprocess.call(cmd)
            if cmd_return_code > 0:
                return False

        return True

    def execute_start_command(self, orig_master_host, orig_master_ip, 
                                new_master_host, new_master_ip, 
                                ssh_user, ssh_options):
        config_helper = MHA_config_helper(host=new_master_host)
        
        new_master = MySQL_helper(host=new_master_ip, 
                                    user=config_helper.get_mysql_user(),
                                    password=config_helper.get_mysql_password())

        # Connect to the new master
        if new_master.connect() == False:
            return False

        # If we have to manage the VIP, then assign the VIP to the new master
        if config_helper.get_manage_vip() == 'yes':
            ifconfig_cmd = "/sbin/ifconfig %s %s up" % (config_helper.get_cluster_interface(),
                                                            config_helper.get_writer_vip())

            arping_cmd = "/sbin/arping -q -c 3 -A -I %s %s" % (config_helper.get_cluster_interface(),
                                                            config_helper.get_writer_vip())

            cmd = ["ssh", "%s@%s" % (ssh_user, new_master_ip), ssh_options, "%s && %s" % (ifconfig_cmd, arping_cmd)]
            cmd_return_code = subprocess.call(cmd)
            if cmd_return_code > 0:
                return False

        # Remove the read_only flag
        self.debug_message("Removing the read_only flag from the new master")
        new_master.unset_read_only()

        # Disconnect from the new master
        new_master.disconnect()

        return True

    def execute_status_command(self, orig_master_host, orig_master_ip, 
                                ssh_user, ssh_options):
        config_helper = MHA_config_helper(host=orig_master_host)

        orig_master = MySQL_helper(host=orig_master_ip, 
                                    user=config_helper.get_mysql_user(),
                                    password=config_helper.get_mysql_password())

        # Connect to the original master
        if orig_master.connect() == False:
            return False

        return_val = True

        # Check SSH connectivity
        cmd = ["ssh", "%s@%s" % (ssh_user, orig_master_ip), ssh_options, "-q", "exit"]
        cmd_return_code = subprocess.call(cmd)
        if cmd_return_code > 0:
            return False

        # Fetch the MySQL version to test MySQL connectivity
        if orig_master.get_version() == False:
            return_val = False

        # Disconnect from the original master
        orig_master.disconnect()
    
        return return_val

