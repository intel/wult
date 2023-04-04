# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""
This module provides the capability of populating the "Measured CPU" turbostat level 2 tab.

Please, refer to '_TurbostatL2TabBuilderBase' for more information about level 2 tabs.
"""

import pandas
from statscollectlibs.htmlreport.tabs.turbostat import _TurbostatL2TabBuilderBase

class MCPUL2TabBuilder(_TurbostatL2TabBuilderBase.TurbostatL2TabBuilderBase):
    """
    This class provides the capability of populating the "Measured CPU" turbostat level 2 tab.
    """

    name = "Measured CPU"

    def _get_cpus_tstat(self, tstat):
        """
        Get a dictionary in the format {'cpu': 'tstat_subdict'}' from the 'tstat' dictionary
        produced by 'TurbostatParser', where 'tstat_subdict' is a sub-dictionary of 'tstat' limited
        to turbostat statistics only for the 'cpu' CPU.
        """

        cpus_tstat = {}

        # Only return turbostat data for measured CPUs.
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
                    if cpus_to_keep - set(cpus_tstat.keys()) == set():
                        return cpus_tstat

        return cpus_tstat

    def _turbostat_to_df(self, tstat, path):
        """
        Convert the 'tstat' dictionary produced by 'TurbostatParser' to a 'pandas.DataFrame'. See
        base class '_TurbostatL2TabBuilderBase.TurbostatL2TabBuilderBase' for arguments.
        """

        _time_colname = "Time_Of_Day_Seconds"
        totals = tstat["totals"]
        cpu_tstat = self._get_cpus_tstat(tstat)
        mcpu = self._statdir_to_mcpu[path.parent]

        # 'tstat_reduced' is a reduced version of the 'tstat' which contains only the columns we
        # want to include in the report. Initialize it by adding the timestamp column.
        tstat_reduced = {self._time_metric: [totals[_time_colname]]}

        for metric in self._defs.info:
            if metric == self._time_metric:
                continue

            if metric in totals:
                tstat_reduced[metric] = [cpu_tstat[mcpu][metric]]

        return pandas.DataFrame.from_dict(tstat_reduced)

    def __init__(self, rsts, outdir, basedir):
        """
        The class constructor. Adding a "measured CPU" turbostat level 2 tab will create a
        "MeasuredCPU" sub-directory and store data tabs inside it for metrics stored in the raw
        turbostat statistics files for each measured CPU. The arguments are the same as in
        '_TurbostatL2TabBuilder.TurbostatL2TabBuilder'.
        """

        self._statdir_to_mcpu = {}
        for res in rsts:
            if "cpunum" in res.info:
                self._statdir_to_mcpu[res.stats_path] = str(res.info["cpunum"])

        super().__init__(rsts, outdir / self.name, basedir)
