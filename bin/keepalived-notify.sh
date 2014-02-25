#!/bin/bash

TYPE=$1
NAME=$2
STATE=$3

case $STATE in
    "MASTER")
        /etc/init.d/haproxy start
        /etc/init.d/mha_manager_daemon-test_cluster-init start
        exit 0
        ;;
    "BACKUP")
        /etc/init.d/haproxy stop
        /etc/init.d/mha_manager_daemon-test_cluster-init stop
        exit 0
        ;;
    "FAULT")
        /etc/init.d/haproxy stop
        /etc/init.d/mha_manager_daemon-test_cluster-init stop
        exit 0
        ;;
    *)
        echo "unknown state"
        exit 1
        ;;
esac
