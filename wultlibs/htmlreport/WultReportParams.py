# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Vladislav Govtva <vladislav.govtva@intel.com>
#          Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module provides parameters for generating HTML reports for wult test results.
"""

# The constants below define which diagrams are included in a report. There are 2 groups of
# constants: for a small report, and a large report. The small report includes the minimum amount of
# diagrams, the large report includes all diagrams.
SMALL_XAXES = "SilentTime"
SMALL_YAXES = r".*Latency"
SMALL_HIST = f"{SMALL_YAXES}"
SMALL_CHIST = None

LARGE_XAXES = "SilentTime,LDist"
LARGE_YAXES = r".*Latency.*,.*Delay,[PMC]C.+%,SilentTime,ReqCState,CPUFreq"
LARGE_HIST = f"{LARGE_YAXES},LDist"
LARGE_CHIST = r".*Latency"

DEFAULT_XAXES = SMALL_XAXES
DEFAULT_YAXES = SMALL_YAXES
DEFAULT_HIST  = SMALL_HIST
DEFAULT_CHIST = SMALL_CHIST

# All diagrams with an X-axis and a Y-axis in 'EXCLUDE_XAXES' and 'EXCLUDE_YAXES' respectively will
# be excluded from the report. By default, the only excluded diagram is "SilentTime vs. LDist".
EXCLUDE_XAXES = "LDist"
EXCLUDE_YAXES = "SilentTime"

# Defines which summary functions should be calculated and included in the report for each metric.
# Metrics are represented by their name or a regular expression and paired with a list of summary
# functions.
SMRY_FUNCS = {
    ".*Latency.*": ["max", "99.999%", "99.99%", "99.9%", "99%", "med", "avg", "min", "std"],
    "SilentTime": ["max", "min"],
    "LDist": ["max", "min"],
    "[PMC]C.*%": ["max", "99.999%", "99.99%", "99.9%", "99%", "med", "avg", "min", "std"],
    ".*Delay": ["max", "99.999%", "99.99%", "99.9%", "99%", "med", "avg", "min", "std"]
}
