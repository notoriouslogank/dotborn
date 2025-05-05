from typing import Tuple, Optional, Dict
from pathlib import Path
import shutil
import tempfile
import datetime
import json
from dotborn.logger import setup_logger
from dotborn.hash import hash_file

log = setup_logger()


def write_manifest(manifest_data:dict, output_path:Path):
    """Write manifest of backed-up files

    Args:
        manifest_data (dict): Dictionary containing the list(s) of files backed up
        output_path (Path): Destination path for dotborn_manifest.json
    """
    try:
        with open(output_path, "w") as f:
            json.dump(manifest_data, f, indent=2)
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


class BackupManager:
    """Represents a collection of configuration settings for backup utility.

    This class manages dictionaries of usr_configs and backup_configs (config/user.yaml, config/backup.yaml). It provides easy access to necessary configuration variables.

    Attributes:
        backup_configs (dict): A dictionary of configuration settings
        usr_configs (dict): A dictionary of system-wide user configuration settings
        windows_configs (dict): A dictionary containing the Windows-specific subset of configurations from backup_configs
        linux_configs (dict): A dictionary containing the Linux-specific subset of configurations from backup_configs
    """

    def __init__(self, usr_configs: dict, backup_configs: dict):
        log.info(f"Getting backup configs...")
        self.backup_configs = backup_configs.get("backup_settings", {})
        self.usr_configs = usr_configs
        self.windows_configs = self.backup_configs.get("platform", {}).get(
            "windows", {}
        )
        self.linux_configs = self.backup_configs.get("platform", {}).get("linux", {})

    def prepare_windows(self) -> Tuple[str, Path, bool, bool, bool, bool, Dict]:
        """Parse the backup config file and return Windows-specific settings.

        Returns:
            tuple: A 7-element tuple containing:
                - backup_name (str): Name for the output backed-up directory.
                - output_dir (Path): Destination path for the output backup
                - include_prive_keys (bool): Whether to copy private keys
                - compress (bool): Whether or not to compress the output backup archive
                - output_tarball (bool): Whether or not to archive the backup as a .tar.gz
                - encrypt_backup (bool): Whether or not to encrypt the output archive
                - targets (dict): Dictionary containing the paths/files to be backed up
        """
        backup_name = self.windows_configs.get("backup_name")
        output_dir = Path(self.windows_configs.get("output_dir"))
        output_dir = Path(self.windows_configs.get("output_dir")).expanduser().resolve()
        print(output_dir)
        include_private_keys = self.windows_configs.get("flags", {}).get(
            "include_private_keys"
        )
        compress = self.windows_configs.get("flags", {}).get("compress")
        output_tarball = self.windows_configs.get("flags", {}).get("output_tarball")
        encrypt_backup = self.windows_configs.get("flags", {}).get("encrypt_backup")
        targets = self.windows_configs.get("targets", {})
        return (
            backup_name,
            output_dir,
            include_private_keys,
            compress,
            output_tarball,
            encrypt_backup,
            targets,
        )

    def prepare_linux(self):
        """Parse the backup config file and return Linux-specific settings.

        Returns:
            tuple: A 7-element tuple containing:
                - backup_name (str): Name for the output backed-up directory.
                - output_dir (Path): Destination path for the output backup
                - include_prive_keys (bool): Whether to copy private keys
                - compress (bool): Whether or not to compress the output backup archive
                - output_tarball (bool): Whether or not to archive the backup as a .tar.gz
                - encrypt_backup (bool): Whether or not to encrypt the output archive
                - targets (dict): Dictionary containing the paths/files to be backed up
        """
        backup_name = self.linux_configs.get("backup_name")
        output_dir = self.linux_configs.get("output_dir")
        include_private_keys = self.linux_configs.get("flags", {}).get(
            "include_private_keys"
        )
        compress = self.linux_configs.get("flags", {}).get("compress")
        output_tarball = self.linux_configs.get("flags", {}).get("output_tarball")
        encrypt_backup = self.linux_configs.get("flags", {}).get("encrypt_backup")
        targets = self.linux_configs.get("targets", {})
        return (
            backup_name,
            output_dir,
            include_private_keys,
            compress,
            output_tarball,
            encrypt_backup,
            targets,
        )


