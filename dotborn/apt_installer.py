import subprocess
from dotborn.logger import setup_logger
from dotborn.config import load_config

log = setup_logger()
conf = load_config()

def simulate_apt_install(pkg, allow_sudo=True):
    cmd = ["apt", "install", "--simulate", '-y', pkg]
    if allow_sudo:
        cmd.insert(0, "sudo")
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError:
        return False

def install_apt_packages(config):
    apt_config = config.get('install_settings', {}).get('installed_by', {}).get('apt', [])
    flags = config.get("system_settings", {}).get("flags", {})
    quiet = flags.get('quiet', False)
    interactive = flags.get('interactive', True)
    dry_run = flags.get('dry_run', False)
    allow_sudo = flags.get('allow_sudo', True)
    simulate = flags.get('simulate_before_apt', True)
    if not apt_config:
        log.info(f"No APT packages to install.")
        return

    log.info(f"Found {len(apt_config)} apt packages to install.")

    if dry_run:
        print(f"[DRY RUN] Would run: apt update && apt install ...")
        for pkg in apt_config:
            print(f"  - {pkg}")
        return

    try:
        if allow_sudo:
            subprocess.run(["sudo", "apt", "update"], check=True)
        else:
            subprocess.run(["apt", "update"], check=True)

        for pkg in apt_config:
            if simulate:
                log.debug(f"Simulating install for {pkg}...")
                if not simulate_apt_install(pkg, allow_sudo=allow_sudo):
                    log.warning(f"Simulation failed for {pkg}; skipping install.")
                    continue

            if interactive:
                prompt = input(f"Install {pkg}? [Y/n] ").strip().lower()
                if prompt not in ('y', 'yes', ''):
                    continue
            cmd = ["sudo", "apt", "install", "-y", pkg] if allow_sudo else ["apt", "install", "-y", pkg]
            if quiet:
                cmd.append("-qq")
            log.info(f"Installing {pkg}...")
            subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        log.error(f"Failed to install {pkg}: {e}")

def ensure_cargo(pkg):
    try:
        output = subprocess.check_output(["cargo", "install", "--list"], text=True)
        return pkg in output
    except Exception:
        return False

def install_cargo_packages(config):
    cargo_packages = config.get('install_settings', {}).get('installed_by', {}).get('cargo', [])
    flags = config.get('system_settings', {}).get("flags", {})
    quiet = flags.get('quiet', False)
    interactive = flags.get('interactive', True)
    dry_run = flags.get('dry_run', False)

    if not cargo_packages:
        log.info(f"No Cargo packages to install.")
        return

    log.info(f"Found {len(cargo_packages)} cargo packages to install.")

    for pkg in cargo_packages:
        if ensure_cargo(pkg):
            log.info(f"{pkg} is already installed; skipping.")
            continue

        if dry_run:
            print(f"[DRY RUN] Would install cargo package: {pkg}")
            continue

        if interactive:
            prompt=input(f"Install cargo package {pkg}? [Y/n] ").strip().lower()
            if prompt not in ('y', 'yes', ''):
                continue

        cmd = ['cargo', 'install', pkg]
        log.info(f"Installing {pkg} via cargo...")
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL if quiet else None)
        except subprocess.CalledProcessError as e:
            log.error(f"Failed to install cargo package {pkg}: {e}")

def install_script_packages(config):
    script_blocks = config.get('install_settings', {}).get('installed_by', {}).get('script', {})
    flags = config.get('system_settings', {}).get('flags')
    dry_run = flags.get('dry_run', False)
    interactive = flags.get('interactive', True)
    quiet = flags.get('quiet', False)

    if not script_blocks:
        log.info(f"No scripts found.")
        return

    for name, entry in script_blocks.items():
        command = entry.get('install')
        desc = entry.get('description', '')

        if not command or "# TODO" in str(command).lower():
            log.info(f"Skipping '{name}' - no valid install command.")
            continue

        if dry_run:
            print(f"[DRY RUN] Would run install script for {name}: {command}")
            continue

        if interactive:
            prompt=input(f"Run install for {name} ({desc})? [Y/n] ").strip().lower()
            if prompt not in ('y', 'yes', ''):
                continue

        log.info(f"Installing {name}: {desc}")
        try:
            subprocess.run(command, shell=True, check=True, stdout=subprocess.DEVNULL if quiet else None, stderr=subprocess.STDOUT if quiet else None)
        except subprocess.CalledProcessError as e:
            log.error(f"Script install for {name} failed: {e}")