#
# Cookbook Name:: base_test_setup
# Recipe:: dev_install
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

include_recipe 'python::pip'

# Remove the mha-helper package installed via yum
package node["mysql_mha"]["helper"]["package"] do
  action :remove
end

python_pip '/tmp/mha-helper' do
  version 'latest'
  options '-e'
end

include_recipe 'base_test_setup::sysbench'
