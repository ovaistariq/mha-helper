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
export SSH_TEST_HOST="master"
export SSH_TEST_IP="192.168.30.11"
export SSH_TEST_USER="root"
export SSH_TEST_PORT="22"

# Export the variables that are needed by the MHAHelper test
export ORIG_MASTER_HOST="master"
export ORIG_MASTER_IP="192.168.30.11"
export ORIG_MASTER_PORT=3306
export ORIG_MASTER_USER="msandbox"
export ORIG_MASTER_PASSWORD="msandbox"
export ORIG_MASTER_SSH_HOST="manager"
export ORIG_MASTER_SSH_IP="192.168.30.11"
export ORIG_MASTER_SSH_PORT=22
export ORIG_MASTER_SSH_USER="root"
export NEW_MASTER_HOST="node1"
export NEW_MASTER_IP="192.168.30.12"
export NEW_MASTER_PORT=3306
export NEW_MASTER_USER="msandbox"
export NEW_MASTER_PASSWORD="msandbox"
export NEW_MASTER_SSH_USER="root"
export NEW_MASTER_SSH_HOST="node1"
export NEW_MASTER_SSH_IP="192.168.30.12"
export NEW_MASTER_SSH_PORT=22

function unit_test_python_classes() {
    # Run the Unit tests for the Python classes
    echo "-- Running ${script_root}/test_mysql_helper.py"
    python ${script_root}/test_mysql_helper.py -v
    echo
    echo "-- Running ${script_root}/test_config_helper.py"
    python ${script_root}/test_config_helper.py -v
    echo
    echo "-- Running ${script_root}/test_ssh_helper.py"
    python ${script_root}/test_ssh_helper.py -v
    echo
    echo "-- Running ${script_root}/test_vip_metal_helper.py"
    python ${script_root}/test_vip_metal_helper.py -v
    echo
    echo "-- Running ${script_root}/test_email_helper.py"
    python ${script_root}/test_email_helper.py -v
    echo
    echo "-- Running ${script_root}/test_mha_helper.py"
    python ${script_root}/test_mha_helper.py -v
}

function test_python_scripts() {
    # Run the unit tests for the Python scripts
    echo
    echo "-- Running ${script_root}/test_master_ip_online_failover_helper.py"
    python ${script_root}/test_master_ip_online_failover_helper.py -v
    echo
    echo "-- Running ${script_root}/test_master_ip_hard_failover_helper.py"
    python ${script_root}/test_master_ip_hard_failover_helper.py -v
}

#unit_test_python_classes
test_python_scripts
