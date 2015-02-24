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

import subprocess
from mha_config_helper import MHA_config_helper

class MHA_VIP_helper(object):
    @staticmethod
    def remove_vip(config_helper, host_ip, ssh_user, ssh_port, ssh_options):
        cluster_interface = config_helper.get_cluster_interface()
        writer_vip_cidr = config_helper.get_writer_vip_cidr()

        if ssh_user == None:
           ssh_user = config_helper.get_ssh_user()

        ip_cmd = "%s addr delete %s dev %s" % (MHA_config_helper.IP,
                                            writer_vip_cidr, cluster_interface)

        if config_helper.get_requires_sudo() == True:
            ip_cmd = "%s %s" % (MHA_config_helper.SUDO, ip_cmd)

        cmd = "%s %s -q -p %s %s@%s \"%s\"" % (MHA_config_helper.SSH,
                ssh_options, ssh_port, ssh_user, host_ip, ip_cmd)

        print "Executing command %s" % cmd

        cmd_return_code = subprocess.call(cmd, shell=True)
        if cmd_return_code > 0:
            return False

        return True

    @staticmethod
    def assign_vip(config_helper, host_ip, ssh_user, ssh_port, ssh_options):
        cluster_interface = config_helper.get_cluster_interface()
        writer_vip_cidr = config_helper.get_writer_vip_cidr()
        writer_vip = config_helper.get_writer_vip()

        if ssh_user == None:
            ssh_user = config_helper.get_ssh_user()

        ip_cmd = "%s addr add %s dev %s" % (MHA_config_helper.IP,
                                        writer_vip_cidr, cluster_interface)

        arping_cmd = "%s -q -c 3 -A -I %s %s" % (MHA_config_helper.ARPING,
                                        cluster_interface, writer_vip)

        if config_helper.get_requires_sudo() == True:
            ip_cmd = "%s %s" % (MHA_config_helper.SUDO, ip_cmd)
            arping_cmd = "%s %s" % (MHA_config_helper.SUDO, arping_cmd)

        cmd = "%s %s -q -p %s %s@%s \"%s && %s\"" % (MHA_config_helper.SSH,
                ssh_options, ssh_port, ssh_user, host_ip, ip_cmd, arping_cmd)

        print "Executing command %s" % cmd

        cmd_return_code = subprocess.call(cmd, shell=True)
        if cmd_return_code > 0:
            return False

        return True
