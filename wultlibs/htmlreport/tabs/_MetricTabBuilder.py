# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
#          Vladislav Govtva <vladislav.govtva@intel.com>
#          Adam Hawley <adam.james.hawley@intel.com>

"""
This module defines what is expected by the JavaScript side when adding a Metric tab to HTML
reports.
"""

from pepclibs.helperlibs.Exceptions import Error
from pepclibs.helperlibs import Trivial
from wultlibs.htmlreport import _SummaryTable
from wultlibs.htmlreport.tabs import _PlotsBuilder, _Tabs


class MetricTabBuilder:
    """
    This class provides the functionality to build '_Tabs.DTabDC' instances which contain data
    for a given metric.

    Public methods overview:
    1. Add a summary table to the tab.
       * 'add_smrytbl()'
    2. Add plots to the tab.
       * 'add_plots()'
    3. Generate '_Tabs.DTabDC' instance.
       * 'get_tab()'
    """

    def add_smrytbl(self, smry_metrics, smry_funcs):
        """
        Summaries table includes values like average and median values for a single metric (column).
        It "summarizes" the metric. This function creates and dumps the summary table for this tab.
        This means that it includes summaries of all the metrics referenced in this tab.
        """

        smry_tbl = _SummaryTable.SummaryTable()

        # Summaries are calculated only for numeric metrics. Tab metric name is represented by
        # 'smrytblpath.name', this should come first.
        metrics = [self.tabname] if self._refres.is_numeric(self.tabname) else []
        metrics += [metric for metric in smry_metrics if self._refres.is_numeric(metric)]
        # Dedupe the list so that each metric only appears once.
        metrics = Trivial.list_dedup(metrics)

        for metric in metrics:
            # Create row in the summary table for each metric.
            defs = self._refres.defs.info[metric]
            fmt = "{:.2f}" if defs["type"] == "float" else None
            smry_tbl.add_metric(metric, defs["short_unit"], defs["descr"], fmt)

            # Select only those functions that are present in all test results. For example, 'std'
            # will not be present if the result has only one datapoint. In this case, we need to
            # exclude the 'std' function.
            funcs = []
            for funcname in smry_funcs:
                if all(res.smrys[metric].get(funcname) for res in self._rsts):
                    funcs.append(funcname)

            # Populate each row with summary functions for each result.
            for res in self._rsts:
                for funcname in funcs:
                    val = res.smrys[metric][funcname]
                    smry_tbl.add_smry_func(res.reportid, metric, funcname,  val)
        try:
            smry_tbl.generate(self._smrytblpath)
        except Error as err:
            raise Error("Failed to generate summary table.") from err

    def _generate_scatter_plots(self, plot_axes):
        """Generate the scatter plots."""

        ppaths = []
        for xcolname, ycolname in plot_axes:
            ppath = self._pbuilder.build_scatter(self._rsts, xcolname, ycolname)
            ppaths.append(ppath)
        return ppaths

    def _generate_histograms(self, hist, chist):
        """Generate the histograms."""

        ppaths = []

        hist = self.tabname in set(hist)
        chist = self.tabname in set(chist)
        ppaths += self._pbuilder.build_histograms(self._rsts, self.tabname , hist=hist, chist=chist)
        return ppaths

    def add_plots(self, plot_axes, hist, chist, hover_metrics):
        """
        Generate and add plots to the tab.
        Arguments are as follows:
         * plot_axes - tuples of axes to create scatter plots for in the format (xaxis, yaxis).
         * hist - metrics to create histograms for.
         * chist - metrics to create cumulative histograms for.
         * hover_metrics - specifies which metrics hovertext in plots should be generated for.
        """

        # The diagram/histogram transparency level. It is helpful to have some transparency in case
        # there are several test results rendered on the same diagram.
        opacity = 0.8 if len(self._rsts) > 1 else 1

        self._pbuilder = _PlotsBuilder.PlotsBuilder(self._refres.defs, hover_metrics, opacity,
                                                    self.outdir)

        ppaths = []
        ppaths += self._generate_scatter_plots(plot_axes)
        ppaths += self._generate_histograms(hist, chist)
        self._ppaths = ppaths

    def get_tab(self):
        """
        Returns a '_Tabs.DTabDC' instance representative of the data already added to the class.
        """

        ppaths = [p.relative_to(self._basedir) for p in self._ppaths]
        smrytblpath = self._smrytblpath.relative_to(self._basedir)

        return _Tabs.DTabDC(self.tabname, ppaths, smrytblpath)

    def __init__(self, tabname, rsts, outdir):
        """
        The class constructor. Arguments as follows:
         * tabname - the metric which this tab represents.
         * rsts - sets of results containing the data to represent in this tab.
         * outdir - the output directory, in which to create the tab sub-dictionary which will
                    contain plot HTML files and summary table files.
        """

        self.tabname = tabname
        self._rsts = rsts
        self._refres = rsts[0]
        self._basedir = outdir
        self._fsname = self._refres.defs.info[tabname]["fsname"]
        self.outdir = outdir / self._fsname
        self._pbuilder = None
        self._ppaths = []

        self._smrytblpath = self.outdir / "summary-table.txt"

        try:
            self.outdir.mkdir(parents=True, exist_ok=True)
        except OSError as err:
            raise Error(f"failed to create directory '{self.outdir}': {err}") from None
