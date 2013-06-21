MHA Helper
==========
MHA helper (mha-helper) is a set of helper scripts that supplement in doing proper failover using MHA (https://code.google.com/p/mysql-master-ha/). MHA is responsible for executing the important failover steps such as finding the most recent slave to failover to, applying differential logs, monitoring master for failure, etc. But it does not deal with additional steps that need to be taken before and after failover. These would include steps such as setting the read-only flag, killing connections, moving writer virtual IP, etc. Furthermore, the monitor that does the monitoring of masters to test for failure is not daemonized and exits after performing the failover which might not be intended, because of course we need the monitor to keep monitoring even after failover.

There are three functions of mha-helper:  
1. Execute pre-failover and post-failover steps during an online failover. An online failover is one in which the original master is not dead and the failover is performed for example for maintenance purposes.  
2. Execute pre-failover and post-failover steps during master failover. In this case the original master is dead, meaning either the host is dead or the MySQL server is dead.  
3. Daemonize the monitor that monitors the masters for failure.  

Package Requirements and Dependencies
=====================================
mha-helper is written using Python 2.6 so if you have an older version of Python running you must upgrade to Python 2.6 or change the shebang line to point to the appropriate python 2.6 binary.

In addition to Python 2.6, you would need the following packages installed:
+ **MHA** - Of course you need the MHA manager and node packages installed. You can read more about installing MHA and its dependencies here: http://code.google.com/p/mysql-master-ha/wiki/Installation
+ **MySQL-python**

Configuration
=============
There are two configuration files needed by mha-helper, one of them is the mha-helper specific global configuration file named **global.conf** and the other is the MHA specific application configuration file. Currently mha-helper always assumes that the global configuration file is available in the conf directory inside the mha-helper directory. So if you have mha-helper at the location /usr/local/mha-helper, then the global configuration file will be available at /usr/local/mha-helper/conf/global.conf  

The **global configuration** file has a section named **'default'** and also has other sections named after the hostnames of the master and slave servers that are being managed by MHA. Moreover the options defined in the host sections override the options defined in the default section.  

mha-helper supports the following options in the **global configuration** file that can be specified in the **'default'** section:  

+ requires_sudo
+ manage_vip
+ writer_vip_cidr
+ writer_vip
+ cluster_interface
+ report_email


All the options above can also be specified in the host specific sections and they will override the values of options defined in the 'default' section. The host specific section has one additional option:  

+ cluster_conf_path


Note that you must have separate sections defined for each of the master-slave servers that MHA is managing. Let me show you an example global configuration file:

---
    [default]
    requires_sudo       = yes
    manage_vip          = yes
    writer_vip_cidr     = 192.168.1.155/24
    writer_vip          = 192.168.1.155
    cluster_interface   = eth0
    report_email        = ovaistariq@gmail.com

    [db1]
    cluster_conf_path   = /usr/local/mha-helper/conf/test_cluster.conf.sample

    [db2]
    cluster_conf_path   = /usr/local/mha-helper/conf/test_cluster.conf.sample

    [db3]
    cluster_conf_path   = /usr/local/mha-helper/conf/test_cluster.conf.sample

    [db4]
    cluster_conf_path   = /usr/local/mha-helper/conf/test_cluster.conf.sample
---

Note that this **global configuration** file is specific to mha-helper and is different from the global configuration file specific to MHA.  

Apart from the global configuration file is the MHA specific application configuration file which basically defines the master-slave hosts. Please read the content at this link to see how the application configuration file should be written: https://code.google.com/p/mysql-master-ha/wiki/Configuration#Writing_an_application_configuration_file and go through this URL to see all the available MHA configuration options: https://code.google.com/p/mysql-master-ha/wiki/Parameters


Following are the important options that must be specified in the MHA application configuration file:  

+ user
+ password
+ ssh_user
+ manager_workdir
+ manager_log
+ master_ip_failover_script       = /usr/local/mha-helper/scripts/master_ip_failover
+ master_ip_online_change_script  = /usr/local/mha-helper/scripts/master_ip_online_change
+ report_script                   = /usr/local/mha-helper/scripts/failover_report


Let me show you an example application configuration file:

---
    [server default]
    user                            = mha_helper
    password                        = helper
    ssh_user                        = mysql
    ssh_options                     = '-i /home/mysql/.ssh/id_rsa'
    ssh_port                        = 2202
    repl_user                       = repl
    repl_password                   = repl
    master_binlog_dir               = /var/lib/mysql
    manager_workdir                 = /var/log/mha/test_cluster
    manager_log                     = /var/log/mha/test_cluster/test_cluster.log
    remote_workdir                  = /var/log/mha/test_cluster
    master_ip_failover_script       = /usr/local/mha-helper/scripts/master_ip_failover
    master_ip_online_change_script  = /usr/local/mha-helper/scripts/master_ip_online_change
    report_script                   = /usr/local/mha-helper/scripts/failover_report

    [server1]
    hostname            = repl01
    candidate_master    = 1
    check_repl_delay    = 0

    [server2]
    hostname            = repl02
    candidate_master    = 1
    check_repl_delay    = 0

    [server3]
    hostname            = repl03
    no_master           = 1
---


An important things to note is that the MySQL user you specify in the MHA config must have all the privileges.


Pre-failover Steps During an Online Failover
============================================
To make sure that the failover is safe and does not cause any data inconsistencies, mha-helper takes the following steps before the failover:

1. Set read_only on the new master to avoid any data inconsistencies
2. Execute the following steps on the original master with binlogging disabled so that these are not replicated to the new master:
   1. Revoke ALL privileges from the users on original master so that no one can write
   2. Wait upto 5 seconds for all connected threads to disconnect and then terminate the ones that are still connected
   3. Set read_only=1 on the original master
   4. Disconnect from the original master and restore binlogging

If any of the above steps fail, any changes made during pre-failover are rolledback.

Post-failover Steps During an Online Failover
============================================
Once the failover is completed by MHA, mha-helper takes the following steps:

1. Remove the read_only flag from the new master
2. Regrant privileges that were revoked during the pre-failover steps

**Note that the pre-failover and post-failover steps revoke and grant user privileges respectively. For the user accounts to be safely restored on post-failover, its important to make sure that the users that exist on both the original master and the current master are the same.**

Pre-failover Steps During Master Failover
=========================================
Currently nothing is done in the pre-failover stage.

Post-failover Steps During Master Failover
==========================================
Once the failover is completed by MHA, mha-helper script takes the following steps:

1. Remove the read_only flag from the new master

Usage Examples
==============
Once everything is configured and running, doing the failover is pretty simple.

Do a failover when the master db1 goes down:

    /usr/local/mha-helper/bin/mysql_failover db1

Do an online failover:

    /usr/local/mha-helper/bin/mysql_online_failover
