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
import paramiko
import socket


class SSHHelper(object):
    SSH_CMD_TIMEOUT = 30

    def __init__(self, host, host_ip, ssh_user, ssh_port, ssh_options):
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
        self._ssh_client.set_missing_host_key_policy(paramiko.WarningPolicy())

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
        try:
            print("Executing command on '%s': %s" % (self._host, cmd))
            stdin, stdout, stderr = self._ssh_client.exec_command(cmd, get_pty=True,
                                                                  timeout=SSHHelper.SSH_CMD_TIMEOUT)

            stdout_lines = stdout.readlines()
            stderr_lines = stderr.readlines()

            if stdout.channel.recv_exit_status() != 0:
                if len(stderr_lines) > 0:
                    print("Command failed with the following error: %s" % "\n".join(stderr_lines))
                else:
                    print("Command failed with the following error: %s" % "\n".join(stdout_lines))

                return False
        except paramiko.SSHException as e:
            print("Failed to execute the command on '%s': %s" % (self._host, repr(e)))
            return False

        return True
