import subprocess
import shlex
from mha_config_helper import MHA_config_helper

class MHA_VIP_helper(object):
    @staticmethod
    def remove_vip(config_helper, host_ip, ssh_user, ssh_port, ssh_options):
        cluster_interface = config_helper.get_cluster_interface()
        writer_vip_cidr = config_helper.get_writer_vip_cidr()

        if ssh_user == None:
           ssh_user = config_helper.get_ssh_user()

        ip_cmd = "%s addr delete %s dev %s" % (MHA_config_helper.IP, 
                                            writer_vip_cidr, cluster_interface)

        if config_helper.get_requires_sudo() == True:
            ip_cmd = "%s %s" % (MHA_config_helper.SUDO, ip_cmd)

        cmd = "%s %s -t -q -p %s %s@%s \"%s\"" % (MHA_config_helper.SSH, 
                ssh_options, ssh_port, ssh_user, host_ip, ip_cmd)

        print "Executing command %s" % cmd

        cmd_list = shlex.split(cmd)
        cmd_return_code = subprocess.call(cmd_list)
        if cmd_return_code > 0:
            return False

        return True

    @staticmethod
    def assign_vip(config_helper, host_ip, ssh_user, ssh_port, ssh_options):
        cluster_interface = config_helper.get_cluster_interface()
        writer_vip_cidr = config_helper.get_writer_vip_cidr()
        writer_vip = config_helper.get_writer_vip()

        if ssh_user == None:
            ssh_user = config_helper.get_ssh_user()

        ip_cmd = "%s addr add %s dev %s" % (MHA_config_helper.IP, 
                                        writer_vip_cidr, cluster_interface)

        arping_cmd = "%s -q -c 3 -A -I %s %s" % (MHA_config_helper.ARPING,
                                        cluster_interface, writer_vip)

        if config_helper.get_requires_sudo() == True:
            ip_cmd = "%s %s" % (MHA_config_helper.SUDO, ip_cmd)
            arping_cmd = "%s %s" % (MHA_config_helper.SUDO, arping_cmd)

        cmd = "%s %s -t -q -p %s %s@%s \"%s && %s\"" % (MHA_config_helper.SSH, 
                ssh_options, ssh_port, ssh_user, host_ip, ip_cmd, arping_cmd)

        print "Executing command %s" % cmd

        cmd_return_code = subprocess.call(cmd, shell=True)
        if cmd_return_code > 0:
            return False

        return True
