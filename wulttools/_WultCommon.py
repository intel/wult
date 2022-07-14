# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
Misc. helpers shared between various 'wult' commands.
"""

from wultlibs.htmlreport import WultReportParams

# Regular expressions for the metrics that should show up in the hover text of the scatter plot. The
# middle element selects all the core and package C-state residency columns.
HOVER_METRIC_REGEXS = [".*Latency", "IntrOff", ".*Delay", "LDist", "ReqCState", r"[PC]C.+%",
                       "SMI.*", "NMI.*"]

def get_axes(optname, report_size=None):
    """
    Returns the CSV column name regex for a given plot option name and report size setting.
      * optname - plot option name ('xaxes', 'yaxes', 'hist' or 'chist')
      * report_size - report size setting ('small', 'medium' or 'large'), defaults to 'small'.
    """

    if not report_size:
        report_size = "small"

    optnames = getattr(WultReportParams, f"{report_size.upper()}_{optname.upper()}")

    # The result is used for argparse, which does not accept '%' symbols.
    if optnames:
        return optnames.replace("%", "%%")
    return None
