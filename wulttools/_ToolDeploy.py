# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
Implement the 'wult/pbe/ndl deploy' command.
"""

from __future__ import annotations # Remove when switching to Python 3.10+.

import sys
import typing
from pathlib import Path

try:
    import argcomplete
    _ARGCOMPLETE_AVAILABLE = True
except ImportError:
    # We can live without argcomplete, we only lose tab completions.
    _ARGCOMPLETE_AVAILABLE = False

from pepclibs.helperlibs import Logging, ArgParse, ProcessManager, ProjectFiles
from pepclibs.helperlibs.Exceptions import Error
from wultlibs.deploy import _Deploy

if typing.TYPE_CHECKING:
    import argparse
    from typing import cast, Callable
    from pepclibs.helperlibs.ArgParse import CommonArgsTypedDict, SSHArgsTypedDict
    from pepclibs.helperlibs.ProcessManager import ProcessManagerType
    from statscollectlibs.deploy.DeployBase import DeployInfoTypedDict

    class _DeployCmdlArgsTypedDict(CommonArgsTypedDict, SSHArgsTypedDict, total=False):
        """
        Typed dictionary for the "wult/pbe/ndl deploy" command-line arguments.

        Attributes:
            (All attributes from 'CommonArgsTypedDict')
            (All attributes from 'SSHArgsTypedDict')
            toolname: Name of the tool to deploy.
            ksrc: Path to the kernel source directory.
            drv_make_opts: Additional options to pass to 'make' when building the kernel module.
            lbuild: If True, build the kernel module on the target host.
            keep_tmpdir: If True, do not delete the temporary directory used for deployment.
            tmpdir_path: Path to the temporary directory to use for deployment.
        """

        toolname: str
        ksrc: str
        drv_make_opts: str
        lbuild: bool
        keep_tmpdir: bool
        tmpdir_path: str

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.wult.{__name__}")

def _format_args(args: argparse.Namespace) -> _DeployCmdlArgsTypedDict:
    """
    Build and return a typed dictionary containing the formatted command-line arguments.

    Args:
        args: The command-line arguments.

    Returns:
        _DeployCmdlArgsTypedDict: A typed dictionary containing the formatted arguments.
    """

    if typing.TYPE_CHECKING:
        cmdl1 = cast(dict, ArgParse.format_common_args(args))
        cmdl2 = cast(dict, ArgParse.format_ssh_args(args))
        # Merge the two dictionaries.
        cmdl = cast(_DeployCmdlArgsTypedDict, cmdl1 | cmdl2)
    else:
        cmdl1 = ArgParse.format_common_args(args)
        cmdl2 = ArgParse.format_ssh_args(args)
        cmdl = cmdl1 | cmdl2

    cmdl["toolname"] = args.toolname
    cmdl["ksrc"] = args.ksrc
    cmdl["drv_make_opts"] = args.drv_make_opts
    cmdl["lbuild"] = args.lbuild
    cmdl["keep_tmpdir"] = args.keep_tmpdir
    cmdl["tmpdir_path"] = args.tmpdir_path
    return cmdl

def _run_stats_collect_deploy(cmdl: _DeployCmdlArgsTypedDict, pman: ProcessManagerType):
    """
    Run the 'stats-collect deploy' command to deploy statistics collectors.

    Args:
        cmdl: The command-line arguments.
        pman: The process manager defining the target host.
    """

    # pylint: disable=import-outside-toplevel
    from pepclibs.helperlibs import LocalProcessManager
    from statscollecttools.ToolInfo import TOOLNAME as STATS_COLLECT_TOOLNAME
    # pylint: enable=import-outside-toplevel

    stcoll_path = ProjectFiles.find_project_helper("stats-collect", STATS_COLLECT_TOOLNAME)
    cmd = str(stcoll_path)

    if Logging.getLogger(Logging.MAIN_LOGGER_NAME).colored:
        cmd += " --force-color deploy"
    else:
        cmd += " deploy"

    if cmdl["debug"]:
        cmd += " -d"
    if cmdl["quiet"]:
        cmd += " -q"

    if cmdl["hostname"] != "localhost":
        cmd += f" -H {cmdl['hostname']}"
        if cmdl["username"]:
            cmd += f" -U {cmdl['username']}"
        if cmdl["privkey"]:
            cmd += f" -K {cmdl['privkey']}"
        if cmdl["timeout"]:
            cmd += f" -T {cmdl['timeout']}"

    _LOG.info("Deploying statistics collectors%s", pman.hostmsg)

    with LocalProcessManager.LocalProcessManager() as lpman:
        try:
            if cmdl["debug"]:
                kwargs = {"output_fobjs" : (sys.stdout, sys.stderr)}
            else:
                kwargs = {}
            lpman.run_verify(cmd, **kwargs)
        except Error as err:
            _LOG.warning("Failed to deploy statistics collectors%s", pman.hostmsg)
            _LOG.debug(str(err))

def deploy_command(args: argparse.Namespace, deploy_info: DeployInfoTypedDict):
    """
    Implement the 'wult/pbe/ndl deploy' command.

    Args:
        args: The command-line arguments.
        deploy_info: The tool deployment information dictionary.
    """

    cmdl = _format_args(args)

    with ProcessManager.get_pman(cmdl["hostname"], username=cmdl["username"],
                                 privkeypath=cmdl["privkey"], timeout=cmdl["timeout"]) as pman:
        with _Deploy.Deploy(cmdl["toolname"], deploy_info, pman=pman, ksrc=cmdl["ksrc"],
                            lbuild=cmdl["lbuild"], drv_make_opts=cmdl["drv_make_opts"],
                            tmpdir_path=cmdl["tmpdir_path"], keep_tmpdir=cmdl["keep_tmpdir"],
                            debug=cmdl["debug"]) as depl:
            depl.deploy()

        _run_stats_collect_deploy(cmdl, pman)

def add_deploy_cmdline_args(toolname: str,
                            deploy_info: DeployInfoTypedDict,
                            subparsers: ArgParse.SubParsersType,
                            func: Callable[[argparse.Namespace], None]) -> argparse.ArgumentParser:
    """
    Add the 'deploy' command and command-line options.

    Args:
        toolname: Name of the tool to add the 'deploy' command for.
        deploy_info: The tool deployment information dictionary.
        subparsers: The 'Argparse' subparsers object to add the 'deploy' command to.
        func: The function to handle the 'deploy' command.

    Returns:
        The 'argparse.ArgumentParser' object for the 'deploy' command.
    """

    # pylint: disable=import-outside-toplevel
    from statscollectlibs.deploy import DeployBase
    from wultlibs.deploy import _DeployDrivers
    if typing.TYPE_CHECKING:
        from statscollectlibs.deploy.DeployBase import InstallableCategoriesType
    # pylint: enable=import-outside-toplevel

    if typing.TYPE_CHECKING:
        cats: dict[InstallableCategoriesType, list[str]]
    cats = {cat: [] for cat in DeployBase.CATEGORIES}

    for name, info in deploy_info["installables"].items():
        cats[info["category"]].append(name)

    what = ""
    if cats["shelpers"] or cats["pyhelpers"]:
        if cats["drivers"]:
            what = "helpers and drivers"
        else:
            what = "helpers"
    elif cats["drivers"]:
        what = "drivers"
    else:
        raise Error("BUG: No helpers and no drivers")

    if _ARGCOMPLETE_AVAILABLE:
        completer = argcomplete.completers.DirectoriesCompleter()
    else:
        completer = None

    text = f"Compile and deploy {toolname} {what}."
    descr = f"""Compile and deploy {toolname} {what} to the System Under Test (SUT), which may be
                either the local or a remote host, depending on the '-H' option. By default, all
                components are built on the SUT. Use the '--local-build' option to build on the
                local system instead."""

    if cats["drivers"]:
        searchdirs = ProjectFiles.get_project_data_search_descr("wult",
                                                                _DeployDrivers.DRIVERS_SRC_SUBDIR)
        descr += f""" The driver sources are searched in the following directories (in order) on the
                     local host: {searchdirs}."""

    if cats["shelpers"] or cats["pyhelpers"]:
        searchdirs = ProjectFiles.get_project_data_search_descr("wult", _Deploy.HELPERS_SRC_SUBDIR)
        helpernames = ", ".join(cats["shelpers"] + cats["pyhelpers"])
        descr += f""" The {toolname} tool requires the following helpers: {helpernames}. These
                      helpers will be compiled and deployed to the SUT. The helper source files are
                      searched in the following directories (in order) on the local host:
                      {searchdirs}. By default, helpers are deployed to the location specified by
                      the 'WULT_HELPERSPATH' environment variable. If this variable is not set,
                      helpers are deployed to '$HOME/{_Deploy.HELPERS_DEPLOY_SUBDIR}/bin', where
                      '$HOME' is the home directory of user 'USERNAME' on host 'HOST' (see '--host'
                      and '--username' options)."""

    subpars = subparsers.add_parser("deploy", help=text, description=descr)
    if typing.TYPE_CHECKING:
        subpars = cast(ArgParse.ArgsParser, subpars)

    if cats["drivers"]:
        text = """Path to the Linux kernel source directory used for building drivers. By default,
                  this is '/lib/modules/$(uname -r)/build' on the SUT. If '--local-build' is
                  specified, the path refers to the local system instead of the SUT."""
        subpars.add_argument("--kernel-src", dest="ksrc", type=Path,
                             help=text).completer = completer # type: ignore[attr-defined]

        text = """Additional options or variables to pass to 'make' when building the drivers. For
                  example, use 'CC=clang LLVM=1' to build the drivers with clang and LLVM tools."""
        subpars.add_argument("--drivers-make-opts", dest="drv_make_opts", help=text)

        text = """Skip deploying drivers. Intended for debugging and development only."""
        subpars.add_argument("--skip-drivers", action="store_true", help=text)

    text = f"""Build {what} on the local system instead of on SUT (HOSTNAME)."""
    subpars.add_argument("--local-build", dest="lbuild", action="store_true", help=text)

    text = f"""By default, {toolname} uses a randomly generated temporary directory during
               deployment. Use this option to specify a custom path for the temporary directory. The
               provided path will be used on both the local and remote hosts. This option is
               intended for debugging."""
    subpars.add_argument("--tmpdir-path", help=text).completer = completer

    text = f"""Preserve the temporary directories created during deployment of {toolname}. This
               option is intended for debugging."""
    subpars.add_argument("--keep-tmpdir", action="store_true", help=text)

    ArgParse.add_ssh_options(subpars)

    subpars.set_defaults(func=func)
    return subpars
