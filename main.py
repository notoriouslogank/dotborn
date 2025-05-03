from dotborn.version import get_version
import sys # these lines are for DEV ONLY and should be
from pathlib import Path
sys.path.append(str(Path(__file__).parent.resolve()))           # fixed later per ChatGPT
from dotborn import logger, paths, config, platform_check, linback
from dotborn.installer import Installer

log = logger.setup_logger(log_file=Path(paths.LOG_PATH))

conf = config.load_config()

def main():
    log.debug(f"MAIN LOOP START")
    print(f'Dotborn v{get_version()}')
    platform = platform_check.check_platform()

    if platform == "Windows":
        print(f"Windows")
    if platform == "Linux":
        #linback.run_backup()
        install = Installer(conf)
        install.install_apt_packages()
        install.install_script_packages()
        install.install_cargo_packages()
    else:
        print(f"Some sort of Godless heathen")


    # backup
    #print(backup.copy_windows_credentials())
    #print(backup.copy_windows_browser_data())
    #print(backup.copy_windows_ect())
    #make_tempdir()
    # install
    # dotfiles
    # post-install
    #pass

main()