import sys  # these lines are for DEV ONLY and should be
from pathlib import Path

from dotborn import config, linback, logger, paths, platform_check
from dotborn.installer import AptInstaller, CargoInstaller, InstallManager
from dotborn.version import get_version

sys.path.append(
        str(Path(
            __file__
            ).parent.resolve()))  # fixed later per ChatGPT

log = logger.setup_logger(log_file=Path(paths.LOG_PATH))

conf = config.load_config()


def main():
    log.debug(f"dotborn {get_version()}")

    platform = platform_check.check_platform()

    log.debug(f"User platform: {platform}")

    if platform == "Windows":
        raise NotImplementedError
    if platform == "Linux":
        install_manager = InstallManager(conf)
        # apt_installer = AptInstaller(
        #    install_manager.apt_installs,
        #    install_manager.flags)
        cargo_installer = CargoInstaller(
            install_manager.cargo_installs,
            install_manager.flags)

        # apt_installer.dry_run()
        cargo_installer.dry_run()
    else:
        print("Some sort of Godless heathen")


main()
