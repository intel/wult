# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""
This module provides the capability of populating the IPMI statistics Tab.
"""

import numpy
import pandas

from pepclibs.helperlibs.Exceptions import Error
from wultlibs import _DefsBase, IPMIDefs
from wultlibs.parsers import IPMIParser
from wultlibs.htmlreport.tabs.stats import _DTabBuilder, _TabBuilderBase
from wultlibs.htmlreport.tabs import _Tabs


class IPMITabBuilder(_TabBuilderBase.TabBuilderBase):
    """
    This class provides the capability of populating the IPMI statistics tab.

    Public methods overview:
    1. Generate a '_Tabs.CTabDC' instance containing tabs which display IPMI statistics.
       * 'get_tab()'
    """

    name = "IPMI"

    def get_tab(self):
        """
        Generate a '_Tabs.CTabDC' instance containing tabs which display IPMI statistics. The
        container tab will contain another container tab for each of the following categories:

            1. "Fan Speed"
            2. "Temperature"
            3. "Power"

        Each of these container tabs contain data tabs for each IPMI metric which is common to all
        results. For example, the "Fan Speed" container tab might contain several data tabs titled
        "Fan1", "Fan2" etc. if each raw IPMI statistics file contains these measurements. If there
        were no common IPMI metrics between all of the results for a given category, the container
        tab will not be generated.
        """

        col_sets = [set(sdf.columns) for sdf in self._reports.values()]
        common_cols = set.intersection(*col_sets)

        metric_ctabs = []
        for metric, colnames in self._metrics.items():
            coltabs = []
            mtab_outdir = self._outdir / metric
            for col in colnames:
                if col not in common_cols:
                    continue

                # Since we use column names which aren't known until runtime as tab titles, use the
                # defs for the metric but overwrite the 'title', 'metric' and 'fsname' attributes.
                # Use 'copy' so that 'defs.info' can be used to create the container tab.
                col_def = self._defs.info[metric].copy()
                col_def["title"] = col
                col_def["fsname"] = _DefsBase.get_fsname(col)
                col_def["metric"] = col

                coltab = _DTabBuilder.DTabBuilder(self._reports, mtab_outdir, self._basedir,
                                                  col_def, self._defs.info[self._time_metric])
                scatter_axes = [(self._defs.info[self._time_metric], col_def)]
                coltab.add_plots(scatter_axes, [col_def])
                coltabs.append(coltab.get_tab())

            # Only add a container tab for 'metric' if any data tabs were generated to populate it.
            if coltabs:
                metric_ctabs.append(_Tabs.CTabDC(self._defs.info[metric]["title"], coltabs))

        if not metric_ctabs:
            raise Error(f"no common {self.name} metrics between reports.")

        return _Tabs.CTabDC(self.name, metric_ctabs)

    def _categorise_cols(self, ipmi):
        """
        Associates column names in the IPMIParser dict 'ipmi' to the metrics they represent. For
        example, 'FanSpeed' can be represented by several columns such as 'Fan1', 'Fan Speed' etc.
        This function will add those column names to the 'FanSpeed' metric.
        """

        for colname, val in ipmi.items():
            unit = val[1]
            metric = self._defs.get_metric_from_unit(unit)
            if metric:
                self._metrics[metric].add(colname)

    def _read_stats_file(self, path):
        """
        Returns a 'pandas.DataFrame' containing the data stored in the raw IPMI statistics file at
        'path'.
        """

        time_colname = "timestamp"

        def _ipmi_to_df(ipmi):
            """Convert IPMIParser dict to 'pandas.DataFrame'."""

            # Reduce IPMI values from ('value', 'unit') to just 'value'.
            # If "no reading" is parsed in a line of a raw IPMI file, 'None' is returned. In this
            # case, we should exclude that IPMI metric.
            i = {k:[v[0]] for k, v in ipmi.items() if v[0] is not None}
            return pandas.DataFrame.from_dict(i)

        ipmi_gen = IPMIParser.IPMIParser(path).next()

        try:
            # Try to read the first data point from raw statistics file.
            i = next(ipmi_gen)
        except StopIteration:
            raise Error(f"empty or incorrectly formatted {self.name} raw statistics file at "
                        f"'{path}'.") from None

        # Populate 'self._metrics' using the columns from the first data point.
        self._categorise_cols(i)
        sdf = _ipmi_to_df(i)

        for i in ipmi_gen:
            df = _ipmi_to_df(i)
            # Append dataset for a single timestamp to the main 'pandas.DataFrame'.
            sdf = pandas.concat([sdf, df], ignore_index=True)

        # Confirm that the time column is in the 'pandas.DataFrame'.
        if time_colname not in sdf:
            raise Error(f"column '{time_colname}' not found in statistics file '{path}'.")

        # Convert Time column from time stamp to time since the first data point was recorded.
        sdf[time_colname] = sdf[time_colname] - sdf[time_colname][0]
        sdf[time_colname] = sdf[time_colname] / numpy.timedelta64(1, "s")

        sdf = sdf.rename(columns={time_colname: self._time_metric})
        return sdf

    def __init__(self, stats_paths, outdir):
        """
        The class constructor. Adding an IPMI statistics container tab will create an 'IPMI'
        sub-directory and store tabs inside it. These tabs will represent all of the metrics stored
        in the raw IPMI statistics file. The arguments are the same as in
        '_TabBuilderBase.TabBuilderBase'.
        """

        self._defs = IPMIDefs.IPMIDefs()
        self._time_metric = "Time"

        # Metrics in IPMI statistics can be represented by multiple columns. For example the
        # "FanSpeed" of several different fans can be measured and represented in columns "Fan1",
        # "Fan2" etc. This dictionary maps the metrics to the appropriate columns. Initialise it
        # with empty column sets for each metric.
        self._metrics = {metric: set() for metric in self._defs.info}

        super().__init__(stats_paths, outdir, ["ipmi.raw.txt", "ipmi-inband.raw.txt"])
