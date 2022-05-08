# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""
This module provides the capability of populating the AC Power statistics tab.
"""

import pandas
from pepclibs.helperlibs.Exceptions import Error
from wultlibs.htmlreport.tabs import _DTabBuilder
from wultlibs.htmlreport.tabs.stats import _TabBuilderBase
from wultlibs import ACPowerDefs

class ACPowerTabBuilder(_TabBuilderBase.TabBuilderBase):
    """
    This class provides the capability of populating the AC Power statistics tab.

    Public methods overview:
    1. Generate a '_Tabs.DTabDC' instance containing a summary table and plots describing data in
       raw AC Power statistics files.
        * 'get_tab()'
    """

    name = "AC Power"

    def _read_stats_file(self, path):
        """
        Returns a 'pandas.DataFrame' containing the data stored in the raw AC Power statistics CSV
        file at 'path'.
        """

        sdf = pandas.DataFrame()

        try:
            # 'skipfooter' parameter only available with Python pandas engine.
            sdf = pandas.read_csv(path, skipfooter=1, engine="python")
        except pandas.errors.ParserError as err:
            raise Error(f"unable to parse CSV '{path}': {err}.") from None

        # Confirm that the time metric is in the CSV headers.
        if self._time_metric not in sdf:
            raise Error(f"column '{self._time_metric}' not found in statistics file '{path}'.")

        # Convert Time column from time since epoch to time since the first data point was recorded.
        sdf[self._time_metric] = sdf[self._time_metric] - sdf[self._time_metric][0]

        return sdf

    def get_tab(self):
        """
        Returns a '_Tabs.DTabDC' instance containing a summary table and plots describing data in
        raw AC Power statistics files.
        """

        dtab_bldr = _DTabBuilder.DTabBuilder(self._reports, self._outdir, self._basedir,
                                             self._defs.info[self._power_metric])
        scatter_axes = [(self._defs.info[self._time_metric], self._defs.info[self._power_metric])]
        dtab_bldr.add_plots(scatter_axes, [self._defs.info[self._power_metric]])
        dtab_bldr.add_smrytbl([self._defs.info[self._power_metric]])
        tab = dtab_bldr.get_tab()

        # By default the tab will be titled 'self._metric'. Change the title to "AC Power".
        tab.name = self.name
        return tab

    def __init__(self, stats_paths, outdir):
        """
        The class constructor. Adding an ACPower tab will create an 'ACPower' sub-directory and
        store plots and the summary table in it. The arguments are the same as in
        '_TabBuilderBase.TabBuilderBase'.
        """

        self._defs = ACPowerDefs.ACPowerDefs()

        self._power_metric = "P"
        self._time_metric = "T"

        super().__init__(stats_paths, outdir, ["acpower.raw.txt"])
