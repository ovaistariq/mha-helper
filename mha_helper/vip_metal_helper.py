# (c) 2015, Ovais Tariq <ovaistariq@gmail.com>
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
from ssh_helper import SSHHelper
from config_helper import ConfigHelper
import re


class VIPMetalHelper(object):
    IP_CMD = "/sbin/ip"
    ARPING_CMD = "/usr/sbin/arping"

    def __init__(self, host, host_ip=None, ssh_user=None, ssh_port=None, ssh_options=None):
        config_helper = ConfigHelper(host)
        self._cluster_interface = config_helper.get_cluster_interface()
        self._writer_vip_cidr = config_helper.get_writer_vip_cidr()
        self._writer_vip = config_helper.get_writer_vip()
        self._requires_sudo = config_helper.get_requires_sudo()

        self._ssh_client = SSHHelper(host, host_ip, ssh_user, ssh_port, ssh_options)

    def assign_vip(self):
        ip_cmd = "%s addr add %s dev %s" % (VIPMetalHelper.IP_CMD, self._writer_vip_cidr, self._cluster_interface)
        arping_cmd = "%s -q -c 3 -A -I %s %s" % (VIPMetalHelper.ARPING_CMD, self._cluster_interface, self._writer_vip)

        if self._requires_sudo:
            ip_cmd = "sudo %s" % ip_cmd
            arping_cmd = "sudo %s" % arping_cmd

        # Connect to the host over SSH
        if not self._ssh_client.make_ssh_connection():
            return False

        # Assign the VIP to the host
        ret_code, stdout_lines = self._ssh_client.execute_ssh_command(ip_cmd)
        if not ret_code:
            if len(stdout_lines) > 0:
                print("Command output: %s" % "\n".join(stdout_lines))
            return False

        # Send ARP update requests to all the listening hosts
        ret_code, stdout_lines = self._ssh_client.execute_ssh_command(arping_cmd)
        if not ret_code:
            if len(stdout_lines) > 0:
                print("Command output: %s" % "\n".join(stdout_lines))
            return False

        return True

    def remove_vip(self):
        ip_cmd = "%s addr delete %s dev %s" % (VIPMetalHelper.IP_CMD, self._writer_vip_cidr, self._cluster_interface)
        if self._requires_sudo:
            ip_cmd = "sudo %s" % ip_cmd

        # Connect to the host over SSH
        if not self._ssh_client.make_ssh_connection():
            return False

        # Remove the VIP from the host
        ret_code, stdout_lines = self._ssh_client.execute_ssh_command(ip_cmd)
        if not ret_code:
            if len(stdout_lines) > 0:
                print("Command output: %s" % "\n".join(stdout_lines))
            return False

        return True

    def has_vip(self):
        ip_cmd = "%s addr show dev %s" % (VIPMetalHelper.IP_CMD, self._cluster_interface)
        if self._requires_sudo:
            ip_cmd = "sudo %s" % ip_cmd

        # Connect to the host over SSH
        if not self._ssh_client.make_ssh_connection():
            return False

        # Fetch the output of the command `ip addr show dev eth` and parse it to list the IP addresses
        # If the VIP is in that list then that means the VIP is assigned to the host
        ret_code, stdout_lines = self._ssh_client.execute_ssh_command(ip_cmd)
        if not ret_code:
            if len(stdout_lines) > 0:
                print("Command output: %s" % "\n".join(stdout_lines))
            return False

        vip_found = False
        for line in stdout_lines:
            # We want to match a line similar to the following:
            #   inet 192.168.30.11/24 brd 192.168.30.255 scope global eth1
            if re.search(r'\binet\b', line):
                # The second element of the matching line is the IP address in CIDR format
                if line.split()[1] == self._writer_vip_cidr:
                    vip_found = True
                    break

        return vip_found
