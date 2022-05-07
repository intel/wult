# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""
This module provides the capability of populating a statistics data tab.
"""

from pepclibs.helperlibs.Exceptions import Error
from wultlibs.htmlreport import _SummaryTable, _ScatterPlot, _Histogram
from wultlibs import DFSummary
from wultlibs.htmlreport.tabs import _Tabs

class DTabBuilder:
    """
    This base class provides the capability of populating a statistics data tab.

    Public methods overview:
    1. Generate a '_Tabs.DTabDC' instance containing plots and a summary table which represent all
       of the statistics found during initialisation.
       * 'get_tab()'
    """

    def _prepare_smrys_tbl(self):
        """Construct a 'SummaryTable' to summarise the statistics added with '_add_stats()'."""

        smrytbl = _SummaryTable.SummaryTable()

        smrytbl.add_metric(self.title, self._metric_def["short_unit"], self.descr,
                           fmt="{:.2f}")

        for rep, df in self._reports.items():
            smry_dict = DFSummary.calc_col_smry(df, self._metric, self.smry_funcs)
            for fname in self.smry_funcs:
                smrytbl.add_smry_func(rep, self.title, fname, smry_dict[fname])

        smrytbl.generate(self.smry_path)

    def get_tab(self):
        """
        Returns a '_Tabs.DTabDC' instance which contains an aggregate of all of the statistics found
        in 'stats_paths', provided to the class constructor. This '_Tabs.DTabDC' can then be used to
        populate an HTML tab.
        """

        plotpaths = []
        for plot in self._plots:
            plot.generate()
            plotpaths.append(plot.outpath.relative_to(self._basedir))

        try:
            self._prepare_smrys_tbl()
        except Exception as err:
            raise Error(f"failed to generate summary table: {err}") from None

        return _Tabs.DTabDC(self.title, plotpaths, self.smry_path.relative_to(self._basedir))

    def _add_scatter(self, xdef, ydef):
        """
        Helper function for '_init_plots()'. Add a scatter plot to the report. Arguments are as
        follows:
         * xdef - definitions dictionary for the metric on the X-axis.
         * ydef - definitions dictionary for the metric on the Y-axis.
        """

        # Initialise scatter plot.
        fname = f"{ydef['fsname']}-vs-{xdef['fsname']}.html"
        s_path = self._outdir / fname
        s = _ScatterPlot.ScatterPlot(xdef["metric"], ydef["metric"], s_path, xdef["title"],
                                     ydef["title"], xdef["short_unit"], ydef["short_unit"])

        for reportid, df in self._reports.items():
            s.add_df(s.reduce_df_density(df, reportid), reportid)

        self._plots.append(s)

    def _add_histogram(self, mdef, cumulative=False):
        """
        Helper function for '_init_plots()'. Add a histogram to the report for metric with
        definitions dictionary 'mdef'.
        """

        # Initialise histogram.
        if cumulative:
            h_path = self._outdir / f"Percentile-vs-{mdef['fsname']}.html"
        else:
            h_path = self._outdir / f"Count-vs-{mdef['fsname']}.html"

        h = _Histogram.Histogram(mdef["metric"], h_path, mdef["title"], mdef["short_unit"],
                                 cumulative=cumulative)

        for reportid, df in self._reports.items():
            h.add_df(df, reportid)

        self._plots.append(h)

    def _init_plots(self, plot_axes=None, hist=None, chist=None):
        """
        Initialise the plots and populate them using the 'pandas.DataFrame' objects in
        'self._reports'. Arguments are as follows:
         * plot_axes - tuples of defs which represent axes to create scatter plots for in the format
                       (xdef, ydef).
         * hist - a list of defs which represent metrics to create histograms for.
         * chist - a list of defs which represent metrics to create cumulative histograms for.
        """

        if (plot_axes is None) and (hist is None) and (chist is None):
            raise Error("no arguments provided for '_init_plots()', unable to generate plots.")

        if plot_axes is None:
            plot_axes = []
        if hist is None:
            hist = []
        if chist is None:
            chist = []

        for xdef, ydef in plot_axes:
            self._add_scatter(xdef, ydef)

        for mdef in hist:
            self._add_histogram(mdef)

        for mdef in chist:
            self._add_histogram(mdef, cumulative=True)

    def __init__(self, reports, outdir, basedir, metric_def, time_def):
        """
        The class constructor. Adding a stats tab will create a 'metricname' sub-directory and
        store plots and the summary table in it. Arguments are as follows:
         * reports - dictionary containing the statistics data for each report:
                     '{reportid: stats_df}'
         * outdir - the output directory in which to create the 'metricname' sub-directory.
         * basedir - base directory of the report. All paths should be made relative to this.
         * metric_def - dictionary containing the definition for this metric.
         * time_def - dictionary containing the definition for the elapsed time.
        """

        # File system-friendly tab name.
        self._fsname = metric_def["fsname"]
        self._metric = metric_def["metric"]
        self._basedir = basedir
        self._outdir = outdir / self._fsname
        self.smry_path = self._outdir / "summary-table.txt"

        try:
            self._outdir.mkdir(parents=True, exist_ok=True)
        except OSError as err:
            raise Error(f"failed to create directory '{self._outdir}': {err}") from None

        self._metric_def = metric_def
        self._time_def = time_def
        self._time_metric = time_def["metric"]
        self.title = self._metric_def["title"]
        self.descr = self._metric_def["descr"]

        # List of functions to provide in the summary tables.
        smry_funcs = ("nzcnt", "max", "99.999%", "99.99%", "99.9%", "99%", "med", "avg", "min",
                      "std")

        # Only use a summary function if it is included in the default funcs for this statistic.
        default_funcs = set(self._metric_def["default_funcs"])
        self.smry_funcs = DFSummary.filter_smry_funcs(smry_funcs, default_funcs)

        # Reduce 'reports' to only the metric and time columns which are needed for this tab.
        self._reports = {}
        for reportid, df in reports.items():
            if self._metric in df:
                self._reports[reportid] = df[[self._metric, self._time_metric]].copy()

        if not self._reports:
            raise Error(f"failed to generate '{self.title}' tab: no data under column"
                        f"'{self._metric}' provided.")


        self._plots = []
        try:
            self._init_plots([(self._time_def, self._metric_def)], [self._metric_def])
        except Exception as err:
            raise Error(f"failed to initialise plots: {err}") from None
