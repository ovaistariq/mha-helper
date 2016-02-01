#
# Cookbook Name:: base_test_setup
# Recipe:: sysbench
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

include_recipe 'build-essential::default'

%w(automake libtool libaio libaio-devel git rubygems ruby-devel rpm-build python-pip).each do |pkg|
  package pkg do
    action :install
  end
end

git "#{Chef::Config[:file_cache_path]}/sysbench" do
  repository 'https://github.com/akopytov/sysbench.git'
  revision '0.5'
  action :sync
  notifies :run, 'bash[sysbench :install from source]', :immediately
  not_if 'which sysbench'
end

bash 'sysbench :install from source' do
  user 'root'
  cwd "#{Chef::Config[:file_cache_path]}/sysbench"
  code <<-EOH
  ./autogen.sh
  ./configure
  make
  make install
  EOH
  action :nothing
end
