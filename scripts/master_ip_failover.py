#!/usr/bin/env python

import sys
from optparse import OptionParser
from lib.mha_ip_failover_helper import MHA_IP_failover_helper

# parse comand line arguments
parser = OptionParser()
parser.add_option('--command', type='string')
parser.add_option('--orig_master_host', type='string')
parser.add_option('--orig_master_ip', type='string')
parser.add_option('--orig_master_port', type='string')
parser.add_option('--orig_master_ssh_port', type='string')
parser.add_option('--new_master_host', type='string')
parser.add_option('--new_master_ip', type='string')
parser.add_option('--new_master_port', type='string')
parser.add_option('--new_master_ssh_port', type='string')
parser.add_option('--ssh_user', type='string')
parser.add_option('--ssh_options', type='string')

(options, args) = parser.parse_args()

# do the actual work
exit_code = 1

if options.command is None:
    sys.exit(exit_code)

mha_ip_failover_helper = MHA_IP_failover_helper()

if options.command == 'stop':
    if (options.orig_master_ip is not None and
            options.ssh_user is not None and
            options.ssh_options is not None):
        return_val = mha_ip_failover_helper.execute_stop_command(orig_master_host=options.orig_master_host,
                                                orig_master_ip=options.orig_master_ip,
                                                ssh_user=options.ssh_user, 
                                                ssh_port=options.orig_master_ssh_port,
                                                ssh_options=options.ssh_options)
        if return_val == True:
            exit_code = 0

if options.command == 'stopssh':
    if (options.orig_master_ip is not None and
            options.ssh_user is not None and
            options.ssh_options is not None):
        return_val = mha_ip_failover_helper.execute_stopssh_command(orig_master_host=options.orig_master_host,
                                                orig_master_ip=options.orig_master_ip,
                                                ssh_user=options.ssh_user,
                                                ssh_port=options.orig_master_ssh_port,
                                                ssh_options=options.ssh_options)
        if return_val == True:
            exit_code = 0

elif options.command == 'start':
    if (options.orig_master_ip is not None and 
            options.new_master_ip is not None and
            options.ssh_user is not None and
            options.ssh_options is not None):
        return_val = mha_ip_failover_helper.execute_start_command(orig_master_host=options.orig_master_host,
                                                orig_master_ip=options.orig_master_ip,
                                                new_master_host=options.new_master_host,
                                                new_master_ip=options.new_master_ip,
                                                ssh_user=options.ssh_user,
                                                ssh_port=new_master_ssh_port,
                                                ssh_options=options.ssh_options)

        if return_val == True:
            exit_code = 0

elif options.command == 'status':
    if (options.orig_master_ip is not None and
            options.ssh_user is not None and
            options.ssh_options is not None):
        return_val = mha_ip_failover_helper.execute_status_command(orig_master_host=options.orig_master_host,
                                                orig_master_ip=options.orig_master_ip,
                                                ssh_user=options.ssh_user,
                                                ssh_port=options.orig_master_ssh_port,
                                                ssh_options=options.ssh_options)

        if return_val == True:
            exit_code = 0

# exit the script with the appropriate code
# if script exits with a 0 status code, MHA continues with the failover
sys.exit(exit_code)
