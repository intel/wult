# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Vladislav Govtva <vladislav.govtva@intel.com>
#          Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module provides paramets for generating HTML reports for wult test results.
"""

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
LARGE_YAXES = r".*Latency.*,.*Delay(?!Cyc).*,[PC]C.+%,SilentTime,ReqCState"
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
EXCLUDE_YAXES = "SilentTime"

# Defines which summary functions should be calculated and included in the report for each metric.
# Metrics are represented by their name or a regular expression and paired with a list of summary
# functions.
SMRY_FUNCS = {
    ".*Latency.*": ["max", "99.999%", "99.99%", "99.9%", "99%", "med", "avg", "min", "std"],
    "SilentTime": ["max", "min"],
    "LDist": ["max", "min"],
    "[P|C]C.*%": ["max", "99.999%", "99.99%", "99.9%", "99%", "med", "avg", "min", "std"],
    ".*Delay": ["max", "99.999%", "99.99%", "99.9%", "99%", "med", "avg", "min", "std"]
}
