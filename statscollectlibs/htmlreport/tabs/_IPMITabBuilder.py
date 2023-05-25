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

import logging
from pepclibs.helperlibs import Trivial
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.defs import DefsBase, IPMIDefs
from statscollectlibs.dfbuilders import IPMIDFBuilder
from statscollectlibs.htmlreport.tabs import _TabBuilderBase

_LOG = logging.getLogger()

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
                col_def["fsname"] = DefsBase.get_fsname(colname)
                col_def["name"] = colname
                self._defs.info[colname] = col_def

        tab_hierarchy = self._get_tab_hierarchy(common_cols)

        # Configure which axes plots will display in the data tabs.
        plots = {}
        smry_funcs = {}
        for metric, colnames in self._metrics.items():
            for col in colnames:
                if col not in common_cols:
                    continue

                defs_info = self._defs.info
                plots[col] = {
                    "scatter": [(defs_info[self._time_metric], defs_info[col])],
                    "hist": [defs_info[col]]
                }

        # Define which summary functions should be included in the generated summary table
        # for a given metric.
        for metric in common_cols:
            smry_funcs[metric] = ["max", "99.999%", "99.99%", "99.9%", "99%",
                                  "med", "avg", "min", "std"]

        return self._build_ctab(self.name, tab_hierarchy, self._outdir, plots, smry_funcs)

    def _read_stats_file(self, path):
        """
        Returns a 'pandas.DataFrame' containing the data stored in the raw IPMI statistics file at
        'path'.
        """

        raise NotImplementedError()

    def __init__(self, rsts, outdir):
        """
        The class constructor. Adding an IPMI statistics container tab will create an 'IPMI'
        sub-directory and store tabs inside it. These tabs will represent all of the metrics stored
        in the raw IPMI statistics file. Arguments are as follows:
         * rsts - a list of 'RORawResult' instances for which data should be included in the built
                  tab.
         * outdir - the output directory in which to create the sub-directory for the built tab.
        """

        self._time_metric = "Time"

        # Metrics in IPMI statistics can be represented by multiple columns. For example the
        # "FanSpeed" of several different fans can be measured and represented in columns "Fan1",
        # "Fan2" etc. This dictionary maps the metrics to the appropriate columns. Initialise it
        # with empty column sets for each metric.
        defs = IPMIDefs.IPMIDefs()
        self._metrics = {}

        stnames = set()
        dfs = {}
        dfbldr = IPMIDFBuilder.IPMIDFBuilder()
        for res in rsts:
            for stname in ("ipmi-oob", "ipmi-inband"):
                if stname not in res.info["stinfo"]:
                    continue

                dfs[res.reportid] = res.load_stat(stname, dfbldr, f"{stname}.raw.txt")
                self._metrics.update(dfbldr.metrics)
                stnames.add(stname)
                break

        if len(stnames) > 1:
            _LOG.warning("generating '%s' tab with a combination of data collected both inband "
                         "and out-of-band.", self.name)

        super().__init__(dfs, outdir, defs=defs)
