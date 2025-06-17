from typing import Tuple, Optional, Dict, List
from pathlib import Path
import shutil
import tempfile
import datetime
import json
import os
from dotborn.logger import setup_logger
from dotborn.hash import hash_file

log = setup_logger()


def expand_safe(path_str:str) -> Path:
    return Path(os.path.expandvars(os.path.expanduser(path_str)))

def write_manifest(manifest_data:dict, output_path:Path):
    """Write manifest of backed-up files

    Args:
        manifest_data (dict): Dictionary containing the list(s) of files backed up
        output_path (Path): Destination path for dotborn_manifest.json
    """
    try:
        with open(output_path, "w") as f:
            json.dump(str(manifest_data), f, indent=2)
        log.info(f"Backup manifest written to: {output_path}")
    except Exception as e:
        log.error(f"Failed to write manifest: {e}")

def compress_backup(src:Path, dest:Path, backup_name:str) -> str:
    """Compress a directory and return the compressed file
    Args:
        src (Path): Directory to compress
        dest (Path): Destination to output compressed archive
        backup_name (str): Name for the output archive
    Returns:
        str: Path to the resultant compressed archive
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    archive_name = f"{dest}/{backup_name}_{timestamp}"
    archive_path = shutil.make_archive(str(archive_name), "gztar", root_dir=src)
    log.info(f"Compressed backup to {archive_path}")
    return archive_path

class Backup:

    def __init__(self, config:dict):
        self.backup_name = config.get("backup_name")
        self.output_dir = expand_safe(config.get("output_dir"))
        self.include_private_keys = config.get("flags", {}).get("include_private_keys")
        self.compress = config.get("flags", {}).get("compress")
        self.output_tarball = config.get("flags", {}).get("output_tarball")
        self.encrypt_backup = config.get("flags", {}).get("encrypt_backup")
        self.targets = config.get("targets", {})

    def create_empty_backup_dirs(self, base_dir: Path) -> Dict[str, Path]:
        log.debug(f'Making backup directories...')
        subdirs = ["browser_data", "credentials", "dotfiles", "configs", "sysfiles", "usr_dirs"]
        paths = {}
        for name in subdirs:
            path = base_dir/name
            path.mkdir(parents=True, exist_ok=True)
            paths[name] = path
        return paths

    def copy_items(self, items: Optional[List[str]], dest_dir:Path, item_type:str) -> List[Dict[str, str]]:
        results = []
        for item in items:
            src = expand_safe(item)
            try:
                if not src.exists():
                    log.warning(f"{item_type} not found: {src}")
                    continue
                dst = dest_dir/src.name
                if src.is_dir():
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                else:
                    shutil.copy2(src, dst)
                file_hash = hash_file(dst) if dst.is_file() else None
                results.append({"source": str(src), "dest":str(dst), "hash":{file_hash}})
                log.info(f"Copied {item_type}: {src} -> {dst}")
            except Exception as e:
                log.error(f"Failed to copy {item_type}: {src} - {e}")
        return results

    def run_backup(self) -> None:
        backup_root = self.output_dir
        with tempfile.TemporaryDirectory() as tmpdir:
            staging_dir = Path(tmpdir)
            subdirs = self.create_empty_backup_dirs(staging_dir)

            manifest = {"timestamp": datetime.datetime.now().isoformat()}
            for key in subdirs:
                copied = self.copy_items(self.targets.get(key, []), subdirs[key], key)
                manifest[key] = copied

            manifest_path = staging_dir/"backup_manifest.json"
            write_manifest(manifest, manifest_path)

            if self.compress and self.output_tarball:
                return compress_backup(staging_dir, backup_root, self.backup_name)
            else:
                final_backup = (backup_root/self.backup_name).expanduser().resolve()
                shutil.copytree(staging_dir, final_backup, dirs_exist_ok=True)
                log.info(f"Backup copied to {final_backup}")


class LinBack(Backup):
    def __init__(self, backup_configs:dict):
        config = backup_configs.get('backup_settings', {}).get('platform', {}).get('linux', {})
        super().__init__(config)

class WinBack(Backup):
    def __init__(self, backup_configs:dict):
        config = backup_configs.get('backup_settings', {}).get("platform", {}).get("windows", {})
        super().__init__(config)

