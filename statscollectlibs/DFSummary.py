# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module provides the capability of calculating summarising statistics for a given
'pandas.DataFrame'.
"""

import numpy
from pepclibs.helperlibs import Trivial
from pepclibs.helperlibs.Exceptions import Error

# Summary function names and titles.
_SMRY_FUNCS = {"min"       : "the minimum value",
               "min_index" : "index of the minimum value",
               "max"       : "the maximum value",
               "max_index" : "index of the maximum value",
               "avg"       : "the average value",
               "med"       : "the median value",
               "std"       : "standard deviation",
               "N%"        : "N-th percentile, 0 < N < 100",
               "nzcnt"     : "datapoints with non-zero value"}


def get_smry_funcs():
    """
    Yields all the supported summary function names along with short description as a tuple.
    """

    for funcname, descr in _SMRY_FUNCS.items():
        yield funcname, descr

def _get_percentile(funcname):
    """
    Parses and validates the percentile statistics function name (e.g., "99%") and returns the
    percent value (99).
    """

    percent = Trivial.str_to_num(funcname[:-1])
    if percent <= 0 or percent >= 100:
        raise Error(f"bad percentile number in '{funcname}', should be in range of "
                    f"(0, 100)")
    return percent

def get_smry_func_descr(funcname):
    """Returns description for a summary function 'funcname'."""

    if funcname in _SMRY_FUNCS:
        return _SMRY_FUNCS[funcname]

    if "%" in funcname:
        percent = _get_percentile(funcname)
        return f"{percent}-th percentile"

    funcnames = ", ".join([fname for fname, _ in get_smry_funcs()])
    raise Error(f"unknown function name '{funcname}', supported names are:\n{funcnames}")

def calc_col_smry(df, colname, funcnames=None):
    """
    Calculate summary function 'funcname' for 'pandas.DataFrame' column 'colname' in
    'pandas.DataFrame' 'df' and return the resulting dictionary. Note, 'smry' comes from "summary".
    """

    fmap = {"min" : "idxmin", "min_index" : "idxmin", "max" : "idxmax", "max_index" : "idxmax",
            "avg" : "mean", "med" : "median", "std" : "std"}
    smry = {}

    if not funcnames:
        funcnames = get_smry_funcs()

    # Turn 'N%' into 99%, 99.9%, 99.99%, and 99.999%.
    fnames = []
    for fname in funcnames:
        if fname != "N%":
            fnames.append(fname)
        else:
            fnames += ["99%", "99.9%", "99.99%", "99.999%"]

    for funcname in fnames:
        # We do not need the description, calling this method just to let it validate the
        # function name.
        get_smry_func_descr(funcname)

        if funcname in fmap:
            # Other summaries can be handled in a generic way.
            datum = getattr(df[colname], fmap[funcname])()
        elif funcname == "nzcnt":
            datum = int((df[colname] != 0).sum())
        else:
            # Handle percentiles separately.
            percent = _get_percentile(funcname)
            datum = df[colname].quantile(percent / 100)

        if numpy.isnan(datum):
            return {}, None

        # Min/max are a bit special.
        if fmap.get(funcname, "").startswith("idx"):
            # Datum is the index, not the actual value.
            idx_funcname = f"{funcname[0:3]}_index"
            funcname = funcname[0:3]
            if "idx" not in funcname:
                # This makes sure that the order is the same as in 'funcnames'.
                smry[funcname] = None
            smry[idx_funcname] = datum
            datum = df[colname].loc[datum]

        smry[funcname] = datum
    return smry
