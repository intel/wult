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
from wultlibs import Defs
from wultlibs.parsers import IPMIParser
from wultlibs.htmlreport.tabs.stats import _StatsTab, _StatsTabBuilderBase
from wultlibs.htmlreport.tabs import _Tabs


class IPMITabBuilder(_StatsTabBuilderBase.StatsTabBuilderBase):
    """
    This class provides the capability of populating the IPMI statistics tab.

    Public methods overview:
    1. Generate a '_Tabs.ContainerTabDC' instance containing a group of sub-tabs which display
       different IPMI statistics.
       * 'get_tab_group()'
    """

    # File system-friendly tab name.
    name = "IPMI"

    def get_tab_group(self):
        """
        Generate a '_Tabs.ContainerTabDC' instance containing a group of sub-tabs which display
        different IPMI statistics.
        """

        col_sets = [set(sdf.columns) for sdf in self._reports.values()]
        common_cols = set.intersection(*col_sets)

        defs = Defs.Defs("ipmi")

        mgroups = []
        for metric, colnames in self._metrics.items():
            coltabs = []
            mtab_outdir = self._outdir / metric
            for col in colnames:
                if col not in common_cols:
                    continue

                # Since we use column names which aren't known until runtime as tab titles, use the
                # defs for the metric but overwrite the 'title' attribute.
                col_defs = defs.info[metric]
                col_defs["title"] = col
                col_defs["metric"] = col

                coltab = _StatsTab.StatsTabBuilder(self._reports, mtab_outdir, self._basedir,
                                                   col_defs, defs.info[self._time_metric])
                coltabs.append(coltab.get_tab())

            # Only add a tab group for 'metric' if any tabs were generated to populate it.
            if coltabs:
                mgroups.append(_Tabs.ContainerTabDC(metric, coltabs))

        if not mgroups:
            raise Error(f"no common {self.name} metrics between reports.")

        return _Tabs.ContainerTabDC(self.name, mgroups)

    def _categorise_cols(self, ipmi):
        """
        Associates column names in the IPMIParser dict 'ipmi' to the metrics they represent. For
        example, 'FanSpeed' can be represented by several columns such as 'Fan1', 'Fan Speed' etc.
        This function will add those column names to the 'FanSpeed' metric.
        """

        for colname, val in ipmi.items():
            unit = val[1]
            if unit == "RPM":
                self._metrics["FanSpeed"].add(colname)
            elif unit == "degrees C":
                self._metrics["Temperature"].add(colname)
            elif unit == "Watts":
                self._metrics["Power"].add(colname)


    def _read_stats_file(self, path):
        """
        Returns a pandas DataFrame containing the data stored in the raw IPMI statistics file at
        'path'.
        """

        time_colname = "timestamp"

        def _ipmi_to_df(ipmi):
            """Convert IPMIParser dict to pandas DataFrame."""

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
            # Append dataset for a single timestamp to the main Dataframe.
            sdf = pandas.concat([sdf, df], ignore_index=True)

        # Confirm that the time column is in the Dataframe.
        if time_colname not in sdf:
            raise Error(f"column '{time_colname}' not found in statistics file '{path}'.")

        # Convert Time column from time stamp to time since the first data point was recorded.
        sdf[time_colname] = sdf[time_colname] - sdf[time_colname][0]
        sdf[time_colname] = sdf[time_colname] / numpy.timedelta64(1, "s")

        sdf = sdf.rename(columns={time_colname: self._time_metric})
        return sdf

    def __init__(self, stats_paths, outdir):
        """
        The class constructor. Adding an IPMI statistics group tab will create an 'IPMI'
        sub-directory and store sub-tabs inside it. Sub-tabs will represent all of the metrics
        stored in the raw IPMI statistics file. The arguments are the same as in
        '_StatsTabContainer.StatsTabContainerBuilderBase'.
        """

        self._time_metric = "Time"

        # Metrics in IPMI statistics can be represented by multiple columns. For example the
        # "FanSpeed" of several different fans can be measured and represented in columns "Fan1",
        # "Fan2" etc. This dictionary maps the metrics to the appropriate columns.
        self._metrics = {
            "FanSpeed": set(),
            "Temperature": set(),
            "Power": set()
        }

        super().__init__(stats_paths, outdir, ["ipmi.raw.txt", "ipmi-inband.raw.txt"])
