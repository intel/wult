# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""
This module provides the capability of populating the turbostat statistics tab.
"""

import pandas
from pepclibs.helperlibs.Exceptions import Error
from wultlibs.htmlreport.tabs.stats import _TabBuilderBase, _DTabBuilder
from wultlibs.htmlreport.tabs import _Tabs
from wultlibs.parsers import TurbostatParser
from wultlibs import MetricDefs

class TurbostatTabBuilder(_TabBuilderBase.TabBuilderBase):
    """
    This class provides the capability of populating the turbostat statistics tab.

    Public methods overview:
    1. Generate a '_Tabs.CTabDC' instance containing sub-tabs which represent different turbostat
       metrics.
       * 'get_tab_group()'
    """

    name = "Turbostat"

    def _turbostat_to_df(self, tstat):
        """Convert 'TurbostatParser' dict to 'pandas.DataFrame'."""

        _time_colname = "Time_Of_Day_Seconds"
        totals = tstat["totals"]

        # 'tstat_reduced' is a reduced version of the 'TurbostatParser' dict which should contain
        # only the columns we want to include in the report. Initialise it by adding the timestamp
        # column.
        tstat_reduced = {self._time_metric: [totals[_time_colname]]}

        for metric, colname in self._metrics.items():
            if colname in totals:
                tstat_reduced[metric] = [totals[colname]]

        return pandas.DataFrame.from_dict(tstat_reduced)

    def _read_stats_file(self, path):
        """
        Returns a 'pandas.DataFrame' containing the data stored in the raw turbostat statistics file
        at 'path'.
        """

        sdf = pandas.DataFrame()

        try:
            tstat_gen = TurbostatParser.TurbostatParser(path)

            for tstat in tstat_gen.next():
                df = self._turbostat_to_df(tstat)
                sdf = pandas.concat([sdf, df], ignore_index=True)
        except Exception as err:
            raise Error(f"error reading raw statistics file '{path}': {err}.") from None

        # Confirm that the time column is in the 'pandas.DataFrame'.
        if self._time_metric not in sdf:
            raise Error(f"timestamps could not be parsed in raw statistics file '{path}'.")

        # Convert 'Time' column from time since epoch to time since first data point was recorded.
        sdf[self._time_metric] = sdf[self._time_metric] - sdf[self._time_metric][0]

        return sdf

    def get_tab(self):
        """
        Returns a '_Tabs.CTabDC' instance containing turbostat sub-tabs which are tabs for metrics
        within the turbostat raw stastics file.
        """

        defs = MetricDefs.MetricDefs("turbostat")
        totals_tabs = []
        for metric in self._metrics:
            mdefs = defs.info[metric]
            dtab = _DTabBuilder.DTabBuilder(self._reports, self.outdir / mdefs["fsname"],
                                            self.outdir, mdefs, defs.info[self._time_metric])
            totals_tabs.append(dtab.get_tab())
        totals_ctab = _Tabs.CTabDC("Totals", totals_tabs)

        return _Tabs.CTabDC(self.name, [totals_ctab])


    def __init__(self, stats_paths, outdir):
        """
        The class constructor. Adding a turbostat statistics group tab will create a 'Turbostat'
        sub-directory and store sub-tabs inside it.  Sub-tabs will represent metrics stored in the
        raw turbostat statistics file. The arguments are the same as in
        '_StatsTabGroup.StatsTabGroupBuilder'.
        """

        self._time_metric = "Time"
        self.outdir = outdir

        # Dictionary in the format {'metric': 'colname'} where 'colname' in the raw turbostat
        # statistics file represents 'metric'.
        self._metrics = {
            "CC0%": "Busy%"
        }

        super().__init__(stats_paths, outdir, ["turbostat.raw.txt"])
