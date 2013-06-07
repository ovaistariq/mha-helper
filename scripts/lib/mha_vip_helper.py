import subprocess
from mha_config_helper import MHA_config_helper

class MHA_VIP_helper(object):
    IFCONFIG = "/sbin/ifconfig"
    ARPING = "/sbin/arping"
    SSH = "/usr/bin/ssh"

    @staticmethod
    def remove_vip(host, host_ip, ssh_user, ssh_options):
        config_helper = MHA_config_helper(host=host)

        cluster_interface = config_helper.get_cluster_interface()
        writer_vip = config_helper.get_writer_vip()

        ifconfig_cmd = "%s %s %s down" % (MHA_VIP_helper.IFCONFIG, 
                                        cluster_interface, writer_vip)

        cmd = [MHA_VIP_helper.SSH, 
                "%s@%s" % (ssh_user, host_ip), 
                ssh_options, 
                ifconfig_cmd]

        cmd_return_code = subprocess.call(cmd)
        if cmd_return_code > 0:
            return False

        return True

    @staticmethod
    def assign_vip(host, host_ip, ssh_user, ssh_options):
        config_helper = MHA_config_helper(host=host)

        cluster_interface = config_helper.get_cluster_interface()
        writer_vip = config_helper.get_writer_vip()

        ifconfig_cmd = "%s %s %s up" % (MHA_VIP_helper.IFCONFIG, 
                                        cluster_interface, writer_vip)

        arping_cmd = "%s -q -c 3 -A -I %s %s" % (MHA_VIP_helper.ARPING,
                                        cluster_interface, writer_vip)

        cmd = [MHA_VIP_helper.SSH, 
                "%s@%s" % (ssh_user, host_ip), 
                ssh_options, 
                "%s && %s" % (ifconfig_cmd, arping_cmd)]

        cmd_return_code = subprocess.call(cmd)
        if cmd_return_code > 0:
            return False

        return True
