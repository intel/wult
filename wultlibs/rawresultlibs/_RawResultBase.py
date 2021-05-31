# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2020 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module contains the base class for the read-only and write-only raw test result classes.

A raw test result is a directory containing the following files.
 * datapoints.csv - a CSV file named 'datapoints.csv' which keeps all the datapoints (one datapoint
                    per row). This file may be very large.
 * info.yml - a YAML file containing miscellaneous test information, such as the report ID.
 * logs - optional directory containing wult run logs.
 * stats - optional directory containing various statistics, such as 'lscpu'.
 * description.txt - optional file containing free-form descritpion of this test result.
"""

from pathlib import Path
from wultlibs.helperlibs.Exceptions import Error

# The latest supported raw results format version.
FORMAT_VERSION = "1.1"

class RawResultBase:
    """
    Base class for read-only and write-only test result classes, contains the common bits.
    """

    def clear_filts(self):
        """Clear all the filters and selectors for both rows and columns."""

        self._rfilt = None
        self._cfilt = None
        self._rsel = None
        self._csel = None

    def _get_rsel(self):
        """Merge row filter and selector and return the result."""

        expr = None

        if self._rsel:
            if self._rfilt:
                expr = f"({self._rsel}) and not ({self._rfilt})"
            else:
                expr = self._rsel
        else:
            if self._rfilt:
                expr = f"not ({self._rfilt})"
            else:
                expr = None

        return expr

    def _get_csel(self, colnames):
        """
        Merge column filter and selector and apply it to the list of column names in 'colnames'.
        Return list of filtered column names.
        """

        if not self._csel and not self._cfilt:
            return None

        csel = self._csel
        if self._csel is None:
            csel = colnames

        cfilt = self._cfilt
        if self._cfilt is None:
            cfilt = []

        result = []
        cfilt_set = set(cfilt)
        for colname in csel:
            if colname not in cfilt_set:
                result.append(colname)

        return result

    def __init__(self, dirpath):
        """The class constructor. The 'dirpath' argument is path raw test result directory."""

        self.reportid = None
        # This dictionary represents the info file.
        self.info = {}

        # The row and column filters and selectors.
        self._rfilt = None
        self._cfilt = None
        self._rsel = None
        self._csel = None

        if not dirpath:
            raise Error("raw test results directory path was not specified")

        self.dirpath = Path(dirpath)

        if self.dirpath.exists() and not self.dirpath.is_dir():
            raise Error(f"path '{self.dirpath}' is not a directory")

        self.dp_path = self.dirpath.joinpath("datapoints.csv")
        self.info_path = self.dirpath.joinpath("info.yml")
        self.logs_path = self.dirpath.joinpath("logs")
        self.stats_path = self.dirpath.joinpath("stats")
        self.descr_path = self.dirpath.joinpath("description.txt")

        for name in ("dp_path", "info_path", "descr_path"):
            path = getattr(self, name)
            if path.exists() and not path.is_file():
                raise Error(f"path '{path}' exists, but it is not a regular file")

        for name in ("logs_path", "stats_path"):
            path = getattr(self, name)
            if path.exists() and not path.is_dir():
                raise Error(f"path '{path}' exists, but it is not a directory")
