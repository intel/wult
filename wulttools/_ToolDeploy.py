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

import typing
from pepclibs.helperlibs import ArgParse, ProcessManager
from wulttools import _Common
from wultlibs.deploy import _Deploy

if typing.TYPE_CHECKING:
    import argparse
    from typing import cast
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

def deploy_command(args: argparse.Namespace, deploy_info: DeployInfoTypedDict):
    """
    Implement the 'wult/pbe/ndl deploy' command.

    Args:
        args: The command-line arguments.
        deploy_info: The 'wult/pbe/ndl' tool deployment information.
    """

    cmdl = _format_args(args)

    with ProcessManager.get_pman(cmdl["hostname"], username=cmdl["username"],
                                 privkeypath=cmdl["privkey"], timeout=cmdl["timeout"]) as pman:
        with _Deploy.Deploy(cmdl["toolname"], deploy_info, pman=pman, ksrc=cmdl["ksrc"],
                            lbuild=cmdl["lbuild"], drv_make_opts=cmdl["drv_make_opts"],
                            tmpdir_path=cmdl["tmpdir_path"], keep_tmpdir=cmdl["keep_tmpdir"],
                            debug=cmdl["debug"]) as depl:
            depl.deploy()

        _Common.run_stats_collect_deploy(args, pman)
