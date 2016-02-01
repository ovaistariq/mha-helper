#
# Cookbook Name:: mysql_replication
# Recipe:: slave
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
node.default["mysql"]["server"]["read_only"] = 1

# Include the base recipe that sets up and configures the MySQL server
include_recipe "mysql_replication::_server"

# During the first converge of slave we setup replication
master_host = node['mysql_replication']['master_host']
repl_user = node["mysql"]["replication"]["user"]
repl_pass = node["mysql"]["replication"]["password"]
log_bin_file = "#{node['mysql']['server']['log_bin_filename']}.000002"

bash 'slave replication :change_master during first run' do
  user 'root'
  code <<-EOH
  /usr/bin/mysql -e 'CHANGE MASTER TO MASTER_HOST="#{master_host}", MASTER_USER="#{repl_user}", MASTER_PASSWORD="#{repl_pass}", MASTER_LOG_FILE="#{log_bin_file}", MASTER_LOG_POS=0; START SLAVE;'
  EOH
  notifies :create, 'file[/tmp/slave_replication_done]', :immediately
  not_if { File.exist?('/tmp/slave_replication_done') }
end

file '/tmp/slave_replication_done' do
  owner 'root'
  group 'root'
  mode 0755
  action :nothing
end
