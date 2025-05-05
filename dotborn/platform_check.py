import platform
from dotborn import logger

log = logger.setup_logger()


def check_platform():
    log.debug(f"Checking platform...")
    system = platform.system()
    log.info(f"Platform detected: {system}")
    return system
