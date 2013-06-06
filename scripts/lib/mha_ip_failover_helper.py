import time
from datetime import datetime
from mysql_helper import MySQL_helper
from mha_config_helper import MHA_config_helper

class MHA_IP_failover_helper(object):
    def __init__(self):
        config_helper = MHA_config_helper()
        self._user = config_helper.get_username()
        self._password = config_helper.get_password()

    def debug_message(self, message):
	current_datetime = datetime.now().strftime("%Y-%m-%-d %H:%M:%S")
	print "[%s] %s" % (current_datetime, message)

    def execute_stop_command(self, orig_master_ip, ssh_user, ssh_options):
        orig_master = MySQL_helper(host=orig_master_ip, user=self._user,
                                    password=self._password)

	# We do not really need to do anything here
	return True

    def execute_start_command(self, orig_master_ip, new_master_ip, ssh_user,
                                ssh_options):
        new_master = MySQL_helper(host=new_master_ip, user=self._user,
                                    password=self._password)

        # Connect to the new master
        if new_master.connect() == False:
            return False

        # Remove the read_only flag
        self.debug_message("Removing the read_only flag from the new master")
        new_master.unset_read_only()

        # Disconnect from the new master
        new_master.disconnect()

        return True

    def execute_status_command(self, orig_master_ip, ssh_user, ssh_options):
        orig_master = MySQL_helper(host=orig_master_ip, user=self._user,
                                    password=self._password)

        # Connect to the original master
        if orig_master.connect() == False:
            return False

        return_val = True

        # Fetch the MySQL version
        if orig_master.get_version() == False:
            return_val = False

        # Disconnect from the original master
        orig_master.disconnect()
    
        return return_val

