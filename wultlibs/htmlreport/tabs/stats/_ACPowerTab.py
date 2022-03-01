# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""
This module provides the capability of populating the AC Power statistics Tab.
"""

import pandas

from pepclibs.helperlibs.Exceptions import Error
from wultlibs.htmlreport.tabs.stats import _StatsTabGroup


class ACPowerTabBuilder(_StatsTabGroup.StatsTabGroupBuilder):
    """
    This class provides the capability of populating the AC Power statistics tab.

    Public methods overview:
    1. Generate a 'StatsTabGroup' instance containing sub-tabs which represent ACPower statistics
       contained within the group.
       * 'get_tab_group()'
    """
    # File system-friendly tab name.
    name = "ACPower"

    def _read_stats_file(self, path):
        """
        Returns a pandas DataFrame containing the data stored in the raw AC Power statistics CSV
        file at 'path'.
        """

        sdf = pandas.DataFrame()

        try:
            # 'skipfooter' parameter only available with Python pandas engine.
            sdf = pandas.read_csv(path, skipfooter=1, engine="python")
        except pandas.errors.ParserError as err:
            raise Error(f"unable to parse CSV '{path}': {err}.") from None

        # Confirm that the time column name is in the CSV headers.
        if self._time_colname not in sdf:
            raise Error(f"column '{self._time_colname}' not found in statistics file '{path}'.")

        # Convert Time column from time since epoch to time since the first data point was recorded.
        sdf[self._time_colname] = sdf[self._time_colname] - sdf[self._time_colname][0]

        return sdf

    def get_tab_group(self):
        """
        Returns a 'StatsTabGroup' instance containing AC Power sub-tabs which are tabs for metrics
        within the ACPower raw stastics file.
        """

        # This dictionary tells the parent class which metric is represented by which column in the
        # statistics dataframes.
        metrics = {
            "ACPower": "P",
        }
        return super()._get_tab_group(metrics, self._time_colname).tabs[0]

    def __init__(self, stats_paths, outdir, bmname):
        """
        The class constructor. Adding an ACPower tab will create an 'ACPower' sub-directory and
        store plots and the summary table in it. The arguments are the same as in
        '_StatsTabGroup.StatsTabGroupBuilder'.
        """

        self._time_colname = "T"

        super().__init__(stats_paths, outdir, bmname, "defs/acpower.yml", ["acpower.raw.txt"])
