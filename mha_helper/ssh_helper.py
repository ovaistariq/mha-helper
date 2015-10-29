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

        self._host = host
        self._host_ip = host_ip
        self._ssh_user = ssh_user
        self._ssh_port = ssh_port
        self._ssh_options = ssh_options

        self._ssh_client = None

    def make_ssh_connection(self):
        if self._ssh_client is not None:
            return True

        self._ssh_client = paramiko.SSHClient()
        self._ssh_client.load_system_host_keys()
        self._ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Merge any configuration present in ssh-config with the ones passed on the command-line
        ssh_config = paramiko.SSHConfig()
        user_config_file = os.path.expanduser("~/.ssh/config")
        if os.path.exists(user_config_file):
            f = open(user_config_file)
            ssh_config.parse(f)
            f.close()

        user_config = ssh_config.lookup(self._host_ip)

        # If SSH port is not passed by the user then lookup in ssh-config, if port is configured there then use it,
        # otherwise use the default ssh port '22'
        if self._ssh_port is None or self._ssh_port < 1:
            if 'port' in user_config:
                self._ssh_port = user_config['port']
            else:
                self._ssh_port = 22
        else:
            self._ssh_port = int(self._ssh_port)

        # If SSH username is not passed by the user then lookup in ssh-config, if username is configured there then
        # use it, otherwise use the current system user
        if self._ssh_user is None:
            if 'username' in user_config:
                self._ssh_user = user_config['username']
            else:
                self._ssh_user = pwd.getpwuid(os.getuid())[0]

        cfg = dict(hostname=self._host_ip, username=self._ssh_user, port=self._ssh_port)

        if 'identityfile' in user_config:
            cfg['key_filename'] = user_config['identityfile']

        try:
            print("Connecting to '%s'@'%s'" % (self._ssh_user, self._host))
            self._ssh_client.connect(**cfg)
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
