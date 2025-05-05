import hashlib
from pathlib import Path
import shutil
import tempfile
import datetime
import json
import os
from dotborn.logger import setup_logger
from dotborn.config import Configure
from dotborn.hash import hash_file

log = setup_logger()


def write_manifest(manifest_data, output_path):
    try:
        with open(output_path, 'w') as f:
            json.dump(manifest_data, f, indent=2)
        log.info(f"Backup manifest written to: {output_path}")
    except Exception as e:
        log.error(f"Failed to write manifest: {e}")

class BackupManager:

    def __init__(self, usr_configs:dict, backup_configs:dict):
        log.info(f"Getting backup configs...")
        self.backup_configs = backup_configs.get('backup_settings', {})
        self.usr_configs = usr_configs
        self.windows_configs = self.backup_configs.get('platform', {}).get('windows', {})
        self.linux_configs = self.backup_configs.get("platform", {}).get('linux', {})

    def prepare_windows(self):
        backup_name = self.windows_configs.get('backup_name')
        output_dir = Path(self.windows_configs.get('output_dir').expanduser().resolve())
        include_private_keys = self.windows_configs.get('flags', {}).get('include_private_keys')
        compress = self.windows_configs.get('flags', {}).get('compress')
        output_tarball = self.windows_configs.get('flags', {}).get('output_tarball')
        encrypt_backup = self.windows_configs.get('flags', {}).get('encrypt_backup')
        targets = self.windows_configs.get('targets', {})
        return backup_name, output_dir, include_private_keys, compress, output_tarball, encrypt_backup, targets


    def prepare_linux(self):
        backup_name = self.linux_configs.get('backup_name')
        output_dir = self.linux_configs.get('output_dir')
        include_private_keys = self.linux_configs.get('flags', {}).get('include_private_keys')
        compress = self.linux_configs.get('flags', {}).get('compress')
        output_tarball = self.linux_configs.get('flags', {}).get('output_tarball')
        encrypt_backup = self.linux_configs.get('flags', {}).get('encrypt_backup')
        targets = self.linux_configs.get('targets', {})
        return backup_name, output_dir, include_private_keys, compress, output_tarball, encrypt_backup, targets

class LinBack:

    def __init__(self, linconfigs:tuple):
        self.backup_name, self.output_dir, self.include_private_keys, self.compress, self.output_tarball, self.encrypt_backup, self.targets = linconfigs

    def create_empty_backup_dirs(self, staging_dir):
        log.debug(f"Making backup directories...")
        base_dir = Path(staging_dir)
        print(base_dir)
        browser_data = base_dir/"browser_data"
        credentials = base_dir/"credentials"
        dotfiles = base_dir/"dotfiles"
        configs = base_dir/"configs"
        sysfiles = base_dir/"sysfiles"
        usr_dirs = base_dir/"usr_dirs"
        for d in [browser_data, credentials, dotfiles, configs, sysfiles, usr_dirs]:
            d.mkdir(parents=True, exist_ok=True)
        return {"browser_data":browser_data, "credentials":credentials, "dotfiles":dotfiles, "configs":configs, "sysfiles":sysfiles, "usr_dirs":usr_dirs}

    def copy_items(self, items: list, dest_dir: Path, item_type:str):
        results = []
        for item in items:
            src = Path(item).expanduser().resolve()
            if not src.exists():
                log.warning(f'{item_type} not found: {src}')
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
                log.error(f"Failed to copy {item_type}: {src} - {e}")
        return results

    def compress_backup(self, src:Path, dest:Path):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        archive_name = f"{dest}/{self.backup_name}_{timestamp}"
        archive_path = shutil.make_archive(str(archive_name), "gztar", root_dir=src)
        log.info(f"Compressed backup to {archive_path}")
        return archive_path

    def backup(self):
        backup_root = Path(f"{self.output_dir}")
        backup_root = backup_root.expanduser().resolve()
        print(backup_root)
        with tempfile.TemporaryDirectory() as tmpdir:
            staging_dir = Path(tmpdir)
            subdirs = self.create_empty_backup_dirs(staging_dir)
            browser_data = self.targets.get('browser_data', [])
            credentials = self.targets.get('credentials', [])
            configs = self.targets.get('configs', [])
            dotfiles = self.targets.get('dotfiles', [])
            sysfiles = self.targets.get('sysfiles', [])
            usr_dirs = self.targets.get('usr_dirs', [])

            copied_browser_data = self.copy_items(browser_data, subdirs['browser_data'], 'browser_data')
            copied_credentials = self.copy_items(credentials, subdirs['credentials'], 'credential')
            copied_configs = self.copy_items(configs, subdirs['configs'], 'config')
            copied_dotfiles = self.copy_items(dotfiles, subdirs['dotfiles'], 'dotfile')
            copied_sysfiles = self.copy_items(sysfiles, subdirs['sysfiles'], 'sysfile')
            copied_usr_dirs = self.copy_items(usr_dirs, subdirs['usr_dirs'], 'usr_dir')

            manifest = {
                "timestamp": datetime.datetime.now().isoformat(),
                "broswer_data": copied_browser_data,
                "credentials": copied_credentials,
                "configs": copied_configs,
                "sysfiles": copied_sysfiles,
                "dotfiles": copied_dotfiles,
                "usr_dirs": copied_usr_dirs
            }

            manifest_path = Path.joinpath(staging_dir, "backup_manifest.json")
            write_manifest(manifest, manifest_path)

            if self.compress and self.output_tarball:
                self.compress_backup(staging_dir, backup_root)
            else:
                final_backup = Path(backup_root/self.backup_name).expanduser().resolve()
                shutil.copytree(staging_dir, final_backup, dirs_exist_ok=True)
                log.info(f"Backup copied to {final_backup}")

