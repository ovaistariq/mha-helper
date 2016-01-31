require 'spec_helper'

set :backend, :exec

puts "os: #{os}"

describe command('whoami') do
  its(:stdout) { should match /root/ }
end

describe 'mha4mysql-node package is installed' do
  describe package('mha4mysql-node') do
    it { should be_installed }
  end
end

describe 'mha4mysql-manager package is installed' do
  describe package('mha4mysql-manager') do
    it { should be_installed }
  end
end

describe 'python-mha_helper package is installed' do
  describe package('python-mha_helper') do
    it { should be_installed }
  end
end

describe 'MySQL replication is setup correctly and MHA can reach MySQL and SSH' do
  describe command("/usr/bin/masterha_check_repl --conf /etc/mha/test_pod.conf") do
    its(:stdout) { should match /MySQL Replication Health is OK./ }
  end
end
