#
# Cookbook Name:: mysql_replication
# Recipe:: slave
#

# Set attributes that need to be set differently for the master
node.default["mysql"]["server"]["read_only"] = 1

# Include the base recipe that sets up and configures the MySQL server
include_recipe "mysql_replication::_server"
