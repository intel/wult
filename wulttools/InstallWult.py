# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2026 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
Implement the 'install-wult' tool and provide a public 'install_wult()' API.

The 'install_wult()' function installs 'wult' into a virtual environment. 'pepc' and
'stats-collect' must be installed into the same virtual environment first, since 'wult' depends on
both. Use 'InstallPepc.install_pepc()' and 'InstallStatsCollect.install_stats_collect()' for that.
"""

from __future__ import annotations # Remove when switching to Python 3.10+.

import types
import typing
from pathlib import Path

try:
    argcomplete: types.ModuleType | None
    import argcomplete
except ImportError:
    # We can live without argcomplete, we only lose tab completions.
    argcomplete = None

from pepclibs.helperlibs import ProcessManager, ArgParse, Logging
from pepclibs.helperlibs.Exceptions import Error
from pepctools import PythonPrjInstaller, InstallPepc
from statscollecttools import InstallStatsCollect

if typing.TYPE_CHECKING:
    import argparse
    from typing import Final, Literal
    from pepclibs.helperlibs.ArgParse import SSHArgsTypedDict
    from pepclibs.helperlibs.ProcessManager import ProcessManagerType
    from pepctools.PythonPrjInstaller import SudoAliasStyle

    class _CmdlineArgsTypedDict(SSHArgsTypedDict, total=False):
        """
        A typed dictionary for command-line arguments of this tool. Includes all attributes from
        'SSHArgsTypedDict', plus the following:

        Attributes:
            install_path: The path to install 'wult' to.
            src_path: The path to install 'wult' from (a filesystem path or a Git URL).
            no_pkg_install: Do not install missing OS packages.
            no_rcfile: Do not modify the user's shell RC file (e.g. '.bashrc').
            no_sudo_alias: Prevent adding the 'sudo' aliases to the shell RC file.
            sudo_alias_style: The style of the 'sudo' alias to add. One of 'refresh' or 'wrap'.
                             Empty string means use the per-tool default.
        """

        install_path: Path
        src_path: str
        no_pkg_install: bool
        no_rcfile: bool
        no_sudo_alias: bool
        sudo_alias_style: SudoAliasStyle | Literal[""]

_VERSION: Final[str] = "0.1"
_TOOLNAME: Final[str] = "install-wult"

# Configure the root 'main' logger, not the child 'main.wult', so that debug messages from
# pepclibs ('main.pepc.*') and statscollecttools ('main.stats-collect.*') are also captured.
_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.wult")
Logging.getLogger(Logging.MAIN_LOGGER_NAME).configure(prefix=_TOOLNAME)

# The upstream 'wult' project Git URL and branch.
WULT_GIT_INSTALL_SRC: Final[str] = "git+https://github.com/intel/wult.git@release"

# The tools wult relies on to be installed and to operate.
WULT_DEPENDENCIES: Final[tuple[str, ...]] = (
    "virtualenv",
    "pip3",
    "cat",
    "id",
    "taskset",
    "uname",
    "pgrep",
    "ps")

# Directories and files to exclude when copying wult project sources to a remote host.
WULT_COPY_EXCLUDE: Final[tuple[str, ...]] = ("/tests", "/docs", "**/*.md", ".*")

def _build_arguments_parser() -> ArgParse.ArgsParser:
    """
    Build and return the command-line arguments parser.

    Returns:
        An initialized command-line arguments parser object.
    """

    text = f"""{_TOOLNAME} - install 'wult' on the local or a remote host into a Python virtual
               environment."""
    parser = ArgParse.ArgsParser(description=text, prog=_TOOLNAME, ver=_VERSION)
    ArgParse.add_ssh_options(parser)

    text = f"""Installation directory on the target host
               (default: '{PythonPrjInstaller.DEFAULT_INSTALL_PATH}')."""
    parser.add_argument("-p", "--install-path", type=Path, help=text)

    text = f"""Installation source: a local directory path or a Git URL
               (default: '{WULT_GIT_INSTALL_SRC}')."""
    parser.add_argument("-s", "--src-path", help=text)

    text = """Do not install missing OS packages required for 'wult' to work."""
    parser.add_argument("--no-pkg-install", action="store_true", help=text)

    text = """Do not modify the user's shell RC file (e.g. '.bashrc'). By default, the installer
              adds a line to the shell RC file to set up the 'wult' environment."""
    parser.add_argument("--no-rcfile", action="store_true", help=text)

    text = """By default, the installer adds 'sudo' aliases for 'wult', 'ndl', 'pbe', and
              'exercise-sut' to the shell RC file so that the tools always run with the required
              privileges. Use this option to prevent adding the aliases."""
    parser.add_argument("--no-sudo-alias", action="store_true", help=text)

    text = """The style of the 'sudo' alias to add when one is needed. 'refresh' pre-authorizes
              'sudo' credentials before each invocation. 'wrap' runs the entire process under
              'sudo', preserving the virtual environment configuration. Currently, 'refresh' is
              supported only for 'pepc'. If 'refresh' is selected, it is used for 'pepc' and
              'wrap' is used for the wult tools. Refresh support for the wult tools is planned for
              a future release. Default: 'refresh' for 'pepc', 'wrap' for the wult tools."""
    parser.add_argument("--sudo-alias-style", choices=["refresh", "wrap"], default="",
                        help=text)

    if argcomplete is not None:
        getattr(argcomplete, "autocomplete")(parser)

    return parser

def _parse_arguments() -> argparse.Namespace:
    """
    Parse the command-line arguments.

    Returns:
        argparse.Namespace: The parsed arguments.
    """

    parser = _build_arguments_parser()
    args = parser.parse_args()

    return args

def _get_cmdline_args(args: argparse.Namespace) -> _CmdlineArgsTypedDict:
    """
    Format command-line arguments into a typed dictionary.

    Args:
        args: Command-line arguments namespace.

    Returns:
        A dictionary containing the parsed command-line arguments.
    """

    cmdl: _CmdlineArgsTypedDict = {**ArgParse.format_ssh_args(args)}

    install_path = args.install_path
    cmdl["install_path"] = install_path if install_path else PythonPrjInstaller.DEFAULT_INSTALL_PATH

    src_path = args.src_path
    cmdl["src_path"] = src_path if src_path else WULT_GIT_INSTALL_SRC

    cmdl["no_pkg_install"] = args.no_pkg_install
    cmdl["no_rcfile"] = args.no_rcfile
    cmdl["no_sudo_alias"] = args.no_sudo_alias

    sudo_alias_style = args.sudo_alias_style
    if sudo_alias_style and cmdl["no_sudo_alias"]:
        raise Error("The '--no-sudo-alias' and '--sudo-alias-style' options are mutually "
                    "exclusive")

    if cmdl["no_rcfile"] and cmdl["no_sudo_alias"]:
        raise Error("The '--no-sudo-alias' and '--no-rcfile' options are mutually exclusive")

    cmdl["sudo_alias_style"] = sudo_alias_style

    return cmdl

def install_wult(pman: ProcessManagerType,
                 src: str,
                 install_path: Path = PythonPrjInstaller.DEFAULT_INSTALL_PATH,
                 no_pkg_install: bool = False,
                 no_rcfile: bool = False,
                 no_sudo_alias: bool = False,
                 sudo_alias_style: SudoAliasStyle = "refresh") -> None:
    """
    Install 'wult' on the target host into a Python virtual environment.

    Note: 'pepc' and 'stats-collect' must be installed into the same virtual environment first,
    since 'wult' depends on both. Use 'InstallPepc.install_pepc()' and
    'InstallStatsCollect.install_stats_collect()' for that.

    Args:
        pman: The process manager object that defines the target host.
        src: Installation source for 'wult': a local directory path or a Git URL.
        install_path: Installation directory on the target host.
        no_pkg_install: Do not install missing OS packages.
        no_rcfile: Do not modify the user's shell RC file.
        no_sudo_alias: Prevent adding a 'sudo' alias to the RC file.
        sudo_alias_style: The style of the 'sudo' alias ('refresh' or 'wrap').
    """

    installer = PythonPrjInstaller.PythonPrjInstaller("wult", src, pman=pman,
                                                      install_path=install_path,
                                                      logging=True)
    if not no_pkg_install:
        installer.install_dependencies(WULT_DEPENDENCIES)

    installer.install(exclude=WULT_COPY_EXCLUDE)
    installer.create_rc_file(("wult", "ndl", "pbe", "exercise-sut"))

    if not no_rcfile and not no_sudo_alias:
        # 'refresh' is not yet supported for the wult tools. Use 'wrap' and notify the user.
        if sudo_alias_style == "refresh":
            _LOG.notice("Refresh sudo alias style is not yet supported for the wult tools. "
                        "Using 'wrap' for the wult tools.")
        installer.add_sudo_aliases(("wult", "ndl", "pbe", "exercise-sut"), style="wrap")

    if not no_rcfile:
        installer.hookup_rc_file()
    else:
        _LOG.info("Skipping shell RC file hookup%s, run '. %s' to configure "
                  "the 'wult' environment manually.", pman.hostmsg, installer.rcfile_path)

def _main(pman: ProcessManagerType, cmdl: _CmdlineArgsTypedDict):
    """
    The main body of the tool.

    Args:
        pman: The process manager object that defines the target host.
        cmdl: The command-line arguments description dictionary.
    """

    src_path = cmdl["src_path"]
    if src_path.startswith(("git+", "http://", "https://")):
        pepc_src = InstallPepc.PEPC_GIT_INSTALL_SRC
        stc_src = InstallStatsCollect.STC_GIT_INSTALL_SRC
    else:
        parent = Path(src_path).resolve().parent
        pepc_src = str(parent / "pepc")
        stc_src = str(parent / "stats-collect")

    _LOG.info("Installing 'pepc' (required dependency of 'wult')%s", pman.hostmsg)

    InstallPepc.install_pepc(pman, pepc_src, install_path=cmdl["install_path"],
                             no_pkg_install=cmdl["no_pkg_install"],
                             no_rcfile=cmdl["no_rcfile"],
                             no_sudo_alias=cmdl["no_sudo_alias"],
                             sudo_alias_style=cmdl["sudo_alias_style"] or "refresh")

    _LOG.info("Installing 'stats-collect' (required dependency of 'wult')%s", pman.hostmsg)

    InstallStatsCollect.install_stats_collect(pman, stc_src,
                                              install_path=cmdl["install_path"],
                                              no_pkg_install=cmdl["no_pkg_install"],
                                              no_rcfile=cmdl["no_rcfile"],
                                              no_sudo_alias=cmdl["no_sudo_alias"],
                                              sudo_alias_style=cmdl["sudo_alias_style"] or "wrap")

    _LOG.info("Installing 'wult'%s", pman.hostmsg)

    install_wult(pman, src_path,
                 install_path=cmdl["install_path"],
                 no_pkg_install=cmdl["no_pkg_install"],
                 no_rcfile=cmdl["no_rcfile"],
                 no_sudo_alias=cmdl["no_sudo_alias"],
                 sudo_alias_style=cmdl["sudo_alias_style"] or "wrap")

def main():
    """
    The 'install-wult' tool entry point. Parse command-line arguments, install 'pepc', then
    'stats-collect', then 'wult'.

    Returns:
        The program exit code.
    """

    try:
        args = _parse_arguments()
        cmdl = _get_cmdline_args(args)

        with ProcessManager.get_pman(cmdl["hostname"], username=cmdl["username"],
                                     privkeypath=cmdl["privkey"]) as pman:
            _main(pman, cmdl)
    except KeyboardInterrupt:
        _LOG.info("\nInterrupted, exiting")
    except Error as err:
        _LOG.error_out(str(err))
