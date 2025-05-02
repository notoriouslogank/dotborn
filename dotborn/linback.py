"""
linback.py - Dotfile link-and-backup utilities for dotborn

Provides functions to safely symlink configuration files to their target locations, creating timestamped backups of any existing files.
"""

import hashlib
from pathlib import Path
import shutil
import tempfile
import datetime
import json
import os
from dotborn.logger import setup_logger
from dotborn.config import load_config

log = setup_logger()
conf = load_config()


def hash_file(path: Path, algo: str = "sha256") -> str:
    """
    Hash a given file.

    Parameters:
        path (Path): The file to hash.
        algo (str): The algorithm to use [default=sha256]

    Returns:
        str: The hash of the file.
    """
    log.info(f"Hashing {path}....")
    h = hashlib.new(algo)
    with open(path, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    hash = h.hexdigest()
    log.info(f"Hash: {hash}")
    return hash


def create_backup_dirs(base_dir: Path) -> dict:
    """
    Create output directory for backups.

    Parameters:
        base_dir (Path): The destination path for the output backup directory

    Returns:
        dict: File paths for dotfiles, configs, and system configuration file backups
    """
    dotfiles = base_dir/"dotfiles"
    configs = base_dir/"configs"
    system = base_dir/"system"
    for d in [dotfiles, configs, system]:
        d.mkdir(parents=True, exist_ok=True)
    return {"dotfiles": dotfiles, "configs": configs, "system": system}


def copy_items(item_list: list, dest_dir: Path, item_type) -> list:
    """
    Copy given files and directories to backup destination.

    Parameters:
        item_list (list): The compiled list of item dirs and files to be backed up.
        dest_dir (Path): The destination path for backed up file or dir.
        item_type: The type (file|dir) of each item.

    Returns:
        list: All copied file and directory paths.
    """
    results = []
    for item in item_list:
        raw = Path(item)
        # item = Path(f"{conf['user']['home_dir']}/{item}")
        src = raw.expanduser().resolve() if str(raw).startswith("~") else raw.resolve()
        if not src.exists():
            log.warning(f"{item_type} not found: {src}")
            continue
        try:
            dst = Path(dest_dir, src.name)
            if src.is_dir():
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)
            file_hash = hash_file(dst) if dst.is_file() else None
            results.append({"source": str(src),
                            "dest": str(dst),
                            "hash": file_hash})
            log.info(f"Copied {item_type}: {src} -> {dst}")
        except Exception as e:
            log.error(f"Failed to cpy {item_type}: {src} - {e}")
    return results


def write_manifest(manifest_data: dict, output_path: Path) -> None:
    """
    Write the backup manifest (dotborn_manifest.json).

    Parameters:
        manifest_data (dict): Data entry for each file/directory backed up
        output_path (Path): File path to create output file/directory

    Returns:
        None
    """
    try:
        with open(output_path, 'w') as f:
            json.dump(manifest_data, f, indent=2)
        log.info(f"Backup manifest written to {output_path}")
    except Exception as e:
        log.error(f"Failed to write manifest: {e}")


def compress_backup(source_dir: Path, output_dir: Path, name='dotborn_backup') -> Path:
    """
    Compress a given directory to a .tar.gz archive.

    Parameters:
        source_dir (Path): Directory to archive.
        output_dir (Path): Destination file path for compressed archive.
        name (str): Name for the compressed archive [{name}.tar.gz]

    Returns:
        Path: File path for the destination of the compressed archive.
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    archive_name = f"{output_dir}/{name}_{timestamp}"
    archive_path = shutil.make_archive(
        str(archive_name), "gztar", root_dir=source_dir)
    log.info(f"Compressed backup to {archive_path}")
    return archive_path


def run_backup():
    """
    Run the backup utility for the Linux configuration.
    """
    backup_root = Path(conf['system_settings']
                       ['backup_dir']).expanduser().resolve()
    compress = conf['backup_settings'].get('compress', False)
    output_tarball = conf['backup_settings'].get('output_tarball', False)

    with tempfile.TemporaryDirectory() as tmpdir:
        staging_dir = Path(tmpdir)
        subdirs = create_backup_dirs(staging_dir)

        dotfiles = conf['backup_settings']['backup_targets']['linux']['paths'].get(
            'dotfiles', [])
        for i in dotfiles:
            print(i)
        configs = conf['backup_settings']['backup_targets']['linux']['paths'].get(
            'config_dirs', [])
        for i in configs:
            print(i)
        system = conf['backup_settings']['backup_targets']['linux']['paths'].get(
            'sys_dirs', [])
        for i in system:
            print(i)
        copied_dotfiles = copy_items(dotfiles, subdirs['dotfiles'], 'dotfile')
        copied_configs = copy_items(configs, subdirs['configs'], 'config')
        copied_system = copy_items(system, subdirs['system'], 'system config')

        manifest = {
            "timestamp": datetime.datetime.now().isoformat(),
            "dotfiles": copied_dotfiles,
            "configs": copied_configs,
            "system": copied_system,
        }

        manifest_path = Path.joinpath(staging_dir, "dotborn_manifest.json")
        write_manifest(manifest, manifest_path)

        if compress and output_tarball:
            compress_backup(staging_dir, backup_root)
        else:
            final_backup = backup_root/"dotborn_backup"
            shutil.copytree(staging_dir, final_backup, dirs_exist_ok=True)
            log.info(f"Backup copied to {final_backup}")
