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
import optparse
import shlex


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

        # Disable keep alive for SSH connection by default
        self._keep_alive_interval_seconds = 0

        # Timeout for initiating the connection, as well as the number of retries
        self._ssh_connect_timeout_seconds = 30
        self._ssh_connect_retries = 1

        self._ssh_client = None

    def make_ssh_connection(self):
        if self._ssh_client is not None:
            return True

        self._ssh_client = paramiko.SSHClient()

        # We first load the SSH options from user's SSH config file
        ssh_options = self._get_options_from_ssh_config()

        # Parse SSH options passed in by MHA to the Helper
        # Any options passed over the command-line overrides the options that are set in the user's SSH config file
        parser = optparse.OptionParser()
        parser.add_option('-o', '--additional_options', action='append', type='string')
        parser.add_option('-i', '--key_file_path', type='string')

        if self._ssh_options is not None:
            (options, args) = parser.parse_args(shlex.split(self._ssh_options))
        else
            (options, args) = parser.parse_args()

        if options.key_file_path is not None:
            ssh_options['key_filename'] = options.key_file_path

        # Load the host keys and set the default policy, later on we may do strict host key checking
        self._ssh_client.load_system_host_keys()
        self._ssh_client.set_missing_host_key_policy(paramiko.WarningPolicy())

        # Handle additional options that are passed to ssh via the '-o' flag
        # Some of the common options that are ignored are 'PasswordAuthentication' and 'BatchMode'
        for ssh_opt in options.additional_options:
            (opt_name, opt_value) = ssh_opt.split('=')

            if opt_name == 'StrictHostKeyChecking':
                if opt_value == 'no':
                    self._ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                else:
                    self._ssh_client.set_missing_host_key_policy(paramiko.RejectPolicy())

            if opt_name == 'ServerAliveInterval':
                self._keep_alive_interval_seconds = int(opt_value)

            if opt_name == 'ConnectionAttempts':
                self._ssh_connect_retries = int(opt_value)

        # Calculate the SSH connection timeout
        ssh_options['timeout'] = self._ssh_connect_timeout_seconds * self._ssh_connect_retries

        # Make the SSH connection
        try:
            print("Connecting to '%s'@'%s'" % (self._ssh_user, self._host))
            self._ssh_client.connect(**ssh_options)
        except paramiko.SSHException as e:
            print("Error connecting to '%s': %s" % (self._host, repr(e)))
            return False
        except socket.error as e:
            print("Failed to connect to '%s': %s" % (self._host, repr(e)))
            return False

        # If the user asked for keep alive then we configure it here after the SSH connection has been made
        transport = self._ssh_client.get_transport()
        transport.set_keepalive(self._keep_alive_interval_seconds)

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

    def _get_options_from_ssh_config(self):
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

        return cfg
