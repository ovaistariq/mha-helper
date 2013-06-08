import time
from datetime import datetime
import subprocess
from mysql_helper import MySQL_helper
from mha_config_helper import MHA_config_helper
from mha_vip_helper import MHA_VIP_helper

class MHA_IP_failover_helper(object):
    def debug_message(self, message):
	current_datetime = datetime.now().strftime("%Y-%m-%-d %H:%M:%S")
	print "[%s] %s" % (current_datetime, message)

    def execute_stop_command(self, orig_master_host, orig_master_ip, 
                                ssh_user, ssh_port=22, ssh_options):
        orig_master = MySQL_helper(host=orig_master_ip, user=self._user,
                                    password=self._password)

	# We do not really need to do anything here because there is no SSH access
	return True

    def execute_stopssh_command(self, orig_master_host, orig_master_ip, 
                                ssh_user, ssh_port=22, ssh_options):
        config_helper = MHA_config_helper(host=orig_master_host)

        orig_master = MySQL_helper(host=orig_master_ip, 
                                    user=config_helper.get_mysql_user(),
                                    password=config_helper.get_mysql_password())

        # If we have to manage the VIP, then remove the VIP from the original master
        if config_helper.get_manage_vip() == True:
            return_val = MHA_VIP_helper.remove_vip(config_helper=config_helper,
                                                host_ip=orig_master_ip,
                                                ssh_user=ssh_user,
                                                ssh_port=ssh_port,
                                                ssh_options=ssh_options)

        return return_val

    def execute_start_command(self, orig_master_host, orig_master_ip, 
                                new_master_host, new_master_ip, 
                                ssh_user, ssh_port=22, ssh_options):
        config_helper = MHA_config_helper(host=new_master_host)
        
        new_master = MySQL_helper(host=new_master_ip, 
                                    user=config_helper.get_mysql_user(),
                                    password=config_helper.get_mysql_password())

        # Connect to the new master
        if new_master.connect() == False:
            return False

        # If we have to manage the VIP, then assign the VIP to the new master
        if config_helper.get_manage_vip() == True:
            return_val = MHA_VIP_helper.assign_vip(config_helper=config_helper,
                                                host_ip=new_master_ip,
                                                ssh_user=ssh_user,
                                                ssh_port=ssh_port,
                                                ssh_options=ssh_options)

        if return_val == False:
            new_master.disconnect()
            return False

        # Remove the read_only flag
        self.debug_message("Removing the read_only flag from the new master")
        new_master.unset_read_only()

        # Disconnect from the new master
        new_master.disconnect()

        return True

    def execute_status_command(self, orig_master_host, orig_master_ip, 
                                ssh_user, ssh_port=22, ssh_options):
        config_helper = MHA_config_helper(host=orig_master_host)

        orig_master = MySQL_helper(host=orig_master_ip, 
                                    user=config_helper.get_mysql_user(),
                                    password=config_helper.get_mysql_password())

        # Connect to the original master
        if orig_master.connect() == False:
            return False

        return_val = True

        # Check SSH connectivity
        self.debug_message("Checking SSH connectivity to original master %s" % orig_master_host)

        cmd = "%s -q -p %s %s %s@%s exit" % (MHA_config_helper.SSH, ssh_port, 
                ssh_options, ssh_user, orig_master_ip)
        cmd_return_code = subprocess.call(cmd, shell=True)
        if cmd_return_code > 0:
            self.debug_message("SSH connection to %s failed" % orig_master_host)
            return False

        self.debug_message("SSH connection to %s successfull" % orig_master_host)

        # Fetch the MySQL version to test MySQL connectivity
        self.debug_message("Checking MySQL connection on original master %s" % orig_master_host)

        if orig_master.get_version() == False:
            self.debug_message("MySQL connection to %s failed" % orig_master_host)
            return_val = False

        self.debug_message("MySQL connection to %s successfull" % orig_master_host)

        # Disconnect from the original master
        orig_master.disconnect()
    
        return return_val
