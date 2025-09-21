# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
Implement 'pbe start' command.
"""

# TODO: finish adding type hints to this module.
from __future__ import annotations # Remove when switching to Python 3.10+.

import typing
import contextlib
from pepclibs import CPUInfo
from pepclibs.helperlibs import Logging, Trivial, ProcessManager
from statscollectlibs.collector import StatsCollectBuilder
from wultlibs.result import WORawResult
from wultlibs.helperlibs import Human
from wultlibs.deploy import _Deploy
from wultlibs import Devices, PbeRunner
from wulttools import _Common
from wulttools.pbe import ToolInfo

if typing.TYPE_CHECKING:
    import argparse
    from typing import cast
    from wulttools._Common import StartCmdlArgsTypedDict
    from pepclibs.helperlibs.ProcessManager import ProcessManagerType
    from statscollectlibs.deploy.DeployBase import DeployInfoTypedDict

    class PbeStartCmdlArgsTypedDict(StartCmdlArgsTypedDict, total=False):
        """
        Typed dictionary for the "wult start" command-line arguments.

        Attributes:
            (All attributes from 'StartCmdlArgsTypedDict')
        """

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.wult.{__name__}")

def _format_args(args: argparse.Namespace) -> PbeStartCmdlArgsTypedDict:
    """
    Build and return a typed dictionary containing the formatted command-line arguments.

    Args:
        args: The command-line arguments.

    Returns:
        PbeStartCmdlArgsTypedDict: A typed dictionary containing the formatted arguments.
    """

    if typing.TYPE_CHECKING:
        cmdl = cast(PbeStartCmdlArgsTypedDict,
                    _Common.format_start_command_args(args, ToolInfo.TOOLNAME))
    else:
        cmdl = _Common.format_start_command_args(args, ToolInfo.TOOLNAME)

    return cmdl

def _generate_report(cmdl: StartCmdlArgsTypedDict):
    """
    Generate an HTML report from the raw results in "html-report" subdirectory of the raw results
    directory.

    Args:
        cmdl: The command-line arguments.
    """

    from wultlibs.htmlreport import PbeReport # pylint: disable=import-outside-toplevel

    rsts = _Common.open_raw_results([cmdl["outdir"]], cmdl["toolname"])
    rep = PbeReport.PbeReport(rsts, cmdl["outdir"] / "html-report", report_descr=cmdl["reportid"])
    rep.generate()

def start_command(args: argparse.Namespace, deploy_info: DeployInfoTypedDict):
    """
    Implement the 'pbe start' command.

    Args:
        args: The command-line arguments.
        deploy_info: The deployment information dictionary, used for checking the tool deployment.
    """

    cmdl = _format_args(args)
    if typing.TYPE_CHECKING:
        _cmdl = cast(StartCmdlArgsTypedDict, cmdl)
    else:
        _cmdl = cmdl

    with contextlib.ExitStack() as stack:
        pman = ProcessManager.get_pman(cmdl["hostname"], username=cmdl["username"],
                                       privkeypath=cmdl["privkey"], timeout=cmdl["timeout"])
        stack.enter_context(pman)

        ldist_step_pct, ldist_step_ns = None, None
        if args.ldist_step.endswith("%"):
            ldist_step_pct = Trivial.str_to_num(args.ldist_step.rstrip("%"))
        else:
            ldist_step_ns = Human.parse_human(args.ldist_step, unit="us", target_unit="ns",
                                              what="launch distance step")
        if Trivial.is_num(args.span):
            args.span = f"{args.span}m"
        span = Human.parse_human(args.span, unit="s", integer=True, what="span")

        if Trivial.is_num(args.warmup):
            args.warmup = f"{args.warmup}m"
        warmup = Human.parse_human(args.warmup, unit="s", integer=True, what="warm-up period")

        cpuinfo = CPUInfo.CPUInfo(pman=pman)
        stack.enter_context(cpuinfo)

        offline_cpus = cpuinfo.get_offline_cpus()
        if offline_cpus:
            _LOG.notice(f"the following CPUs are offline and will not participate in measurements: "
                        f"{Trivial.rangify(offline_cpus)}")

        args.lead_cpu = cpuinfo.normalize_cpu(args.lead_cpu)

        res = WORawResult.WORawResult(ToolInfo.TOOLNAME, ToolInfo.VERSION, cmdl["reportid"],
                                      cmdl["outdir"], cpu=args.lead_cpu)
        stack.enter_context(res)

        dev = Devices.GetDevice(ToolInfo.TOOLNAME, args.devid, pman, dmesg=True)
        stack.enter_context(dev)

        _Common.configure_log_file(res.logs_path, ToolInfo.TOOLNAME)

        stcoll_builder = StatsCollectBuilder.StatsCollectBuilder()
        stack.enter_context(stcoll_builder)

        if args.stats and args.stats != "none":
            stcoll_builder.parse_stnames(args.stats)
        if args.stats_intervals:
            stcoll_builder.parse_intervals(args.stats_intervals)

        stcoll = stcoll_builder.build_stcoll_nores(pman, cmdl["reportid"], cpus=(args.lead_cpu,),
                                                   local_outdir=res.stats_path)
        if stcoll:
            stack.enter_context(stcoll)

        deploy_info = _Common.reduce_installables(deploy_info, dev)
        with _Deploy.DeployCheck("wult", ToolInfo.TOOLNAME, deploy_info, pman=pman) as depl:
            depl.check_deployment()

        runner = PbeRunner.PbeRunner(pman, dev, res, cmdl["ldist"], span, warmup, stcoll,
                                     ldist_step_pct=ldist_step_pct,
                                     ldist_step_ns=ldist_step_ns, lcpu=args.lead_cpu)
        stack.enter_context(runner)

        runner.prepare()
        runner.run()

    if args.report:
        _generate_report(_cmdl)
