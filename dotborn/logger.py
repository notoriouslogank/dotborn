import logging
from pathlib import Path
from rich.logging import RichHandler
from dotborn.config import Configure

configs = Configure()


def setup_logger(
    name: str = __name__,
    level=logging.INFO,
    verbose: bool = False,
    quiet=False,
    log_file: Path = configs.LOG_PATH,
) -> logging.Logger:
    if quiet:
        level = logging.WARNING
    elif verbose:
        level = logging.DEBUG

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    if not logger.handlers:
        # Console Handler
        rich_handler = RichHandler(
            rich_tracebacks=True,
            markup=True,
            show_time=True,
            show_level=True,
            show_path=True,
        )
        rich_formatter = logging.Formatter(">> %(message)s")
        rich_handler.setFormatter(rich_formatter)
        logger.addHandler(rich_handler)

        # File Handler
        file_handler = logging.FileHandler(log_file)
        file_formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(level)
        logger.addHandler(file_handler)

    return logger
