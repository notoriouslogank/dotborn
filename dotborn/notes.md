# Dotborn Workflows

This document outlines the core workflows available in Dotborn. Each workflow is a distinct use-case with its own purpose, required configuration, and expected output. Use these workflows as building blocks for system setup, migration, backup, and customization.

---

## 🧪 1. Dry Run Config Audit

**Purpose:**
Preview what actions Dotborn would take without making changes.

**Command:**

```bash
python3 main.py --dry-run
```

**Requires:**

* Any config files referenced (user.yaml, backup.yaml, etc.)

**Does:**

* Parses all config
* Logs warnings for:

  * Missing or invalid paths
  * Misconfigured YAML types
* Prints intended actions for each enabled module

**Flags:**

* `--platform linux|windows`

---

## 🛠️ 2. Dotfile Installation

**Purpose:**
Install dotfiles from templates or source repo into the user environment.

**Command:**

```bash
python3 main.py --run install
```

**Requires:**

* `install.yaml`
* Template or repo dotfiles present in `templates/` or defined in config

**Does:**

* Copies selected dotfiles to user’s home
* Honors overwrite rules
* May trigger shell reload or additional post-install steps

**Flags:**

* `--dry-run`

---

## 💾 3. System Backup

**Purpose:**
Back up system files, dotfiles, credentials, and user-defined directories.

**Command:**

```bash
python3 main.py --run backup --platform linux
```

**Requires:**

* `backup.yaml`

**Does:**

* Resolves and copies configured file targets
* Organizes them into structured temp tree
* Generates `backup_manifest.json`
* Optionally compresses or encrypts the result

**Flags:**

* `--dry-run`
* `--encrypt`

---

## ♻️ 4. Migration Preparation

**Purpose:**
Bundle a set of user configuration files and environment info for transport to another machine.

**Command:**

```bash
python3 main.py --run migrate --platform windows
```

**Requires:**

* All config files
* Backup + install modules working

**Does:**

* Runs both `backup` and `install` logic
* Creates a portable directory or archive containing:

  * Dotfiles
  * System preferences
  * Manifest/logs

**Flags:**

* `--dry-run`
* `--output [custom dir]`

---

## ✨ 5. First-Time Setup

**Purpose:**
Bootstrap a user’s Dotborn setup from scratch.

**Command:**

```bash
python3 main.py --init
```

**Does:**

* Creates `config/` directory (if missing)
* Copies example config files from `config/examples/`
* Prompts user to review them before proceeding
* Optionally runs a dry run or walks through config interactively

**Flags:**

* `--platform linux|windows`
* `--default` to skip prompts and use sane defaults

---

Each of these workflows should be treated as atomic and scriptable. They can be combined in shell scripts or DevOps pipelines depending on user goals.

Future plans include an interactive CLI menu system to select and chain workflows dynamically.
