import ConfigParser

class MHA_config_helper(object):
    CONFIG_PATH = "/usr/local/mha-helper/conf/global.conf.sample"
    IP = "/sbin/ip"
    ARPING = "/sbin/arping"
    SSH = "/usr/bin/ssh"
    SUDO = "/usr/bin/sudo"

    def __init__(self, host):
       self._config = ConfigParser.RawConfigParser()
       self._config.read(MHA_config_helper.CONFIG_PATH)
       self._host = host

    def get_cluster_conf_path(self):
        return self.get_param_value(param_name='cluster_conf_path')

    def get_mysql_user(self):
        return self.get_param_value(param_name='mysql_user')

    def get_mysql_password(self):
        return self.get_param_value(param_name='mysql_password')

    def get_ssh_user(self):
        return self.get_param_value(param_name='ssh_user')

    def get_requires_sudo(self):
        param_value = self.get_param_value(param_name='requires_sudo')

        return_val = False
        if param_value.lower() == "yes":
            return_val = True

        return return_val

    def get_manage_vip(self):
        param_value = self.get_param_value(param_name='manage_vip')

        return_val = False
        if param_value.lower() == "yes":
            return_val = True

        return return_val

    def get_writer_vip(self):
        return self.get_param_value(param_name='writer_vip')

    def get_cluster_interface(self):
        return self.get_param_value(param_name='cluster_interface')

    def get_param_value(self, param_name):
        if self._config.has_section('default') == False:
            return False

        param_value = self._config.get('default', param_name)
        for section in self._config.sections():
            if(self._host is not None and
                    section == self._host and
                    self._config.has_option(section, param_name)):
                param_value = self._config.get(section, param_name)

        return param_value
