"""
template.py - Dotfile template loader utility for dotborn
"""

import importlib.resources as pkg_resources

from dotborn.logger import setup_logger

log = setup_logger()

def load_template(filename:str) -> str:
    """Load template from dotborn/templates.

    Args:
        filename (str): The template to load.

    Returns:
        str: Data to write to outfile.
    """
    log.info(f"Template loaded: {filename}")
    template_text = pkg_resources.files("dotborn.data.templates").joinpath(filename).read_text()
    return template_text