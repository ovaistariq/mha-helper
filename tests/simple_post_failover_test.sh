#!/usr/bin/env bash

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
