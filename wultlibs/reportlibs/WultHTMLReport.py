# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2020 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Vladislav Govtva <vladislav.govtva@intel.com>
#          Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module provides API for generating HTML reports for wult test results.
"""

from wultlibs.reportlibs import _HTMLReportBase

# The constants below define the diagrams and histograms that are included into a report. There are
# 3 groups of constands - for a small report, a medium report, and large report. The former includes
# minimum amount of diagrams/histograms, the latter includes all of them.
SMALL_XAXES = "SilentTime"
SMALL_YAXES = r".*Latency"
SMALL_HIST = f"{SMALL_YAXES}"
SMALL_CHIST = None

MEDIUM_XAXES = "SilentTime"
MEDIUM_YAXES = r".*Latency,.*Delay"
MEDIUM_HIST = f"{MEDIUM_YAXES}"
MEDIUM_CHIST = r".*Latency"

LARGE_XAXES = "SilentTime,LDist"
LARGE_YAXES = r".*Latency,.*Delay,[PC]C.+%,SilentTime,ReqCState"
LARGE_HIST = f"{LARGE_YAXES},LDist"
LARGE_CHIST = r".*Latency"

DEFAULT_XAXES = SMALL_XAXES
DEFAULT_YAXES = SMALL_YAXES
DEFAULT_HIST  = SMALL_HIST
DEFAULT_CHIST = SMALL_CHIST

# All diagrams and histograms with the combinations of EXCLUDE_XAXES and EXCLUDE_YAXES will not be
# included to the report. By default this will be all "Whatever vs LDist" diagram, except for
# "SilentTime vs LDist". The reason is that 'SilentTime' and 'LDist' are highly correlated, and it
# is enough to include "Whatever vs SilentTime", and "Whatever vs LDist" will just cluttering the
# report. But "SilentTime vs LDist" is almost always useful and it shows how the two are correlated.
EXCLUDE_XAXES = "LDist"
EXCLUDE_YAXES = r"(?!SilentTime)"

class WultHTMLReport(_HTMLReportBase.HTMLReportBase):
    """This module provides API for generating HTML reports for wult test results."""

    def __init__(self, rsts, outdir, title_descr=None, xaxes=None, yaxes=None, hist=None,
                 chist=None):
        """The class constructor. The arguments are the same as in 'HTMLReportBase()'."""

        args = {"xaxes": xaxes, "yaxes": yaxes, "hist": hist, "chist": chist}

        for name, default in zip(args, (DEFAULT_XAXES, DEFAULT_YAXES, DEFAULT_HIST, DEFAULT_CHIST)):
            if args[name] is None and default:
                args[name] = default.split(",")

        super().__init__(rsts, outdir, title_descr=title_descr, xaxes=args["xaxes"],
                         yaxes=args["yaxes"], hist=args["hist"], chist=args["chist"],
                         exclude_xaxes=EXCLUDE_XAXES, exclude_yaxes=EXCLUDE_YAXES)
