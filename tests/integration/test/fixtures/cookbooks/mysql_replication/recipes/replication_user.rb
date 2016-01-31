#
# Cookbook Name:: mysql_replication
# Recipe:: replication_user
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

# Setup credentials that are used by the database cook LWRPs
connection_info = {
  host: "127.0.0.1",
  username: "root",
  password: node["mysql"]["root_password"],
  port: node["mysql"]["server"]["port"]
}

# This is a prerequisite for the database cookbook
mysql2_chef_gem "default" do
  client_version node["mysql"]["version"]
  action :install
end

# Setup the grants for the slave users
# But create the users only if we are running on the master
mysql_database_user node["mysql"]["replication"]["user"] do
  connection connection_info
  password node["mysql"]["replication"]["password"]
  host '%'
  privileges [:"replication slave", :"replication client"]
  action :grant
end
