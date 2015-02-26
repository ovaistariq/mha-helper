#!/bin/bash
set -e

mysql_binary_path="~/.mysql/binaries/mysql-5.6.19-osx10.7-x86_64.tar.gz"
mysql_binary_path=$(realpath ${mysql_binary_path})

clean_exit() {
    local error_code="$?"
    kill -9 $(jobs -p) >/dev/null 2>&1 || true
    (cd ${sandbox_dir} && ./clear)
    return $error_code
}

check_for_cmd () {
    if ! which "$1" >/dev/null 2>&1
    then
        echo "Could not find $1 command" 1>&2
        exit 1
    fi
}

check_for_cmd make_sandbox

trap "clean_exit" EXIT

# Create a MySQL sandbox for tests
sandbox_cmd_output=$(make_sandbox ${mysql_binary_path} -- --no_confirm --force)
sandbox_dir=$(echo "${sandbox_cmd_output}" | grep "Your sandbox server was installed" | awk '{print $7}')

# Fetch the MySQL config parameters
mysql_user=$(grep user ${sandbox_dir}/my.sandbox.cnf -m 1 | cut -d '=' -f 2 | awk '{print $1}')
mysql_pass=$(grep password ${sandbox_dir}/my.sandbox.cnf -m 1 | cut -d '=' -f 2 | awk '{print $1}')
mysql_port=$(grep port ${sandbox_dir}/my.sandbox.cnf -m 1 | cut -d '=' -f 2 | awk '{print $1}')
mysql_host=$(grep bind-address ${sandbox_dir}/my.sandbox.cnf -m 1 | cut -d '=' -f 2 | awk '{print $1}')

# Export the variables to be used by the tests
export MYSQL_TEST_IP="${mysql_host}"
export MYSQL_TEST_USER="${mysql_user}"
export MYSQL_TEST_PASSWORD="${mysql_pass}"
export MYSQL_TEST_PORT="${mysql_port}"

# Run the tests
python test_mysql_helper.py
