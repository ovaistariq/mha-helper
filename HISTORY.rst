.. :changelog:

History
-------

0.4.0 ("2015-11-01")
--------------------

* Completely redesigned MHA Helper.
* MHA Helper is now a Python module.
* MHA Helper now installs scripts inside /usr/bin/
* Paramiko is now used for SSH based communication.
* User's ssh-config file is now parsed to read in additional SSH options if set.
* PyMySQL is now used instead of MySQLdb as the Python MySQL driver.
* Configuration files are now located in /etc/mha-helper with one file per MySQL replication cluster.
* MHA Helper now kills the sleeping threads from the old master after failover.
* MHA Helper writer Virtual IP support is now pluggable and can support more than one implementations. Currently only traditional Virtual IP support has been implemented which involves moving an IP from one machine to the other and broadcasting ARP packets.

0.3.0 ("2013-10-26")
--------------------

* Initial release.
