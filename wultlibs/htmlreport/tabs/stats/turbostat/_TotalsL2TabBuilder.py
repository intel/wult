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

    def _get_tab_hierarchy(self, common_metrics):
        """
        Extends '_get_tab_hierarchy()' from the parent class to add tabs specifically for this
        level 2 turbostat tab as they are not added by 'super()._get_tab_hierarchy()'. Arguments are
        the same as 'super()._get_tab_hierarchy()'.
        """

        harchy = super()._get_tab_hierarchy(common_metrics)

        # Add extra metrics to the metrics in 'harchy' if they are common to all results.
        extra_dtabs = ["PkgWatt", "GFXWatt", "PkgTmp"]
        harchy["Temperature / Power"]["dtabs"] += [m for m in extra_dtabs if m in common_metrics]

        # Add uncore frequency D-tab to the "Frequency" C-tab.
        unc_metric = "UncMHz"
        if unc_metric in common_metrics:
            harchy["Frequency"]["dtabs"].append(unc_metric)

        # Add package C-states.
        hw_pkg_cs = self._get_common_elements(self._cstates["hardware"]["package"])
        for cs in hw_pkg_cs:
            harchy["C-states"]["Hardware"]["dtabs"].append(f"Pkg%p{cs.lower()}")

        return harchy

    def _turbostat_to_df(self, tstat, path=None):
        """
        Convert the 'tstat' dictionary produced by 'TurbostatParser' to a 'pandas.DataFrame'. See
        base class '_TurbostatL2TabBuilderBase.TurbostatL2TabBuilderBase' for arguments.
        """

        _time_colname = "Time_Of_Day_Seconds"
        totals = tstat["totals"]

        # 'tstat_reduced' is a reduced version of the 'tstat' which contains only the columns we
        # want to include in the report. Initialise it by adding the timestamp column.
        tstat_reduced = {self._time_metric: [totals[_time_colname]]}

        for metric in self._defs.info:
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
