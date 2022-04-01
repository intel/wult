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
from pepclibs.helperlibs import YAML
from wultlibs import Deploy
from wultlibs.htmlreport.tabs import _BaseTab
from wultlibs.htmlreport.tabs.stats import _StatsTab

_LOG = logging.getLogger()


class StatsTabContainerDC(_BaseTab.TabContainerDC):
    """
    This class defines what is expected by the JavaScript side when adding a group of statistics
    tabs to HTML reports.
    """

class StatsTabContainerBuilderBase:
    """
    This base class can be inherited from to populate a group of statistics tabs.

    This base class requires child classes to implement the following methods:
    1. Read a raw statistics file and convert the statistics data into a pandas Dataframe.
       * '_read_stats_file()'
    2. Generate a 'StatsTabCollectionBuilderBase' instance containing sub-tabs which represent
       statistics contained within the group. This method provides an interface for the child
       classes. '_get_tab_group()' contains common logic which can be used to implement this method.
       * 'get_tab_group()'
    """

    # File system-friendly tab name.
    name = None

    def get_tab_group(self):
        """
        Returns a 'StatsTabContainerDC' instance containing sub-tabs which represent metrics within
        the raw statistic files.
        """

        raise NotImplementedError()

    def _get_tab_group(self, tab_metrics, time_metric):
        """
        Returns a 'StatsTabContainerDC' instance containing sub-tabs which represent statistics
        contained within the group.
         * tab_metrics - a list of metrics to include in the tab container.
         * time_metric - the metric which represents the time elapsed.
        """

        # Create child tabs.
        tbldrs = []
        for metric in tab_metrics:
            tab = _StatsTab.StatsTabBuilder(self._reports, self._outdir, self._basedir, metric,
                                            time_metric, self._defs)
            tbldrs.append(tab)

        tabs = []
        for tbldr in tbldrs:
            tabs.append(tbldr.get_tab())

        return StatsTabContainerDC(self.name, tabs)

    def _read_stats_file(self, path):
        """
        Returns a pandas DataFrame containing the data stored in the raw statistics file at 'path'.
        """

        raise NotImplementedError()

    def _add_stats(self, reportid, rawpath):
        """
        Add statistics contained in the raw statistics file at 'rawpath' for report 'reportid'. This
        will parse and associate the stats data with the report 'reportid'.
        """

        try:
            sdf = self._read_stats_file(rawpath)
        except Error as err:
            _LOG.warning("unfortunately report '%s' had issues with %s data, here are the details: "
                         "\nInvalid statistics file: %s \n", reportid, self.name, err)
            return

        self._reports[reportid] = sdf


    def _read_stats(self, stats_paths):
        """
        Given a dictionary of statistics directories, check which directories contain raw statistic
        files. If any of those files are found, process them and add the statistics they contain to
        the tab. 'stats_paths' is in the format:
        {'reportid': 'statistics_directory_path'}.
        """

        for reportid, statsdir in stats_paths.items():
            stats_exist = False
            if statsdir:
                for stats_file in self._stats_files:
                    statspath = Path(statsdir) / stats_file
                    if statspath.exists():
                        self._add_stats(reportid, statspath)
                        stats_exist = True
                        break

            if not stats_exist:
                raise ErrorNotFound(f"failed to generate '{self.name}' tab: no raw statistics file "
                                    f"found for report '{reportid}'.")

        if not self._reports:
            raise ErrorNotFound(f"failed to generate '{self.name}' tab: none of the following raw "
                                f"statistics files were found in any statistics directory: "
                                f"'{self._stats_files}'.")

    def __init__(self, stats_paths, outdir, bmname, defs_path, stats_files):
        """
        The class constructor. Adding a statistics group tab will create a sub-directory and store
        sub-tabs inside it. Sub-tabs will represent all of the metrics stored in 'stats_file'.
        Arguments are as follows:
         * stats_paths - dictionary in the format {'reportid': 'statistics_directory_path'}.
           This class will use these directories to locate raw statistic files.
         * outdir - the output directory in which to create the sub-directory for this tab group.
         * bmname - name of the benchmark ran during statistics collection.
         * defs_path - path to definitions file for this metric.
         * stats_files - a list of the possible names of the raw statistics file.
        """

        if self.name is None:
            raise Error(f"failed to initalise '{type(self).__name__}': 'name' class attribute not "
                        f"populated.")

        self._reports = {}
        self._basedir = outdir
        self._outdir = outdir / self.name

        try:
            self._outdir.mkdir(parents=True, exist_ok=True)
        except OSError as err:
            raise Error(f"failed to create directory '{self._outdir}': {err}") from None

        try:
            path = Deploy.find_app_data(bmname, Path(defs_path), appname=bmname,
                                        descr=f"{self.name} definitions file")
            self._defs = YAML.load(path)
        except Error as err:
            raise Error(f"failed to build '{self.name}' tab: {err}") from None

        self._stats_files = stats_files
        self._read_stats(stats_paths)
