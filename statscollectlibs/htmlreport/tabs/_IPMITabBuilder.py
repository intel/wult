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
from pepclibs.helperlibs import Trivial
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs import IPMIDefs
from statscollectlibs.htmlreport.tabs import _TabBuilderBase
from statscollectlibs import _DefsBase
from wultlibs.parsers import IPMIParser

class IPMITabBuilder(_TabBuilderBase.TabBuilderBase):
    """
    This class provides the capability of populating the IPMI statistics tab.

    Public methods overview:
    1. Generate a '_Tabs.CTabDC' instance containing tabs which display IPMI statistics.
       * 'get_tab()'
    """

    name = "IPMI"

    def _get_tab_hierarchy(self, common_cols):
        """
        Helper function for 'get_tab()'. Get the tab hierarchy which is populated with IPMI column
        names which are common to all raw IPMI statistic files 'common_cols'.
        """

        tab_hierarchy = {}

        # Dedupe cols in 'self._metrics'.
        for metric in self._metrics:
            self._metrics[metric] = Trivial.list_dedup(self._metrics[metric])

        # Add fan speed-related D-tabs to a separate C-tab.
        fspeed_cols = self._metrics["FanSpeed"]
        tab_hierarchy["Fan Speed"] = {"dtabs": [c for c in fspeed_cols if c in common_cols]}

        # Add temperature-related D-tabs to a separate C-tab.
        temp_cols = self._metrics["Temperature"]
        tab_hierarchy["Temperature"] = {"dtabs": [c for c in temp_cols if c in common_cols]}

        # Add power-related D-tabs to a separate C-tab.
        pwr_cols = self._metrics["Power"] + self._metrics["Current"] + self._metrics["Voltage"]
        tab_hierarchy["Power"] = {"dtabs": [c for c in pwr_cols if c in common_cols]}

        return tab_hierarchy

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

        # Reports may have the "Time" column in common or none at all. In both of these cases, an
        # IPMI tab won't be generated.
        if len(common_cols) < 2:
            raise Error("unable to generate IPMI tab, no common IPMI metrics between reports.")

        # Update defs with IPMI column names for each column.
        for metric, colnames in self._metrics.items():
            for colname in colnames:
                if colname not in common_cols:
                    continue

                # Since we use column names which aren't known until runtime as tab titles, use the
                # defs for the metric but overwrite the 'name' and 'fsname' attributes. Use 'copy'
                # so that 'defs.info' can be used to create the container tab.
                col_def = self._defs.info[metric].copy()
                # Don't overwrite the 'title' attribute so that the metric name is shown in plots
                # and the summary table.
                col_def["fsname"] = _DefsBase.get_fsname(colname)
                col_def["name"] = colname
                self._defs.info[colname] = col_def

        tab_hierarchy = self._get_tab_hierarchy(common_cols)

        # Configure which axes plots will display in the data tabs.
        plots = {}
        for metric, colnames in self._metrics.items():
            for col in colnames:
                if col not in common_cols:
                    continue

                defs_info = self._defs.info
                plots[col] = {
                    "scatter": [(defs_info[self._time_metric], defs_info[col])],
                    "hist": [defs_info[col]]
                }

        return self._build_ctab(self.name, tab_hierarchy, self._outdir, plots)

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
                self._metrics[metric].append(colname)

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

        self._time_metric = "Time"

        # Metrics in IPMI statistics can be represented by multiple columns. For example the
        # "FanSpeed" of several different fans can be measured and represented in columns "Fan1",
        # "Fan2" etc. This dictionary maps the metrics to the appropriate columns. Initialise it
        # with empty column sets for each metric.
        defs = IPMIDefs.IPMIDefs()
        self._metrics = {metric: [] for metric in defs.info}

        super().__init__(stats_paths, outdir, ["ipmi.raw.txt", "ipmi-inband.raw.txt"], defs)
