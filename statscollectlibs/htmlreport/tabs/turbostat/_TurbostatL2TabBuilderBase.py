# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022-2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""
This module contains the base class for turbostat level 2 tab builder classes.

'Level 2 turbostat tabs' refer to tabs in the second level of tabs in the turbostat tab hierarchy.
For each level 2 turbostat tab, we parse raw turbostat statistics files differently.  Therefore this
base class expects child classes to implement '_turbostat_to_df()'.
"""

from statscollectlibs.defs import TurbostatDefs
from statscollectlibs.htmlreport.tabs import _TabBuilderBase

class TurbostatL2TabBuilderBase(_TabBuilderBase.TabBuilderBase):
    """
    The base class for turbostat level 2 tab builder classes.

    This base class requires child classes to implement the following methods:
    1. Convert the 'tstat' dictionary produced by 'TurbostatParser' to a 'pandas.DataFrame'.
       * '_turbostat_to_df()'
    """

    def _get_tab_hierarchy(self, common_metrics):
        """
        Get the tab hierarchy which is populated with 'common_metrics' and using the C-states in
        'self._hw_cstates' and 'self._req_cstates'.
        """

        tab_hierarchy = {
            "C-states": {
                "Hardware": {"dtabs":[]},
                "Requested": {"dtabs": []}
            }
        }

        # Add frequency-related D-tabs to a separate C-tab.
        freq_metrics = ["Bzy_MHz", "Avg_MHz"]
        tab_hierarchy["Frequency"] = {"dtabs": [m for m in freq_metrics if m in common_metrics]}

        # Add temperature/power-related D-tabs to a separate C-tab.
        tp_metrics = ["CorWatt", "CoreTmp"]
        tp_metrics = [m for m in tp_metrics if m in common_metrics]
        tab_hierarchy["Temperature / Power"] = {"dtabs": tp_metrics}

        # Add miscellaneous D-tabs to a separate C-tab.
        misc_metrics = ["IRQ", "SMI", "IPC"]
        tab_hierarchy["Misc"] = {"dtabs": [m for m in misc_metrics if m in common_metrics]}

        for cs in self._cstates["requested"]:
            tab_hierarchy["C-states"]["Requested"]["dtabs"].append(cs.metric)

        tab_hierarchy["C-states"]["Hardware"]["dtabs"].append("Busy%")
        for cs in self._cstates["hardware"]["core"]:
            tab_hierarchy["C-states"]["Hardware"]["dtabs"].append(cs.metric)

        return tab_hierarchy

    def get_tab(self):
        """
        Returns a '_Tabs.CTabDC' instance, titled 'self.name', containing tabs which represent
        different metrics within raw turbostat statistic files.

        The container tab returned by this function will contain a "CC0%" data tab and a "C-states"
        container tab. The "C-states" container tab will contain two further container tabs,
        "Hardware" and "Requested", which will contain data tabs representing hardware and
        requestable C-states respectively.

        Note that the hierarchy of the tabs will will only include turbostat metrics which are
        common to all results.
        """

        # Find metrics which are common to all raw turbostat statistic files.
        metric_sets = [set(sdf.columns) for sdf in self._reports.values()]
        common_metrics = set.intersection(*metric_sets)

        # Limit metrics to only those with definitions.
        common_metrics.intersection_update(set(self._defs.info.keys()))

        # All raw turbostat statistic files have been parsed so we can now get a tab hierarchy with
        # tabs which are common to all sets of results.
        tab_hierarchy = self._get_tab_hierarchy(common_metrics)

        # Define which plots should be generated in the data tab and which summary functions
        # should be included in the generated summary table for a given metric.
        plots = {}
        smry_funcs = {}
        for metric in common_metrics:
            defs_info = self._defs.info
            plots[metric] = {
                "scatter": [(defs_info[self._time_metric], defs_info[metric])],
                "hist": [defs_info[metric]]
            }
            if metric in ('IRQ', 'SMI'):
                smry_funcs[metric] = ["max", "avg", "min", "std"]
            else:
                smry_funcs[metric] = ["max", "99.999%", "99.99%", "99.9%", "99%",
                                      "med", "avg", "min", "std"]

        # Build L2 CTab with hierarchy represented in 'self._tab_hierarchy'.
        return self._build_ctab(self.name, tab_hierarchy, self.outdir, plots, smry_funcs)

    def _init_cstates(self, dfs):
        """
        Find common C-states present in all results in 'dfs' and categorise them into the
        'self._cstates' dictionary. Returns a list of all of the common C-states.
        """

        req_cstates = []
        core_cstates = []
        pkg_cstates = []
        mod_cstates = []

        for metric in list(dfs.values())[0]:
            if not all(metric in df.columns for df in dfs.values()):
                continue

            if TurbostatDefs.ReqCSDef.check_metric(metric):
                req_cstates.append(TurbostatDefs.ReqCSDef(metric))
            elif TurbostatDefs.CoreCSDef.check_metric(metric):
                core_cstates.append(TurbostatDefs.CoreCSDef(metric))
            elif TurbostatDefs.PackageCSDef.check_metric(metric):
                pkg_cstates.append(TurbostatDefs.PackageCSDef(metric))
            elif TurbostatDefs.ModuleCSDef.check_metric(metric):
                mod_cstates.append(TurbostatDefs.ModuleCSDef(metric))

        self._cstates["hardware"]["core"] = core_cstates
        self._cstates["hardware"]["package"] = pkg_cstates
        self._cstates["hardware"]["module"] = mod_cstates
        self._cstates["requested"] = req_cstates

        all_cstates = req_cstates + core_cstates + pkg_cstates + mod_cstates
        return [csdef.cstate for csdef in all_cstates]

    def __init__(self, dfs, outdir, basedir):
        """
        The class constructor. Adding a turbostat level 2 tab will create a sub-directory and store
        data tabs inside it for metrics stored in the raw turbostat statistics file.  The arguments
        are the same as in '_TabBuilderBase.TabBuilderBase' except for:
         * dfs - a dictionary in the format '{ReportId: pandas.DataFrame}' for each result where the
                 'pandas.DataFrame' contains that statistics data for that result.
         * basedir - base directory of the report. All asset paths will be made relative to this.
        """

        self._time_metric = "Time"
        self.outdir = outdir

        # After C-states have been extracted from the first raw turbostat statistics file, this
        # property will be assigned a 'TurbostatDefs.TurbostatDefs' instance.
        self._defs = None

        # Store C-states for which there is data in each raw turbostat statistics file.
        self._cstates = {
            "requested": [],
            "hardware": {
                "core": [],
                "package": [],
                "module": []
            }
        }

        super().__init__(dfs, outdir)

        self._basedir = basedir

        all_cstates = self._init_cstates(dfs)
        self._defs = TurbostatDefs.TurbostatDefs(all_cstates)
