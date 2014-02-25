#!/bin/bash

TYPE=$1
NAME=$2
STATE=$3

/etc/init.d/haproxy stop
/etc/init.d/mha_manager_daemon-test_cluster-init stop

