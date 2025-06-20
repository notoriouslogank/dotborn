import yaml

from pathlib import Path

class Configure:
    def __init__(self):
        self.PROJECT_ROOT = Path(__file__).resolve().parents[1]
        self.CONFIG_PATH = self.PROJECT_ROOT / "dotborn" / "config"
        self.TEMPLATE_PATH = self.PROJECT_ROOT / "dotborn" / "templates"
        self.LOG_PATH = self.PROJECT_ROOT / "dotborn.log"
        self.user_config = self.load_user_config()
        self.install_config = self.load_install_config()
        self.logging_config = self.load_logging_config()
        self.backup_config = self.load_backup_config()

    def load_user_config(self) -> str:
        """Read and return the configuration data from config/user.yaml

        Returns:
            str: Configuration data (user.yaml)
        """
        user_config = self.CONFIG_PATH / "user.yaml"
        with open(user_config, "r") as f:
            config = yaml.safe_load(f)
        return config

    def load_install_config(self) -> str:
        """Read and return the configuration data from config/install.yaml

        Returns:
            str: Configuration data (install.yaml)
        """
        install_config = self.CONFIG_PATH / "install.yaml"
        with open(install_config, "r") as f:
            config = yaml.safe_load(f)
        return config

    def load_logging_config(self) -> str:
        """Read and return the configuration data from config/install.yaml

        Returns:
            str: Configuration data (logging.yaml)
        """
        logging_config = self.CONFIG_PATH / "logging.yaml"
        with open(logging_config, "r") as f:
            config = yaml.safe_load(f)
        return config

    def load_backup_config(self) -> str:
        """Read and return the configuration data from config/backup.yaml

        Returns:
            str: Configuration data (backup.yaml)
        """
        backup_config = self.CONFIG_PATH / "backup.yaml"
        with open(backup_config, "r") as f:
            config = yaml.safe_load(f)
        return config