#!/usr/bin/env ruby

require 'optparse'
require 'logger'
require 'open3'
require 'rubygems' 
require 'net/ssh'

### Colorized Logger ###
# source: https://gist.githubusercontent.com/janlelis/962344/raw/logger-colors.rb
class Logger
  module Colors
    VERSION = '1.0.0'

    NOTHING      = '0;0'
    BLACK        = '0;30'
    RED          = '0;31'
    GREEN        = '0;32'
    BROWN        = '0;33'
    BLUE         = '0;34'
    PURPLE       = '0;35'
    CYAN         = '0;36'
    LIGHT_GRAY   = '0;37'
    DARK_GRAY    = '1;30'
    LIGHT_RED    = '1;31'
    LIGHT_GREEN  = '1;32'
    YELLOW       = '1;33'
    LIGHT_BLUE   = '1;34'
    LIGHT_PURPLE = '1;35'
    LIGHT_CYAN   = '1;36'
    WHITE        = '1;37'

    SCHEMA = {
      STDOUT => %w[nothing green brown red purple cyan],
      STDERR => %w[nothing green yellow light_red light_purple light_cyan],
    }
  end
end

class Logger
  alias format_message_colorless format_message

  def format_message(level, *args)
    if Logger::Colors::SCHEMA[@logdev.dev]
      color = begin
        Logger::Colors.const_get \
          Logger::Colors::SCHEMA[@logdev.dev][Logger.const_get(level.sub "ANY","UNKNOWN")].to_s.upcase
      rescue NameError
        "0;0"
      end
      "\e[#{ color }m#{ format_message_colorless(level, *args) }\e[0;0m" 
    else
      format_message_colorless(level, *args)
    end
  end
end
### End Colorized Logger ###

### Vagrant cluster configuration options ###
class Cluster_vagrant_config
  @mha_manager_vm_name = "manager"
  @mha_master_vm_name = "master"
  @mha_node1_vm_name = "node1"
  @mha_node2_vm_name = "node2"

  @mha_manager_ip  = "192.168.30.10"
  @mha_master_ip   = "192.168.30.11"
  @mha_node1_ip    = "192.168.30.12"
  @mha_node2_ip    = "192.168.30.13"

  @mha_helper_path_on_vm = "/home/vagrant/mha-helper"

  @mysql_socket_path = "/var/lib/mysql/mysql.sock"
  @mysql_root_password = "r00t"
  @mysql_replication_user = "repl"
  @mysql_replication_password = "repl"

  class << self
    attr_accessor :mha_manager_vm_name
    attr_accessor :mha_master_vm_name
    attr_accessor :mha_node1_vm_name
    attr_accessor :mha_node2_vm_name
    attr_accessor :mha_manager_ip
    attr_accessor :mha_master_ip
    attr_accessor :mha_node1_ip
    attr_accessor :mha_node2_ip
    attr_accessor :mha_helper_path_on_vm
    attr_accessor :mysql_socket_path
    attr_accessor :mysql_root_password
    attr_accessor :mysql_replication_user
    attr_accessor :mysql_replication_password
  end
end
### End Vagrant cluster configuration options ###


