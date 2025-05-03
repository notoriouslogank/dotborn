from dotborn.config import load_config
from dotborn.logger import setup_logger
import subprocess

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

    def simulate_install(self):

        pass

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

install_manager = InstallManager(load_config())

apt_installer = AptInstaller(install_manager.apt_installs, install_manager.flags)

dry_run = install_manager.flags.get('dry_run')

installed, failed = apt_installer.dry_run()
print(installed, failed)