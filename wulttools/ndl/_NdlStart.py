# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module includes the "start" 'ndl' command implementation.
"""

import logging
import contextlib
from pathlib import Path
from pepclibs import CPUInfo
from pepclibs.helperlibs import Logging, Trivial
from pepclibs.helperlibs.Exceptions import Error, ErrorNotFound
from statscollectlibs.collector import StatsCollectBuilder
from wulttools import _Common
from wultlibs import NdlRunner, Devices
from wultlibs.deploylibs import _Deploy
from wultlibs.helperlibs import Human
from wultlibs.rawresultlibs import WORawResult

_LOG = logging.getLogger()

def _generate_report(args):
    """Implements the 'report' command for start."""

    from wultlibs.htmlreport import NdlReport # pylint: disable=import-outside-toplevel

    rsts = _Common.open_raw_results([args.outdir], args.toolname)
    rep = NdlReport.NdlReport(rsts, args.outdir / "html-report", report_descr=args.reportid)
    rep.relocatable = False
    rep.generate()

def _resolve_cpu(pman, devid):
    """Resolve first local CPU number for the device 'devid'. Return CPU number as integer."""

    try:
        path = f"/sys/class/net/{devid}/device/local_cpulist"
        local_cpulist = pman.read(path).strip()
    except Error as err:
        raise Error(f"failed to resolve local CPU number for the device '{devid}', use "
                    f"'--cpunum' to select CPU.") from err

    # local_cpulist is a string of one or multiple comma-separated CPU numbers or CPU number
    # ranges, e.g. "24-27,31-33,37-39". Pick first CPU from the list."
    local_cpulist = local_cpulist.split(",")[0]
    return int(local_cpulist.split("-")[0])

def start_command(args):
    """Implements the 'start' command."""

    if args.list_stats:
        _Common.start_command_list_stats()
        return

    with contextlib.ExitStack() as stack:
        pman = _Common.get_pman(args)
        stack.enter_context(pman)

        args.reportid = _Common.start_command_reportid(args, pman)

        if not args.outdir:
            args.outdir = Path(f"./{args.reportid}")
        if args.tlimit:
            args.tlimit = Human.parse_duration(args.tlimit, default_unit="m", name="time limit")

        args.ldist = _Common.parse_ldist(args.ldist)

        if not Trivial.is_int(args.dpcnt) or int(args.dpcnt) <= 0:
            raise Error(f"bad datapoints count '{args.dpcnt}', should be a positive integer")
        args.dpcnt = int(args.dpcnt)

        cpuinfo = CPUInfo.CPUInfo(pman=pman)
        stack.enter_context(cpuinfo)

        try:
            dev = Devices.GetDevice(args.toolname, args.devid, pman, dmesg=True)
        except ErrorNotFound as err:
            msg = f"{err}\nTo list all usable network interfaces, please run: ndl scan"
            if pman.is_remote:
                msg += f" -H {pman.hostname}"
            raise ErrorNotFound(msg) from err
        stack.enter_context(dev)

        if args.cpunum is None:
            args.cpunum = _resolve_cpu(pman, args.devid)

        args.cpunum = cpuinfo.normalize_cpu(args.cpunum)
        res = WORawResult.WORawResult(args.toolname, args.toolver, args.reportid, args.outdir,
                                      cpunum=args.cpunum)
        stack.enter_context(res)

        Logging.setup_stdout_logging(args.toolname, res.logs_path)
        _Common.set_filters(args, res)

        stcoll_builder = StatsCollectBuilder.StatsCollectBuilder()
        if args.stats and args.stats != "none":
            stcoll_builder.parse_stnames(args.stats)
        if args.stats_intervals:
            stcoll_builder.parse_intervals(args.stats_intervals)

        stcoll = stcoll_builder.build_stcoll(pman, args.reportid, cpunum=args.cpunum,
                                             local_outdir=res.stats_path)
        if stcoll:
            stack.enter_context(stcoll)

        deploy_info = _Common.reduce_installables(args.deploy_info, dev)
        with _Deploy.DeployCheck("wult", args.toolname, deploy_info, pman=pman) as depl:
            depl.check_deployment()

        _Common.start_command_check_network(args, pman, dev.netif)

        info = dev.netif.get_pci_info()
        if info.get("aspm_enabled"):
            _LOG.notice("PCI ASPM is enabled for the NIC '%s', and this typically increases "
                        "the measured latency.", args.devid)

        runner = NdlRunner.NdlRunner(pman, dev, res, args.ldist, stcoll=stcoll)
        stack.enter_context(runner)

        runner.prepare()
        runner.run(dpcnt=args.dpcnt, tlimit=args.tlimit)

    if args.report:
        _generate_report(args)
