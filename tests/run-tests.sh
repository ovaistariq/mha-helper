#!/bin/bash
set -e

script_root=$(dirname $(readlink -f $0))

# Export the variables to be used by the MySQLHelper tests
export MYSQL_TEST_VERSION="5.6.19-log"
export MYSQL_TEST_IP="192.168.30.11"
export MYSQL_TEST_USER="msandbox"
export MYSQL_TEST_PASSWORD="msandbox"
export MYSQL_TEST_PORT="3306"

# Export the variables that are needed by the SSHHelper test
export SSH_TEST_HOST="master.localhost"
export SSH_TEST_IP="192.168.30.11"
export SSH_TEST_USER="root"
export SSH_TEST_PORT="22"

# Run the tests
python ${script_root}/test_mysql_helper.py -v
python ${script_root}/test_config_helper.py -v
python ${script_root}/test_ssh_helper.py -v
