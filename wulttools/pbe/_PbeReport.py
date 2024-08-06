# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Adam Hawley <adam.james.hawley@intel.com>

"""This module includes the "report" 'pbe' command implementation."""

from pathlib import Path
from pepclibs.helperlibs import Logging
from wulttools import _Common
from wulttools.pbe import ToolInfo
from wultlibs.htmlreport import PbeReport

def report_command(args):
    """Implements the 'report' command."""

    rsts = _Common.open_raw_results(args.respaths, args.toolname, reportids=args.reportids)

    args.outdir = _Common.report_command_outdir(args, rsts)

    logpath = Logging.setup_stdout_logging(ToolInfo.TOOLNAME, args.outdir)
    logpath = Path(logpath).relative_to(args.outdir)

    rep = PbeReport.PbeReport(rsts, args.outdir, report_descr=args.report_descr, logpath=logpath)
    rep.generate()
