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

from __future__ import print_function
import fnmatch
import os
import ConfigParser


class ConfigHelper(object):
    MHA_HELPER_CONFIG_DIR = '/etc/mha-helper'
    MHA_HELPER_CONFIG_OPTIONS = ['writer_vip', 'writer_vip_cidr', 'manage_vip', 'report_email', 'requires_sudo',
                                 'cluster_interface']

    # This stores the configuration for every host
    host_config = dict()


    @staticmethod
    def load_config():
        pattern = '*.conf'

        for root, dirs, files in os.walk(ConfigHelper.MHA_HELPER_CONFIG_DIR):
            for filename in fnmatch.filter(files, pattern):
                config_file_path = os.path.join(ConfigHelper.MHA_HELPER_CONFIG_DIR, filename)
                print("Reading config file: %s" % config_file_path)

                config_parser = ConfigParser.RawConfigParser()
                config_parser.read(config_file_path)

                # Read the default config values first. The default config values are used when a config option is not
                # defined for the specific host
                if not config_parser.has_section('default'):
                    return False

                default_config = dict()
                for opt in ConfigHelper.MHA_HELPER_CONFIG_OPTIONS:
                    default_config[opt] = config_parser.get('default', opt)

                # Setup host based configs. Initially hosts inherit config from the default section but override them
                # within their own sections
                for hostname in config_parser.sections():
                    ConfigHelper.host_config[hostname] = dict()

                    for key, value in default_config.iteritems():
                        ConfigHelper.host_config[hostname][key] = value

                    for opt in ConfigHelper.MHA_HELPER_CONFIG_OPTIONS:
                        if config_parser.has_option(hostname, opt) and opt not in ['writer_vip', 'writer_vip_cidr']:
                            ConfigHelper.host_config[hostname][opt] = config_parser.get(hostname, opt)

        return True

    def __init__(self, host):
        self._host = host
        self._host_config = self.__class__.host_config[host]

    def get_writer_vip(self):
        return self._host_config['writer_vip']

    def get_writer_vip_cidr(self):
        return self._host_config['writer_vip_cidr']

    def get_manage_vip(self):
        return self._host_config['manage_vip']

    def get_report_email(self):
        return self._host_config['report_email']

    def get_requires_sudo(self):
        return self._host_config['requires_sudo']

    def get_cluster_interface(self):
        return self._host_config['cluster_interface']
