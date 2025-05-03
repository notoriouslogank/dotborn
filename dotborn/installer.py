from dotborn.config import load_config
from dotborn.logger import setup_logger
import subprocess
import os

log = setup_logger()

class AptInstaller:

    apt_update_cmd = ["apt", "update", "-y"]

    def __init__(self, packages:list, flags:list):
        self.packages = packages
        self.flags = flags

    def _apt_update(self):
        cmd = ["apt", "update", "-y"]
        if self.flags.get('allow_sudo') == False:
            try:
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                log.warning(f"This command requires sudo. Please ensure the `allow_sudo` flag is set to True.")
            except subprocess.CalledProcessError as e:
                log.warning(f"This command requires the `allow_sudo` flag to be on in `config.yaml`.\n{e}")
                return
        elif self.flags.get('allow_sudo') == True:
            try:
                cmd.insert(0, "sudo")
                log.info(f"Updating apt repositories...")
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                log.info(f"apt repositories up to date")
            except subprocess.CalledProcessError as e:
                log.error(f"{e}")

    def dry_run(self):
        installed = []
        failed = []

        if self.flags.get('allow_sudo') == False:
            for pkg in self.packages:
                cmd = ["apt", "install", "--simulate", "-y"]
                try:
                    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                    log.info(f"[DRY RUN] Successfully installed {pkg}")
                    installed.append(pkg)
                except subprocess.CalledProcessError as e:
                    log.warning(f"This command requires `sudo`. Please verify `allow_sudo` flag is TRUE in `config.yaml`.\n{e}")
                    failed.append(pkg)

        elif self.flags.get('allow_sudo') == True:
            for pkg in self.packages:
                cmd = ["sudo", "apt", "install", "--simulate", "-y", pkg]
                try:
                    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                    log.info(f"[DRY RUN] Successfully installed {pkg}")
                    installed.append(pkg)
                except subprocess.CalledProcessError as e:
                    log.warning(f"Failed to install {pkg}: {e}")
                    failed.append(pkg)
        return installed, failed

    # TODO: `--interactive` support

    def install(self):
        log.debug(f"Installer goes here...")

class CargoInstaller:

    def __init__(self, packages:list, flags:list):
        self.packages = packages
        self.flags = flags

    def _check_current_installs(self):
        currently_installed_packages = []
        currently_installed_raw = subprocess.run(["cargo", "install", "--list"], capture_output=True, text=True)
        currently_installed_lines = currently_installed_raw.stdout.splitlines()
        for package in currently_installed_lines:
            if not package.endswith(":"):
                install = package.strip()
                currently_installed_packages.append(install)
        return currently_installed_packages


    def dry_run(self):
        matches = []

        currently_installed_packages = self._check_current_installs()

        log.debug(f"Crate installation candidates: {self.packages}")
        log.debug(f"Already installed crates: {currently_installed_packages}")
        for package in self.packages:
            if package in currently_installed_packages:
                log.info(f"[DRY RUN] Already installed: {package}; skipping")
            else:
                search_results = subprocess.run(["cargo", "search", f"{package}"], capture_output=True, text=True)
                search_result_lines = search_results.stdout.splitlines()
                for line in search_result_lines:
                    line = line.split("=")
                    if line[0].startswith(package):
                        log.info(f"Found install candidate for {package}: {line[1]}")
                #log.info(f"[DRY RUN] Found crate to install {package}:\n{match}")

    def install(self):
        pass

class ScriptInstaller:

    def __init__(self, packages:list, flags:list):
        self.packages = packages
        self.flags = flags

    def simulate_install(self):
        pass

    def install(self):
        pass

class InstallManager:

    def __init__(self, config):
        self.config = config or load_config()
        self.flags = self.config.get("system_settings", {}).get("flags")
        self.apt_installs = self.config.get('install_settings', {}).get('installed_by', {}).get('apt', [])
        self.cargo_installs = self.config.get('install_settings', {}).get('installed_by', {}).get('cargo', [])
        self.script_installs = self.config.get('install_settings', {}).get('installed_by', {}).get('script', [])

def test_main():
    install_manager = InstallManager(load_config())
    apt_installer = AptInstaller(install_manager.apt_installs, install_manager.flags)

#install_manager = InstallManager(load_config())
#apt_installer = AptInstaller(install_manager.##apt_installs, install_manager.flags)
#dry_run = install_manager.flags.get('dry_run')
#installed, failed = apt_installer.dry_run()
#print(installed, failed)