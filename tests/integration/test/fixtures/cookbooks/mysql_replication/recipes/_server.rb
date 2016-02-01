#
# Cookbook Name:: mysql_replication
# Recipe:: server
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

# Setup the MySQL service
mysql_service "default" do
  port node["mysql"]["server"]["port"]
  data_dir node["mysql"]["server"]["datadir"]
  version node["mysql"]["version"]
  initial_root_password node["mysql"]["root_password"]
  socket node["mysql"]["server"]["socket"]
  action [:create, :start]
end

# Setup the main MySQL configuration
mysql_config "default" do
  source "my.cnf.erb"
  action :create
  notifies :restart, "mysql_service[default]", :immediately
end

# Setup the .my.cnf file for the root user
template "/root/.my.cnf" do
    variables(
        :root_password => node["mysql"]["root_password"],
        :mysql_socket => node["mysql"]["server"]["socket"]
    )
    source "my.cnf.root.erb"
    owner "root"
    group "root"
    mode "0600"
    action :create
end

# Include the recipe that sets up the replication user
include_recipe "mysql_replication::replication_user"

# Include the recipe that sets up the MHA user
include_recipe "mysql_replication::mha_user"

# Include the recipe that creates the test database used during testing
include_recipe "mysql_replication::test_db"
