import subprocess
from mha_config_helper import MHA_config_helper

class MHA_VIP_helper(object):
    @staticmethod
    def remove_vip(config_helper, host_ip, ssh_user, ssh_options):
        cluster_interface = config_helper.get_cluster_interface()
        writer_vip = config_helper.get_writer_vip()

        if ssh_user == None:
           ssh_user = config_helper.get_ssh_user()

        ifconfig_cmd = "%s %s %s down" % (MHA_config_helper.IFCONFIG, 
                                        cluster_interface, writer_vip)

        if config_helper.get_requires_sudo() == True:
            ifconfig_cmd = "%s %s" % (MHA_config_helper.SUDO, ifconfig_cmd)

        cmd = "%s %s -t -q %s@%s \"%s\"" % (MHA_config_helper.SSH, ssh_options, 
                                ssh_user, host_ip, ifconfig_cmd)

        cmd_return_code = subprocess.call(cmd, shell=True)
        if cmd_return_code > 0:
            return False

        return True

    @staticmethod
    def assign_vip(config_helper, host_ip, ssh_user, ssh_options):
        cluster_interface = config_helper.get_cluster_interface()
        writer_vip = config_helper.get_writer_vip()

        if ssh_user == None:
            ssh_user = config_helper.get_ssh_user()

        ifconfig_cmd = "%s %s %s up" % (MHA_config_helper.IFCONFIG, 
                                        cluster_interface, writer_vip)

        arping_cmd = "%s -q -c 3 -A -I %s %s" % (MHA_config_helper.ARPING,
                                        cluster_interface, writer_vip)

        if config_helper.get_requires_sudo() == True:
            ifconfig_cmd = "%s %s" % (MHA_config_helper.SUDO, ifconfig_cmd)
            arping_cmd = "%s %s" % (MHA_config_helper.SUDO, arping_cmd)

        cmd = "%s %s -t -q %s@%s \"%s && %s\"" % (MHA_config_helper.SSH,
                                        ssh_options, ssh_user, host_ip, 
                                        ifconfig_cmd, arping_cmd)

        cmd_return_code = subprocess.call(cmd, shell=True)
        if cmd_return_code > 0:
            return False

        return True
