# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2020 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module provides API to the datapoints CSV file definitions (AKA 'defs').
"""

from pathlib import Path
from wultlibs.helperlibs.Exceptions import Error
from wultlibs.helperlibs import FSHelpers, YAML

# A unique object used as the default value for the 'default' keyword argument in various
# functions.
_RAISE = object()

def is_cscyc_colname(colname):
    """Returns 'True' if 'colname' is a C-state cycles count CSV column name."""

    return (colname.startswith("CC") or colname.startswith("DerivedCC") or \
            colname.startswith("PC")) and colname.endswith("Cyc") and len(colname) > 5

def is_csres_colname(colname):
    """Returns 'True' if 'colname' is a C-state residency CSV column name."""

    return (colname.startswith("CC") or colname.startswith("DerivedCC") or \
            colname.startswith("PC")) and colname.endswith("%") and len(colname) > 3

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
    elif colname.endswith("%"):
        csname = colname[:-1]

    if not csname or not (colname.startswith("CC") or colname.startswith("DerivedCC") or \
                          colname.startswith("PC")):
        if default is _RAISE:
            raise Error(f"cannot get C-state name for CSV column '{colname}'")
        return default

    return csname

def is_core_cs(csname):
    """
    If 'csname' is a core C-state name, returns 'True'. Returns 'False' otherwise (even if
    'csname' is not a valid C-state name).
    """

    return (csname.startswith("CC") or csname.startswith("DerivedCC")) and len(csname) > 2

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

def get_cs_colnames(colnames):
    """
    For every C-state cyscles column name in 'columns', yield a tuple of the following elements.
    * the C-state cycles column name.
    * the C-state residency column name corresponging to the found cycles column name.
    """

    for colname in colnames:
        if is_cscyc_colname(colname):
            csname = get_csname(colname)
            yield get_csres_colname(csname)

def get_cscyc_colnames(colnames):
    """Yield all C-state cycles column names found in 'colnames'."""

    for colname in colnames:
        if is_cscyc_colname(colname):
            yield colname

def get_csres_colnames(colnames):
    """Yield all C-state residency column names found in 'colnames'."""

    for colname in colnames:
        if is_csres_colname(colname):
            yield colname

class Defs:
    """This class provides API to the datapoints CSV file definitions (AKA 'defs')."""

    def get_cs_colnames(self):
        """Similar to the module-level 'get_cs_colnames()'."""

        for colname in get_cs_colnames(self.info):
            yield colname

    def get_cscyc_colnames(self):
        """Similar to the module-level 'get_cscyc_colnames()'."""

        for colnames in get_cscyc_colnames(self.info):
            yield colnames

    def get_csres_colnames(self):
        """Similar to the module-level 'get_csres_colnames()'."""

        for colnames in get_csres_colnames(self.info):
            yield colnames

    def populate_cstates(self, hdr):
        """
        The definitions YAML file does not contain information about C-states supported by various
        platforms. It only defines general core and package C-states ('CCx' and 'PCx'). Depending on
        the platform, there may be different amount of C-states with different names.

        This method should should be invoked to populate the definitions dictionary with the C-state
        information for a specific platform. The 'hdr' argument is the CSV file header containing
        the list of CSV column names.
        """

        if self.info is not self.vanilla_info:
            # Already populated.
            return

        # Copy all keys one-by-one to preserve the order.
        info = {}
        for colname, colinfo in self.vanilla_info.items():
            if not is_cs_colname(colname) or "Cx" not in colname:
                info[colname] = colinfo
                continue

            colcsname = get_csname(colname, default=None)
            is_core_colcsname = is_core_cs(colcsname)

            for hdrname in hdr:
                csname = get_csname(hdrname, default=None)
                if not csname:
                    continue
                if is_core_cs(csname) != is_core_colcsname:
                    continue

                if is_cscyc_colname(colname):
                    new_colname = get_cscyc_colname(csname)
                else:
                    new_colname = get_csres_colname(csname)

                info[new_colname] = colinfo.copy()

                # Correct title and description to refer to real C-state names.
                info[new_colname]["title"] = info[new_colname]["title"].replace(colcsname, csname)
                info[new_colname]["descr"] = info[new_colname]["descr"].replace(colcsname, csname)

        self.info = info

    def __init__(self, name):
        """
        The class constructor. The arguments are as follows.
          * name - name of the tool to load the definitions for (e.g., 'wult').
        """

        self.name = name
        self.info = None
        self.vanilla_info = None

        path = FSHelpers.find_app_data("wult", Path(f"defs/{name}.yml"),
                                       descr=f"{name} datapoints definitions file")
        self.info = self.vanilla_info = YAML.load(path)
