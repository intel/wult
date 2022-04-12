# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""
This module contains the base class for turbostat level 2 tab builder classes.
"""

import pandas
from pepclibs.helperlibs.Exceptions import Error
from wultlibs.htmlreport.tabs.stats import _TabBuilderBase, _DTabBuilder
from wultlibs.htmlreport.tabs import _Tabs
from wultlibs.parsers import TurbostatParser
from wultlibs import MetricDefs

class TurbostatL2TabBuilderBase(_TabBuilderBase.TabBuilderBase):
    """
    The base class for turbostat level 2 tab builder classes.

    'level 2 turbostat tabs' refer to tabs in the second level of tabs in the turbostat tab
    hierarchy. For each level 2 turbostat tab, we parse raw turbostat statistics files differently.
    Therefore this base class expects child classes to implement '_turbostat_to_df()'.

    Public methods overview:
    1. Generate a '_Tabs.CTabDC' instance containing data tabs which represent different turbostat
       metrics.
       * 'get_tab()'

    This base class requires child classes to implement the following methods:
    1. Convert a 'TurbostatParser' dict to 'pandas.DataFrame'.
       * '_turbostat_to_df()'
    """

    def _turbostat_to_df(self, tstat, path):
        """Convert 'TurbostatParser' dict to 'pandas.DataFrame'."""

        raise NotImplementedError()

    def _read_stats_file(self, path):
        """
        Returns a 'pandas.DataFrame' containing the data stored in the raw turbostat statistics file
        at 'path'.
        """

        sdf = pandas.DataFrame()

        try:
            tstat_gen = TurbostatParser.TurbostatParser(path)

            for tstat in tstat_gen.next():
                df = self._turbostat_to_df(tstat, path)
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
        Returns a '_Tabs.CTabDC' instance containing tabs which represent different metrics within
        the turbostat raw stastics file.
        """

        defs = MetricDefs.MetricDefs("turbostat")
        child_tabs = []
        for metric in self._metrics:
            mdefs = defs.info[metric]
            dtab = _DTabBuilder.DTabBuilder(self._reports, self.outdir / mdefs["fsname"],
                                            self._basedir, mdefs, defs.info[self._time_metric])
            child_tabs.append(dtab.get_tab())

        return _Tabs.CTabDC(self.name, child_tabs)


    def __init__(self, stats_paths, outdir, basedir):
        """
        The class constructor. Adding a turbostat level 2 tab will create a sub-directory and store
        data tabs inside it for metrics stored in the raw turbostat statistics file.  The arguments
        are the same as in '_TabBuilderBase.TabBuilderBase' except for:
         * basedir - base directory of the report. All asset paths will be made relative to this.
        """

        self._time_metric = "Time"
        self.outdir = outdir

        # Dictionary in the format {'metric': 'colname'} where 'colname' in the raw turbostat
        # statistics file represents 'metric'.
        self._metrics = {
            "CC0%": "Busy%"
        }

        super().__init__(stats_paths, outdir, ["turbostat.raw.txt"])
        self._basedir = basedir
