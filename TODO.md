# TODO

- [] Write install script for copying templates
- [] Template engine support for config files
- [] Write scripts for copying/migrating Windows data
- [] Confirm file location(s)
- [] Breakup linback.py into a Backupper and platform-dependant backuppers (a la installer.py)
- [] Create different workflows: backup-only, system migration, etc.

## Main Menu Options(?)

1. Migrate from Windows
2. Install fresh dotfiles
3. Backup current system
4. Manually explore options

## Windows Migration Flow

1. Locate Windows partition(s)
    a) auto-detect NTFS partition(s)
    b) offer to mount them
    c) confirm path to `Users/USERNAME`
2. Extract relevant data
    a) browser bookmarks (Chrome/Edge/Firefox)
    b) Documents, Downloads, Music, Pictures
    c) saved games (Steam, etc.)
    d) WSL configs?
    e) Git credentials, SSH keys
3. Backup and Copy Files
    a) create local backup folder
    b) copy selected files to standard Linux equivatlents (Documents -> ~/Documents, etc.)
4. Setup Linux
    a) prompt for User Profile
        - select dotfiles
        - select packages
        - apply shell environment
    b) install dotfiles
        - prompt: default or custom?
        - optionally backup current dotfiles
        - apply templates to:
            - shell
            - git
            - editor(?)
    c) System Tweaks
        - set default shell
        - configure hostname
        - add aliases, functions, tools
5. Dry Run
    a) Show:
        - files to be copied
        - files to be overwritten
        - packages to be installed
        - configs to be generated
    b) "Continue [y/N]?"
6. Execute and Finalize
    a) reboot or logout/login
    b) show success (or failure) summary
    c) offers tips:
        - try 'dotborn status' or 'dotborn backup' next time

## Windows vs Linux File System Copying Info

- Set default permissions after copy (files: 644 directories: 755)
- filter for Windows 'hidden' files via blacklist:
  - Thumbs.db
  - desktop.ini
  - *.lnk
  - $Recycle.Bin/
  - System Volume Information/
- Line endings vary:
  - Windows: CRLF (\r\n)
  - Linux: LF (\n)
  - auto-convert text files (.txt, .md, .conf, .sh) using `dos2unix` or manually
  - `--normalize-line-endings` flag option?
- Escape or rename filenames if going back to Windows (`--windows-compatible`)
- Log files that may fail to copy due to encoding errors

**Use `shutil.copy2()`**
`robocopy` if Windows FS is prepped
