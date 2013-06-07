#!/usr/bin/python

import sys
from optparse import OptionParser
from lib.mha_online_change_helper import MHA_online_change_helper

# set some config variables
privileged_users = ['root']

#/usr/local/mha-helper/scripts/master_ip_online_change.py \
#        --command=stop --orig_master_host=repl01 --orig_master_ip=192.168.122.151 
#        --orig_master_port=3306 --orig_master_user='mha_helper' --orig_master_password='xxx' 
#        --new_master_host=repl02 --new_master_ip=192.168.122.152 --new_master_port=3306 
#        --new_master_user='mha_helper' --new_master_password='xxx'  
#        --ssh_options='-o ServerAliveInterval=60 -o ServerAliveCountMax=20 -o StrictHostKeyChecking=no -o ConnectionAttempts=5 -o PasswordAuthentication=no -o BatchMode=yes -i /root/.ssh/id_rsa' 

# parse comand line arguments
parser = OptionParser()
parser.add_option('--command', type='string')
parser.add_option('--orig_master_host', type='string')
parser.add_option('--orig_master_ip', type='string')
parser.add_option('--orig_master_port', type='string')
parser.add_option('--orig_master_user', type='string')
parser.add_option('--orig_master_password', type='string')
parser.add_option('--new_master_host', type='string')
parser.add_option('--new_master_ip', type='string')
parser.add_option('--new_master_port', type='string')
parser.add_option('--new_master_user', type='string')
parser.add_option('--new_master_password', type='string')
parser.add_option('--ssh_options', type='string')

(options, args) = parser.parse_args()

# do the actual work
exit_code = 1

if (options.orig_master_host is not None and 
    options.orig_master_ip is not None and 
    options.new_master_host is not None and
    options.new_master_ip is not None and 
    options.command is not None):
    mha_online_change_helper = MHA_online_change_helper(orig_master_host=options.orig_master_host,
                                                    orig_master_ip=options.orig_master_ip,
                                                    new_master_host=options.new_master_host,
					            new_master_ip=options.new_master_ip,
                                                    privileged_users=privileged_users)
    if options.command == 'stop':
    	if mha_online_change_helper.execute_stop_command() == True:
	    exit_code = 0
	else:
	    mha_online_change_helper.rollback_stop_command()
    elif options.command == 'start':
        mha_online_change_helper.execute_start_command()
        exit_code = 0

# exit the script with the appropriate code
# if script exits with a 0 status code, MHA executes FLUSH TABLES WITH READ LOCK 
# and continues with the online failover
sys.exit(exit_code)
