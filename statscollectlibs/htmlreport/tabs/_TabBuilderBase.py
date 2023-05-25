# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""
This module provides a base class and common logic for populating a group of statistics tabs.
"""

from pathlib import Path
import logging
from pepclibs.helperlibs.Exceptions import Error, ErrorNotFound
from statscollectlibs.defs import DefsBase
from statscollectlibs.htmlreport.tabs import _DTabBuilder, _Tabs

_LOG = logging.getLogger()

class TabBuilderBase:
    """
    This base class can be inherited from to populate a group of statistics tabs.

    For classes with names such as '_XStatsTabBuilder' and the 'Builder' suffix, their purpose is to
    produce a tab containing data from 'XStats'. These classes do not represent the tab itself but a
    builder which creates those tabs.

    This base class requires child classes to implement the following methods:
    1. Read a raw statistics file and convert the statistics data into a 'pandas.DataFrame'.
       * '_read_stats_file()'
    2. Generate a '_Tabs.DTabDC' or '_Tabs.CTabDC' instance which represent statistics found in raw
       statistics file. This method provides an interface for the child classes.
       * 'get_tab()'
    """

    # The name of the statistics represented in the produced tab.
    name = None

    def _build_ctab(self, name, tab_hierarchy, outdir, plots, smry_funcs):
        """
        This is a helper function for 'get_tab()'. Build a container tab according to the
        'tab_hierarchy' dictionary. If no sub-tabs can be generated then raises an 'Error'.
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
         * smry_funcs - dictionary representation of the summary functions to include in the summary
                    table for each metric. Schema is as follows:
                    {
                        Metric1: ["99.999%", "99.99%",...],
                        Metric2: ["max", "min",...]
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
                    tab.add_smrytbl({metric: smry_funcs[metric]}, self._defs)
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
            subdir = Path(outdir) / DefsBase.get_fsname(tab_name)
            subtab = self._build_ctab(tab_name, sub_hierarchy, subdir, plots, smry_funcs)
            if subtab:
                sub_tabs.append(subtab)

        if sub_tabs:
            return _Tabs.CTabDC(name, sub_tabs)

        raise Error(f"unable to generate a container tab for {self.name}.")

    def get_tab(self):
        """
        Returns a '_Tabs.DTabDC' or '_Tabs.CTabDC' instance which represent statistics found in raw
        statistic files. This method should be implemented by a child class.
        """

        raise NotImplementedError()

    def __init__(self, dfs, outdir, defs=None):
        """
        The class constructor. Adding a statistics container tab will create a sub-directory and
        store tabs inside it. These tabs will represent all of the metrics stored in 'stats_file'.
        Arguments are as follows:
         * dfs - a dictionary in the format '{ReportId: pandas.DataFrame}' for each result where the
                 'pandas.DataFrame' contains that statistics data for that result.
         * outdir - the output directory in which to create the sub-directory for the container tab.
         * defs - a '_DefsBase.DefsBase' instance containing definitions for the metrics which
                  should be included in the output tab.
        """

        if self.name is None:
            raise Error(f"failed to initalise '{type(self).__name__}': 'name' class attribute not "
                        f"populated.")

        if not dfs:
            raise ErrorNotFound(f"failed to initalise '{type(self).__name__}': no results contain "
                                f"data for this statistic.")

        self._reports = dfs
        self._basedir = outdir
        self._outdir = outdir / DefsBase.get_fsname(self.name)
        self._defs = defs

        try:
            self._outdir.mkdir(parents=True, exist_ok=True)
        except OSError as err:
            msg = Error(err).indent(2)
            raise Error(f"failed to create directory '{self._outdir}':\n{msg}") from None
