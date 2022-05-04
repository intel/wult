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
from wultlibs.htmlreport.tabs.stats import _TabBuilderBase, _DTabBuilder
from wultlibs.htmlreport.tabs import _Tabs
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

    def _turbostat_to_df(self, tstat, metrics, path):
        """Convert the 'tstat' dictionary produced by 'TurbostatParser' to a 'pandas.DataFrame'."""

        raise NotImplementedError()

    def _extract_cstates(self, tstat):
        """
        Extract the C-states with data in 'tstat', the dictionary produced by 'TurbostatParser'.
        """

        req_cstates = []
        hw_cstates = []

        for key in tstat["totals"]:
            # Each requestable C-state has a column in the raw turbostat statistics file in the
            # format "Cx%".
            if key.startswith("C") and key[1].isdigit() and key.endswith("%"):
                req_cstates.append(key[:-1])
                continue

            # Each core/logical CPU hardware C-state has a column in the raw turbostat statistics
            # file in the format "CPU%cx".
            if key.startswith("CPU%"):
                hw_cstates.append(key[4:].upper())
                continue

        self._hw_cstates.append(hw_cstates)
        self._req_cstates.append(req_cstates)
        return hw_cstates, req_cstates

    def _populate_metrics(self, hw_cstates, req_cstates):
        """
        This is a helper function for '_read_stats_file()'. Returns a metrics dictionary with
        metrics representing the C-states given as arguments. The returned dictionary decides which
        metrics '_turbostat_to_df()' will extract from 'tstat' and is in the same format as
        'self._metrics'.
        """

        populated_metrics = self._metrics.copy()
        for cs in req_cstates:
            populated_metrics[f"{cs}%"] = f"{cs}%"

        for cs in hw_cstates:
            populated_metrics[f"C{cs}%"] = f"CPU%{cs.lower()}"

        return populated_metrics

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

            # Populate a metrics dictionary based on 'self._metrics' for the C-states with data
            # in 'tstat'. This is so that 'self._turbostat_to_df()' knows which metrics to extract
            # from 'tstat'.
            populated_metrics = self._populate_metrics(hw_cstates, req_cstates)

            # Initialise the stats 'pandas.DataFrame' ('sdf') with data from the first 'tstat'
            # dictionary.
            sdf = self._turbostat_to_df(tstat, populated_metrics, path)

            # Add the rest of the data from the raw turbostat statistics file to 'sdf'.
            for tstat in tstat_gen:
                df = self._turbostat_to_df(tstat, populated_metrics, path)
                sdf = pandas.concat([sdf, df], ignore_index=True)
        except Exception as err:
            raise Error(f"error reading raw statistics file '{path}': {err}.") from None

        # Confirm that the time column is in the 'pandas.DataFrame'.
        if self._time_metric not in sdf:
            raise Error(f"timestamps could not be parsed in raw statistics file '{path}'.")

        # Convert 'Time' column from time since epoch to time since first data point was recorded.
        sdf[self._time_metric] = sdf[self._time_metric] - sdf[self._time_metric][0]

        return sdf

    def _build_ctab(self, name, tab_hierarchy, outdir, defs):
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
         * defs - 'TurbostatDefs.TurbostatDefs' instance which contains all of the definitions for
                   the metrics which appear in 'tab_hierarchy'.
        """

        # Sub-tabs which will be contained by the returned container tab.
        sub_tabs = []

        # Start by checking if 'tab_hierarchy' includes data tabs at this level. If it does, create
        # them and append them to 'sub_tabs'.
        if "dtabs" in tab_hierarchy:
            for metric in tab_hierarchy["dtabs"]:
                try:
                    tab = _DTabBuilder.DTabBuilder(self._reports, outdir, self._basedir,
                                                   defs.info[metric], defs.info[self._time_metric])
                    sub_tabs.append(tab.get_tab())
                except Error as err:
                    _LOG.info("Skipping '%s' tab in turbostat '%s' tab: error occured during tab "
                              "generation.", metric, self.name)
                    _LOG.debug(err)

        # Process the rest of the tabs in the tab hierarchy.
        for tab_name, sub_hierarchy in tab_hierarchy.items():
            # Data tabs are handled by the check above so skip them.
            if tab_name == "dtabs":
                continue

            # Tabs not labelled by the "dtabs" key in the tab hierarchy are container tabs. For each
            # sub container tab, recursively call 'self._build_ctab()'.
            subdir = Path(outdir) / _DefsBase.get_fsname(tab_name)
            subtab = self._build_ctab(tab_name, sub_hierarchy, subdir, defs)
            if subtab:
                sub_tabs.append(subtab)

        if sub_tabs:
            return _Tabs.CTabDC(name, sub_tabs)

        # If no sub tabs were generated then return 'None'.
        return None

    def _populate_tab_hierarchy(self, hw_cstates, req_cstates):
        """Populate the tab hierarchy with the C-states provided as arguments."""

        self._tab_hierarchy["C-states"] = {
            "Hardware": {"dtabs":[]},
            "Requested": {"dtabs": []}
        }

        for cs in req_cstates:
            self._tab_hierarchy["C-states"]["Requested"]["dtabs"].append(f"{cs}%")

        for cs in hw_cstates:
            self._tab_hierarchy["C-states"]["Hardware"]["dtabs"].append(f"C{cs}%")

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

        # Find C-states which are common to all test results.
        common_hw_cstates = set.intersection(*[set(lst) for lst in self._hw_cstates])
        common_req_cstates = set.intersection(*[set(lst) for lst in self._req_cstates])

        defs = TurbostatDefs.TurbostatDefs(common_hw_cstates.union(common_req_cstates))

        # Maintain the order of C-states as they appeared in the raw turbostat statistic files.
        req_cstates = [cs for cs in self._req_cstates[0] if cs in common_req_cstates]
        hw_cstates = [cs for cs in self._hw_cstates[0] if cs in common_hw_cstates]

        # Populate the tab hierarchy with C-state related tabs for C-states which are common to all
        # sets of results.
        self._populate_tab_hierarchy(hw_cstates, req_cstates)

        # Find metrics which are common to all raw turbostat statistic files.
        metric_sets = [set(sdf.columns) for sdf in self._reports.values()]
        common_metrics = set.intersection(*metric_sets)

        # Limit metrics to only those which are common to all test results.
        for reportid, sdf in self._reports.items():
            self._reports[reportid] = sdf[list(common_metrics)]

        # Build L2 CTab with hierarchy represented in 'self._tab_hierarchy'.
        return self._build_ctab(self.name, self._tab_hierarchy, self.outdir, defs)

    def __init__(self, stats_paths, outdir, basedir):
        """
        The class constructor. Adding a turbostat level 2 tab will create a sub-directory and store
        data tabs inside it for metrics stored in the raw turbostat statistics file.  The arguments
        are the same as in '_TabBuilderBase.TabBuilderBase' except for:
         * basedir - base directory of the report. All asset paths will be made relative to this.
        """

        self._time_metric = "Time"
        self.outdir = outdir

        # Store C-states for which there is data in each raw turbostat statistics file. A list of
        # lists where each file has its own sub-list of C-states.
        self._hw_cstates = []
        self._req_cstates = []

        # Dictionary in the format {'metric': 'colname'} where 'colname' in the raw turbostat
        # statistics file represents 'metric'.
        self._metrics = {
            "Busy%": "Busy%"
        }

        # Add data tabs for all the metrics in 'self._metrics' to the tab hierarchy.
        self._tab_hierarchy = {"dtabs": list(self._metrics)}

        super().__init__(stats_paths, outdir, ["turbostat.raw.txt"])
        self._basedir = basedir
