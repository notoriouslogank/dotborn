import sys
from pathlib import Path

from dotborn import logger, platform_check
from dotborn.backupper import BackupManager, WinBack, LinBack
from dotborn.installer import (
    AptInstaller,
    CargoInstaller,
    InstallManager,
    ScriptInstaller,
)
from dotborn.version import get_version
from dotborn.config import Configure

configs = Configure()

sys.path.append(str(Path(__file__).parent.resolve()))  # fixed later per ChatGPT

log = logger.setup_logger(log_file=Path(configs.LOG_PATH))


def main():
    log.debug(f"dotborn {get_version()}")

    platform = platform_check.check_platform()

    log.debug(f"User platform: {platform}")
    backup_manager = BackupManager(configs.user_config, configs.backup_config)

    if platform == "Windows":
        winconfigs = backup_manager.prepare_windows()
        winback = WinBack(winconfigs)
        winback.backup()
    if platform == "Linux":
        linconfigs = backup_manager.prepare_linux()
        # print(linconfigs)
        linback = LinBack(linconfigs)
        linback.backup()

        install_manager = InstallManager(configs.user_config, configs.install_config)
        apt_installer = AptInstaller(
            install_manager.apt_list,
            install_manager.flags)
        cargo_installer = CargoInstaller(
                install_manager.cargo_list,
                install_manager.flags)
        script_installer = ScriptInstaller(
                install_manager.script_list,
                install_manager.flags)
        apt_installer.dry_run()
        cargo_installer.dry_run()
        script_installer.dry_run()
    else:
        log.debug(f"Unsupported platform: {platform}")


main()
