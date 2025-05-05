import hashlib
from pathlib import Path
from dotborn.logger import setup_logger

log = setup_logger()


def hash_file(path: Path, algo="sha256"):
    log.info(f"Hashing {path}....")
    h = hashlib.new(algo)
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    hash = h.hexdigest()
    log.info(f"Hash: {hash}")
    return hash
