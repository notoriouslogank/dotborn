# Dotborn

**Dotborn** is a declarative, YAML-driven system setup and dotfile management tool designed for Linux environments. It streamlines the installation of packages, configuration of dotfiles, and execution of custom scripts, providing a cohesive and automated setup experience.

---

## Features

- **YAML Configuration**: Define system settings, backup preferences, and installation methods in a single `config.yaml` file.
- **Package Management**:
  - **APT**: Install system packages with optional simulation to check dependencies.
  - **Cargo**: Manage Rust-based tools, skipping already-installed packages.
  - **Custom Scripts**: Execute user-defined installation scripts with metadata support.
- **Dotfile Management**: Backup and restore dotfiles and configuration directories with options for compression and encryption.
- **Logging & FLags**: Control verbosity, interactivity, and execution modes (`dry_run`, `quiet`, `interactive`, `allow_sudo`)

---

## Installation

1. ### Clone the repository

    ```bash
    git clone https://github.com/notoriouslogank/dotborn.git
    cd dotborn
    ```

2. ### Install dependencies

    Ensure Python 3.6+ is installed. Then, install required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

3. ### Configure

    Edit the `config.yaml` file to suit your system setup and preferences.

4. ### Run Dotborn

    ```bash
    python dotborn.py
    ```

---

## Configuration

The `config.yaml` file is structured into three main sections:

- `system_settings`: Define user-specific settings, logging preferences, and execution flags
- `backup_settings`: Specify backup options, including compression, encryption, and target directories
- `install_settings`: List packages and scripts to be installed via APT, Cargo, or custom methods

Example snippet:

```yaml
system_settings:
  username: logank
  home_dir: /home/logank
  flags:
    dry_ryn: false
    interactive: false
    quiet: false
    allow_sudo: true
```

---

## Supported Installers

- APT: Installs packages listed under `install_settings.installed_by.apt`. Supports simulation mode to check for dependencies.
- Cargo: Installs Rust-based tools specified in `install_settings.installed_by.cargo`. Skips installation if the package is already present.
- Custom Scripts: Executes scripts defined in `install_settings.installed_by.script`, allowing for complex or third-party installations.

---

## Flags & Options

Control Dotborn's behavior using the following flags in `config.yaml`:

- `dry_run`: If `true`, commands are printed but not executed.
- `interactive`: If `true`, prompts before executing each installation.
- `quiet`: If `true`, allows the use of `sudo` in installation commands.
- `simulate_before_apt`: If `true`, runs `apt install --simulate` before actual installation to check for dependency issues.

---

## Manifest Generation

Dotborn writes a manifest file (`dotborn_manifest.yaml`) at the end of each run, detailing:

- What was installed
- What was skipped or errored
- What you told it to do -- and what it actually did

Perfect for postmortems or sharing loadouts with fellow terminal occultists.

---

## Contributing

Pull requests and patch sigils welcome.  Open an issue to report bugs, request features, submit PRs -- especially if you're adding new install sources, backup options, or cool hidden features.

---

## License

This project is licensed under the MIT License.  See the `LICENSE` file for the boring parts.

---

## Contact

Raise an issue on [GitHub](https://github.com/notoriouslogank/dotborn) or whisper into `/dev/null` and hope the daemon is listening.
