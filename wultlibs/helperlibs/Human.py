# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2020-2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module contains misc. helper functions with the common theme of representing something in a
human-readable format, or turning human-oriented data into a machine format.
"""

# pylint: disable=wildcard-import,unused-wildcard-import
from pepclibs.helperlibs.Human import *

def dict2str(dct):
    """Print a dictionary into a string and return the result."""

    import numpy                      # pylint: disable=import-outside-toplevel
    from itertools import zip_longest # pylint: disable=import-outside-toplevel

    # Printing one element per line takes too many lines and it is hard to read. So we attempt to
    # print 3 elements per line and align them for readability. So split items on 3 groups, each
    # group represents a column. The easy way of doing this is using 'numpy.array_split()'.
    split = [list(column) for column in numpy.array_split(numpy.array(list(dct)), 3)]

    columns = []
    for keys in split:
        # Create list of values for the keys in the column. Shorten the floating point numbers.
        vals = []
        for key in keys:
            val = dct[key]
            if isinstance(val, float):
                vals.append(f"{val:.2f}")
            else:
                vals.append(f"{val}")

        longest_key = max([len(key) for key in keys])
        longest_val = max([len(val) for val in vals])

        elts = []
        for key, val in zip(keys, vals):
            # Pad the keys/values to the longer key/value in the column.
            key = f"{(key + ':').ljust(longest_key + 1)}"
            val = f"{val.ljust(longest_val)}"
            elts.append(f"{key} {val}")

        columns.append(elts)

    return "\n".join(["    ".join(row).strip() for row in zip_longest(*columns, fillvalue="")])
