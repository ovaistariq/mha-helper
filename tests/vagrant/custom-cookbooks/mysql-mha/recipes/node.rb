#
# Cookbook Name:: mysql-mha
# Recipe:: node
#

# Setup file paths
src_filepath = "#{Chef::Config['file_cache_path']}/#{node["mysql_mha"]["node"]["package_name"]}"

# Installing dependency packages first
package "perl-DBD-MySQL"

# Download the MHA node RPM
remote_file src_filepath do
  owner "root"
  group "root"
  mode "0644"
  source "#{node["mysql_mha"]["node"]["source"]}"
  checksum node["mysql_mha"]["node"]["checksum"]
  notifies :install, "package[mha4mysql-node]", :immediately
end

# Install the MHA manager RPM
package "mha4mysql-node" do
  action  :install
  source src_filepath
  action :nothing
end