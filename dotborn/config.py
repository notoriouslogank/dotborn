import yaml
from dotborn import logger, paths

log = logger.setup_logger()


def load_config():
    log.info(f"Loading configfile {paths.CONFIG_PATH}")
    # TODO: Validate that file exists, etc
    with open(paths.CONFIG_PATH, 'r') as f:
        config = yaml.safe_load(f)
    return config

