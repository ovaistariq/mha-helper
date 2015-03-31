#
# Cookbook Name:: mysql-mha
# Attributes:: node
#

# MHA node package related
default["mysql_mha"]["node"]["version"] = "0.56-0.el6"
default["mysql_mha"]["node"]["package_name"] = "mha4mysql-node-#{node["mysql_mha"]["node"]["version"]}.noarch.rpm"
default["mysql_mha"]["node"]["source"] = "https://72003f4c60f5cc941cd1c7d448fc3c99e0aebaa8.googledrive.com/host/0B1lu97m8-haWeHdGWXp0YVVUSlk/#{node["mysql_mha"]["node"]["package_name"]}"
default["mysql_mha"]["node"]["checksum"] = "1e287e762150e6cd37df9420ecbb6c40e309832b5d3d8c778572867501c297ad"

# MHA node configuration related
default["mysql_mha"]["node"]["mysql_port"] = "3306"
default["mysql_mha"]["node"]["mysql_binlog_dir"] = "/var/lib/mysql"
default["mysql_mha"]["node"]["ssh_port"] = "22"
default["mysql_mha"]["node"]["requires_sudo"] = "yes"
default["mysql_mha"]["node"]["cluster_interface"] = "eth0"