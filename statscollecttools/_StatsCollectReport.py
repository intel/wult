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

from pepclibs.helperlibs import Trivial
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.helperlibs import ReportID
from statscollectlibs.rawresultlibs import RORawResult
from statscollecttools import _Common, ToolInfo

def open_raw_results(respaths, reportids=None):
    """
    Opens the input raw test results, and returns the list of 'RORawResult' objects.
      * respaths - list of paths to raw results.
      * reportids - list of reportids to override report IDs in raw results.
    """

    if reportids:
        reportids = Trivial.split_csv_line(reportids)
    else:
        reportids = []

    if len(reportids) > len(respaths):
        raise Error(f"there are {len(reportids)} report IDs to assign to {len(respaths)} input "
                    f"test results. Please, provide {len(respaths)} or fewer report IDs.")

    # Append the required amount of 'None's to make the 'reportids' list be of the same length as
    # the 'respaths' list.
    reportids += [None] * (len(respaths) - len(reportids))

    rsts = []
    for respath, reportid in zip(respaths, reportids):
        if reportid:
            ReportID.validate_reportid(reportid)

        res = RORawResult.RORawResult(respath, reportid=reportid)
        if ToolInfo.TOOLNAME != res.info["toolname"]:
            raise Error(f"cannot generate '{ToolInfo.TOOLNAME}' report, results are collected with "
                        f"'{res.info['toolname']}':\n{respath}")
        rsts.append(res)

    return rsts

def report_command(args):
    """Implements the 'report' command."""

    rsts = open_raw_results(args.respaths, args.reportids)

    if not args.outdir:
        args.outdir = args.respaths[0] / "html-report"

    _Common.generate_stc_report(rsts, args.outdir)
