import importlib.resources as pkg_resources

from dotborn.logger import setup_logger

log = setup_logger()

def load_template(filename:str) -> str:
    log.info(f"Template loaded: {filename}")
    template_text = pkg_resources.files("dotborn.data.templates").joinpath(filename).read_text()
    return template_text