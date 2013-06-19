# (c) 2013, Ovais Tariq <ovaistariq@gmail.com>
#
# This file is part of mha-helper
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

import ConfigParser

class MHA_config_helper(object):
    IP = "/sbin/ip"
    ARPING = "/sbin/arping"
    SSH = "/usr/bin/ssh"
    SUDO = "/usr/bin/sudo"

    def __init__(self, host):
        self._host = host
        self._global_config_helper = MHA_global_config_helper(host=host)
        
        cluster_conf_path = self._global_config_helper.get_cluster_conf_path()
        self._config = ConfigParser.RawConfigParser()
        self._config.read(cluster_conf_path)

    def get_mysql_user(self):
        return self.get_param_value(param_name='user')

    def get_mysql_password(self):
        return self.get_param_value(param_name='password')

    def get_ssh_user(self):
        return self.get_param_value(param_name='ssh_user')

    def get_requires_sudo(self):
        return self._global_config_helper.get_requires_sudo()

    def get_manage_vip(self):
        return self._global_config_helper.get_manage_vip()

    def get_writer_vip_cidr(self):
        return self._global_config_helper.get_writer_vip_cidr()

    def get_writer_vip(self):
        return self._global_config_helper.get_writer_vip()

    def get_cluster_interface(self):
        return self._global_config_helper.get_cluster_interface()

    def get_report_email(self):
        return self._global_config_helper.get_report_email()

    def get_param_value(self, param_name):
        if self._config.has_section('server default') == False:
            return False

        param_value = False

        if self._config.has_option('server default', param_name):
            param_value = self._config.get('server default', param_name)

        for section in self._config.sections():
            if(self._host is not None and 
                    section == self._host and 
                    self._config.has_option(section, param_name)):
                param_value = self._config.get(section, param_name)

        return param_value

class MHA_global_config_helper(object):
    CONFIG_PATH = "/usr/local/mha-helper/conf/global.conf"

    def __init__(self, host):
       self._config = ConfigParser.RawConfigParser()
       self._config.read(MHA_global_config_helper.CONFIG_PATH)
       self._host = host

    def get_cluster_conf_path(self):
        return self.get_param_value(param_name='cluster_conf_path')

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

    def get_writer_vip_cidr(self):
        return self.get_param_value(param_name='writer_vip_cidr')

    def get_writer_vip(self):
        return self.get_param_value(param_name='writer_vip')

    def get_cluster_interface(self):
        return self.get_param_value(param_name='cluster_interface')

    def get_report_email(self):
        return self.get_param_value(param_name='report_email')

    def get_param_value(self, param_name):
        if self._config.has_section('default') == False:
            return False

        param_value = False

        if self._config.has_option('default', param_name):
            param_value = self._config.get('default', param_name)

        for section in self._config.sections():
            if(self._host is not None and
                    section == self._host and
                    self._config.has_option(section, param_name)):
                param_value = self._config.get(section, param_name)

        return param_value
