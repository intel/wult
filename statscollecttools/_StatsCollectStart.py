# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022-2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
#          Adam Hawley <adam.james.hawley@intel.com>

"""This module includes the "start" 'stats-collect' command implementation."""

import contextlib
import logging
from pathlib import Path
from pepclibs import CPUInfo
from pepclibs.helperlibs import Human, Logging
from statscollecttools import _Common
from statscollectlibs import Runner
from statscollectlibs.deploylibs import _Deploy
from statscollectlibs.collector import StatsCollectBuilder
from statscollectlibs.helperlibs import ReportID
from statscollectlibs.rawresultlibs import WORawResult

_LOG = logging.getLogger()

def generate_reportid(args, pman):
    """
    If user provided report ID for the 'start' command, this function validates it and returns.
    Otherwise, it generates the default report ID and returns it.
    """

    if not args.reportid and pman.is_remote:
        prefix = pman.hostname
    else:
        prefix = None

    return ReportID.format_reportid(prefix=prefix, reportid=args.reportid,
                                    strftime=f"{args.toolname}-%Y%m%d")

def start_command(args):
    """Implements the 'start' command."""

    with contextlib.ExitStack() as stack:
        pman = _Common.get_pman(args)
        stack.enter_context(pman)

        if args.tlimit:
            args.tlimit = Human.parse_duration(args.tlimit, default_unit="m", name="time limit")

        args.reportid = generate_reportid(args, pman)

        if not args.outdir:
            args.outdir = Path(f"./{args.reportid}")

        cpuinfo = CPUInfo.CPUInfo(pman=pman)
        stack.enter_context(cpuinfo)
        args.cpunum = cpuinfo.normalize_cpu(args.cpunum)

        with _Deploy.DeployCheck("stats-collect", args.toolname, args.deploy_info,
                                 pman=pman) as depl:
            depl.check_deployment()

        res = WORawResult.WORawResult(args.reportid, args.outdir, args.cpunum, args.cmd)

        Logging.setup_stdout_logging(args.toolname, res.logs_path)

        if not args.stats or args.stats == "none":
            args.stats = None
            _LOG.warning("no statistics will be collected")

        if args.stats:
            stcoll_builder = StatsCollectBuilder.StatsCollectBuilder()
            stcoll_builder.parse_stnames(args.stats)
            if args.stats_intervals:
                stcoll_builder.parse_intervals(args.stats_intervals)

            stcoll = stcoll_builder.build_stcoll(pman, args.outdir)
            if not stcoll:
                return

            stack.enter_context(stcoll)

            stcoll.start()

        stdout, stderr = Runner.run_command(args.cmd, pman, args.tlimit)

        if args.stats:
            stcoll.stop()
            stcoll.finalize()
            stinfo = stcoll.get_stinfo()
            if stinfo:
                res.info["stinfo"] = stinfo

        for ftype, txt in [("stdout", stdout,), ("stderr", stderr,)]:
            if not txt:
                continue
            fpath = args.outdir / "logs" / f"cmd-{ftype}.log.txt"
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(txt)
            res.info[ftype] = fpath.relative_to(args.outdir)

        res.write_info()

    if args.report:
        _Common.generate_stc_report([res], args.outdir / "html-report")
