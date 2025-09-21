# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
Implement 'wult start' command.
"""

# TODO: finish adding type hints to this module.
from __future__ import annotations # Remove when switching to Python 3.10+.

import typing
import contextlib
from pepclibs.helperlibs import Logging, Trivial, ProcessManager
from pepclibs.helperlibs.Exceptions import Error, ErrorNotSupported
from pepclibs.msr import PowerCtl
from pepclibs import CPUIdle, CPUInfo
from statscollectlibs.collector import StatsCollectBuilder
from wultlibs.deploy import _Deploy
from wultlibs.helperlibs import Human
from wultlibs.result import WORawResult
from wultlibs import Devices, WultRunner
from wulttools import _Common
from wulttools.wult import _WultCommon, ToolInfo

if typing.TYPE_CHECKING:
    import argparse
    from typing import cast
    from wulttools._Common import StartCmdlArgsTypedDict
    from pepclibs.helperlibs.ProcessManager import ProcessManagerType
    from statscollectlibs.deploy.DeployBase import DeployInfoTypedDict

    class WultStartCmdlArgsTypedDict(StartCmdlArgsTypedDict, total=False):
        """
        Typed dictionary for the "wult start" command-line arguments.

        Attributes:
            (All attributes from 'StartCmdlArgsTypedDict')
        """

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.wult.{__name__}")

def _format_args(args: argparse.Namespace) -> WultStartCmdlArgsTypedDict:
    """
    Build and return a typed dictionary containing the formatted command-line arguments.

    Args:
        args: The command-line arguments.

    Returns:
        WultStartCmdlArgsTypedDict: A typed dictionary containing the formatted arguments.
    """

    if typing.TYPE_CHECKING:
        cmdl = cast(WultStartCmdlArgsTypedDict,
                    _Common.format_start_command_args(args, ToolInfo.TOOLNAME))
    else:
        cmdl = _Common.format_start_command_args(args, ToolInfo.TOOLNAME)

    return cmdl

def _check_settings(args, pman, dev, csinfo, cpuinfo):
    """
    Some settings of the SUT may lead to results that are potentially confusing for the user. Look
    for such settings and if found, print a notice message.
    """

    _Common.check_aspm_setting(pman, dev, f"the '{args.devid}' delayed event device")

    enabled_cstates = []
    for _, info in csinfo.items():
        if info["disable"] == 0 and info["name"] != "POLL":
            enabled_cstates.append(info["name"])

    with contextlib.suppress(ErrorNotSupported), PowerCtl.PowerCtl(cpuinfo, pman=pman) as powerctl:
        # Check for the following 3 conditions to be true at the same time.
        # * C6 is enabled.
        # * C6 pre-wake is enabled.
        # * A timer-based method is used.

        if dev.is_timer and "C6" in enabled_cstates and \
           powerctl.is_cpu_feature_supported("cstate_prewake", args.cpu) and \
           powerctl.is_cpu_feature_enabled("cstate_prewake", args.cpu):
            _LOG.notice("C-state prewake is enabled, and this usually hides the real "
                        "latency when using '%s' as delayed event device", args.devid)

        # Check for the following 2 conditions to be true at the same time.
        # * C1 is enabled.
        # * C1E auto-promotion is enabled.
        if enabled_cstates in [["C1"], ["C1_ACPI"]]:
            if powerctl.is_cpu_feature_enabled("c1e_autopromote", args.cpu):
                _LOG.notice("C1E autopromote is enabled, all %s requests are converted to C1E",
                            enabled_cstates[0])

def _generate_report(cmdl: StartCmdlArgsTypedDict):
    """
    Generate an HTML report from the raw results in "html-report" subdirectory of the raw results
    directory.

    Args:
        cmdl: The command-line arguments.
    """

    from wultlibs.htmlreport import WultReport # pylint: disable=import-outside-toplevel

    rsts = _Common.open_raw_results([cmdl["outdir"]], ToolInfo.TOOLNAME)
    rep = WultReport.WultReport(rsts, cmdl["outdir"] / "html-report", report_descr=cmdl["reportid"])
    rep.set_hover_metrics(_WultCommon.HOVER_METRIC_REGEXS)
    rep.generate()

def _check_cpu_vendor(args, cpuinfo, pman):
    """
    Check if the CPU vendor is compatible with the requested measurement method.
    """

    vendor = cpuinfo.info["vendor"]
    if vendor == "GenuineIntel":
        # Every method supports at least some Intel CPUs.
        return

    if vendor != "AuthenticAMD":
        raise ErrorNotSupported(f"unsupported CPU vendor '{vendor}'{pman.hostmsg}.\nOnly Intel and "
                                f"AMD CPUs are currently supported.")

    # In case of AMD CPU the TDT-based methods are not currently supported, other methods are
    # supported.
    if "tdt" in args.devid:
        raise ErrorNotSupported("methods based on TSC deadline timer (TDT) support only Intel "
                                "CPUs.\nPlease, use a non-TDT method for measuring AMD CPUs.")

def start_command(args: argparse.Namespace, deploy_info: DeployInfoTypedDict):
    """
    Implement the 'wult start' command.

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

        if args.tlimit:
            if Trivial.is_num(args.tlimit):
                args.tlimit = f"{args.tlimit}m"
            args.tlimit = Human.parse_human(args.tlimit, unit="s", integer=True, what="time limit")

        if not Trivial.is_int(args.dpcnt) or int(args.dpcnt) <= 0:
            raise Error(f"bad datapoints count '{args.dpcnt}', should be a positive integer")
        args.dpcnt = int(args.dpcnt)

        args.tsc_cal_time = Human.parse_human(args.tsc_cal_time, unit="s",
                                              what="TSC calculation time", integer=True)

        cpuinfo = CPUInfo.CPUInfo(pman=pman)
        stack.enter_context(cpuinfo)

        _check_cpu_vendor(args, cpuinfo, pman)

        args.cpu = cpuinfo.normalize_cpu(args.cpu)
        res = WORawResult.WORawResult(ToolInfo.TOOLNAME, ToolInfo.VERSION, cmdl["reportid"],
                                      cmdl["outdir"], cpu=args.cpu)
        stack.enter_context(res)

        _Common.configure_log_file(res.logs_path, ToolInfo.TOOLNAME)
        _Common.set_filters(args, res)

        stcoll_builder = StatsCollectBuilder.StatsCollectBuilder()
        stack.enter_context(stcoll_builder)

        if args.stats and args.stats != "none":
            stcoll_builder.parse_stnames(args.stats)
        if args.stats_intervals:
            stcoll_builder.parse_intervals(args.stats_intervals)

        stcoll = stcoll_builder.build_stcoll_nores(pman, cmdl["reportid"], cpus=(args.cpu,),
                                                   local_outdir=res.stats_path)
        if stcoll:
            stack.enter_context(stcoll)

        dev = Devices.GetDevice(ToolInfo.TOOLNAME, args.devid, pman, cpu=args.cpu, dmesg=True)
        stack.enter_context(dev)

        deploy_info = _Common.reduce_installables(deploy_info, dev)
        with _Deploy.DeployCheck("wult", ToolInfo.TOOLNAME, deploy_info, pman=pman) as depl:
            depl.check_deployment()

        if getattr(dev, "netif", None):
            _Common.start_command_check_network(args, pman, dev.netif)

        cpuidle = CPUIdle.CPUIdle(pman=pman, cpuinfo=cpuinfo)
        csinfo = cpuidle.get_cpu_cstates_info(res.cpu)

        _check_settings(args, pman, dev, csinfo, cpuinfo)

        runner = WultRunner.WultRunner(pman, dev, res, cmdl["ldist"],
                                       tsc_cal_time=args.tsc_cal_time, cpuidle=cpuidle,
                                       stcoll=stcoll, unload=not args.no_unload)
        stack.enter_context(runner)

        runner.prepare()
        runner.run(dpcnt=args.dpcnt, tlimit=args.tlimit, keep_rawdp=args.keep_rawdp)

    if args.report:
        _generate_report(_cmdl)