class LinBack:
    """Represents a collection of Linux-specific configurations regarding backups.

    This class handles copying, moving, naming, hashing, and otherwise handling backed up system files.

    Attributes:
        backup_name (str): The name for the backup archive
        output_dir (Path): Path to write the output directory
        include_private_keys (bool): Whether or not to backup private key files
        compress (bool): Whether or not to compress the backup to an archive
        output_tarball (bool): Whether or not to output the backup as a 'tar.gz' archive
        encrypt_backup (bool): Whether or not to encrypt the output backup archive
        targets (dict): Dictionary containing a list of dirs and files to be backed up on the Linux system
    """

    def __init__(self, linconfigs: tuple):
        (
            self.backup_name,
            self.output_dir,
            self.include_private_keys,
            self.compress,
            self.output_tarball,
            self.encrypt_backup,
            self.targets,
        ) = linconfigs

    def create_empty_backup_dirs(self, staging_dir:Path) -> dict:
        """Create a hierarchy of empty directories inside a temp file

        Args:
            staging_dir (Path[tempfile.TemporaryDirectory]): Destination path to create directory tree

        Returns:
            dict: The directory names and file paths as a key:value pair
        """
        log.debug(f"Making backup directories...")
        base_dir = Path(staging_dir)

        browser_data = base_dir / "browser_data"
        credentials = base_dir / "credentials"
        dotfiles = base_dir / "dotfiles"
        configs = base_dir / "configs"
        sysfiles = base_dir / "sysfiles"
        usr_dirs = base_dir / "usr_dirs"
        for d in [browser_data, credentials, dotfiles, configs, sysfiles, usr_dirs]:
            d.mkdir(parents=True, exist_ok=True)
        return {
            "browser_data": browser_data,
            "credentials": credentials,
            "dotfiles": dotfiles,
            "configs": configs,
            "sysfiles": sysfiles,
            "usr_dirs": usr_dirs,
        }

    def copy_items(self, items: list, dest_dir: Path, item_type: str) -> list[dict]:
        """Copy each individual item in the item list to the destination directory and note its' type; return a list of all items copied.

        Args:
            items (list): List of items to copy
            dest_dir (Path): The destination directory for each copy
            item_type (str): The type of each item copied

        Returns:
            list[dict]: A list of dictionaries containing the source, destination, and hash of the copied file
        """
        results = []
        for item in items:
            src = Path(item).expanduser().resolve()
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
                results.append(
                    {"source": str(src), "dest": str(dst), "hash": file_hash}
                )
                log.info(f"Copied {item_type}: {src} -> {dst}")
            except Exception as e:
                log.error(f"Failed to copy {item_type}: {src} - {e}")
        return results

    def backup(self):
        """
        """
        backup_root = Path(f"{self.output_dir}")
        backup_root = backup_root.expanduser().resolve()
        print(backup_root)
        with tempfile.TemporaryDirectory() as tmpdir:
            staging_dir = Path(tmpdir)
            subdirs = self.create_empty_backup_dirs(staging_dir)
            browser_data = self.targets.get("browser_data", [])
            credentials = self.targets.get("credentials", [])
            configs = self.targets.get("configs", [])
            dotfiles = self.targets.get("dotfiles", [])
            sysfiles = self.targets.get("sysfiles", [])
            usr_dirs = self.targets.get("usr_dirs", [])

            copied_browser_data = self.copy_items(
                browser_data, subdirs["browser_data"], "browser_data"
            )
            copied_credentials = self.copy_items(
                credentials, subdirs["credentials"], "credential"
            )
            copied_configs = self.copy_items(configs, subdirs["configs"], "config")
            copied_dotfiles = self.copy_items(dotfiles, subdirs["dotfiles"], "dotfile")
            copied_sysfiles = self.copy_items(sysfiles, subdirs["sysfiles"], "sysfile")
            copied_usr_dirs = self.copy_items(usr_dirs, subdirs["usr_dirs"], "usr_dir")

            manifest = {
                "timestamp": datetime.datetime.now().isoformat(),
                "broswer_data": copied_browser_data,
                "credentials": copied_credentials,
                "configs": copied_configs,
                "sysfiles": copied_sysfiles,
                "dotfiles": copied_dotfiles,
                "usr_dirs": copied_usr_dirs,
            }

            manifest_path = Path.joinpath(staging_dir, "backup_manifest.json")
            write_manifest(manifest, manifest_path)

            if self.compress and self.output_tarball:
                compress_backup(staging_dir, backup_root, self.backup_name)
            else:
                final_backup = (
                    Path(backup_root / self.backup_name).expanduser().resolve()
                )
                shutil.copytree(staging_dir, final_backup, dirs_exist_ok=True)
                log.info(f"Backup copied to {final_backup}")


