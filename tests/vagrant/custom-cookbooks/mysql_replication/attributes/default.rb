#
# Cookbook Name:: mysql_replication
# Attributes:: default
#

# MySQL version
default["mysql"]["version"] = "5.6"

# MySQL root user
default["mysql"]["root_password"] = "root"

# MySQL replication credentials
default["mysql"]["replication"]["user"] = "repl"
default["mysql"]["replication"]["password"] = "repl"

# MySQL configuration
# GENERAL #
default["mysql"]["server"]["user"]                              = "mysql"
default["mysql"]["server"]["socket"]                            = "/var/lib/mysql/mysql.sock"
default["mysql"]["server"]["port"]                              = "3306"
default["mysql"]["server"]["pidfile"]                           = "/var/run/mysqld/mysql.pid"

# DATA STORAGE #
default["mysql"]["server"]["datadir"]                           = "/var/lib/mysql"
default["mysql"]["server"]["logdir"]                            = "/var/lib/mysql"

# BINARY LOGGING #
default["mysql"]["server"]["log_bin"]                           = "#{node["mysql"]["server"]["logdir"]}/mysql-bin"
default["mysql"]["server"]["sync_binlog"]                       = 0

# REPLICATION #
default["mysql"]["server"]["server_id"]                         = node["ipaddress"].gsub(/^.{0,3}|[.]/, "")
default["mysql"]["server"]["read_only"]                         = 1
default["mysql"]["server"]["log_slave_updates"]                 = 1
default["mysql"]["server"]["relay_log"]                         = "#{node["mysql"]["server"]["logdir"]}/relay-bin"
default["mysql"]["server"]["slave_net_timeout"]                 = 60

# InnoDB #
default["mysql"]["server"]["innodb_buffer_pool_size"]           = "128M"

# LOGGING #
default["mysql"]["server"]["log_error"]                         = "#{node["mysql"]["server"]["logdir"]}/mysql-error.log"
default["mysql"]["server"]["log_warnings"]                      = 2