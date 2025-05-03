import subprocess
from dotborn.logger import setup_logger
from dotborn.config import load_config
from rich.console import Console
from rich.text import Text
from rich.panel import Panel

class Installer:
    def __init__(self, config=None):
        self.log = setup_logger()
        self.config = config or load_config()
        self.flags = self.config.get('system_settings', {}).get("flags", {})
        self.console = Console()

    def _should_prompt(self, prompt_msg:str) -> str:
        if not self.flags.get("interactive", True):
            return True
        response = input(f"{prompt_msg} [Y/n] ").strip().lower()
        return response in ('y', 'yes', '')

    def _run(self, cmd, allow_sudo=True) -> subprocess.CompletedProcess[bytes]:
        if allow_sudo:
            cmd.insert(0, "sudo")
        return subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def _simulate_apt(self, pkg, allow_sudo=True) -> bool:
        cmd = ["apt", "install", "--simulate", "-y", pkg]
        try:
            self._run(cmd, allow_sudo=allow_sudo)
            return True
        except subprocess.CalledProcessError:
            return False

    def _rich_status(self, prefix, message, status="info"):
        colors = {
            "info":"cyan",
            "success":"green",
            "warn":"yellow",
            "error":"bold red",
            "dry":"magenta"
        }
        tag = Text(f"[{prefix}] {message}", style=colors.get(status, "white"))
        self.console.print(tag)
        log_method = getattr(self.log, status if status in ("info", "warning", "error") else "info")
        log_method(f"[{prefix}] {message}")

    def _rich_script_dry_run(self, name, desc, cmd):
        self.console.print(Panel.fit(
            f"[bold magenta]{name}[/bold magenta]\n",
            f"[cyan]Description:[/cyan] {desc}\n",
            f"[yellow]Command:[/yellow] {cmd}",
            title="DRY RUN: Script Install", border_style='magenta'
        ))

    def install_apt_packages(self):
        packages = self.config.get("install_settings", {}).get("installed_by", {}).get("apt", [])
        if not packages:
            self._rich_status("apt", "No apt packages to install.", status="info")
            return

        self._rich_status("apt", f"Found {len(packages)} apt packages to install.", status="info")
        if self.flags.get("dry_run", False):
            for pkg in packages:
                self._rich_status("apt", f"Would install: {pkg}", status="dry")
                self._simulate_apt(pkg, allow_sudo=self.flags.get("allow_sudo", True))
            return

        subprocess.run(["sudo", "apt", "update"], check=True)
        for pkg in packages:
            if self._should_prompt(f"Install {pkg}?"):
                cmd = ["apt", "install", "-y", pkg]
                if self.flags.get("quiet", False):
                    cmd.append("-qq")
                self._rich_status("apt", f"Installing {pkg}...", status="info")
                try:
                    subprocess.run(["sudo"] + cmd if self.flags.get("allow_sudo", True) else cmd, check=True)
                    self._rich_status("apt", f"Successfully installed {pkg}", status="success")
                except subprocess.CalledProcessError as e:
                    self._rich_status("apt", f"Failed to install {pkg}: {e}", status="error")


    def _cargo_installed(self, pkg):
        try:
            output = subprocess.check_output(["cargo", "install", "--list"], text=True)
            return pkg in output
        except Exception:
            return False

    def install_cargo_packages(self):
        packages = self.config.get("install_settings", {}).get("installed_by", {}).get("cargo", [])
        if not packages:
            self._rich_status("Cargo", "No Cargo packages to install.", status="info")
            return

        self._rich_status("Cargo", f"Found {len(packages)} cargo packages to install.", status="info")
        for pkg in packages:
            if self._cargo_installed(pkg):
                self._rich_status("Cargo", f"{pkg} is already installed; skipping.", status="info")

            if self.flags.get("dry_run", False):
                self._rich_status("Cargo", f"Would install: {pkg}", status="dry")
                continue

            if self._should_prompt(f"Install cargo package {pkg}?"):
                cmd = ["cargo", "install", pkg]
                self._rich_status("Cargo", f"Installing {pkg} via cargo...", status='info')
                try:

                    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL if self.flags.get("quiet", False) else None)
                    self._rich_status("Cargo", f"Successfully installed {pkg}", status="success")
                except subprocess.CalledProcessError as e:
                    self._rich_status("Cargo", f"Failed to install {pkg}: {e}", status="error")

    def install_script_packages(self):
        scripts = self.config.get("install_settings", {}).get("installed_by", {}).get("script", {})
        if not scripts:
            self._rich_status("script", "No scripts found.", status="info")
            return

        for name, entry in scripts.items():
            cmd = entry.get("install")
            desc = entry.get("description", "")
            if not cmd or "# TODO" in str(cmd).lower():
                self._rich_status("script", f"Skipping '{name}' - no valid install script.", status="info")
                continue

            if self.flags.get(f"dry_run", False):
                self._rich_status(name, desc, cmd)
                continue

            if self._should_prompt(f"Run install script for {name} ({desc})?"):
                self._rich_status(f"Run install for {name} ({desc})?")
                try:
                    subprocess.run(cmd, shell=True, check=True, stdout=subprocess.DEVNULL if self.flags.get("quiet", False) else None, stderr=subprocess.STDOUT if self.flags.get("quiet", False) else None)
                    self._rich_status("script", f"Successfully ran install script for {name}", status="success")
                except subprocess.CalledProcessError as e:
                    self._rich_status("script", f"Script install for {name} failed: {e}", status="error")






"""

log = setup_logger()
conf = load_config()

class Installer:

    def __init__(self, config):
        self.config = config
        self.flags = self.config.get("system_settings", {}).get("flags", {})
        self.quiet = self.flags.get('interactive', True)
        self.allow_sudo = self.flags.get('allow_sudo', True)
        self.simulate = self.flags.get('simulate_before_apt', True)
        self.dry_run = self.flags.get('dry_run', False)
        self.apt_config = config.get('install_settings', {}).get('installed_by', {}).get('apt', [])


    def install_apt_packages(self):
        if not self.apt_config:
            log.info(f'No APT packages to install.')
            return

        log.info(f'Found {len(self.apt_config)} apt packages to install.')

        if not self.apt_config: # No apt packages in list
            log.info(f"No APT packages to install.")
            return

        if self.dry_run or self.simulate: # TODO: Merge this functionality with `--simulate`
            print(f'[DRY RUN] Would run: `apt update && apt install ...` ')
            for pkg in self.apt_config:
                subprocess.run(['sudo', 'apt', 'install', '--simulate', pkg], check=True)
"""