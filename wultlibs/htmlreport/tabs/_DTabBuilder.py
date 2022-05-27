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

import logging
from pepclibs.helperlibs.Exceptions import Error
from wultlibs.htmlreport import _SummaryTable, _ScatterPlot, _Histogram
from wultlibs import DFSummary
from wultlibs.htmlreport.tabs import _Tabs

_LOG = logging.getLogger()

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

        smrytbl = _SummaryTable.SummaryTable()
        if smry_funcs is None:
            smry_funcs = ("nzcnt", "max", "99.999%", "99.99%", "99.9%", "99%", "med", "avg", "min",
                          "std")

        for metric in smry_metrics:
            smrytbl.add_metric(metric["title"], metric["short_unit"], metric["descr"], fmt="{:.2f}")

            for rep, df in self._reports.items():
                # Only use a summary function if it is included in the default funcs for this
                # metric.
                default_funcs = set(metric["default_funcs"])
                smry_funcs = DFSummary.filter_smry_funcs(smry_funcs, default_funcs)

                smry_dict = DFSummary.calc_col_smry(df, metric["name"], smry_funcs)
                for fname in smry_funcs:
                    smrytbl.add_smry_func(rep, metric["title"], fname, smry_dict[fname])

        smrytbl.generate(self.smry_path)

    def get_tab(self):
        """
        Returns a '_Tabs.DTabDC' instance which contains an aggregate of all of the data given to
        the class constructor in 'reports', provided to the class constructor. This '_Tabs.DTabDC'
        can then be used to populate an HTML tab.
        """

        ppaths = [p.relative_to(self._basedir) for p in self._ppaths]
        smry_path = self.smry_path.relative_to(self._basedir)

        return _Tabs.DTabDC(self.title, ppaths, smry_path)

    def _add_scatter(self, xdef, ydef, hover_defs=None):
        """
        Helper function for 'add_plots()'. Add a scatter plot to the report. Arguments are as
        follows:
         * xdef - definitions dictionary for the metric on the X-axis.
         * ydef - definitions dictionary for the metric on the Y-axis.
         * hover_defs - a mapping between report id and lists of definitions dictionaries which
                        represent metrics for which hovertext should be generated for that result.
                        By default, only includes hovertext for 'xdef' and 'ydef'.
        """

        # Initialise scatter plot.
        fname = f"{ydef['fsname']}-vs-{xdef['fsname']}.html"
        s_path = self._outdir / fname
        s = _ScatterPlot.ScatterPlot(xdef["name"], ydef["name"], s_path, xdef["title"],
                                     ydef["title"], xdef["short_unit"], ydef["short_unit"])

        for reportid, df in self._reports.items():
            if hover_defs is not None:
                hovertext = s.get_hover_text(hover_defs[reportid], df)
            else:
                hovertext = None
            s.add_df(s.reduce_df_density(df, reportid), reportid, hovertext)

        s.generate()
        self._ppaths.append(s_path)

    def _add_histogram(self, mdef, cumulative=False, xbins=None):
        """
        Helper function for 'add_plots()'. Add a histogram to the report for metric with
        definitions dictionary 'mdef'. See '_Histogram.Histogram' for details of 'cumulative' and
        'xbins' arguments.
        """

        # Initialise histogram.
        if cumulative:
            h_path = self._outdir / f"Percentile-vs-{mdef['fsname']}.html"
        else:
            h_path = self._outdir / f"Count-vs-{mdef['fsname']}.html"

        h = _Histogram.Histogram(mdef["name"], h_path, mdef["title"], mdef["short_unit"],
                                 cumulative=cumulative, xbins=xbins)

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
         * hover_defs - a mapping from 'reportid' to defs of metrics which should be included in
                        the hovertext of scatter plots.
        """

        if plot_axes is None and hist is None and chist is None:
            raise Error("BUG: no arguments provided for 'add_plots()', unable to generate plots.")

        if plot_axes is None:
            plot_axes = []
        if hist is None:
            hist = []
        if chist is None:
            chist = []

        sdfs = self._reports.values()
        for xdef, ydef in plot_axes:
            if not all(xdef["name"] in sdf and ydef["name"] in sdf for sdf in sdfs):
                _LOG.warning("skipping scatter plot '%s' vs '%s' since not all results have data "
                             "for both.", ydef["name"], xdef["name"])
                continue
            self._add_scatter(xdef, ydef, hover_defs)

        for mdef in hist:
            if not all(mdef["name"] in sdf for sdf in sdfs):
                _LOG.warning("skipping histogram for metric '%s' since not all results have data "
                             "for this metric.", mdef["name"])
                continue
            self._add_histogram(mdef)

        for mdef in chist:
            if not all(mdef["name"] in sdf for sdf in sdfs):
                _LOG.warning("skipping cumulative histogram for metric '%s' since not all results "
                             "have data for this metric.", mdef["name"])
                continue
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
        self.title = metric_def["name"]
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
