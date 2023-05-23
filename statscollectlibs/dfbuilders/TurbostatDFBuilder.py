# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""
This module provides the capability of building 'pandas.DataFrames' out of raw turbostat statistics
files.
"""

import pandas
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.dfbuilders import _DFBuilderBase
from statscollectlibs.parsers import TurbostatParser

class TurbostatDFBuilderBase(_DFBuilderBase.DFBuilderBase):
    """
    This class provides the capability of building a 'pandas.DataFrames' out of raw turbostat
    statistics files.
    """

    def _turbostat_to_df(self, tstat, path):
        """
        Convert the 'tstat' dictionary to a 'pandas.DataFrame'. Arguments are as follows:
         * tstat - dictionary produced by 'TurbostatParser'.
         * path - path of the original raw turbostat statistics file which was parsed to produce
                  'tstat'.
        """

        raise NotImplementedError()

    def _read_stats_file(self, path):
        """
        Returns a 'pandas.DataFrame' containing the data stored in the raw turbostat statistics file
        at 'path'.
        """

        try:
            tstat_gen = TurbostatParser.TurbostatParser(path).next()

            # Use the first turbostat snapshot to see which hardware and requestable C-states the
            # platform under test has.
            tstat = next(tstat_gen)

            # Initialise the stats 'pandas.DataFrame' ('sdf') with data from the first 'tstat'
            # dictionary.
            sdf = self._turbostat_to_df(tstat, path)

            # Add the rest of the data from the raw turbostat statistics file to 'sdf'.
            for tstat in tstat_gen:
                df = self._turbostat_to_df(tstat, path)
                sdf = pandas.concat([sdf, df], ignore_index=True)
        except Exception as err:
            msg = Error(err).indent(2)
            raise Error(f"error reading raw statistics file '{path}':\n{msg}.") from None

        # Confirm that the time column is in the 'pandas.DataFrame'.
        if self._time_metric not in sdf:
            raise Error(f"timestamps could not be parsed in raw statistics file '{path}'.")

        # Convert 'Time' column from time since epoch to time since first data point was recorded.
        sdf[self._time_metric] = sdf[self._time_metric] - sdf[self._time_metric][0]

        return sdf

    def __init__(self):
        """
        The class constructor.

        Note, the constructor does not load the potentially huge test result data into the memory.
        The data are loaded "on-demand" by 'load_df()'.
        """

        self._time_metric = "Time"

        super().__init__()

class MCPUDFBuilder(TurbostatDFBuilderBase):
    """
    This class provides the capability of building a 'pandas.DataFrames' out of raw turbostat
    statistics files for a specific CPU.
    """

    def _get_cpus_tstat(self, tstat):
        """
        Get a dictionary in the format {'cpu': 'tstat_subdict'}' from the 'tstat' dictionary
        produced by 'TurbostatParser', where 'tstat_subdict' is a sub-dictionary of 'tstat' limited
        to turbostat statistics only for the 'cpu' CPU.
        """

        cpus_tstat = {}

        # Only return turbostat data for measured CPUs.

        # Traverse dictionary looking for measured CPUs.
        for package in tstat["packages"].values():
            for core in package["cores"].values():
                if self._mcpu not in core["cpus"]:
                    continue

                tstats = core["cpus"][self._mcpu]

                # Include the package and core totals as for metrics which are not available at the
                # CPU level.
                cpus_tstat[self._mcpu] = {**package["totals"], **core["totals"], **tstats}

                return cpus_tstat

        raise Error(f"not data for measured cpu '{self._mcpu}'")

    def _turbostat_to_df(self, tstat, path):
        """
        Convert the 'tstat' dictionary produced by 'TurbostatParser' to a 'pandas.DataFrame'. See
        base class '_TurbostatL2TabBuilderBase.TurbostatL2TabBuilderBase' for arguments.
        """

        _time_colname = "Time_Of_Day_Seconds"
        totals = tstat["totals"]
        cpu_tstat = self._get_cpus_tstat(tstat)

        # 'tstat_reduced' is a reduced version of the 'tstat' which contains only the columns we
        # want to include in the report. Initialize it by adding the timestamp column.
        tstat_reduced = {self._time_metric: [totals[_time_colname]]}

        for metric in totals:
            if metric == self._time_metric:
                continue

            try:
                tstat_reduced[metric] = [cpu_tstat[self._mcpu][metric]]
            except KeyError:
                raise Error(f"no value available for metric '{metric}' for cpu "
                            f"'{self._mcpu}'.") from None

        return pandas.DataFrame.from_dict(tstat_reduced)

    def __init__(self, mcpu):
        """
        The class constructor. Arguments are as follows:
         * mcpu - the name of the measured CPU for which data should be extracted from the raw
                  turbostat statistics file.
        """

        self._mcpu = mcpu
        super().__init__()

class TotalsDFBuilder(TurbostatDFBuilderBase):
    """
    This class provides the capability of building a 'pandas.DataFrames' out of raw turbostat
    statistics files. Specifically, this class will aggregate the data for all CPUs into the
    'pandas.DataFrame'.
    """

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

        for metric in totals:
            if metric == self._time_metric:
                continue

            tstat_reduced[metric] = [totals[metric]]

        return pandas.DataFrame.from_dict(tstat_reduced)
