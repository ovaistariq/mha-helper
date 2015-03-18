#
# Cookbook Name:: mysql_replication
# Recipe:: replication_user
#

# Setup credentials that are used by the database cook LWRPs
connection_info = {
  host: "127.0.0.1",
  username: "root",
  password: node["mysql"]["root_password"]
}

# This is a prerequisite for the database cookbook
mysql2_chef_gem "default" do
  client_version node["mysql"]["version"]
  action :install
end

# Setup the grants for the slave users
# But create the users only if we are running on the master
if node["mysql"]["server"]["read_only"] == 0
  node["mysql"]["replication"]["slaves"].each do |slave_host_ip|
    mysql_database_user node["mysql"]["replication"]["user"] do
      connection connection_info
      password node["mysql"]["replication"]["password"]
      host slave_host_ip
      privileges [:all]
      action :grant
    end
  end
end