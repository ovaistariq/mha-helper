#!/usr/bin/env bash

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

writer_vip="192.168.1.155"
mysql_user="mha_helper"
mysql_password="mha_helper"

db1_eth0_mac="00:24:A8:10:E8:12"
db2_eth0_mac="00:22:B9:32:B0:47"

db1_eth0_ip="192.168.1.50"
db2_eth0_ip="192.168.1.51"

app_servers="app01 app02 app03"
slave_servers="db2 db3 db4"

echo "-- Checking ARP cache entries for writer VIP mapping entry"
for host in $app_servers
do
        arp_mac_entry=$(ssh $host "/sbin/arp -an" | grep "$writer_vip" | awk '{print $4}')
        
        if [[ "$arp_mac_entry" == "$db1_eth0_mac" ]]
        then
                writer_vip_host=db1
        else
                writer_vip_host=db2
        fi

        printf "host: %5s maps VIP to %s\n" "$host" "$writer_vip_host"
done

echo
echo "-- Checking Hostname from MySQL client"
for host in $app_servers
do
        mysql_cmd="/usr/bin/mysql -h${writer_vip} -u${mysql_user} -p${mysql_password}"
        mysql_hostname=$(ssh $host "$mysql_cmd -e \"show variables like 'hostname'\" -NB" | awk '{print $2}')
        printf "host: %5s sees %s\n" "$host" "$mysql_hostname"
done

echo
echo "-- Checking Slaves"
for host in $slave_servers
do
        mysql_cmd="/usr/bin/mysql -h${host} -u${mysql_user} -p${mysql_password}"
        slave_status=$($mysql_cmd -e "show slave status" --vertical)

        master_ip=$(ssh $host "$mysql_cmd -e \"show slave status\" --vertical" | awk '/Master_Host/ {print $2}')
        slave_io_running=$(ssh $host "$mysql_cmd -e \"show slave status\" --vertical" | awk '/Slave_IO_Running/ {print $2}')
        slave_sql_running=$(ssh $host "$mysql_cmd -e \"show slave status\" --vertical" | awk '/Slave_SQL_Running/ {print $2}')

        if [[ "$master_ip" == "$db1_eth0_ip" ]]
        then 
                master_host=db1
        else
                master_host=db2
        fi

        printf "slave %4s: master %4s, IO_thread %3s, SQL_thread %3s\n" "$host" "$master_host" "$slave_io_running" "$slave_sql_running"
done
