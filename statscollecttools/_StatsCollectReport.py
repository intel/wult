# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Adam Hawley <adam.james.hawley@intel.com>

"""
This module includes the "report" 'stats-collect' command implementation.
"""

from statscollecttools import _Common
from statscollectlibs.htmlreport import HTMLReport
from statscollectlibs.rawresultlibs import RORawResult

def report_command(args):
    """Implements the 'report' command."""

    rsts = [RORawResult.RORawResult(respath) for respath in args.respaths]

    if not args.outdir:
        args.outdir = args.respaths[0] / "html-report"

    rep = HTMLReport.HTMLReport(args.outdir)
    stats_paths = {res.reportid: res.stats_path for res in rsts}
    stdout_tab = _Common.generate_captured_output_tab(rsts, args.outdir)
    tabs = [stdout_tab] if stdout_tab else None
    rep.generate_report(tabs=tabs, stats_paths=stats_paths, title="stats-collect report")
