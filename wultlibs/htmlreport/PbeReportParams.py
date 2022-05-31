# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Adam Hawley <adam.james.hawley@intel.com>

"""This module provides parameters for generating HTML reports for pbe test results."""

DEFAULT_XAXES = "Time"
DEFAULT_YAXES = "WakePeriod"

# Defines which summary functions should be calculated and included in the report for each metric.
# Metrics are represented by their name or a regular expression and paired with a list of summary
# functions.
SMRY_FUNCS = {
    "WakePeriod": ["max", "min"],
}
