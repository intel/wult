# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2022 Intel Corporation
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
"""

from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.rawresultlibs import _RawResultBase

# The latest supported raw results format version.
FORMAT_VERSION = "1.2"

class RawResultBase(_RawResultBase.RawResultBase):
    """
    Base class for read-only and write-only test result classes, contains the common bits.
    """

    def clear_filts(self):
        """Clear all the filters and selectors for both rows and columns."""

        self._exclude = None
        self._mexclude = None
        self._include = None
        self._minclude = None

    def _get_dp_filter(self):
        """
        Get the datapoint filter expression by merging the expressions in 'self._include' and
        'self._exclude'.
        """

        expr = None

        if self._include:
            if self._exclude:
                expr = f"({self._include}) and not ({self._exclude})"
            else:
                expr = self._include
        else:
            if self._exclude:
                expr = f"not ({self._exclude})"
            else:
                expr = None

        return expr

    def _get_filtered_metrics(self, metrics):
        """
        Return the list of metrics to include in the report. Filter the list of metrics 'metrics' by
        merging and applying the metric filter expressions 'self._minclude' and 'self._mexclude'.
        """

        if not self._minclude and not self._mexclude:
            return None

        minclude = self._minclude
        if self._minclude is None:
            minclude = metrics

        mexclude = self._mexclude
        if self._mexclude is None:
            mexclude = []

        result = []
        mexclude_set = set(mexclude)
        for metric in minclude:
            if metric not in mexclude_set:
                result.append(metric)

        return result

    def __init__(self, dirpath):
        """The class constructor. The 'dirpath' argument is path raw test result directory."""

        super().__init__(dirpath)

        # The datapoint and metric filters.
        self._exclude = None
        self._mexclude = None
        self._include = None
        self._minclude = None

        self.dp_path = self.dirpath.joinpath("datapoints.csv")

        if self.dp_path.exists() and not self.dp_path.is_file():
            raise Error(f"path '{self.dp_path}' exists, but it is not a regular file")