class WinBack:

    def __init__(self, winconfigs: tuple):
        self.backup_name, self.output_dir, self.include_private_keys, self.compress, self.output_tarball, self.encrypt_backup, self.targets = winconfigs

    def create_empty_backup_dirs(self):
        log.debug(f"Making backup directories...")
        base_dir = Path(self.output_dir/self.backup_name).expanduser().resolve()
        browser_data = base_dir/"browser_data"
        credentials = base_dir/"credentials"
        dotfiles = base_dir/"dotfiles"
        configs = base_dir/"configs"
        sysfiles = base_dir/"sysfiles"
        usr_dirs = base_dir/"usr_dirs"
        for d in [browser_data, credentials, dotfiles, configs, sysfiles, usr_dirs]:
            d.mkdir(parents=True, exist_ok=True)
        return {"browser_data":browser_data, "credentials":credentials, "dotfiles":dotfiles, "configs":configs, "sysfiles":sysfiles, "usr_dirs":usr_dirs}

    def copy_items(self, items:list, dest_dir:Path, item_type:str):
        results = []
        for item in items:
            raw = Path(item)
            src = raw.expanduser().resolve()
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
                log.error(f"Failed to copy {item_type}: {src} - {e}")
        return results

    def compress_backup(self, src:Path, dest:Path):

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        archive_name = f"{dest}/{self.backup_name}_{timestamp}"
        archive_path = shutil.make_archive(str(archive_name), "gztar", root_dir=src)
        log.info(f"Compressed backup to {archive_path}")
        return archive_path

    def backup(self):
        backup_root = Path(self.output_dir/self.backup_name).expanduser().resolve()
        with tempfile.TemporaryDirectory() as tmpdir:
            staging_dir = Path(tmpdir)
            subdirs = self.create_empty_backup_dirs(staging_dir)

            browser_data = self.targets.get('browser_data', [])
            credentials = self.targets.get('credentials', [])
            configs = self.targets.get('configs', [])
            dotfiles = self.targets.get('dotfiles', [])
            sysfiles = self.targets.get('sysfiles', [])
            usr_dirs = self.targets.get('usr_dirs', [])

            copied_browser_data = self.copy_items(browser_data, subdirs['browser_data'], 'browser_data')
            copied_credentials = self.copy_items(credentials, subdirs['credentials'], 'credential')
            copied_configs = self.copy_items(configs, subdirs['configs'], 'config')
            copied_sysfiles = self.copy_items(sysfiles, subdirs['sysfiles'], 'system file')
            copied_dotfiles = self.copy_items(dotfiles, subdirs['dotfiles'], 'dotfile')
            copied_usr_dirs = self.copy_items(usr_dirs, subdirs['usr_dirs'], 'usr_dir')


            manifest = {
                "timestamp": datetime.datetime.now().isoformat(),
                "browser_data": copied_browser_data,
                "credentials": copied_credentials,
                "configs": copied_configs,
                "sysfiles": copied_sysfiles,
                "dotfiles": copied_dotfiles,
                "usr_dirs": copied_usr_dirs
            }

            manifest_path = Path.joinpath(staging_dir, "backup_manifest.json")
            write_manifest(manifest, manifest_path)

            if self.compress and self.output_tarball:
                self.compress_backup(staging_dir, backup_root)
            else:
                final_backup = Path(backup_root/self.backup_name).expanduser().resolve()
                shutil.copytree(staging_dir, final_backup, dirs_exist_ok=True)
                log.info(f"Backup copied to {final_backup}")