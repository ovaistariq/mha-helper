#
# Cookbook Name:: mysql-mha
# Recipe:: manager
#

# Some of the dependent packages are only available in the EPEL repo hence we set it up here
include_recipe "yum-epel"

# The manager needs the node package to be installed as well
include_recipe "mysql-mha::node"

# Setup file paths
src_filepath = "#{Chef::Config['file_cache_path']}/#{node["mysql_mha"]["manager"]["package_name"]}"

# Install package dependencies
for pkg in [ "perl-Config-Tiny", "perl-Log-Dispatch", "perl-Parallel-ForkManager", "perl-Mail-Sendmail", "perl-Mail-Sender" ]
  package pkg
end

# Download the MHA manager RPM
remote_file src_filepath do
  owner "root"
  group "root"
  mode "0644"
  source "#{node["mysql_mha"]["manager"]["source"]}"
  checksum node["mysql_mha"]["manager"]["checksum"]
  notifies :install, "package[mha4mysql-manager]", :immediately
end

# Install the MHA manager RPM
package "mha4mysql-manager" do
  action  :install
  source src_filepath
  action :nothing
end