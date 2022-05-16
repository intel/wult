# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""
This module provides the capability of populating a data tab.
"""

from pepclibs.helperlibs.Exceptions import Error
from wultlibs.htmlreport import _SummaryTable, _ScatterPlot, _Histogram
from wultlibs import DFSummary
from wultlibs.htmlreport.tabs import _Tabs

class DTabBuilder:
    """
    This base class provides the capability of populating a data tab.

    Public methods overview:
    1. Add a summary table to the tab.
       * 'add_smrytbl()'
    2. Add plots to the tab.
       * 'add_plots()'
    3. Generate a '_Tabs.DTabDC' instance containing plots added with 'add_plots()' and a summary
       table added with 'add_smrytbl()'.
       * 'get_tab()'
    """

    def add_smrytbl(self, smry_metrics, smry_funcs=None):
        """
        Construct a 'SummaryTable' to summarise 'smry_funcs' for 'smry_metrics' in the results given
        to the constructor as 'reports'. Note, 'smry_metrics' should be a list of definitions
        dictionaries for the metrics which should be included in the summary table.
        """

        # List of functions to provide in the summary tables.
        if smry_funcs is None:
            smry_funcs = ("nzcnt", "max", "99.999%", "99.99%", "99.9%", "99%", "med", "avg", "min",
                          "std")

        smrytbl = _SummaryTable.SummaryTable()

        for metric in smry_metrics:
            smrytbl.add_metric(metric["title"], metric["short_unit"], metric["descr"], fmt="{:.2f}")

            for rep, df in self._reports.items():
                # Only use a summary function if it is included in the default funcs for this
                # metric.
                default_funcs = set(metric["default_funcs"])
                smry_funcs = DFSummary.filter_smry_funcs(smry_funcs, default_funcs)

                smry_dict = DFSummary.calc_col_smry(df, metric["metric"], smry_funcs)
                for fname in smry_funcs:
                    smrytbl.add_smry_func(rep, metric["title"], fname, smry_dict[fname])

        smrytbl.generate(self.smry_path)

    def get_tab(self):
        """
        Returns a '_Tabs.DTabDC' instance which contains an aggregate of all of the data given to
        the class constructor in 'reports', provided to the class constructor. This '_Tabs.DTabDC'
        can then be used to populate an HTML tab.
        """

        plotpaths = []
        for path in self._ppaths:
            plotpaths.append(path.relative_to(self._basedir))

        return _Tabs.DTabDC(self.title, plotpaths, self.smry_path.relative_to(self._basedir))

    def _add_scatter(self, xdef, ydef, hover_defs=None):
        """
        Helper function for 'add_plots()'. Add a scatter plot to the report. Arguments are as
        follows:
         * xdef - definitions dictionary for the metric on the X-axis.
         * ydef - definitions dictionary for the metric on the Y-axis.
         * hover_defs - a list of definitions dictionaries which represent metrics for which
                        hovertext should be generated. By default, only includes hovertext for
                        'xdef' and 'ydef'.
        """

        # Initialise scatter plot.
        fname = f"{ydef['fsname']}-vs-{xdef['fsname']}.html"
        s_path = self._outdir / fname
        s = _ScatterPlot.ScatterPlot(xdef["metric"], ydef["metric"], s_path, xdef["title"],
                                     ydef["title"], xdef["short_unit"], ydef["short_unit"])

        for reportid, df in self._reports.items():
            if hover_defs is not None:
                hovertext = s.get_hover_text(hover_defs, df)
            else:
                hovertext = None
            s.add_df(s.reduce_df_density(df, reportid), reportid, hovertext)

        s.generate()
        self._ppaths.append(s_path)

    def _add_histogram(self, mdef, cumulative=False):
        """
        Helper function for 'add_plots()'. Add a histogram to the report for metric with
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

        h.generate()
        self._ppaths.append(h_path)

    def add_plots(self, plot_axes=None, hist=None, chist=None, hover_defs=None):
        """
        Initialise the plots and populate them using the 'pandas.DataFrame' objects in 'reports'
        which was provided to the class constructor. Arguments are as follows:
         * plot_axes - tuples of defs which represent axes to create scatter plots for in the format
                       (xdef, ydef).
         * hist - a list of defs which represent metrics to create histograms for.
         * chist - a list of defs which represent metrics to create cumulative histograms for.
         * hover_defs - specifies which metrics hovertext in plots should be generated for.
        """

        if plot_axes is None and hist is None and chist is None:
            raise Error("BUG: no arguments provided for 'add_plots()', unable to generate plots.")

        if plot_axes is None:
            plot_axes = []
        if hist is None:
            hist = []
        if chist is None:
            chist = []

        for xdef, ydef in plot_axes:
            self._add_scatter(xdef, ydef, hover_defs)

        for mdef in hist:
            self._add_histogram(mdef)

        for mdef in chist:
            self._add_histogram(mdef, cumulative=True)

    def __init__(self, reports, outdir, metric_def, basedir=None):
        """
        The class constructor. Adding a data tab will create a sub-directory named after the metric
        in 'metric_def' and store plots and the summary table in it. Arguments are as follows:
         * reports - dictionary containing the data for each report:
                     '{reportid: dataframe}'
         * outdir - the output directory in which to create the 'metricname' sub-directory.
         * metric_def - dictionary containing the definition for this metric.
         * basedir - base directory of the report. All paths should be made relative to this.
                     Defaults to 'outdir'.
        """

        self._reports = reports
        # File system-friendly tab name.
        self._fsname = metric_def["fsname"]
        self.title = metric_def["title"]
        self._outdir = outdir / self._fsname
        self.smry_path = self._outdir / "summary-table.txt"

        if basedir is None:
            self._basedir = outdir
        else:
            self._basedir = basedir

        try:
            self._outdir.mkdir(parents=True, exist_ok=True)
        except OSError as err:
            raise Error(f"failed to create directory '{self._outdir}': {err}") from None

        # Paths of plots generated for this tab.
        self._ppaths = []
