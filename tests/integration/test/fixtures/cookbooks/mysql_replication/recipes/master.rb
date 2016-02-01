#
# Cookbook Name:: mysql_replication
# Recipe:: master
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

# Set attributes that need to be set differently for the master
node.default["mysql"]["server"]["read_only"] = 0

# Include the base recipe that sets up and configures the MySQL server
include_recipe "mysql_replication::_server"

# During the first converge of master we run 'FLUSH LOGS' to start a fresh
# binlog file that the slaves then can use
bash 'binary logs :flush during first run' do
  user 'root'
  code <<-EOH
  /usr/bin/mysqladmin flush-logs
  EOH
  notifies :create, 'file[/tmp/master_flush_logs_done]', :immediately
  not_if { File.exist?('/tmp/master_flush_logs_done') }
end

file '/tmp/master_flush_logs_done' do
  owner 'root'
  group 'root'
  mode 0755
  action :nothing
end

# During the first converge of master we assign the master VIP, afterwards
# its controlled through MHA
bash 'writer VIP :assign during first run' do
  user 'root'
  code <<-EOH
  ip addr add #{node["mysql"]["mha"]["writer_vip_cidr"]} dev #{node["mysql"]["mha"]["cluster_interface"]}
  arping -q -c 3 -A -I #{node["mysql"]["mha"]["cluster_interface"]} #{node["mysql"]["mha"]["writer_vip"]}
  EOH
  notifies :create, 'file[/tmp/master_writer_vip_done]', :immediately
  not_if { File.exist?('/tmp/master_writer_vip_done') }
end

file '/tmp/master_writer_vip_done' do
  owner 'root'
  group 'root'
  mode 0755
  action :nothing
end
