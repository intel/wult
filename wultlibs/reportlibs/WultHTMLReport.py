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
from wultlibs.helperlibs import Trivial

# The constants below define the diagrams and histograms that are included into a report. There are
# 3 groups of constands - for a small report, a medium report, and large report. The former includes
# minimum amount of diagrams/histograms, the latter includes all of them.
DEFAULT_XAXES = MEDIUM_XAXES = "SilentTime"
DEFAULT_YAXES = MEDIUM_YAXES = r".*Latency,.*Delay"
DEFAULT_HIST = MEDIUM_HIST = f"{DEFAULT_YAXES}"
DEFAULT_CHIST = MEDIUM_CHIST = r".*Latency"

SMALL_XAXES = "SilentTime"
SMALL_YAXES = r"WakeLatency,WarmupDelay,LatchDelay"
SMALL_HIST = f"{SMALL_YAXES}"
SMALL_CHIST = r"WakeLatency"

LARGE_XAXES = "SilentTime,LDist"
LARGE_YAXES = r".*Latency,.*Delay,(Derived)?[PC]C.+%,SilentTime,ReqCState,CStates.*"
LARGE_HIST = f"{LARGE_YAXES},LDist"
LARGE_CHIST = r".*Latency"

# All diagrams and histograms with the combinations of EXCLUDE_XAXES and EXCLUDE_YAXES will not be
# included to the report. By default this will be all "Whatever vs LDist" diagram, except for
# "SilentTime vs LDist". The reason is that 'SilentTime' and 'LDist' are highly correlated, and it
# is enough to include "Whatever vs SilentTime", and "Whatever vs LDist" will just cluttering the
# report. But "SilentTime vs LDist" is almost always useful and it shows how the two are correlated.
EXCLUDE_XAXES = "LDist"
EXCLUDE_YAXES = r"(?!SilentTime)"

class WultHTMLReport(_HTMLReportBase.HTMLReportBase):
    """This module provides API for generating HTML reports for wult test results."""

    def _mangle_loaded_res(self, res):
        """
        Drop 'res.df' dataframe columns corresponding to C-states with no residency. Presumably this
        C-state was either disabled or just does not exist. And drop all the C-state cycle counters
        as they will not be needed any longer.
        """

        for colname in res.df:
            if colname not in self._cs_cyc_colnames:
                continue
            # Drop the corresponding C-state percentage column if no CPU cycles were spent in
            # it.
            cs_colname = f"{colname[0:-3]}%"
            if cs_colname in res.df and not res.df[colname].any():
                res.df.drop(cs_colname, axis="columns", inplace=True)
            # Remove the "C-state cycles" column as well.
            res.df.drop(colname, axis="columns", inplace=True)

        return super()._mangle_loaded_res(res)

    def __init__(self, rsts, outdir, title_descr=None, xaxes=None, yaxes=None, hist=None,
                 chist=None):
        """The class constructor. The arguments are the same as in 'HTMLReportBase()'."""

        args = {"xaxes": xaxes, "yaxes": yaxes, "hist": hist, "chist": chist}

        for name, default in zip(args, (DEFAULT_XAXES, DEFAULT_YAXES, DEFAULT_HIST, DEFAULT_CHIST)):
            if args[name] is None:
                args[name] = default.split(",")

        super().__init__(rsts, outdir, title_descr=title_descr, xaxes=args["xaxes"],
                         yaxes=args["yaxes"], hist=args["hist"], chist=args["chist"],
                         exclude_xaxes=EXCLUDE_XAXES, exclude_yaxes=EXCLUDE_YAXES)

        # Column names representing C-state cycles.
        self._cs_cyc_colnames = set()

        for res in rsts:
            for colname in res.defs.get_cscyc_colnames():
                # Form the list of column names representing C-state cycles. We'll need to load them
                # in order to detect C-states with no residency.
                self._cs_cyc_colnames.add(colname)
                self._more_colnames.append(colname)

        self._more_colnames = Trivial.list_dedup(self._more_colnames)
