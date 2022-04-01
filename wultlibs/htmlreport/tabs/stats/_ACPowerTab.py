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
from wultlibs.htmlreport.tabs.stats import _StatsTabBuilderBase
from wultlibs import Defs


class ACPowerTabBuilder(_StatsTabBuilderBase.StatsTabBuilderBase):
    """
    This class provides the capability of populating the AC Power statistics tab.

    Public methods overview:
    1. Generate a '_Tabs.DataTabDC' instance containing a summary table and plots describing data in
       raw AC Power statistics files.
        * 'get_tab()'
    """
    # File system-friendly tab name.
    name = "ACPower"

    def _read_stats_file(self, path):
        """
        Returns a pandas DataFrame containing the data stored in the raw AC Power statistics CSV
        file at 'path'.
        """

        time_colname = "T"
        metric_colname = "P"

        sdf = pandas.DataFrame()

        try:
            # 'skipfooter' parameter only available with Python pandas engine.
            sdf = pandas.read_csv(path, skipfooter=1, engine="python")
        except pandas.errors.ParserError as err:
            raise Error(f"unable to parse CSV '{path}': {err}.") from None

        # Confirm that the time column name is in the CSV headers.
        if time_colname not in sdf:
            raise Error(f"column '{time_colname}' not found in statistics file '{path}'.")

        # Convert Time column from time since epoch to time since the first data point was recorded.
        sdf[time_colname] = sdf[time_colname] - sdf[time_colname][0]

        metrics = {
            metric_colname: self._metric,
            time_colname: self._time_metric
        }
        sdf.rename(columns=metrics, inplace=True)

        return sdf

    def get_tab(self):
        """
        Returns a '_Tabs.DataTabDC' instance containing a summary table and plots describing data in
        raw AC Power statistics files.
        """

        defs = Defs.Defs("acpower").info
        return super()._get_tab_group([defs["ACPower"]], defs["Time"] ).tabs[0]

    def __init__(self, stats_paths, outdir):
        """
        The class constructor. Adding an ACPower tab will create an 'ACPower' sub-directory and
        store plots and the summary table in it. The arguments are the same as in
        '_StatsTabContainer.StatsTabContainerBuilderBase'.
        """

        self._metric = "ACPower"
        self._time_metric = "Time"

        super().__init__(stats_paths, outdir, ["acpower.raw.txt"])
