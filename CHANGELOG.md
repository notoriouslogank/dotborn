# Changelog

All notable changes to **Dotborn** will be documented here.

---

## [0.2.0] - 2025-05-02

### Added

- `template.py`: add module and function docstrings for clarity and readability
- `linback.py`: add module and function docstrings for clarity and readability
- `TODO.md`: add TODO.md with list of planned features and milestones

## [0.1.0] - 2025-05-02

### Initial Structured Release ("The Ritual Begins")

#### Core Features

Added YAML-driven configuration system with full logical hierarchy:

- `system_settings`: environment, logging, flags
- `backup_settings`: per-platform dotfile and config tracking
- `install_settings`: modular support for apt, cargo, and custom scripts

#### Installers

- Implemented apt installer with:
  - `--simulate` pre-check for dependency sanity
  - `dry_run`, `interactive`, `quiet`, and `allow_sudo` support
- Added Cargo installer
  - Skips already-installed packages
  - Respects flags and logs all attempts
- Custom script installer:
  - Supports shell commands or external script paths
  - Respects metadata (name, description)
  - Designed for one-off installs like `oh-my-zsh`, `gh`, or font setup

#### Config Highlights

- Unified install sections by method (`apt`, `cargo`, `script`)
- Allowed per-script metadata and optional hooks for NerdFonts, fzf, etc
- Placeholder for user-defined scripts (`usr_scripts`)
- Integrated CLI behavior toggles (`dry_run`, `interactive`, `quiet`, `simulate_before_apt`, etc)

#### Aesthetic Alignment

- Configuration and tooling color schemes tuned to match a mystic, glyph-aware terminal aesthetic (Starship, eza, Neofetch, etc)

---

## Notes

- Dotfile sync + manifest generation in progress
- Future additions may include pip3, flatpak, AppImage, and remote dotfile sources
