# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""
This module provides the capability of populating the "Measured CPU" turbostat level 2 tab.
"""

import pandas
from wultlibs.htmlreport.tabs.stats.turbostat import _TurbostatL2TabBuilderBase

class MCPUL2TabBuilder(_TurbostatL2TabBuilderBase.TurbostatL2TabBuilderBase):
    """
    This class provides the capability of populating the "Measured CPU" turbostat level 2 tab.

    See base class '_TurbostatL2TabBuilderBase.TurbostatL2TabBuilderBase' for public methods
    overview.
    """

    name = "MeasuredCPU"

    def _get_cpus_tstat(self, tstat):
        """
        Get a dictionary in the format {'cpu': 'tstat_subdict'}' from a 'TurbostatParser' dict
        'tstat' where 'tstat_subdict' is a sub-dictionary of 'tstat' but limited to only the
        turbostat statistics for that CPU.
        """

        cpus_tstat = {}

        # Only return Turbostat data for measured CPUs.
        cpus_to_keep = set(self._statdir_to_mcpu.values())

        # Traverse dictionary looking for measured CPUs.
        for package in tstat["packages"].values():
            for core in package["cores"].values():
                for cpunum, tstats in core["cpus"].items():
                    if cpunum in cpus_to_keep:
                        # Include the core totals as for metrics which are not available at the CPU
                        # level.
                        cpus_tstat[cpunum] = {**core["totals"], **tstats}

                    # If all measured CPUs have already been extracted then return.
                    if set(cpus_tstat.keys()) - cpus_to_keep == set():
                        return cpus_tstat

        return cpus_tstat

    def _turbostat_to_df(self, tstat, path):
        """Convert 'TurbostatParser' dict to 'pandas.DataFrame'."""

        _time_colname = "Time_Of_Day_Seconds"
        totals = tstat["totals"]
        cpu_tstat = self._get_cpus_tstat(tstat)
        mcpu = self._statdir_to_mcpu[path.parent]

        # 'tstat_reduced' is a reduced version of the 'TurbostatParser' dict which should contain
        # only the columns we want to include in the report. Initialise it by adding the timestamp
        # column.
        tstat_reduced = {self._time_metric: [totals[_time_colname]]}

        for metric, colname in self._metrics.items():
            if colname in totals:
                tstat_reduced[metric] = [cpu_tstat[mcpu][colname]]

        return pandas.DataFrame.from_dict(tstat_reduced)

    def __init__(self, stats_paths, outdir, basedir, measured_cpus):
        """
        The class constructor. Adding a "measured CPU" turbostat level 2 tab will create a
        "MeasuredCPU" sub-directory and store data tabs inside it for metrics stored in the raw
        turbostat statistics files for each measured CPU. The arguments are the same as in
        '_TurbostatL2TabBuilder.TurbostatL2TabBuilder' except for:
         * measured_cpus - dictionary in the format {'reportid': 'measured_cpu'} where
                           'measured_cpu' is the CPU that was being tested during the workload.
        """

        self._statdir_to_mcpu = {stats_paths[repid]: cpu for repid, cpu in measured_cpus.items()}

        super().__init__(stats_paths, outdir / self.name, basedir)
