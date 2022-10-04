# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module includes the "start" 'wult' command implementation.
"""

import logging
import contextlib
from pathlib import Path
from pepclibs.helperlibs import LocalProcessManager, Trivial
from pepclibs.helperlibs.Exceptions import Error, ErrorNotSupported
from pepclibs.msr import PowerCtl
from pepclibs import CStates, CPUInfo
from statscollectlibs.collector import STCHelpers
from wultlibs.helperlibs import Human
from wultlibs.rawresultlibs import WORawResult
from wultlibs import Deploy, WultStatsCollect, ToolsCommon, Devices, WultRunner
from wulttools import _WultCommon

_LOG = logging.getLogger()

def _check_settings(pman, dev, csinfo, cpunum, devid):
    """
    Some settings of the SUT may lead to results that are potentially confusing for the user. This
    function looks for such settings and if found, prints a notice message.
      * pman - the process manager object that defines the host to run the measurements on.
      * dev - the delayed event device object created by 'Devices.GetDevice()'.
      * devid - the ID of the device used for measuring the latency.
      * csinfo - cstate info from 'CStates.get_cstates_info()'.
      * cpunum - the logical CPU number to measure.
    """

    if dev.info.get("aspm_enabled"):
        _LOG.notice("PCI ASPM is enabled for the delayed event device '%s', and this "
                    "typically increases the measured latency.", devid)

    enabled_cstates = []
    for _, info in csinfo.items():
        if info["disable"] == 0 and info["name"] != "POLL":
            enabled_cstates.append(info["name"])

    with contextlib.suppress(ErrorNotSupported), PowerCtl.PowerCtl(pman=pman) as powerctl:
        # Check for the following 3 conditions to be true at the same time.
        # * C6 is enabled.
        # * C6 pre-wake is enabled.
        # * The "tdt" method is used.
        if devid == "tdt" and "C6" in enabled_cstates and \
            powerctl.is_cpu_feature_supported("cstate_prewake", cpunum) and \
            powerctl.is_cpu_feature_enabled("cstate_prewake", cpunum):
            _LOG.notice("C-state prewake is enabled, and this usually hides the real "
                        "latency when using '%s' as delayed event device.", devid)

        # Check for the following 2 conditions to be true at the same time.
        # * C1 is enabled.
        # * C1E auto-promotion is enabled.
        if enabled_cstates in [["C1"], ["C1_ACPI"]]:
            if powerctl.is_cpu_feature_enabled("c1e_autopromote", cpunum):
                _LOG.notice("C1E autopromote is enabled, all %s requests are converted to C1E.",
                            enabled_cstates[0])

def _list_stats():
    """Print information about statistics."""

    if not WultStatsCollect.STATS_INFO:
        raise Error("statistics collection is not supported on your system")

    for stname, stinfo in WultStatsCollect.STATS_INFO.items():
        _LOG.info("* %s", stname)
        if stinfo.get("interval"):
            _LOG.info("  - Default interval: %.1fs", stinfo["interval"])
        _LOG.info("  - %s", stinfo["description"])

def _generate_report(args):
    """Implements the 'report' command for start."""

    from wultlibs.htmlreport import WultReport # pylint: disable=import-outside-toplevel

    rsts = ToolsCommon.open_raw_results([args.outdir], args.toolname)
    rep = WultReport.WultReport(rsts, args.outdir, title_descr=args.reportid)
    rep.relocatable = False
    rep.set_hover_metrics(_WultCommon.HOVER_METRIC_REGEXS)
    rep.generate()

def _create_stcoll(args, pman):
    """
    Create, initialize, and return the 'WultStatsCollect' object, which will be used for collecting
    statistics.
    """

    if not args.stats or args.stats == "none":
        return None

    stconf = STCHelpers.parse_stnames(args.stats)
    if args.stats_intervals:
        STCHelpers.parse_intervals(args.stats_intervals, stconf)

    stcoll = WultStatsCollect.WultStatsCollect(pman, args.outdir)

    # This is a small optimization: if only 'sysinfo' statistics was requested, the 'stc-agent'
    # won't be needed, so we can skip 'stc-agent' path discovery.
    if list(stconf["include"]) != ["sysinfo"]:
        with LocalProcessManager.LocalProcessManager() as lpman:
            lpath = Deploy.get_installed_helper_path(lpman, "wult", "stc-agent")
        if pman.is_remote:
            rpath = Deploy.get_installed_helper_path(pman, "wult", "stc-agent")

        stcoll.set_stcagent_path(local_path=lpath, remote_path=rpath)

    stcoll.apply_stconf(stconf)

    if stconf["discover"] or "acpower" in stconf["include"]:
        # Assume that power meter is configured to match the SUT name.
        if pman.is_remote:
            devnode = pman.hostname
        else:
            devnode = "default"

        with contextlib.suppress(Error):
            stcoll.set_prop("acpower", "devnode", devnode)

    return stcoll

def start_command(args):
    """Implements the 'start' command."""

    if args.list_stats:
        _list_stats()
        return

    with contextlib.ExitStack() as stack:
        pman = ToolsCommon.get_pman(args)
        stack.enter_context(pman)

        args.reportid = ToolsCommon.start_command_reportid(args, pman)

        if not args.outdir:
            args.outdir = Path(f"./{args.reportid}")
        if args.tlimit:
            args.tlimit = Human.parse_duration(args.tlimit, default_unit="m", name="time limit")

        args.ldist = ToolsCommon.parse_ldist(args.ldist)

        if not Trivial.is_int(args.dpcnt) or int(args.dpcnt) <= 0:
            raise Error(f"bad datapoints count '{args.dpcnt}', should be a positive integer")
        args.dpcnt = int(args.dpcnt)

        args.tsc_cal_time = Human.parse_duration(args.tsc_cal_time, default_unit="s",
                                                 name="TSC calculation time")

        cpuinfo = CPUInfo.CPUInfo(pman=pman)
        stack.enter_context(cpuinfo)

        args.cpunum = cpuinfo.normalize_cpu(args.cpunum)

        res = WORawResult.WultWORawResult(args.reportid, args.outdir, args.toolver, args.cpunum)
        stack.enter_context(res)

        ToolsCommon.setup_stdout_logging(args.toolname, res.logs_path)
        ToolsCommon.set_filters(args, res)

        stcoll = _create_stcoll(args, pman)
        if stcoll:
            stack.enter_context(stcoll)

        dev = Devices.GetDevice(args.toolname, args.devid, pman, cpunum=args.cpunum, dmesg=True)
        stack.enter_context(dev)

        deploy_info = ToolsCommon.reduce_installables(args.deploy_info, dev, stcoll=stcoll)
        with Deploy.DeployCheck(args.toolname, deploy_info, pman=pman) as depl:
            depl.check_deployment()

        if getattr(dev, "netif", None):
            ToolsCommon.start_command_check_network(args, pman, dev.netif)

        rcsobj = CStates.ReqCStates(pman=pman)
        csinfo = rcsobj.get_cpu_cstates_info(res.cpunum)

        _check_settings(pman, dev, csinfo, args.cpunum, args.devid)

        runner = WultRunner.WultRunner(pman, dev, res, args.ldist, early_intr=args.early_intr,
                                       tsc_cal_time=args.tsc_cal_time, rcsobj=rcsobj, stcoll=stcoll)
        stack.enter_context(runner)

        runner.unload = not args.no_unload
        runner.prepare()
        runner.run(dpcnt=args.dpcnt, tlimit=args.tlimit, keep_rawdp=args.keep_rawdp)

    if args.report:
        _generate_report(args)
