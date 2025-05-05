import hashlib
from pathlib import Path
import shutil
import tempfile
import datetime
import json
import os
#from dotborn.logger import setup_logger
from config import Configure

#log = setup_logger()

user_configs = Configure().load_user_config()
backup_configs = Configure().load_backup_config()

class BackupManager:

    def __init__(self, usr_configs:dict, backup_configs:dict):
        self.backup_dir = backup_configs.get('backup_settings', {}).get('backup_dir')
        self.compress = backup_configs.get('backup_settings', {}).get('compress')
        self.include_private_keys = backup_configs.get('backup_settings', {}).get('include_private_keys')
        self.output_tarball = backup_configs.get('backup_settings', {}).get('output_tarball')
        self.tarball_name = backup_configs.get('backup_settings', {}).get('tarball_name')
        self.encrypt_backup = backup_configs.get('backup_settings', {}).get('encrypt_backup')
        self.flags = usr_configs.get('system_settings', {}).get('flags', {})


manager = BackupManager(user_configs, backup_configs)
print(manager.backup_dir, manager.compress, manager.include_private_keys, manager.output_tarball, manager.tarball_name, manager.encrypt_backup, manager.flags)