#!/bin/bash
set -e

script_root=$(dirname $(readlink -f $0))

mysql_version="5.6.19"
mysql_binary_path="/Users/ovais.tariq/.mysql/binaries/mysql-5.6.19-osx10.7-x86_64.tar.gz"
mysql_sandbox_path="/Users/ovais.tariq/sandboxes/msb_5_6_19"

clean_exit() {
    local error_code="$?"
    kill -9 $(jobs -p) >/dev/null 2>&1 || true
    (cd ${mysql_sandbox_path} && ./clear)
    return ${error_code}
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
make_sandbox ${mysql_binary_path} -- --no_confirm --force

# Fetch the MySQL config parameters
mysql_user=$(grep user ${mysql_sandbox_path}/my.sandbox.cnf -m 1 | cut -d '=' -f 2 | awk '{print $1}')
mysql_pass=$(grep password ${mysql_sandbox_path}/my.sandbox.cnf -m 1 | cut -d '=' -f 2 | awk '{print $1}')
mysql_port=$(grep port ${mysql_sandbox_path}/my.sandbox.cnf -m 1 | cut -d '=' -f 2 | awk '{print $1}')
mysql_host=$(grep bind-address ${mysql_sandbox_path}/my.sandbox.cnf -m 1 | cut -d '=' -f 2 | awk '{print $1}')

# Export the variables to be used by the tests
export MYSQL_TEST_VERSION="${mysql_version}"
export MYSQL_TEST_IP="${mysql_host}"
export MYSQL_TEST_USER="${mysql_user}"
export MYSQL_TEST_PASSWORD="${mysql_pass}"
export MYSQL_TEST_PORT="${mysql_port}"

# Run the tests
python ${script_root}/test_mysql_helper.py -v
