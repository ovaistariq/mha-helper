#
# Cookbook Name:: mysql-mha
# Recipe:: dev
#

# Install package dependencies first
for pkg in [ "python-pip", "python-devel" ]
  package pkg
end