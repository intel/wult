# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module includes the "report" 'ndl' command implementation.
"""

from pathlib import Path
from pepclibs.helperlibs import Trivial
from wulttools import _Common
from wulttools.ndl import ToolInfo
from wultlibs.htmlreport import NdlReport

def report_command(args):
    """Implements the 'report' command."""

    # Split the comma-separated lists.
    for name in ("xaxes", "yaxes", "hist", "chist"):
        val = getattr(args, name)
        if val:
            if val == "none":
                setattr(args, name, "")
            else:
                setattr(args, name, Trivial.split_csv_line(val))

    rsts = _Common.open_raw_results(args.respaths, args.toolname, reportids=args.reportids)

    if args.list_metrics:
        _Common.list_result_metrics(rsts)
        return

    for res in rsts:
        _Common.apply_filters(args, res)

    if args.even_dpcnt:
        _Common.even_up_dpcnt(rsts)

    args.outdir = _Common.report_command_outdir(args, rsts)

    logpath = _Common.configure_log_file(args.outdir, ToolInfo.TOOLNAME)
    logpath = Path(logpath).relative_to(args.outdir)

    rep = NdlReport.NdlReport(rsts, args.outdir, report_descr=args.report_descr,
                              xaxes=args.xaxes, yaxes=args.yaxes, hist=args.hist,
                              chist=args.chist, logpath=logpath)
    rep.copy_raw= args.copy_raw
    rep.generate()
