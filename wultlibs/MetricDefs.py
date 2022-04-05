# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module provides API to the datapoints CSV file definitions (AKA 'defs').
"""

from pepclibs.helperlibs.Exceptions import Error
from wultlibs import DefsBase

# A unique object used as the default value for the 'default' keyword argument in various
# functions.
_RAISE = object()

def is_cscyc_colname(colname):
    """Returns 'True' if 'colname' is a C-state cycles count CSV column name."""

    return (colname.startswith("CC") or colname.startswith("PC")) and \
            colname.endswith("Cyc") and len(colname) > 5

def is_csres_colname(colname):
    """Returns 'True' if 'colname' is a C-state residency CSV column name."""

    return (colname.startswith("CC") or colname.startswith("PC")) and \
            colname.endswith("%") and len(colname) > 3

def is_cs_colname(colname):
    """Returns 'True' if 'colname' is a C-state residency or cycles counter CSV column name."""

    return is_csres_colname(colname) or is_cscyc_colname(colname)

def get_csname(colname, default=_RAISE):
    """
    If 'colname' is a CSV column name related to a C-state, then returns the C-state name
    string. Otherwise raises an exception, unless the 'default' argument is passed, in which
    case it returns this argument instead of raising an exception.
    """

    csname = None
    if colname.endswith("Cyc"):
        csname = colname[:-3]
        if csname.endswith("Derived"):
            csname = csname[:-len("Derived")]
    elif colname.endswith("%"):
        csname = colname[:-1]

    if not csname or not (colname.startswith("CC") or colname.startswith("PC")):
        if default is _RAISE:
            raise Error(f"cannot get C-state name for CSV column '{colname}'")
        return default

    return csname

def is_core_cs(csname):
    """
    If 'csname' is a core C-state name, returns 'True'. Returns 'False' otherwise (even if
    'csname' is not a valid C-state name).
    """

    return csname.startswith("CC") and len(csname) > 2

def is_package_cs(csname):
    """
    If 'csname' is a package C-state name, returns 'True'. Returns 'False' otherwise (even if
    'csname' is not a valid C-state name).
    """

    return csname.startswith("PC") and len(csname) > 2

def get_cscyc_colname(csname):
    """
    Given 'csname' is a C-state name, this method retruns the corresponding C-state cycles count
    CSV column name.
    """

    return f"{csname}Cyc"

def get_csres_colname(csname):
    """
    Given 'csname' is a C-state name, this method retruns the corresponding C-state residency
    CSV column name.
    """

    return f"{csname}%"

class MetricDefs(DefsBase.DefsBase):
    """This class provides API to the datapoints CSV file definitions (AKA 'defs')."""

    def get_csname(self, colname):
        """Returns the C-state name string for the C-state represented in 'colname'."""

        return get_csname(colname)

    def get_new_colname(self, colname, csname):
        """Returns a new version of column 'colname' for the C-state 'csname'."""

        if is_cscyc_colname(colname):
            return get_cscyc_colname(csname)

        return get_csres_colname(csname)

    def is_cs_colname(self, colname):
        """Returns 'True' if 'colname' is a C-state residency CSV column name."""

        return is_cs_colname(colname)
