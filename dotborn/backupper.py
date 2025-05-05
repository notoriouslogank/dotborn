import hashlib
from pathlib import Path
import shutil
import tempfile
import datetime
import json
import os
from dotborn.logger import setup_logger
from dotborn.config import load_config
from dotborn.hash import hash_file

log = setup_logger()
conf = load_config()

class BackupManager: # Is this class really necessary?
                     # At the end of the day, all it's going to do is call WindowsBackup and LinuxBackup functions...

    def __init__(self):
        pass

