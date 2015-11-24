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
import fnmatch
import os
import socket
import re
import ConfigParser


class ConfigHelper(object):
    MHA_HELPER_CONFIG_DIR = '/etc/mha-helper'
    MHA_HELPER_CONFIG_OPTIONS = ['writer_vip_cidr', 'vip_type', 'report_email', 'smtp_host', 'requires_sudo',
                                 'cluster_interface', 'kill_after_timeout']
    VIP_PROVIDER_TYPE_NONE = 'none'
    VIP_PROVIDER_TYPE_METAL = 'metal'
    VIP_PROVIDER_TYPE_AWS = 'aws'
    VIP_PROVIDER_TYPE_OS = 'openstack'
    VIP_PROVIDER_TYPES = [VIP_PROVIDER_TYPE_NONE, VIP_PROVIDER_TYPE_METAL, VIP_PROVIDER_TYPE_AWS, VIP_PROVIDER_TYPE_OS]

    # This stores the configuration for every host
    host_config = dict()


    @staticmethod
    def load_config():
        pattern = '*.conf'

        if not os.path.exists(ConfigHelper.MHA_HELPER_CONFIG_DIR):
            return False

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
                    opt_value = config_parser.get('default', opt)
                    if not ConfigHelper.validate_config_value(opt, opt_value):
                        print("Parsing the option '%s' with value '%s' failed" % (opt, opt_value))
                        return False

                    default_config[opt] = opt_value

                # Setup host based configs. Initially hosts inherit config from the default section but override them
                # within their own sections
                for hostname in config_parser.sections():
                    ConfigHelper.host_config[hostname] = dict()

                    # We read the options from the host section of the config
                    for opt in ConfigHelper.MHA_HELPER_CONFIG_OPTIONS:
                        if config_parser.has_option(hostname, opt) and opt != 'writer_vip_cidr' and opt != 'smtp_host':
                            ConfigHelper.host_config[hostname][opt] = config_parser.get(hostname, opt)

                    # We now read the options from the default section and if any option has not been set by the host
                    # section we set that to what is defined in the default section, writer_vip_cidr is always read from
                    # the default section because it has to be global for the entire replication cluster
                    # If the option is not defined in both default and host section, we throw an error
                    for opt in ConfigHelper.MHA_HELPER_CONFIG_OPTIONS:
                        if (opt not in ConfigHelper.host_config[hostname] or opt == 'writer_vip_cidr'
                            or opt == 'smtp_host'):
                            # If the host section did not define the config option and the default config also does
                            # not define the config option then we bail out
                            if opt not in default_config:
                                print("Missing required option '%s'. The option should either be set in default "
                                      "section or the host section of the config" % opt)
                                return False

                            ConfigHelper.host_config[hostname][opt] = default_config[opt]

        # If no host configuration was found it is still an error as we may be analyzing empty files
        if len(ConfigHelper.host_config) < 1:
            return False

        return True

    @staticmethod
    def validate_config_value(config_key, config_value):
        if config_key == 'writer_vip_cidr':
            return ConfigHelper.validate_ip_address(config_value)

        if config_key == 'vip_type':
            return config_value in ConfigHelper.VIP_PROVIDER_TYPES

        if config_key == 'report_email':
            return ConfigHelper.validate_email_address(config_value)

        if config_key == 'smtp_host':
            return ConfigHelper.validate_hostname(config_value)

        if config_key == 'kill_after_timeout':
            return ConfigHelper.validate_integer(config_value)

        if config_key == 'requires_sudo':
            return config_value in ['yes', 'no']

        if config_key == 'cluster_interface':
            return config_value is not None and len(config_value) > 0

    @staticmethod
    def validate_ip_address(ip_address):
        pattern = '^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(/([0-9]|[1-2][0-9]|3[0-2]))$'
        return bool(re.match(pattern, ip_address))

    @staticmethod
    def validate_email_address(email_address):
        pattern = '^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$'
        return bool(re.match(pattern, email_address))

    @staticmethod
    def validate_integer(potential_integer):
            try:
                value = int(potential_integer)
            except ValueError:
                return False

            return True

    @staticmethod
    def validate_hostname(hostname):
        if len(hostname) > 255:
            return False

        if hostname[-1] == ".":
            hostname = hostname[:-1] # strip exactly one dot from the right, if present

        allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
        if not all(allowed.match(x) for x in hostname.split(".")):
            return False

        # Now we try to resolve the hostname and error out if we cannot
        try:
            socket.gethostbyname(hostname)
        except Exception as e:
            print("Failed to resolve the hostname %s: %s" % (hostname, str(e)))
            return False

        return True

    def __init__(self, host):
        self._host = host

        if host not in self.__class__.host_config:
            raise ValueError
        self._host_config = self.__class__.host_config[host]

    def get_writer_vip(self):
        return self.get_writer_vip_cidr().split('/')[0]

    def get_writer_vip_cidr(self):
        return self._host_config['writer_vip_cidr']

    def get_vip_type(self):
        return self._host_config['vip_type']

    def get_manage_vip(self):
        return self._host_config['vip_type'] != 'none'

    def get_report_email(self):
        return self._host_config['report_email']

    def get_smtp_host(self):
        return self._host_config['smtp_host']

    def get_kill_after_timeout(self):
        return int(self._host_config['kill_after_timeout'])

    def get_requires_sudo(self):
        if self._host_config['requires_sudo'] == 'yes':
            return True

        return False

    def get_cluster_interface(self):
        return self._host_config['cluster_interface']
