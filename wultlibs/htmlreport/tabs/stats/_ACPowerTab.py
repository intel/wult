# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""
This module provides the capability of populating the AC Power statistics Tab.
"""

from pathlib import Path
import logging
import pandas

from pepclibs.helperlibs.Exceptions import Error, ErrorNotFound
from pepclibs.helperlibs import YAML
from wultlibs.htmlreport import _SummaryTable, _ScatterPlot, _Histogram
from wultlibs import DFSummary, Deploy
from wultlibs.htmlreport.tabs import _BaseTab

_LOG = logging.getLogger()


class ACPowerTabDC(_BaseTab.BaseTabDC):
    """
    This class defines what is expected by the JavaScript side when adding a AC Power tab to HTML
    reports.
    """

class ACPowerTabBuilder:
    """
    This class provides the capability of populating the AC Power statistics tab.

    Public methods overview:
    1. Generate an 'ACPowerTabDC' instance containing plots and a summary table which represent all
       of the AC Power statistics found during initialisation.
       * 'get_tab()'
    """
    # File system-friendly tab name.
    name = "ACPower"

    def _prepare_smrys_tbl(self):
        """Construct a 'SummaryTable' to summarise the statistics added with '_add_stats()'."""

        smrytbl = _SummaryTable.SummaryTable()

        smrytbl.add_metric(self.title, self._metric_defs["short_unit"], self.descr,
                           fmt="{:.2f}")

        for rep, df in self._reports.items():
            smry_dict = DFSummary.calc_col_smry(df, self._metric_colname, self.smry_funcs)
            for fname in self.smry_funcs:
                smrytbl.add_smry_func(rep, self.title, fname, smry_dict[fname])

        smrytbl.generate(self.smry_path)

    def get_tab(self):
        """
        Returns an 'ACPowerTab' instance which contains an aggregate of all of the statistics found
        in 'stats_paths', provided to the class constructor. This 'ACPowerTab' can then be used to
        populate an HTML tab.
        """

        plotpaths = []
        for plot in self._plots:
            plot.generate()
            plotpaths.append(plot.outpath.relative_to(self._basedir))

        self._prepare_smrys_tbl()

        return ACPowerTabDC(self.title, plotpaths, self.smry_path.relative_to(self._basedir))

    def _csv_to_df(self, path):
        """
        AC Power statistics are recorded in a CSV file, this converts the CSV file at the path
        'path' to a pandas DataFrame.
        """

        sdf = pandas.DataFrame()

        try:
            # 'skipfooter' parameter only available with Python pandas engine.
            sdf = pandas.read_csv(path, skipfooter=1, engine="python")
        except pandas.errors.ParserError as err:
            raise Error(f"unable to parse CSV '{path}': {err}.") from None

        # Confirm that the metric and time column names are in the CSV headers.
        for colname in self._time_colname, self._metric_colname:
            if colname not in sdf:
                raise Error(f"column '{colname}' not found in statistics file '{path}'.")

        # Convert Time column from time since epoch to time since the first data point was recorded.
        sdf[self._time_colname] = sdf[self._time_colname] - sdf[self._time_colname][0]

        return sdf

    def _add_stats(self, reportid, rawpath):
        """
        Add AC Power stats for AC Power CSV at 'rawpath' for report 'reportid'. This will parse and
        associate the AC Power data with the report 'reportid'.
        """

        try:
            sdf = self._csv_to_df(rawpath)
        except Error as err:
            _LOG.warning("unfortunately report '%s' had issues with %s data, here are the details: "
                         "\nInvalid statistics file: %s \n", reportid, self.title, err)
            return

        self._reports[reportid] = sdf

        for plot in self._plots:
            if isinstance(plot, _ScatterPlot.ScatterPlot):
                sdf = plot.reduce_df_density(sdf, reportid)
            plot.add_df(sdf, reportid)

    def _read_stats(self, stats_paths):
        """
        Given a dictionary of statistics directories, check which directories contain raw AC Power
        statistic files. If any of those files are found, process them and add the statistics they
        contain to the tab. 'stats_paths' is in the format:
        {'reportid': 'statistics_directory_path'}.
        """

        for reportid, statsdir in stats_paths.items():
            statspath = Path(statsdir) / self._statsfile
            if statspath.exists():
                self._add_stats(reportid, statspath)
            else:
                _LOG.warning("no raw '%s' statistic files found for report '%s'.", self.title,
                             reportid)

        if not self._reports:
            raise ErrorNotFound(f"failed to generate '{self.title}' tab. No '{self._statsfile}' "
                                 "file found in any statistics directory.")

    def __init__(self, stats_paths, outdir, bmname):
        """
        The class constructor. Adding an ACPower tab will create an 'ACPower' sub-directory and
        store plots and the summary table in it. Arguments are as follows:
         * stats_paths - dictionary in the format {Report ID: Stats directory path}.
           This class will use these directories to locate raw AC Power statistic files.
         * outdir - the output directory in which to create the 'ACPower' sub-directory.
         * bmname - name of the benchmark ran during AC Power statistic collection.
        """

        self._reports = {}

        self._basedir = outdir
        self._outdir = outdir / self.name
        self.smry_path = self._outdir / "summary-table.txt"

        try:
            self._outdir.mkdir(parents=True, exist_ok=True)
        except OSError as err:
            raise Error(f"failed to create directory '{self._outdir}': {err}") from None

        try:
            path = Deploy.find_app_data(bmname, Path("defs/acpower.yml"), appname=bmname,
                                        descr=f"{self.name} definitions file")
        except Error as err:
            raise Error(f"failed to build '{self.name}' tab: {err}") from None

        defs = YAML.load(path)
        self._statsfile = "acpower.raw.txt"
        self._metric_defs = defs[self.name]
        self._metric_colname = "P"
        self._time_defs = defs["Time"]
        self._time_colname = "T"
        self.title = self._metric_defs["title"]
        self.descr = self._metric_defs["descr"]
        self.smry_funcs = self._metric_defs["default_funcs"]

        self._plots = []
        s_path = self._outdir / f"{self.name}-scatter.html"
        s = _ScatterPlot.ScatterPlot(self._time_colname, self._metric_colname, s_path,
                                     self._time_defs["title"], self._metric_defs["title"],
                                     self._time_defs["short_unit"], self._metric_defs["short_unit"])
        self._plots.append(s)

        h_path = self._outdir / f"{self.name}-histogram.html"
        h = _Histogram.Histogram("P", h_path, self._metric_defs["title"],
                                 self._metric_defs["short_unit"])
        self._plots.append(h)

        self._read_stats(stats_paths)
