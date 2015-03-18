#
# Cookbook Name:: mysql_replication
# Recipe:: master
#

# Set attributes that need to be set differently for the master
node.default["mysql"]["server"]["read_only"] = 0

# Include the base recipe that sets up and configures the MySQL server
include_recipe "mysql_replication::_server"

# Include the recipe that sets up the replication user
include_recipe "mysql_replication::replication_user"