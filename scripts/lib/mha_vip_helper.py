import subprocess
from mha_config_helper import MHA_config_helper

class MHA_VIP_helper(object):
    @staticmethod
    def remove_vip(host, host_ip, ssh_user, ssh_options):
        config_helper = MHA_config_helper(host=host)

        cluster_interface = config_helper.get_cluster_interface()
        writer_vip = config_helper.get_writer_vip()

        ifconfig_cmd = "%s %s %s down" % (MHA_config_helper.IFCONFIG, 
                                        cluster_interface, writer_vip)

        cmd = "%s %s %s@%s \"%s\"" % (MHA_config_helper.SSH, ssh_options, 
                                ssh_user, host_ip, ifconfig_cmd)

        cmd_return_code = subprocess.call(cmd, shell=True)
        if cmd_return_code > 0:
            return False

        return True

    @staticmethod
    def assign_vip(host, host_ip, ssh_user, ssh_options):
        config_helper = MHA_config_helper(host=host)

        cluster_interface = config_helper.get_cluster_interface()
        writer_vip = config_helper.get_writer_vip()

        ifconfig_cmd = "%s %s %s up" % (MHA_config_helper.IFCONFIG, 
                                        cluster_interface, writer_vip)

        arping_cmd = "%s -q -c 3 -A -I %s %s" % (MHA_config_helper.ARPING,
                                        cluster_interface, writer_vip)

        cmd = "%s %s %s@%s \"%s && %s\"" % (MHA_config_helper.SSH,
                                        ssh_options, ssh_user, host_ip, 
                                        ifconfig_cmd, arping_cmd)

        cmd_return_code = subprocess.call(cmd, shell=True)
        if cmd_return_code > 0:
            return False

        return True