class WinBack:
    """Represents a collection of Windows-specific configurations regarding backups.

    This class handles copying, moving, naming, hashing, and otherwise handling backed up system files.

    Attributes:
        backup_name (str): The name for the backup archive
        output_dir (Path): Path to write the output directory
        include_private_keys (bool): Whether or not to backup private key files
        compress (bool): Whether or not to compress the backup to an archive
        output_tarball (bool): Whether or not to output the backup as a 'tar.gz' archive
        encrypt_backup (bool): Whether or not to encrypt the output backup archive
        targets (dict): Dictionary containing a list of dirs and files to be backed up on the Windows system
    """
    def __init__(self, winconfigs: tuple):
        (
            self.backup_name,
            self.output_dir,
            self.include_private_keys,
            self.compress,
            self.output_tarball,
            self.encrypt_backup,
            self.targets,
        ) = winconfigs

    def create_empty_backup_dirs(self, staging_dir:Path):
        """Create a hierarchy of empty directories inside a temp file

        Args:
            staging_dir (Path[tempfile.TemporaryDirectory]): Destination path to create directory tree

        Returns:
            dict: The directory names and file paths as a key:value pair
        """
        log.debug(f"Making backup directories...")
        base_dir = Path(staging_dir).expanduser().resolve()
        browser_data = base_dir / "browser_data"
        credentials = base_dir / "credentials"
        dotfiles = base_dir / "dotfiles"
        configs = base_dir / "configs"
        sysfiles = base_dir / "sysfiles"
        usr_dirs = base_dir / "usr_dirs"
        for d in [browser_data, credentials, dotfiles, configs, sysfiles, usr_dirs]:
            d.mkdir(parents=True, exist_ok=True)
        return {
            "browser_data": browser_data,
            "credentials": credentials,
            "dotfiles": dotfiles,
            "configs": configs,
            "sysfiles": sysfiles,
            "usr_dirs": usr_dirs,
        }

    def copy_items(self, items: list, dest_dir: Path, item_type: str):
        """Copy each individual item in the item list to the destination directory and note its' type; return a list of all items copied.

        Args:
            items (list): List of items to copy
            dest_dir (Path): The destination directory for each copy
            item_type (str): The type of each item copied

        Returns:
            list[dict]: A list of dictionaries containing the source, destination, and hash of the copied file
        """
        results = []

        for item in items:
            if item == None:
                print("None item")
                pass
            if item != None:
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
                    results.append(
                        {"source": str(src), "dest": str(dst), "hash": file_hash}
                    )
                    log.info(f"Copied {item_type}: {src} -> {dst}")
                except Exception as e:
                    log.error(f"Failed to copy {item_type}: {src} - {e}")
        return results

    def backup(self) -> str:
        """Run the backup utility, copying all files and directories in the configuration file(s) and return the resultant backup file as a string

        Returns:
            str: String representing the file path to the resultant backup
        """
        backup_root = Path(self.output_dir / self.backup_name).expanduser().resolve()
        with tempfile.TemporaryDirectory() as tmpdir:
            staging_dir = Path(tmpdir)
            subdirs = self.create_empty_backup_dirs(staging_dir)

            browser_data = self.targets.get("browser_data", [])
            credentials = self.targets.get("credentials", [])
            configs = self.targets.get("configs", [])
            dotfiles = self.targets.get("dotfiles", [])
            sysfiles = self.targets.get("sysfiles", [])
            usr_dirs = self.targets.get("usr_dirs", [])

            copied_browser_data = self.copy_items(
                browser_data, subdirs["browser_data"], "browser_data"
            )
            copied_credentials = self.copy_items(
                credentials, subdirs["credentials"], "credential"
            )
            copied_configs = self.copy_items(configs, subdirs["configs"], "config")
            copied_sysfiles = self.copy_items(
                sysfiles, subdirs["sysfiles"], "system file"
            )
            copied_dotfiles = self.copy_items(dotfiles, subdirs["dotfiles"], "dotfile")
            copied_usr_dirs = self.copy_items(usr_dirs, subdirs["usr_dirs"], "usr_dir")

            manifest = {
                "timestamp": datetime.datetime.now().isoformat(),
                "browser_data": copied_browser_data,
                "credentials": copied_credentials,
                "configs": copied_configs,
                "sysfiles": copied_sysfiles,
                "dotfiles": copied_dotfiles,
                "usr_dirs": copied_usr_dirs,
            }

            manifest_path = Path.joinpath(staging_dir, "backup_manifest.json")
            write_manifest(manifest, manifest_path)

            if self.compress and self.output_tarball:
                final_backup = compress_backup(staging_dir, backup_root, self.backup_name)
                log.info(f'Backup compressed and archived at: {final_backup}')
            else:
                final_backup = (
                    Path(backup_root / self.backup_name).expanduser().resolve()
                )
                shutil.copytree(staging_dir, final_backup, dirs_exist_ok=True)
                log.info(f"Backup copied to {final_backup}")
            return(str(final_backup))

