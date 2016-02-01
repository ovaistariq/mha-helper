#
# Cookbook Name:: mysql_replication
# Attributes:: default
#
# Copyright 2015, Ovais Tariq <me@ovaistariq.net>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# MySQL version
default["mysql"]["version"] = "5.6"

# MySQL root user
default["mysql"]["root_password"] = "root"

# MySQL replication credentials
default["mysql"]["replication"]["user"] = "repl"
default["mysql"]["replication"]["password"] = "repl"

# MySQL MHA access
default["mysql"]["mha"]["user"] = "mha"
default["mysql"]["mha"]["password"] = "mha"

# Setup the barebone attribute used within the cookbook
default['mysql_replication'] = Hash.new

# This is needed temporarily for the first converge
default["mysql"]["mha"]["writer_vip_cidr"] = "192.168.30.100/24"
default["mysql"]["mha"]["writer_vip"] = "192.168.30.100"
default["mysql"]["mha"]["cluster_interface"] = "eth1"

# MySQL configuration
# GENERAL #
default["mysql"]["server"]["socket"]                            = "/var/lib/mysql/mysql.sock"
default["mysql"]["server"]["port"]                              = "3306"

# DATA STORAGE #
default["mysql"]["server"]["datadir"]                           = "/var/lib/mysql"
default["mysql"]["server"]["logdir"]                            = "/var/lib/mysql"

# BINARY LOGGING #
default["mysql"]["server"]["log_bin_filename"]                  = "mysql-bin"
default["mysql"]["server"]["log_bin"]                           = "#{node["mysql"]["server"]["logdir"]}/#{node["mysql"]["server"]["log_bin_filename"]}"
default["mysql"]["server"]["sync_binlog"]                       = 0

# REPLICATION #
default["mysql"]["server"]["read_only"]                         = 1
default["mysql"]["server"]["log_slave_updates"]                 = 1
default["mysql"]["server"]["relay_log"]                         = "#{node["mysql"]["server"]["logdir"]}/relay-bin"
default["mysql"]["server"]["slave_net_timeout"]                 = 60

# InnoDB #
default["mysql"]["server"]["innodb_buffer_pool_size"]           = "16M"

# LOGGING #
default["mysql"]["server"]["log_error"]                         = "#{node["mysql"]["server"]["logdir"]}/mysql-error.log"
default["mysql"]["server"]["log_warnings"]                      = 2
