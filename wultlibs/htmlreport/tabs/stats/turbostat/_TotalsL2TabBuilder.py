# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""
This module provides the capability of populating the "Totals" turbostat level 2 tab.

Please, refer to '_TurbostatL2TabBuilderBase' for more information about level 2 tabs.
"""

import pandas
from wultlibs.htmlreport.tabs.stats.turbostat import _TurbostatL2TabBuilderBase

class TotalsL2TabBuilder(_TurbostatL2TabBuilderBase.TurbostatL2TabBuilderBase):
    """
    This class provides the capability of populating the "Totals" turbostat level 2 tab.
    """

    name = "Totals"

    def _turbostat_to_df(self, tstat, defs, path=None):
        """
        Convert the 'tstat' dictionary produced by 'TurbostatParser' to a 'pandas.DataFrame'. See
        base class '_TurbostatL2TabBuilderBase.TurbostatL2TabBuilderBase' for arguments.
        """

        _time_colname = "Time_Of_Day_Seconds"
        totals = tstat["totals"]

        # 'tstat_reduced' is a reduced version of the 'tstat' which contains only the columns we
        # want to include in the report. Initialise it by adding the timestamp column.
        tstat_reduced = {self._time_metric: [totals[_time_colname]]}

        for metric in defs.info:
            if metric == self._time_metric:
                continue
            if metric in totals:
                tstat_reduced[metric] = [totals[metric]]

        return pandas.DataFrame.from_dict(tstat_reduced)

    def __init__(self, stats_paths, outdir, basedir):
        """
        The class constructor. Adding a "totals" turbostat level 2 tab will create a "Totals"
        sub-directory and store data tabs inside it for metrics stored in the raw turbostat
        statistics file. The arguments are the same as in
        '_TurbostatL2TabBuilderBase.TurbostatL2TabBuilderBase'.
        """

        super().__init__(stats_paths, outdir / self.name, basedir)
