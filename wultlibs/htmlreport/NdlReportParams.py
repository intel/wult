# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Vladislav Govtva <vladislav.govtva@intel.com>
#          Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module provides parameters for generating HTML reports for ndl test results.
"""

DEFAULT_XAXES = "LDist"
DEFAULT_YAXES = DEFAULT_HIST = DEFAULT_CHIST = "RTD"

# Defines which summary functions should be calculated and included in the report for each metric.
# Metrics are represented by their name or a regular expression and paired with a list of summary
# functions.
SMRY_FUNCS = {
    "LDist": ["max", "min"],
    "RTD": ["max", "99.999%", "99.99%", "99.9%", "99%", "med", "avg", "min", "std"]
}
