MHA Helper
==========
MHA helper (mha-helper) is a set of helper scripts that supplement in doing proper failover using MHA (https://code.google.com/p/mysql-master-ha/). MHA is responsible for doing the actual failover like finding the most recent slave to failover to and applying differential logs, etc. But it does not deal with pre-failover and post-failover steps, such as the steps that need to be taken before doing a safe failover, such as killing connections, blocking apps from writing while the failover is in progress, etc.

There are two functions of mha-helper:  
1. Execute pre-failover and post-failover steps during an online failover. An online failover is one in which the original master is not dead and the failover is performed for example for maintenance purposes.  
2. Execute pre-failover and post-failover steps during master failover. In this case the original master is dead, meaning either the host is dead or the MySQL server is dead.  

Package Requirements and Dependencies
=====================================
mha-helper is written using Python 2.6 so if you an older version of Python running you must upgrade to Python 2.6.

In addition to Python 2.6, you would need the following packages installed:
+ **MHA** - Of course you need the MHA manager and node packages installed. You can read more about installing MHA and its dependencies here: http://code.google.com/p/mysql-master-ha/wiki/Installation
+ **MySQL-python**

Configuration
=============
mha-helper assumes that it is installed in the location /usr/local/mha-helper and hence all paths in the config file and the helper script are relative to this particular location. You would also need to make sure that password-less SSH access using keys is setup. The MHA configuration file should be stored at the location /usr/local/mha-helper/conf/. Of course, if you need to change the location of the files you will have to modify the configs and the scripts. I will decouple the configuration locations in a later version. 

Please go through this URL for general MHA configuration guidelines: https://code.google.com/p/mysql-master-ha/wiki/Configuration  
And take a look at this URL for all the available MHA configuration options: https://code.google.com/p/mysql-master-ha/wiki/Parameters  

An important things to note is that the MySQL user you specify in the MHA config must have all the privileges together with the **GRANT option**

The important MHA configuration options that tie in mha-helper with MHA are the following and make sure you have them specified in the MHA config:

---
    master_ip_failover_script      = /usr/local/mha-helper/scripts/master_ip_failover.py
    master_ip_online_change_script = /usr/local/mha-helper/scripts/master_ip_online_change.py
---

Let me show you an example of a configuration file:

---
    [server default]
    user                    = mha_helper
    password                = xxx
    ssh_user                = mha_helper
    ssh_options             = '-i /home/mha_helper/.ssh/id_rsa'
    repl_user               = repl
    repl_password           = repl
    master_binlog_dir       = /var/lib/mysql
    manager_workdir         = /var/log/mha/test_cluster
    manager_log             = /var/log/mha/test_cluster/test_cluster.log
    remote_workdir          = /var/log/mha/test_cluster
    master_ip_failover_script      = /usr/local/mha-helper/scripts/master_ip_failover.py
    master_ip_online_change_script = /usr/local/mha-helper/scripts/master_ip_online_change.py

    [server1]
    hostname            = db1
    candidate_master    = 1
    check_repl_delay    = 0

    [server2]
    hostname            = db2
    candidate_master    = 1
    check_repl_delay    = 0

    [server3]
    hostname            = db3
    no_master           = 1

    [server4]
    hostname            = db4
    no_master           = 1
---

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
