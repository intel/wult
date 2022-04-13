# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""
This module provides the capability of populating the "Totals" turbostat level 2 tab.
"""

import pandas
from wultlibs.htmlreport.tabs.stats.turbostat import _TurbostatL2TabBuilderBase

class TotalsL2TabBuilder(_TurbostatL2TabBuilderBase.TurbostatL2TabBuilderBase):
    """
    This class provides the capability of populating the "Totals" turbostat level 2 tab.

    See base class '_TurbostatL2TabBuilderBase.TurbostatL2TabBuilderBase' for public methods
    overview.
    """

    name = "Totals"

    def _turbostat_to_df(self, tstat, path=None):
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

    def __init__(self, stats_paths, outdir, basedir):
        """
        The class constructor. Adding a "totals" turbostat level 2 tab will create a "Totals"
        sub-directory and store data tabs inside it for metrics stored in the raw turbostat
        statistics file. The arguments are the same as in
        '_TurbostatL2TabBuilderBase.TurbostatL2TabBuilderBase'.
        """

        super().__init__(stats_paths, outdir / self.name, basedir)
