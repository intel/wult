# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2020 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Antti Laakso <antti.laakso@linux.intel.com>

"""This module contains common code shared only within wultlibs libraries."""

import logging
from wultlibs.helperlibs import Trivial
from wultlibs.helperlibs.Exceptions import Error

_LOG = logging.getLogger()

def get_dpcnt(res, dpcnt):
    """
    This helper function validates number of datapoints the user requested to collect ('dpcnt'). It
    also looks at how many datapoints are already present in the 'res' object (represents a raw test
    result) and returns the number datapoints to collect in order for 'rest' to end up with 'dpcnt'
    datapoints.
    """

    if not Trivial.is_int(dpcnt) or int(dpcnt) <= 0:
        raise Error(f"bad datapoints count '{dpcnt}', should be a positive integer")

    dpcnt = int(dpcnt) - res.csv.initial_rows_cnt
    if dpcnt <= 0:
        _LOG.info("Raw test result at '%s' already includes %d datapoints",
                  res.dirpath, res.csv.initial_rows_cnt)
        _LOG.info("Nothing to collect")
        return 0

    return dpcnt
