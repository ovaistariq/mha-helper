#
# Cookbook Name:: mysql_replication
# Recipe:: server
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
  notifies :restart, "mysql_service[default]"
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