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

require 'rspec/core/rake_task'
require 'rubocop/rake_task'
require 'foodcritic'
require 'kitchen'
require 'mixlib/shellout'
require 'kitchen/rake_tasks'

# Style tests. Rubocop and Foodcritic
namespace :style do
  desc "Run RuboCop style and lint checks"
  task :rubocop do
    RuboCop::RakeTask.new(:rubocop) do |t|
      t.options = ["-D"]
    end
  end

  desc "Run Foodcritic lint checks"
  task :foodcritic do
    FoodCritic::Rake::LintTask.new(:foodcritic) do |t|
      t.options = { :fail_tags => ["any"] }
    end
  end
end

desc "Run all style tests"
task :style => ['style:rubocop', 'style:foodcritic']

# Integration tests. Kitchen.ci
namespace :integration do
  desc 'Setup the test-kitchen vagrant instances'
  task :vagrant_setup do
    Kitchen.logger = Kitchen.default_file_logger
    Kitchen::Config.new.instances.each do |instance|
      # this happens serially because virualbox/vagrant can't handle
      # parallel vm creation
      instance.create()

      # Initial converge
      instance.converge()
    end
  end

  desc 'Verify the test-kitchen vagrant instances'
  task :vagrant_verify do
    Kitchen.logger = Kitchen.default_file_logger
    Kitchen::Config.new.instances.each do |instance|
      # Run the integration tests now
      instance.verify()
    end
  end
end

# TODO: implement sysbench based tests
# sysbench --test=/tmp/kitchen/cache/sysbench/sysbench/tests/db/oltp.lua --db-driver=mysql --oltp-tables-count=8 --oltp-table-size=10000 --mysql-table-engine=innodb --mysql-user=mha --mysql-password=mha --mysql-host=192.168.30.100 --mysql-db=test prepare
#
# sysbench --test=/tmp/kitchen/cache/sysbench/sysbench/tests/db/oltp.lua --db-driver=mysql --oltp-tables-count=8 --oltp-table-size=10000 --mysql-table-engine=innodb --mysql-user=mha --mysql-password=mha --mysql-host=192.168.30.100 --mysql-db=test --max-time=930 --num-threads=8 --max-requests=0 --oltp-reconnect --mysql-ignore-errors=2013 --report-interval=10 run

# Clean up
namespace :cleanup do
  desc 'Destroy test-kitchen instances'
  task :kitchen_destroy do
    destroy = Kitchen::RakeTasks.new do |obj|
      def obj.destroy
        config.instances.each(&:destroy)
      end
    end
    destroy.destroy
  end
end

desc 'Generate the setup'
task setup: ['integration:vagrant_setup']

desc 'Clean up generated files'
task cleanup: ['cleanup:kitchen_destroy']

desc 'Run full integration'
task integration: ['cleanup:kitchen_destroy', 'integration:vagrant_setup', 'integration:vagrant_verify', 'cleanup:kitchen_destroy']

# Default
task default: ['style', 'spec', 'integration', 'cleanup']
