# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module provides the base class for APIs to the datapoints CSV file definitions (AKA 'defs').
"""

from pathlib import Path
from pepclibs.helperlibs import YAML
from wultlibs import Deploy


class DefsBase:
    """
    This base class can be inherited from to provide an API to the datapoints CSV file definitions
    (AKA 'defs').

    This base class requires child classes to implement the following methods:
    1. Return 'True' if a given 'colname' is a C-state residency CSV column name.
       * 'is_cs_colname()'
    2. Return the C-state name string for the C-state represented in 'colname'.
       * 'get_csname()'
    3. Return a new version of column 'colname' for the C-state 'csname'.
       * 'get_new_colname()'

    Optionally child classes can override the '_mangle()' method which mangles the initially loaded
    dictionary to provide more helpful fields.
    """

    def is_cs_colname(self, colname):
        """Returns 'True' if 'colname' is a C-state residency CSV column name."""

        raise NotImplementedError()

    def get_csname(self, colname):
        """Returns the C-state name string for the C-state represented in 'colname'."""

        raise NotImplementedError()

    def get_new_colname(self, colname, csname):
        """Returns a new version of column 'colname' for the C-state 'csname'."""

        raise NotImplementedError()

    @staticmethod
    def _mangle(info):
        """This function mangles the initially loaded dictionary and adds useful fields there."""

        for key, val in info.items():
            val["metric"] = key

        return info

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

        # Filter hdr to only C-state columns.
        hdr = [hdrname for hdrname in hdr if self.is_cs_colname(hdrname)]

        # Copy all keys one-by-one to preserve the order.
        info = {}
        for colname, colinfo in self.vanilla_info.items():
            if not self.is_cs_colname(colname) or "Cx" not in colname:
                info[colname] = colinfo
                continue

            colcsname = self.get_csname(colname)

            for hdrname in hdr:
                csname = self.get_csname(hdrname)
                new_colname = self.get_new_colname(colname, csname)

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
        self.path = Deploy.find_app_data("wult", Path(f"defs/{name}.yml"), appname=name,
                                         descr=f"{name} datapoints definitions file")
        self.info = self.vanilla_info = self._mangle(YAML.load(self.path))
