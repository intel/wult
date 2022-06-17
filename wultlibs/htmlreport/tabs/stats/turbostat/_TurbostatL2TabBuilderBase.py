# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""
This module contains the base class for turbostat level 2 tab builder classes.

'Level 2 turbostat tabs' refer to tabs in the second level of tabs in the turbostat tab hierarchy.
For each level 2 turbostat tab, we parse raw turbostat statistics files differently.  Therefore this
base class expects child classes to implement '_turbostat_to_df()'.
"""

from pathlib import Path
import logging
import pandas
from pepclibs.helperlibs.Exceptions import Error
from wultlibs.htmlreport.tabs.stats import _TabBuilderBase
from wultlibs.htmlreport.tabs import _DTabBuilder, _Tabs
from wultlibs.parsers import TurbostatParser
from wultlibs import _DefsBase, TurbostatDefs

_LOG = logging.getLogger()

class TurbostatL2TabBuilderBase(_TabBuilderBase.TabBuilderBase):
    """
    The base class for turbostat level 2 tab builder classes.

    This base class requires child classes to implement the following methods:
    1. Convert the 'tstat' dictionary produced by 'TurbostatParser' to a 'pandas.DataFrame'.
       * '_turbostat_to_df()'
    """

    def _turbostat_to_df(self, tstat, path):
        """
        Convert the 'tstat' dictionary to a 'pandas.DataFrame'. Arguments are as follows:
         * tstat - dictionary produced by 'TurbostatParser'.
         * path - path of the original raw turbostat statistics file which was parsed to produce
                  'tstat'.
        """

        raise NotImplementedError()

    def _extract_cstates(self, tstat):
        """
        Extract the C-states with data in 'tstat', the dictionary produced by 'TurbostatParser'.
        """

        req_cstates = []
        hw_cstates = []
        pkg_cstates = []

        for metric in tstat["totals"]:
            if TurbostatDefs.is_reqcs_metric(metric):
                req_cstates.append(metric[:-1])
            elif TurbostatDefs.is_hwcs_metric(metric):
                hw_cstates.append(metric[4:].upper())
            elif TurbostatDefs.is_pkgcs_metric(metric):
                pkg_cstates.append(metric[5:].upper())

        self._cstates["hardware"]["core"].append(hw_cstates)
        self._cstates["hardware"]["package"].append(pkg_cstates)
        self._cstates["requested"].append(req_cstates)
        return hw_cstates, req_cstates

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
            hw_cstates, req_cstates = self._extract_cstates(tstat)

            # Instantiate 'self._defs' if it has not already been instantiated.
            if not self._defs:
                self._defs = TurbostatDefs.TurbostatDefs(hw_cstates + req_cstates)

            # Initialise the stats 'pandas.DataFrame' ('sdf') with data from the first 'tstat'
            # dictionary.
            sdf = self._turbostat_to_df(tstat, path)

            # Add the rest of the data from the raw turbostat statistics file to 'sdf'.
            for tstat in tstat_gen:
                df = self._turbostat_to_df(tstat, path)
                sdf = pandas.concat([sdf, df], ignore_index=True)
        except Exception as err:
            raise Error(f"error reading raw statistics file '{path}': {err}.") from None

        # Confirm that the time column is in the 'pandas.DataFrame'.
        if self._time_metric not in sdf:
            raise Error(f"timestamps could not be parsed in raw statistics file '{path}'.")

        # Convert 'Time' column from time since epoch to time since first data point was recorded.
        sdf[self._time_metric] = sdf[self._time_metric] - sdf[self._time_metric][0]

        return sdf

    def _build_ctab(self, name, tab_hierarchy, outdir, plots):
        """
        This is a helper function for 'get_tab()'. Build a container tab according to the
        'tab_hierarchy' dictionary. If no sub-tabs can be generated then returns 'None'.
        Arguments are as follows:
         * name - name of the returned container tab.
         * tab_hierarchy - dictionary representation of the desired tab hierarchy. Schema is as
                           follows:
                           {
                               CTabName1:
                                   {"dtabs": [metric1, metric2...]},
                               CTabName2:
                                   CTabName3:
                                       {"dtabs": [metric3, metric4...]}
                           }
         * outdir - path of the directory in which to store the generated tabs.
         * plots - dictionary representation of the plots to include for each metric. Schema is as
                   follows:
                   {
                        Metric1:
                            {
                                "scatter": [(mdef1, mdef2), (mdef1, mdef5)],
                                "hist": [mdef1, mdef2],
                                "chist": [mdef1]
                            }
                   }
        """

        # Sub-tabs which will be contained by the returned container tab.
        sub_tabs = []

        # Start by checking if 'tab_hierarchy' includes data tabs at this level. If it does, create
        # them and append them to 'sub_tabs'.
        if "dtabs" in tab_hierarchy:
            for metric in tab_hierarchy["dtabs"]:
                if not all(metric in sdf for sdf in self._reports.values()):
                    _LOG.info("Skipping '%s' tab in '%s' tab: one or more results do not contain "
                              "data for this metric.", metric, self.name)
                    continue
                try:
                    tab = _DTabBuilder.DTabBuilder(self._reports, outdir, self._defs.info[metric],
                                                   self._basedir)
                    if metric in plots:
                        tab.add_plots(plots[metric].get("scatter"), plots[metric].get("hist"),
                                      plots[metric].get("chist"))
                    tab.add_smrytbl([self._defs.info[metric]])
                    sub_tabs.append(tab.get_tab())
                except Error as err:
                    _LOG.info("Skipping '%s' tab in '%s' tab: error occured during tab generation.",
                              metric, self.name)
                    _LOG.debug(err)

        # Process the rest of the tabs in the tab hierarchy.
        for tab_name, sub_hierarchy in tab_hierarchy.items():
            # Data tabs are handled by the check above so skip them.
            if tab_name == "dtabs":
                continue

            # Tabs not labelled by the "dtabs" key in the tab hierarchy are container tabs. For each
            # sub container tab, recursively call 'self._build_ctab()'.
            subdir = Path(outdir) / _DefsBase.get_fsname(tab_name)
            subtab = self._build_ctab(tab_name, sub_hierarchy, subdir, plots)
            if subtab:
                sub_tabs.append(subtab)

        if sub_tabs:
            return _Tabs.CTabDC(name, sub_tabs)

        # If no sub tabs were generated then return 'None'.
        return None

    @staticmethod
    def _get_common_elements(lsts):
        """
        Helper function for '_get_tab_hierarchy()'. Expects 'lsts' to be a list of lists. Finds list
        elements which are common to all lists in 'lsts'. Returns elements in the order they appear
        in the first list.
        """

        # Create a set of elements common to all lists in 'lsts'.
        common_elements = set.intersection(*[set(lst) for lst in lsts])

        # Maintain the order of elements as they appear in the first list.
        return [el for el in lsts[0] if el in common_elements]


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
        misc_metrics = ["Busy%", "IRQ", "SMI", "IPC"]
        tab_hierarchy["Misc"] = {"dtabs": [m for m in misc_metrics if m in common_metrics]}

        # Find C-states which are common to all test results.
        hw_core_cs = self._get_common_elements(self._cstates["hardware"]["core"])
        req_cs = self._get_common_elements(self._cstates["requested"])

        for cs in req_cs:
            tab_hierarchy["C-states"]["Requested"]["dtabs"].append(f"{cs}%")

        for cs in hw_core_cs:
            tab_hierarchy["C-states"]["Hardware"]["dtabs"].append(f"CPU%{cs.lower()}")

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

        # Limit metrics to only those which are common to all test results.
        for reportid, sdf in self._reports.items():
            self._reports[reportid] = sdf[list(common_metrics)]

        # All raw turbostat statistic files have been parsed so we can now get a tab hierarchy with
        # tabs which are common to all sets of results.
        tab_hierarchy = self._get_tab_hierarchy(common_metrics)

        # Define which plots should be generated in the data tab for a given metric.
        plots = {}
        for metric in common_metrics:
            defs_info = self._defs.info
            plots[metric] = {
                "scatter": [(defs_info[self._time_metric], defs_info[metric])],
                "hist": [defs_info[metric]]
            }

        # Build L2 CTab with hierarchy represented in 'self._tab_hierarchy'.
        return self._build_ctab(self.name, tab_hierarchy, self.outdir, plots)

    def __init__(self, stats_paths, outdir, basedir):
        """
        The class constructor. Adding a turbostat level 2 tab will create a sub-directory and store
        data tabs inside it for metrics stored in the raw turbostat statistics file.  The arguments
        are the same as in '_TabBuilderBase.TabBuilderBase' except for:
         * basedir - base directory of the report. All asset paths will be made relative to this.
        """

        self._time_metric = "Time"
        self.outdir = outdir

        # After C-states have been extracted from the first raw turbostat statistics file, this
        # property will be assigned a 'TurbostatDefs.TurbostatDefs' instance.
        self._defs = None

        # Store C-states for which there is data in each raw turbostat statistics file. Each leaf
        # value contains a list of lists where each file has its own sub-list of C-states.
        self._cstates = {
            "requested": [],
            "hardware": {
                "core": [],
                "package": []
            }
        }

        super().__init__(stats_paths, outdir, ["turbostat.raw.txt"])
        self._basedir = basedir
