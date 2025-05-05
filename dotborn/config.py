import yaml
#from dotborn import logger, paths
from pathlib import Path

#log = logger.setup_logger()

class Configure:

    def __init__(self):
        self.PROJECT_ROOT = Path(__file__).resolve().parents[1]
        self.CONFIG_PATH = self.PROJECT_ROOT/"dotborn"/"config"
        self.TEMPLATE_PATH = self.PROJECT_ROOT/"dotborn"/"templates"
        self.LOG_PATH = self.PROJECT_ROOT/"dotborn.log"
        self.user_config = self.load_user_config()
        self.install_config = self.load_install_config()
        self.logging_config = self.load_logging_config()
        self.backup_config = self.load_backup_config()

    def load_user_config(self):
        user_config = self.CONFIG_PATH/'user.yaml'
        with open(user_config, 'r') as f:
            config = yaml.safe_load(f)
        return config

    def load_install_config(self):
        install_config = self.CONFIG_PATH/"install.yaml"
        with open(install_config, 'r') as f:
            config = yaml.safe_load(f)
        return config

    def load_logging_config(self):
        logging_config = self.CONFIG_PATH/"logging.yaml"
        with open(logging_config, 'r') as f:
            config = yaml.safe_load(f)
        return config

    def load_backup_config(self):
        backup_config = self.CONFIG_PATH/"backup.yaml"
        with open(backup_config, 'r') as f:
            config = yaml.safe_load(f)
        return config

"""
    def load_install_config(self):
        log.debug(f"Loading install configs: {install_config}")
        pass

    def load_logging_config(self):
        pass

    def load_backup_config(self):
        pass


def load_config():
    log.info(f"Loading configfile {paths.CONFIG_PATH}")
    # TODO: Validate that file exists, etc
    with open(CONFIG_PATH, 'r') as f:
        config = yaml.safe_load(f)
    return config

def load_install():
    with open(CONFIG_PATH, 'r') as f:
        config = yaml.safe_load(f)
    return config


"""