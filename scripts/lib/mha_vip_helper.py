import subprocess
from mha_config_helper import MHA_config_helper

class MHA_VIP_helper(object):
    @staticmethod
    def remove_vip(config_helper, host_ip, ssh_user, ssh_options):
        cluster_interface = config_helper.get_cluster_interface()
        writer_vip = config_helper.get_writer_vip()

        if ssh_user == None:
           ssh_user = config_helper.get_ssh_user()

        ip_cmd = "%s addr delete %s/32 dev %s" % (MHA_config_helper.IP, 
                                            writer_vip, cluster_interface)

        if config_helper.get_requires_sudo() == True:
            ip_cmd = "%s %s" % (MHA_config_helper.SUDO, ip_cmd)

        cmd = "%s %s -t -q %s@%s \"%s\"" % (MHA_config_helper.SSH, ssh_options, 
                                ssh_user, host_ip, ip_cmd)

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

        ip_cmd = "%s addr add %s/32 dev %s" % (MHA_config_helper.IP, 
                                            writer_vip, cluster_interface)

        arping_cmd = "%s -q -c 3 -A -I %s %s" % (MHA_config_helper.ARPING,
                                        cluster_interface, writer_vip)

        if config_helper.get_requires_sudo() == True:
            ip_cmd = "%s %s" % (MHA_config_helper.SUDO, ip_cmd)
            arping_cmd = "%s %s" % (MHA_config_helper.SUDO, arping_cmd)

        cmd = "%s %s -t -q %s@%s \"%s && %s\"" % (MHA_config_helper.SSH,
                                        ssh_options, ssh_user, host_ip, 
                                        ip_cmd, arping_cmd)

        cmd_return_code = subprocess.call(cmd, shell=True)
        if cmd_return_code > 0:
            return False

        return True
