from pathlib import Path

# PROJECT PATHS
PROJECT_ROOT = Path(__file__).resolve().parents[1] # from utils/paths.py
CONFIG_PATH = PROJECT_ROOT/"config.yaml"
TEMPLATE_DIR = PROJECT_ROOT/"dotborn"/"data"/"templates"
LOG_PATH=PROJECT_ROOT/"dotborn.log"

# SYSTEM PATHS
USER_HOME = Path.home()
