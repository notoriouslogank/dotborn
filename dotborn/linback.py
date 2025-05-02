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

def hash_file(path, algo="sha256"):
    log.info(f"Hasing {path}....")
    h = hashlib.new(algo)
    with open(path, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    hash = h.hexdigest()
    log.info(f"Hash: {hash}")
    return hash

def create_backup_dirs(base_dir: Path) -> dict:
    dotfiles = base_dir/"dotfiles"
    configs = base_dir/"configs"
    system = base_dir/"system"
    for d in [dotfiles, configs, system]:
        d.mkdir(parents=True, exist_ok=True)
    return {"dotfiles":dotfiles, "configs":configs, "system":system}

def copy_items(item_list:list, dest_dir:Path, item_type):
    results = []
    for item in item_list:
        raw = Path(item)
        #item = Path(f"{conf['user']['home_dir']}/{item}")
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
            results.append({"source":str(src),
                            "dest":str(dst),
                            "hash":file_hash})
            log.info(f"Copied {item_type}: {src} -> {dst}")
        except Exception as e:
            log.error(f"Failed to cpy {item_type}: {src} - {e}")
    return results

def write_manifest(manifest_data, output_path:Path):
    try:
        with open(output_path, 'w') as f:
            json.dump(manifest_data, f, indent=2)
        log.info(f"Backup manifest written to {output_path}")
    except Exception as e:
        log.error(f"Failed to write manifest: {e}")

def compress_backup(source_dir:Path, output_dir:Path, name='dotborn_backup'):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    archive_name = f"{output_dir}/{name}_{timestamp}"
    archive_path = shutil.make_archive(str(archive_name), "gztar", root_dir=source_dir)
    log.info(f"Compressed backup to {archive_path}")
    return archive_path

def run_backup():
    backup_root = Path(conf['system_settings']['backup_dir']).expanduser().resolve()
    compress = conf['backup_settings'].get('compress', False)
    output_tarball = conf['backup_settings'].get('output_tarball', False)

    with tempfile.TemporaryDirectory() as tmpdir:
        staging_dir = Path(tmpdir)
        subdirs = create_backup_dirs(staging_dir)

        dotfiles = conf['backup_settings']['backup_targets']['linux']['paths'].get('dotfiles', [])
        for i in dotfiles:
            print(i)
        configs = conf['backup_settings']['backup_targets']['linux']['paths'].get('config_dirs', [])
        for i in configs:
            print(i)
        system = conf['backup_settings']['backup_targets']['linux']['paths'].get('sys_dirs', [])
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