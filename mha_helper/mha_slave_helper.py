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

from mysql_helper import MySQL_helper
from mha_config_helper import MHA_config_helper

class MHA_slave_helper(object):
    CODE_SUCCESS = 0
    CODE_ERR_MYSQL_CONN = 1
    CODE_ERR_READ_ONLY = 10
    CODE_ERR_SLAVE_RUNNING = 20
    CODE_ERR_SLAVE_LAG = 30

    def __init__(self, slave_host):
        self._slave_host_config_helper = MHA_config_helper(host=slave_host)

        self._slave_hostname = slave_host

        mysql_user = self._slave_host_config_helper.get_mysql_user()
        mysql_password = self._slave_host_config_helper.get_mysql_password()
        host_ip = self._slave_host_config_helper.get_host_ip()

        self._slave_host = MySQL_helper(host=host_ip, user=mysql_user,
                            password=mysql_password)

    def is_healthy(self):
        # Try to connect to the slave
        if self._slave_host.connect() == False:
            return MHA_slave_helper.CODE_ERR_MYSQL_CONN

        slave_status = self._slave_host.get_slave_status()
        # If we get an empty slave status that means that this is a master
        # If we get a FALSE result that means there was an error running
        # the query
        if slave_status == False or slave_status is None:
            return MHA_slave_helper.CODE_ERR_SLAVE_RUNNING

        # Check if slave threads are running
        if (slave_status['Slave_IO_Running'] != 'Yes' or
            slave_status['Slave_SQL_Running'] != 'Yes'):
            return MHA_slave_helper.CODE_ERR_SLAVE_RUNNING

        # Check if slave lag is within the allowable threshold
        slave_lag_threshold = self._slave_host_config_helper.get_slave_lag_threshold()
        current_slave_lag = slave_status['Seconds_Behind_Master']
        if (current_slave_lag is None or
            int(current_slave_lag) > slave_lag_threshold):
            return MHA_slave_helper.CODE_ERR_SLAVE_LAG

        # Check if read_only flag is set
        if self._slave_host.is_read_only() == False:
            return MHA_slave_helper.CODE_ERR_READ_ONLY

        # We have come here meaning that the slave is healthy
        return MHA_slave_helper.CODE_SUCCESS

    def get_return_code_string(self, code):
        if code == MHA_slave_helper.CODE_SUCCESS:
            return "[%s] Slave is in SYNC" % self._slave_hostname

        if code == MHA_slave_helper.CODE_ERR_MYSQL_CONN:
            return "[%s] Error connecting to MySQL on the slave" % self._slave_hostname

        if code == MHA_slave_helper.CODE_ERR_READ_ONLY:
            return "[%s] READ_ONLY flag is not set on the slave" % self._slave_hostname

        if code == MHA_slave_helper.CODE_ERR_SLAVE_RUNNING:
            return "[%s] IO and/or SQL threads are not running on the slave" % self._slave_hostname

        if code == MHA_slave_helper.CODE_ERR_SLAVE_LAG:
            return "[%s] Slave lag is more than the allowed threshold" % self._slave_hostname

        return "[%s] Unknown error code" % self._slave_hostname
