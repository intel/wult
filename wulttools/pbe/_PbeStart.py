# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2024 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module includes the "start" 'wult' command implementation.
"""

import contextlib
from pathlib import Path
from pepclibs import CPUInfo
from pepclibs.helperlibs import Logging, Trivial
from statscollectlibs.collector import StatsCollectBuilder
from wultlibs.rawresultlibs import WORawResult
from wultlibs.helperlibs import Human
from wultlibs.deploylibs import _Deploy
from wultlibs import Devices, PbeRunner
from wulttools import _Common

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.wult.{__name__}")

def _generate_report(args):
    """Implement the '--report' option for the 'start' command."""

    from wultlibs.htmlreport import PbeReport # pylint: disable=import-outside-toplevel

    rsts = _Common.open_raw_results([args.outdir], args.toolname)
    rep = PbeReport.PbeReport(rsts, args.outdir / "html-report", report_descr=args.reportid)
    rep.generate()

def start_command(args):
    """Implements the 'start' command."""

    if args.list_stats:
        _Common.start_command_list_stats()
        return

    with contextlib.ExitStack() as stack:
        pman = _Common.get_pman(args)
        stack.enter_context(pman)

        args.reportid = _Common.start_command_reportid(args, pman)

        args.ldist = _Common.parse_ldist(args.ldist, single_ok=False)

        ldist_step_pct, ldist_step_ns = None, None
        if args.ldist_step.endswith("%"):
            ldist_step_pct = Trivial.str_to_num(args.ldist_step.rstrip("%"))
        else:
            ldist_step_ns = Human.parse_human(args.ldist_step, unit="us", target_unit="ns",
                                              name="launch distance step")
        if Trivial.is_num(args.span):
            args.span = f"{args.span}m"
        span = Human.parse_human(args.span, unit="s", integer=True, name="span")

        if Trivial.is_num(args.warmup):
            args.warmup = f"{args.warmup}m"
        warmup = Human.parse_human(args.warmup, unit="s", integer=True, name="warm-up period")

        if not args.outdir:
            args.outdir = Path(f"./{args.reportid}")

        cpuinfo = CPUInfo.CPUInfo(pman=pman)
        stack.enter_context(cpuinfo)

        offline_cpus = cpuinfo.get_offline_cpus()
        if offline_cpus:
            _LOG.notice(f"the following CPUs are offline and will not participate in measurements: "
                        f"{Human.rangify(offline_cpus)}")

        res = WORawResult.WORawResult(args.toolname, args.toolver, args.reportid, args.outdir)
        stack.enter_context(res)

        dev = Devices.GetDevice(args.toolname, args.devid, pman, dmesg=True)
        stack.enter_context(dev)

        _Common.configure_log_file(res.logs_path, args.toolname)

        args.lead_cpu = cpuinfo.normalize_cpu(args.lead_cpu)

        stcoll_builder = StatsCollectBuilder.StatsCollectBuilder()
        stack.enter_context(stcoll_builder)

        if args.stats and args.stats != "none":
            stcoll_builder.parse_stnames(args.stats)
        if args.stats_intervals:
            stcoll_builder.parse_intervals(args.stats_intervals)

        stcoll = stcoll_builder.build_stcoll_nores(pman, args.reportid, cpunum=args.lead_cpu,
                                                   local_outdir=res.stats_path)
        if stcoll:
            stack.enter_context(stcoll)

        deploy_info = _Common.reduce_installables(args.deploy_info, dev)
        with _Deploy.DeployCheck("wult", args.toolname, deploy_info, pman=pman) as depl:
            depl.check_deployment()

        runner = PbeRunner.PbeRunner(pman, dev, res, args.ldist, span, warmup, stcoll,
                                     ldist_step_pct=ldist_step_pct,
                                     ldist_step_ns=ldist_step_ns, lcpu=args.lead_cpu)
        stack.enter_context(runner)

        runner.prepare()
        runner.run()

    if args.report:
        _generate_report(args)