class Cluster_test_vagrant
  def initialize()
    # Set environment variables that are read by test-kitchen
    ENV["MHA_MANAGER_HOST_IP"]  = Cluster_vagrant_config.mha_manager_ip
    ENV["MHA_MASTER_HOST_IP"]   = Cluster_vagrant_config.mha_master_ip
    ENV["MHA_NODE1_HOST_IP"]    = Cluster_vagrant_config.mha_node1_ip
    ENV["MHA_NODE2_HOST_IP"]    = Cluster_vagrant_config.mha_node2_ip

    ENV["MHA_HELPER_PATH_ON_VM"]  = Cluster_vagrant_config.mha_helper_path_on_vm

    ENV["MYSQL_SOCKET_PATH"]  = Cluster_vagrant_config.mysql_socket_path
    ENV["MYSQL_ROOT_PASSWORD"]  = Cluster_vagrant_config.mysql_root_password
    ENV["MYSQL_REPLICATION_USER"]  = Cluster_vagrant_config.mysql_replication_user
    ENV["MYSQL_REPLICATION_PASSWORD"]  = Cluster_vagrant_config.mysql_replication_password

    # Setup the logger
    @logger = Logger.new(STDOUT)
    @logger.level = Logger::INFO
    @logger.datetime_format = '%Y-%m-%d %H:%M:%S'
    @logger.formatter = proc do |severity, datetime, progname, msg|
      "[#{datetime}] #{msg}\n"
    end

    # Store the state of the virtual machines
    @state = {}
  end

  def init_cluster()
    @logger.info("Initializing the MySQL replication cluster ...")

    # Initialize the VMs using vagrant
    vagrant_up()

    # Update the internal state with the state of the VMs
    update_state()

    # Provision the VMs using Chef
    chef_client_provision_local_mode()

    # Setup replication between the master and the slave nodes
    setup_replication()

    # Create the test schema on the master and let it replicate
    setup_test_schema()

    # Wait for slaves to get caught up to the master
    wait_slave_catchup()
  end

  def provision_cluster()
    @logger.info("Provisioning cluster using Chef")

    # Update the internal state with the state of the VMs
    update_state()

    # Provision the VMs using chef-client in local mode
    chef_client_provision_local_mode()
  end

  def destroy_cluster()
    @logger.info("Destroying cluster")

    # Update the internal state with the state of the VMs
    update_state()

    # Destroy all the VMs
    vagrant_destroy()
  end

  def status_cluster()
    @logger.info("Querying cluster status")

    # Update the internal state with the state of the VMs
    update_state()

    # Query the status of the VMs and output to stdout
    vagrant_status()
  end

  def vagrant_up()
    # Initialize the VMs using vagrant
    cmd = "vagrant up"
    Open3.popen3(cmd) do |stdin, stdout, stderr, wait_thr|
      while line = stdout.gets
        @logger.info(line)
      end

      exit_status = wait_thr.value
      unless exit_status.success?
        @logger.error("Setting up the VMs using vagrant failed.")
        while line = stderr.gets
          @logger.error(line)
        end
        abort()
      end
    end
  end

  def update_state()
    for vm_name in [Cluster_vagrant_config.mha_manager_vm_name, 
                    Cluster_vagrant_config.mha_master_vm_name, 
                    Cluster_vagrant_config.mha_node1_vm_name, 
                    Cluster_vagrant_config.mha_node2_vm_name]
      hash = vagrant_ssh_config(vm_name)
      @state[vm_name] = {
        "hostname" => hash["HostName"],
        "username" => hash["User"],
        "ssh_key" => hash["IdentityFile"],
        "ssh_port" => hash["Port"]
      }
    end
  end

  def vagrant_ssh_config(vm_name)
    cmd = "vagrant ssh-config #{vm_name}"
    lines = Array.new
    Open3.popen3(cmd) do |stdin, stdout, stderr, wait_thr|
      while line = stdout.gets
        tokens = line.strip.partition(" ")
        lines.push([tokens.first, tokens.last.gsub(/"/, "")])
      end
    end
    Hash[lines]
  end

  def chef_client_provision_local_mode()
    # Provision the VMs using chef client in local mode
    @logger.info("Initializing the cookbooks to be used by the chef client")
    cmd = "rm -rf cookbooks && berks vendor cookbooks"
    Open3.popen3(cmd) do |stdin, stdout, stderr, wait_thr|
      while line = stdout.gets
        @logger.info(line)
      end

      exit_status = wait_thr.value
      unless exit_status.success?
        @logger.error("Failed to initialize the cookbooks.")
        while line = stderr.gets
          @logger.error(line)
        end
        abort()
      end
    end

    # Now we provision each VM using chef-client in local mode
    for vm_name in [Cluster_vagrant_config.mha_manager_vm_name, 
                    Cluster_vagrant_config.mha_master_vm_name, 
                    Cluster_vagrant_config.mha_node1_vm_name, 
                    Cluster_vagrant_config.mha_node2_vm_name]
      @logger.info("Provisioning '#{vm_name}.localhost'")

      host_ip = @state[vm_name]["hostname"]
      ssh_user = @state[vm_name]["username"]
      ssh_port = @state[vm_name]["ssh_port"]
      ssh_keys = [ @state[vm_name]["ssh_key"] ]

      node_json_attributes_file = "/vagrant/#{vm_name}.json"

      Net::SSH.start(host_ip, ssh_user, :port => ssh_port, :keys => ssh_keys) do |ssh|
        cmd = "cd /vagrant/cookbooks && sudo chef-client -z -j #{node_json_attributes_file}"
        command_output = ssh_exec!(ssh, cmd)
        stdout = command_output[0]
        stderr = command_output[1]
        exit_code = command_output[2]

        @logger.info(stdout)

        if exit_code != 0
          @logger.error("Failed to execute the command: #{cmd}")
          @logger.error(stderr)
          abort()
        end
      end
    end
  end

  def vagrant_destroy()
    # Initialize the VMs using test-kitchen
    cmd = "vagrant destroy -f"
    Open3.popen3(cmd) do |stdin, stdout, stderr, wait_thr|
      while line = stdout.gets
        @logger.info(line)
      end

      exit_status = wait_thr.value
      unless exit_status.success?
        @logger.error("Destroying the VMs using vagrant failed.")
        while line = stderr.gets
          @logger.error(line)
        end
        abort()
      end
    end
  end

  def vagrant_status()
    cmd = "vagrant status"
    Open3.popen3(cmd) do |stdin, stdout, stderr, wait_thr|
      while line = stdout.gets
        @logger.info(line)
      end

      exit_status = wait_thr.value
      unless exit_status.success?
        @logger.error("Failed to fetch status of the VMs using vagrant.")
        while line = stderr.gets
          @logger.error(line)
        end
        abort()
      end
    end
  end

  def setup_replication()
    @logger.info("Setting up replication between master and node1, node2")

    # Fetch master coordinates
    master_status = get_master_coordinates()
    @logger.info("Master status fetched:" \
                " MASTER_LOG_FILE=#{master_status['master_log_file']}," \
                " MASTER_LOG_POS=#{master_status['master_log_pos']}")

    master_host = Cluster_vagrant_config.mha_master_ip

    # Configure replication on node1
    if is_replication_running(Cluster_vagrant_config.mha_node1_vm_name)
      @logger.info("Replication already running between master -> node1")
    else
      host_ip = @state[Cluster_vagrant_config.mha_node1_vm_name]["hostname"]
      ssh_user = @state[Cluster_vagrant_config.mha_node1_vm_name]["username"]
      ssh_port = @state[Cluster_vagrant_config.mha_node1_vm_name]["ssh_port"]
      ssh_keys = [ @state[Cluster_vagrant_config.mha_node1_vm_name]["ssh_key"] ]
      Net::SSH.start(host_ip, ssh_user, :port => ssh_port, :keys => ssh_keys) do |ssh|
        sql_change_master = "CHANGE MASTER TO MASTER_HOST=\"#{master_host}\"," \
                            " MASTER_USER=\"#{Cluster_vagrant_config.mysql_replication_user}\"," \
                            " MASTER_PASSWORD=\"#{Cluster_vagrant_config.mysql_replication_password}\"," \
                            " MASTER_LOG_FILE=\"#{master_status['master_log_file']}\"," \
                            " MASTER_LOG_POS=#{master_status['master_log_pos']}"

        @logger.info("Executing the following SQL on node1: #{sql_change_master}")

        cmd = "sudo mysql -NB -e 'STOP SLAVE; #{sql_change_master}; START SLAVE;'"
        command_output = ssh_exec!(ssh, cmd)
        stdout = command_output[0]
        stderr = command_output[1]
        exit_code = command_output[2]

        @logger.info(stdout)

        if exit_code != 0
          @logger.error("Failed to execute CHANGE MASTER on node1.")
          abort()
        end
      end
    end

    # Configure replication on node2
    if is_replication_running(Cluster_vagrant_config.mha_node2_vm_name)
      @logger.info("Replication already running between master -> node2")
    else
      host_ip = @state[Cluster_vagrant_config.mha_node2_vm_name]["hostname"]
      ssh_user = @state[Cluster_vagrant_config.mha_node2_vm_name]["username"]
      ssh_port = @state[Cluster_vagrant_config.mha_node2_vm_name]["ssh_port"]
      ssh_keys = [ @state[Cluster_vagrant_config.mha_node2_vm_name]["ssh_key"] ]
      Net::SSH.start(host_ip, ssh_user, :port => ssh_port, :keys => ssh_keys) do |ssh|
        sql_change_master = "CHANGE MASTER TO MASTER_HOST=\"#{master_host}\"," \
                            " MASTER_USER=\"#{Cluster_vagrant_config.mysql_replication_user}\"," \
                            " MASTER_PASSWORD=\"#{Cluster_vagrant_config.mysql_replication_password}\"," \
                            " MASTER_LOG_FILE=\"#{master_status['master_log_file']}\"," \
                            " MASTER_LOG_POS=#{master_status['master_log_pos']}"

        @logger.info("Executing the following SQL on node2: #{sql_change_master}")

        cmd = "sudo mysql -NB -e 'STOP SLAVE; #{sql_change_master}; START SLAVE;'"
        command_output = ssh_exec!(ssh, cmd)
        stdout = command_output[0]
        stderr = command_output[1]
        exit_code = command_output[2]

        @logger.info(stdout)

        if exit_code != 0
          @logger.error("Failed to execute CHANGE MASTER on node2.")
          abort()
        end
      end
    end
  end

  def setup_test_schema()
    # Here we setup the sakila schema as a test database that we use to test
    # that replication works as expected
    sakila_recipe = "recipe[mysql-test-schema::sakila]"

    @logger.info("Setting up the 'sakila' schema on the master")

    host_ip = @state[Cluster_vagrant_config.mha_master_vm_name]["hostname"]
    ssh_user = @state[Cluster_vagrant_config.mha_master_vm_name]["username"]
    ssh_port = @state[Cluster_vagrant_config.mha_master_vm_name]["ssh_port"]
    ssh_keys = [ @state[Cluster_vagrant_config.mha_master_vm_name]["ssh_key"] ]
    Net::SSH.start(host_ip, ssh_user, :port => ssh_port, :keys => ssh_keys) do |ssh|
      cmd = "cd /vagrant/cookbooks && sudo chef-client -z -o '#{sakila_recipe}'"
      command_output = ssh_exec!(ssh, cmd)
      stdout = command_output[0]
      stderr = command_output[1]
      exit_code = command_output[2]

      @logger.info(stdout)

      if exit_code != 0
        @logger.error("Failed to apply the recipe #{sakila_recipe} on master.")
        abort()
      end
    end

    @logger.info("Setup of 'sakila' schema is complete")

    if not is_replication_running(Cluster_vagrant_config.mha_node1_vm_name)
      @logger.info("Replication between master -> node1 found stopped")
      abort()
    end

    if not is_replication_running(Cluster_vagrant_config.mha_node2_vm_name)
      @logger.info("Replication between master -> node1 found stopped")
      abort()
    end
  end

  def wait_slave_catchup()
    # Wait for the slave to catchup
    master_status = get_master_coordinates()

    threads = []
    threads << Thread.new {
      @logger.info("Waiting for the slave node1 to get caught up " \
                  " to master till the position:" \
                  " MASTER_LOG_FILE=#{master_status['master_log_file']}," \
                  " MASTER_LOG_POS=#{master_status['master_log_pos']}")

      slave_log_file_read = ''
      slave_log_pos_read = ''

      host_ip = @state[Cluster_vagrant_config.mha_node1_vm_name]["hostname"]
      ssh_user = @state[Cluster_vagrant_config.mha_node1_vm_name]["username"]
      ssh_port = @state[Cluster_vagrant_config.mha_node1_vm_name]["ssh_port"]
      ssh_keys = [ @state[Cluster_vagrant_config.mha_node1_vm_name]["ssh_key"] ]
      Net::SSH.start(host_ip, ssh_user, :port => ssh_port, :keys => ssh_keys) do |ssh|
        # Keep checking slave status until slave is caught up
        while ( slave_log_file_read != master_status['master_log_file'] &&
                slave_log_pos_read != master_status['master_log_pos'] ) do
          cmd = "sudo mysql --vertical -e 'SHOW SLAVE STAtUS'"
          command_output = ssh_exec!(ssh, cmd)
          stdout = command_output[0]
          stderr = command_output[1]
          exit_code = command_output[2]

          if exit_code != 0
            @logger.error("Failed to fetch replication status for node1.")
            abort()
          end

          for line in stdout.split("\n")
            slave_log_file_read = line.split(':')[1].downcase().strip() if line.include?("Relay_Master_Log_File:")
            slave_log_pos_read = line.split(':')[1].downcase().strip() if line.include?("Exec_Master_Log_Pos:")
          end

          sleep(1)
        end

        @logger.info("Slave node1 is caught up with the master.")
      end
    }

    threads << Thread.new {
      @logger.info("Waiting for the slave node2 to get caught up " \
                  " to master till the position:" \
                  " MASTER_LOG_FILE=#{master_status['master_log_file']}," \
                  " MASTER_LOG_POS=#{master_status['master_log_pos']}")

      slave_log_file_read = ''
      slave_log_pos_read = ''

      host_ip = @state[Cluster_vagrant_config.mha_node2_vm_name]["hostname"]
      ssh_user = @state[Cluster_vagrant_config.mha_node2_vm_name]["username"]
      ssh_port = @state[Cluster_vagrant_config.mha_node2_vm_name]["ssh_port"]
      ssh_keys = [ @state[Cluster_vagrant_config.mha_node2_vm_name]["ssh_key"] ]
      Net::SSH.start(host_ip, ssh_user, :port => ssh_port, :keys => ssh_keys) do |ssh|
        # Keep checking slave status until slave is caught up
        while ( slave_log_file_read != master_status['master_log_file'] &&
                slave_log_pos_read != master_status['master_log_pos'] ) do
          cmd = "sudo mysql --vertical -e 'SHOW SLAVE STAtUS'"
          command_output = ssh_exec!(ssh, cmd)
          stdout = command_output[0]
          stderr = command_output[1]
          exit_code = command_output[2]

          if exit_code != 0
            @logger.error("Failed to fetch replication status for node2.")
            abort()
          end

          for line in stdout.split("\n")
            slave_log_file_read = line.split(':')[1].downcase().strip() if line.include?("Relay_Master_Log_File:")
            slave_log_pos_read = line.split(':')[1].downcase().strip() if line.include?("Exec_Master_Log_Pos:")
          end

          sleep(1)
        end

        @logger.info("Slave node2 is caught up with the master.")
      end
    }

    threads.each { |thd| thd.join }
  end

  def get_master_coordinates()
    host_ip = @state[Cluster_vagrant_config.mha_master_vm_name]["hostname"]
    ssh_user = @state[Cluster_vagrant_config.mha_master_vm_name]["username"]
    ssh_port = @state[Cluster_vagrant_config.mha_master_vm_name]["ssh_port"]
    ssh_keys = [ @state[Cluster_vagrant_config.mha_master_vm_name]["ssh_key"] ]

    master_log_file = ''
    master_log_pos = 0

    Net::SSH.start(host_ip, ssh_user, :port => ssh_port, :keys => ssh_keys) do |ssh|
      cmd = "sudo mysql -NB -e \"SHOW MASTER STATUS\""
      command_output = ssh_exec!(ssh, cmd)
      stdout = command_output[0]
      stderr = command_output[1]
      exit_code = command_output[2]

      if exit_code != 0
        @logger.error("Failed to execute 'SHOW MASTER STATUS'.")
        abort()
      end

      master_status = stdout.split()
      master_log_file = master_status[0]
      master_log_pos = master_status[1]
    end

    return { 'master_log_file' => master_log_file, 'master_log_pos' => master_log_pos }
  end

  def is_replication_running(vm_name)
    slave_running = false

    host_ip = @state[vm_name]["hostname"]
    ssh_user = @state[vm_name]["username"]
    ssh_port = @state[vm_name]["ssh_port"]
    ssh_keys = [ @state[vm_name]["ssh_key"] ]
    Net::SSH.start(host_ip, ssh_user, :port => ssh_port, :keys => ssh_keys) do |ssh|
      cmd = "sudo mysql --vertical -e 'SHOW SLAVE STAtUS'"
      command_output = ssh_exec!(ssh, cmd)
      stdout = command_output[0]
      stderr = command_output[1]
      exit_code = command_output[2]

      if exit_code != 0
        @logger.error("Failed to fetch replication status.")
        abort()
      end

      slave_io_running = 'no'
      slave_sql_running = 'no'
      slave_io_error_num = 0
      slave_io_error = ''
      slave_sql_error_num = 0
      slave_sql_error = ''

      for line in stdout.split("\n")
        slave_io_running = line.split(':')[1].downcase().strip() if line.include?("Slave_IO_Running:")
        slave_sql_running = line.split(':')[1].downcase().strip() if line.include?("Slave_SQL_Running:")

        slave_io_error_num = line.split(':')[1].strip().to_i() if line.include?("Last_IO_Errno:")
        slave_io_error = line.split(':')[1].strip() if line.include?("Last_IO_Error:")

        slave_sql_error_num = line.split(':')[1].strip().to_i() if line.include?("Last_SQL_Errno:")
        slave_sql_error = line.split(':')[1].strip() if line.include?("Last_SQL_Error:")
      end

      if slave_io_running == 'yes' && slave_sql_running == 'yes'
        slave_running = true
      else
        @logger.error(slave_io_error) if slave_io_error_num > 0
        @logger.error(slave_sql_error) if slave_sql_error_num > 0
        
        slave_running = false
      end
    end

    return slave_running
  end

  def ssh_exec!(ssh, command)
    # Originally submitted by 'flitzwald' over here: http://stackoverflow.com/a/3386375
    stdout_data = ""
    stderr_data = ""
    exit_code = nil

    ssh.open_channel do |channel|
      channel.exec(command) do |ch, success|
        unless success
          abort "FAILED: couldn't execute command (ssh.channel.exec)"
        end
        channel.on_data do |ch,data|
          stdout_data+=data
        end
   
        channel.on_extended_data do |ch,type,data|
          stderr_data+=data
        end
   
        channel.on_request("exit-status") do |ch,data|
          exit_code = data.read_long
        end
      end
    end
    ssh.loop
    return [stdout_data, stderr_data, exit_code]
  end

end



# Command line parsing
options = {}
opt_parser = OptionParser.new do |opts|
  opts.banner = "Usage: test.rb --init|--destroy"

  options['initialize_cluster'] = false
  opts.on("-i", "--init", "Initialize the test MySQL replication cluster") do
    options['initialize_cluster'] = true
  end

  options['destroy_cluster'] = false
  opts.on("-d", "--destroy", "Destroy the test MySQL replication cluster") do
    options['destroy_cluster'] = true
  end

  options['status_cluster'] = false
  opts.on("-s", "--status", "Get the status of MySQL replication cluster") do
    options['status_cluster'] = true
  end

  options['provision_cluster'] = false
  opts.on("-p", "--provision", "Provision MySQL replication cluster using Chef") do
    options['provision_cluster'] = true
  end

  opts.on("-h", "--help", "Show this message") do
    puts opts
    exit
  end
end

begin
  opt_parser.parse!

  if !options['initialize_cluster'] && !options['destroy_cluster'] && !options['status_cluster'] && !options['provision_cluster']
    puts opt_parser
    exit 1
  end

  if options['initialize_cluster'] && options['destroy_cluster']
    puts opt_parser
    exit 1
  end
rescue OptionParser::InvalidOption, OptionParser::MissingArgument
  puts $!.to_s
  puts optparse
  exit 1
end


# Do the actual work
vagrant_cluster = Cluster_test_vagrant.new()

if options['initialize_cluster']
  vagrant_cluster.init_cluster()
elsif options['destroy_cluster']
  vagrant_cluster.destroy_cluster()
elsif options['status_cluster']
  vagrant_cluster.status_cluster()
elsif options['provision_cluster']
  vagrant_cluster.provision_cluster()
end
