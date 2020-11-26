# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2020 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
Miscellaneous helper functions shared by various tools and modules.
"""

import logging
from collections import OrderedDict
from wultlibs.helperlibs import Trivial
from wultlibs.helperlibs.Exceptions import Error

_LOG = logging.getLogger("main")

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

def apply_filters(args, res):
    """
    This is a helper function for the following command-line options: '--rsel', '--rfilt', '--csel',
    '--cfilt'. The 'args' argument should be an 'helperlibs.ArgParse' object, where all the above
    mentioned options are represented by the 'oargs' (ordered arguments) field. The 'res' argument
    is a 'RORawResult' object.
    """

    def do_filter(res, ops):
        """Apply filter operations in 'ops' to wult test result 'res'."""

        res.clear_filts()
        for name, expr in ops.items():
            if name.startswith("c"):
                expr = Trivial.split_csv_line(expr)
            getattr(res, f"set_{name}")(expr)
        res.load_df()

    if not getattr(args, "oargs", None):
        return

    ops = OrderedDict()
    for name, expr in args.oargs:
        if name in ops:
            do_filter(res, ops)
            ops = OrderedDict()
        ops[name] = expr

    if ops:
        do_filter(res, ops)
