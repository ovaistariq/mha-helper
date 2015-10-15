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
import paramiko
import socket
import os
import pwd


class SSHHelper(object):
    SSH_CMD_TIMEOUT = 30

    def __init__(self, host, host_ip=None, ssh_user=None, ssh_port=None, ssh_options=None):
        if host_ip is None:
            host_ip = host

        if ssh_user is None:
            ssh_user = pwd.getpwuid(os.getuid())[0]

        if ssh_port is None or ssh_port < 1:
            ssh_port = 22

        self._host = host
        self._host_ip = host_ip
        self._ssh_user = ssh_user
        self._ssh_port = int(ssh_port)
        self._ssh_options = ssh_options

        self._ssh_client = None

    def make_ssh_connection(self):
        if self._ssh_client is not None:
            return True

        self._ssh_client = paramiko.SSHClient()
        self._ssh_client.load_system_host_keys()
        self._ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            print("Connecting to '%s'@'%s'" % (self._host, self._ssh_user))
            self._ssh_client.connect(hostname=self._host_ip, port=self._ssh_port, username=self._ssh_user)
        except paramiko.SSHException as e:
            print("Error connecting to '%s': %s" % (self._host, repr(e)))
            return False
        except socket.error as e:
            print("Failed to connect to '%s': %s" % (self._host, repr(e)))
            return False

        return True

    def execute_ssh_command(self, cmd):
        cmd_exec_status = True
        stdout_lines = []
        stderr_lines = []

        try:
            print("Executing command on '%s': %s" % (self._host, cmd))
            stdin, stdout, stderr = self._ssh_client.exec_command(cmd, get_pty=True,
                                                                  timeout=SSHHelper.SSH_CMD_TIMEOUT)

            stdout_lines = stdout.readlines()
            stderr_lines = stderr.readlines()

            if stdout.channel.recv_exit_status() != 0:
                raise paramiko.SSHException()

        except paramiko.SSHException as e:
            print("Failed to execute the command on '%s': %s" % (self._host, str(e)))
            if len(stderr_lines) > 0:
                print("Error reported by %s: %s" % (self._host, "\n".join(stderr_lines)))

            cmd_exec_status = False

        return cmd_exec_status, stdout_lines
