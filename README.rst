==========
MHA Helper
==========

.. image:: https://img.shields.io/travis/ovaistariq/mha_helper.svg
        :target: https://travis-ci.org/ovaistariq/mha_helper

.. image:: https://img.shields.io/pypi/v/mha_helper.svg
        :target: https://pypi.python.org/pypi/mha_helper

.. image:: https://badges.gitter.im/Join%20Chat.svg
   :alt: Join the chat at https://gitter.im/ovaistariq/mha-helper
   :target: https://gitter.im/ovaistariq/mha-helper?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge


MHA helper is a Python module that supplements in doing proper failover using MHA (https://code.google.com/p/mysql-master-ha/). MHA is responsible for executing the important failover steps such as finding the most recent slave to failover to, applying differential logs, monitoring master for failure, etc. But it does not deal with additional steps that need to be taken before and after failover. These would include steps such as setting the read-only flag, killing connections, moving writer virtual IP, etc.

* Documentation: https://mha-helper.readthedocs.org.

Introduction
------------
There are three functions of mha-helper:

1. Execute pre-failover and post-failover steps during an online failover. An online failover is one in which the original master is not dead and the failover is performed, for example, for maintenance purposes.
2. Execute pre-failover and post-failover steps during a hard master failover. In this case the original master is dead, meaning either the host is dead or the MySQL server process has died.
3. Daemonize the monitor that monitors the masters for failure.

Package Requirements and Dependencies
-------------------------------------
First and foremost MHA itself needs to be installed. You need the MHA manager and node packages installed. You can read more about installing MHA and its dependencies here: http://code.google.com/p/mysql-master-ha/wiki/Installation

MHA Helper has been developed and tested against Python 2.6 and 2.7. Versions < 2.6 are not supported.

In addition to Python 2.6, the following Python modules are needed:
* paramiko
* PyMySQL

There are other MHA specific requirements, please go through the link below to read about them: https://code.google.com/p/mysql-master-ha/wiki/Requirements

Configuration
-------------
MHA Helper uses ini-style configuration files.

The Helper expects one configuration file per MySQL replication cluster present in the directory */etc/mha-helper*.

The configuration file has a *'default'* section and then one section per host for every host in the MySQL replication cluster.
The following configuration options are supported:

writer_vip_cidr
    The virtual IP that is assigned to the MySQL master. This must be in CIDR format.
vip_type
    The type of VIP which can be anyone of these:
    * none : When this is set then MHA Helper does not do VIP management
    * metal : When this is set then traditional baremetal-style VIP management is done using the standard *ip* command
    * aws : When this is set then VIP management is done in a way relevant to AWS
    * openstack : When this is set then VIP management is done in a way relevant to OpenStack
report_email
    The email address which receives the email notification when a MySQL failover is performed
smtp_host
    The SMTP host that is used to send the failover report email
requires_sudo
    Some of the system commands executed as part of the failover process require either the use of a privileged user or a user with sudo privileges. Set this to *no* when the system user does not need to execute commands using sudo, set to *yes* otherwise
cluster_interface
    The ethernet interface on the machine that gets the Virtual IP assigned or removed

All the options above can be specified either in the default section or in the host specific sections. Values specified in host specific sections override the values specified in the *default* section.

Let me show you an example configuration file:

::
    [default]
    requires_sudo               = yes
    vip_type                    = metal
    writer_vip_cidr             = 192.168.10.155/24
    cluster_interface           = eth1
    report_email                = me@ovaistariq.net
    smtp_host                   = localhost

    [db10]
    cluster_interface           = eth10

    [db11]

    [db12]
    report_email                = notify@host-db12.com
    smtp_host                   = localhost2
    requires_sudo               = no

Apart from the configuration file needed by MHA Helper, you also need to setup the MHA specific application configuration file which defines the master-slave hosts. You can find details on how the application configuration file should be written here: https://code.google.com/p/mysql-master-ha/wiki/Configuration#Writing_an_application_configuration_file

I would also suggest that you go through this link to see all the available MHA configuration options: https://code.google.com/p/mysql-master-ha/wiki/Parameters

Following are the important options that must be specified in the MHA application configuration file:

* user
* password
* ssh_user
* manager_workdir
* manager_log
* master_ip_failover_script       = /usr/bin/master_ip_hard_failover_helper
* master_ip_online_change_script  = /usr/bin/master_ip_online_failover_helper
* report_script                   = /usr/bin/master_failover_report


Below is an example application configuration file:

::
    [server default]
    user                            = mha_helper
    password                        = helper
    ssh_user                        = mha_helper
    ssh_port                        = 2202
    repl_user                       = replicator
    repl_password                   = replicator
    master_binlog_dir               = /var/log/mysql
    manager_workdir                 = /var/log/mha/test_cluster
    manager_log                     = /var/log/mha/test_cluster/test_cluster.log
    remote_workdir                  = /var/log/mha/test_cluster
    master_ip_failover_script       = /usr/bin/master_ip_hard_failover_helper
    master_ip_online_change_script  = /usr/bin/master_ip_online_failover_helper
    report_script                   = /usr/bin/master_failover_report

    [server1]
    hostname            = db10
    candidate_master    = 1
    check_repl_delay    = 0

    [server2]
    hostname            = db11
    candidate_master    = 1
    check_repl_delay    = 0

    [server3]
    hostname            = db12
    no_master           = 1

Pre-failover Steps During Online Failover
-----------------------------------------
To make sure that the failover is safe and does not cause any data inconsistencies, MHA Helper takes the following steps before the failover:

1. Set read_only on the new master to avoid any data inconsistencies
2. Remove the writer VIP from the original master if vip_type != none
3. Set read_only=1 on the original master
4. Wait up to 5 seconds for all connected threads to disconnect on the original master
5. Terminate all the connections except those that are replication-related, the connection made by MHA Helper and the connections opened by the *'system user'*
6. Disconnect from the original master


If any of the above steps fail, any changes made during pre-failover are rolled back.

Post-failover Steps During Online Failover
------------------------------------------
Once MHA has switched the masters and reconfigured replication, the MHA Helper takes the following steps:

1. Remove the read_only flag from the new master
2. Assign the writer VIP to the new master if vip_type != none


Pre-failover Steps During Hard Failover
---------------------------------------
If the original master is accessible via SSH, i.e. in cases where MySQL crashed and stopped but the host is still up, then MHA Helper takes the following step:

1. Remove the writer VIP from the original master if vip_type != none


Post-failover Steps During Hard Failover
----------------------------------------
Once MHA has switched the masters and reconfigured replication, the MHA Helper takes the following steps:

1. Remove the read_only flag from the new master
2. Assign the writer VIP to the new master if vip_type != none


Automated Failover and Monitoring via MHA Manager Daemon
--------------------------------------------------------
**TODO**


Manual Failover Examples
------------------------
Once everything is configured and running, doing the failover is pretty simple.

Do a failover when the master db1 goes down:

    /usr/bin/mysql_failover -d db1 -c /etc/mha/test_cluster.conf

Do an online failover:

    /usr/bin/mysql_online_failover -c /etc/mha/test_cluster.conf


Using Non-root User
===================
If you are using non-root user to connect to master-slave hosts via ssh (the user that you use for this purpose is taken from the *ssh_user* option) then you need to make sure that the user can execute the following commands:
* /sbin/ip
* /sbin/arping

The user should be able to execute the above commands using sudo, and should not have to provide a password. This can accomplished by editing the file /etc/sudoers using visudo and adding the following lines:

::
    mha_helper   ALL=NOPASSWD: /sbin/ip, /sbin/arping

In the example above I am assuming that ssh_user=mha_helper.

Some General Recommendations
----------------------------
There are some general recommendations that I want to make, to prevent race-condition that can cause data inconsistencies:
* Do not persist interface with writer VIP in the network scripts. This is important for example in cases where both the candidate masters go down i.e. hosts go down and then come back online. In which case we should need to manually intervene because there is no automated way to find out which MySQL server should be the source of truth
* Persist read_only in the MySQL configuration file of all the candidate masters as well. This is again important for example in cases where both the candidate masters go down.
