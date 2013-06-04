import ConfigParser

class MHA_config_helper(object):
    CONFIG_PATH = "/usr/local/mha-helper/conf/test_cluster.conf"
    GLOBAL_SECTION = "server default"

    def __init__(self):
       self._config = ConfigParser.RawConfigParser()
       self._config.read(MHA_config_helper.CONFIG_PATH)

    def get_username(self):
        if self._config.has_option(MHA_config_helper.GLOBAL_SECTION, 'user') == False:
            return False

        return self._config.get(MHA_config_helper.GLOBAL_SECTION, 'user')

    def get_password(self):
        if self._config.has_option(MHA_config_helper.GLOBAL_SECTION, 'password') == False:
            return False

        return self._config.get(MHA_config_helper.GLOBAL_SECTION, 'password')
