<!--
-*- coding: utf-8 -*-
vim: ts=4 sw=4 tw=100 et ai si

# Copyright (C) 2026 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause

Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
-->

# Installation Guide

- Author: Artem Bityutskiy <dedekind1@gmail.com>

## Table of Contents

- [Wult Packages](#wult-packages)
- [Running From Source](#running-from-source)
- [Installation Script](#installation-script)
- [Manual Installation](#manual-installation)
  - [Wult Package Dependencies](#wult-package-dependencies)
  - [Installation Using pip](#installation-using-pip)
  - [Using uv](#using-uv)
  - [Sudo Configuration](#sudo-configuration)
  - [Tab completions](#tab-completions)
  - [Man pages](#man-pages)
  - [Example of .bashrc](#example-of-bashrc)

## Wult Packages

Some Linux distributions provide `wult` as an installable package. However, these packages are out
of date, do not use them.

## Running From Source

The wult project provides four tools: `wult`, `ndl`, `pbe`, and `exercise-sut`. You can run them
directly from the source code without installation. Clone all three repositories (`pepc` and
`stats-collect` are required as dependencies), and run the tools from the cloned directory.

```bash
git clone https://github.com/intel/pepc.git
git clone https://github.com/intel/stats-collect.git
git clone https://github.com/intel/wult.git
cd wult
./wult --help
```

This method is not recommended for regular use. For regular use, a proper installation is
recommended: it configures shell tab completions and man pages, so commands like `man wult-start`
work out of the box.

## Installation Script

The `tools/install-wult` script is the simplest way to install `wult`. It takes care of
everything: installing `pepc` and `stats-collect` (required dependencies), installing OS
dependencies, creating the Python virtual environment, configuring shell tab completions, man
pages, and adding `sudo` aliases if needed.

Clone all three repositories. The installation script spans all of them:

```bash
git clone https://github.com/intel/pepc.git
git clone https://github.com/intel/stats-collect.git
git clone https://github.com/intel/wult.git
cd wult
```

**Install the latest release from GitHub**

Run `tools/install-wult` without arguments. It fetches and installs the latest `pepc`,
`stats-collect`, and `wult` releases directly from GitHub.

```bash
sudo -v && ./tools/install-wult
```

**Install from local clones**

Use `--src-path` to install from the local clones instead. The script automatically looks for
`pepc` and `stats-collect` in the sibling directories (`../pepc` and `../stats-collect`).

```bash
sudo -v && ./tools/install-wult --src-path .
```

**Note**: the script runs most steps as the current user, but it requires `sudo` for installing OS
dependencies. The `sudo -v` pre-authorizes `sudo` credentials so the script can install
dependencies without prompting for a password.

**What the script does**

The script performs the steps described below in the [Manual Installation](#manual-installation)
section. Here is a high-level overview:

- Install OS dependencies using the system package manager (`dnf` or `apt`).
- Create a Python virtual environment in `~/.pmtools` and install `pepc`, `stats-collect`, `wult`,
  and their Python dependencies there.
- Create `~/.pmtools/.pepc-rc.sh`, `~/.pmtools/.stats-collect-rc.sh`, and
  `~/.pmtools/.wult-rc.sh` with all the necessary configuration and add lines to `~/.bashrc` to
  source them. The configuration includes the following:
  - Add `~/.pmtools/bin` to `PATH`.
  - Configure tab completions.
  - Configure manual pages.
  - Create `sudo` aliases for all the tools (`wult`, `pepc`, etc.).

`tools/install-wult` has additional options to tune the installation (e.g., the installation path),
install `wult` on a remote host over SSH, and control `sudo` alias creation and style. Run
`./tools/install-wult --help` to see all available options.

## Manual Installation

The following sections describe how to install `wult` manually, without using the
`tools/install-wult` script. This is useful if you want full control over the installation, use a
custom environment, or prefer a different package manager.

`wult` depends on `pepc` and `stats-collect`. Install both first. Refer to the
[pepc installation guide](https://github.com/intel/pepc/blob/main/docs/guide-install.md) and the
[stats-collect installation guide](https://github.com/intel/stats-collect/blob/main/docs/guide-install.md)
for instructions.

### Wult Package Dependencies

`wult` requires a few OS packages. Most are typically pre-installed, but verify they are present on
your system.

**Tools used by `wult` at runtime:**

- `cat`, `id`, `uname` from the `coreutils` package.
- `pgrep`, `ps` from the `procps` package.
- `taskset` from the `util-linux` package.

**Tools needed for installation:**

- `pip3` and `virtualenv`: required for `pip`-based installation
   (see [Installation Using pip](#installation-using-pip)).
- `uv`: an alternative to `pip3` + `virtualenv` (see [Using uv](#using-uv)). Install one or the
  other.
- `rsync`: used to copy sources to a temporary directory during installation from a local path.

The commands below install the `pip3`-based tools. If you prefer `uv`, install it instead and skip
`python3-pip` and `python3-virtualenv`.

**Fedora / CentOS**

```bash
sudo dnf install -y procps-ng util-linux python3-pip python3-virtualenv rsync
```

**Ubuntu**

```bash
sudo apt install -y procps util-linux python3-pip python3-venv rsync
```

### Installation Using pip

This method installs `pepc`, `stats-collect`, and `wult` into the same Python virtual environment.
The installation does not require superuser privileges.

The example below uses `~/.pmtools` as the installation directory, consistent with the `pepc`
installation guide. If you installed `pepc` into a different location, adjust the path accordingly.

Install `pepc` and `stats-collect` first, then install `wult` into the same virtual environment:

```bash
python3 -m venv ~/.pmtools
~/.pmtools/bin/pip3 install git+https://github.com/intel/pepc.git@release
~/.pmtools/bin/pip3 install git+https://github.com/intel/stats-collect.git@release
~/.pmtools/bin/pip3 install git+https://github.com/intel/wult.git@release
```

Ensure that `~/.pmtools/bin` is in your `PATH`. Add the following line to your `~/.bashrc` to make
it persistent.

```bash
export PATH="$PATH:$HOME/.pmtools/bin"
```

### Using uv

`uv` is a modern Python project and package manager. Install it using your distribution's package
manager. For example, on Fedora:

```bash
sudo dnf install uv
```

Install `pepc` and `stats-collect` first, then `wult`:

```bash
uv tool install git+https://github.com/intel/pepc.git@release
uv tool install git+https://github.com/intel/stats-collect.git@release
uv tool install git+https://github.com/intel/wult.git@release
```

`uv` installs tools to `$HOME/.local/bin`. Add the following line to your `~/.bashrc` to ensure
the tools are found.

```bash
export PATH="$PATH:$HOME/.local/bin"
```

### Sudo Configuration

Many wult operations require superuser privileges to access hardware. When the tools are installed
in a Python virtual environment, running them with `sudo` requires extra configuration: `sudo`
resets `PATH` and environment variables, which breaks virtual environment activation.

The same applies to `pepc`, which `wult` depends on. The `pepc` installation guide covers this in
detail, but the snippets below include a `wult` alias for quick reference.

Two `~/.bashrc` snippets are provided below for quick reference.

**Option 1: refresh**

The alias pre-authorizes `sudo` credentials before invoking the tool. Requires passwordless `sudo`
or prompts once per session. Supported by `pepc` (and is its default), but not yet supported by
the wult tools. Refresh support for the wult tools is planned for a future release.

```bash
alias pepc='sudo -v && pepc'
```

**Option 2: wrap**

The alias passes the virtual environment variables to `sudo` explicitly. This is the only supported
option for the wult tools. It also works for `pepc`.

```bash
VENV="$HOME/.pmtools"
VENV_BIN="$VENV/bin"
alias pepc="sudo PATH=$PATH VIRTUAL_ENV=$VENV $VENV_BIN/pepc"
alias wult="sudo PATH=$PATH VIRTUAL_ENV=$VENV $VENV_BIN/wult"
alias ndl="sudo PATH=$PATH VIRTUAL_ENV=$VENV $VENV_BIN/ndl"
alias pbe="sudo PATH=$PATH VIRTUAL_ENV=$VENV $VENV_BIN/pbe"
alias exercise-sut="sudo PATH=$PATH VIRTUAL_ENV=$VENV $VENV_BIN/exercise-sut"
```

### Tab completions

All wult tools support tab completions. Add the relevant line to `~/.bashrc` for each tool,
depending on how they were installed.

```bash
# For pip installation (adjust path if you used a different location):
eval "$($HOME/.pmtools/bin/register-python-argcomplete wult)"
eval "$($HOME/.pmtools/bin/register-python-argcomplete ndl)"
eval "$($HOME/.pmtools/bin/register-python-argcomplete pbe)"
eval "$($HOME/.pmtools/bin/register-python-argcomplete exercise-sut)"

# For uv installation:
eval "$($HOME/.local/bin/register-python-argcomplete wult)"
eval "$($HOME/.local/bin/register-python-argcomplete ndl)"
eval "$($HOME/.local/bin/register-python-argcomplete pbe)"
eval "$($HOME/.local/bin/register-python-argcomplete exercise-sut)"
```

### Man pages

All wult tools provide man pages (e.g., `man wult-start`). When installed via `pip` or `uv`, the
man pages land in Python's `site-packages` directory, which `man` does not search by default. Add
the following line to `~/.bashrc` to make them available.

```bash
export MANPATH="$MANPATH:$(wult --print-man-path)"
```

Verify with:

```bash
man wult-start
```

### Example of .bashrc

The example below is for a `pip`-based installation into `~/.pmtools`. `pepc` uses the `refresh`
sudo style (its default). The wult tools use the `wrap` style (the only style currently
supported). Adjust paths and the sudo aliases as needed for your setup.

```bash
# === pepc, stats-collect, and wult settings ===
VENV="$HOME/.pmtools"
VENV_BIN="$VENV/bin"

# Ensure the virtual environment's bin directory is in the PATH.
export PATH="$PATH:$VENV_BIN"

# Sudo alias for pepc: pre-authorize sudo credentials (refresh style).
alias pepc='sudo -v && pepc'
# Sudo aliases for wult tools: pass virtual environment to sudo (wrap style).
alias wult="sudo PATH=$PATH VIRTUAL_ENV=$VENV $VENV_BIN/wult"
alias ndl="sudo PATH=$PATH VIRTUAL_ENV=$VENV $VENV_BIN/ndl"
alias pbe="sudo PATH=$PATH VIRTUAL_ENV=$VENV $VENV_BIN/pbe"
alias exercise-sut="sudo PATH=$PATH VIRTUAL_ENV=$VENV $VENV_BIN/exercise-sut"

# Enable tab completion for all wult tools.
eval "$($VENV_BIN/register-python-argcomplete wult)"
eval "$($VENV_BIN/register-python-argcomplete ndl)"
eval "$($VENV_BIN/register-python-argcomplete pbe)"
eval "$($VENV_BIN/register-python-argcomplete exercise-sut)"

# Enable man pages.
export MANPATH="$MANPATH:$($VENV_BIN/wult --print-man-path)"
# === end of pepc, stats-collect, and wult settings ===
```
