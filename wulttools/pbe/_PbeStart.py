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

import logging
import contextlib
from pathlib import Path
from pepclibs import CPUInfo
from pepclibs.helperlibs import Trivial, Logging
from wultlibs.rawresultlibs import WORawResult
from wultlibs.helperlibs import Human
from wultlibs.deploylibs import _Deploy
from wultlibs import Devices, PbeRunner
from wulttools import _Common

_LOG = logging.getLogger()

def _generate_report(args):
    """Implement the '--report' option for the 'start' command."""

    from wultlibs.htmlreport import PbeReport

    rsts = _Common.open_raw_results([args.outdir], args.toolname)
    rep = PbeReport.PbeReport(rsts, args.outdir / "html-report", report_descr=args.reportid)
    rep.generate()

def start_command(args):
    """Implements the 'start' command."""

    with contextlib.ExitStack() as stack:
        pman = _Common.get_pman(args)
        stack.enter_context(pman)

        args.reportid = _Common.start_command_reportid(args, pman)

        args.wakeperiod = _Common.parse_ldist(args.wakeperiod, single_ok=False)

        wper_step_pct, wper_step_ns = None, None
        if args.wakeperiod_step.endswith("%"):
            wper_step_pct = Trivial.str_to_num(args.wakeperiod_step.rstrip("%"))
        else:
            wper_step_ns = Human.parse_human(args.wakeperiod_step, unit="us", target_unit="ns",
                                             name="wake period step")
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

        Logging.setup_stdout_logging(args.toolname, res.logs_path)

        deploy_info = _Common.reduce_installables(args.deploy_info, dev)
        with _Deploy.DeployCheck("wult", args.toolname, deploy_info, pman=pman) as depl:
            depl.check_deployment()

        args.lead_cpu = cpuinfo.normalize_cpu(args.lead_cpu)
        runner = PbeRunner.PbeRunner(pman, dev, res, args.wakeperiod, span, warmup,
                                     wper_step_pct=wper_step_pct,
                                     wper_step_ns=wper_step_ns, lcpu=args.lead_cpu)
        stack.enter_context(runner)

        runner.prepare()
        runner.run()

    if args.report:
        _generate_report(args)