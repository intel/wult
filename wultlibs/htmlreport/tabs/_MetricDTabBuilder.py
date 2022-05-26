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

import logging
from pepclibs.helperlibs.Exceptions import Error
from pepclibs.helperlibs import Trivial
from wultlibs import DFSummary
from wultlibs.htmlreport import _SummaryTable
from wultlibs.htmlreport.tabs import _DTabBuilder, _PlotsBuilder

_LOG = logging.getLogger()

class MetricDTabBuilder(_DTabBuilder.DTabBuilder):
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

    def add_smrytbl(self, smry_metrics, smry_funcs=None):
        """
        Summaries table includes values like average and median values for a single metric (column).
        It "summarizes" the metric. This function creates and dumps the summary table for this tab.
        This means that it includes summaries of all the metrics referenced in this tab.
        """

        smry_tbl = _SummaryTable.SummaryTable()
        if smry_funcs is None:
            smry_funcs = DFSummary.get_smry_funcs()

        # Summaries are calculated only for numeric metrics. Tab metric name is represented by
        # 'smrytblpath.name', this should come first.
        metrics = [self._tabmetric] if self._refres.is_numeric(self._tabmetric) else []
        metrics += [metric for metric in smry_metrics if self._refres.is_numeric(metric)]
        # Dedupe the list so that each metric only appears once.
        metrics = Trivial.list_dedup(metrics)

        for metric in metrics:
            # Create row in the summary table for each metric.
            mdef = self._refres.defs.info[metric]
            fmt = "{:.2f}" if mdef["type"] == "float" else None
            smry_tbl.add_metric(mdef["title"], mdef["short_unit"], mdef["descr"], fmt)

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
                    smry_tbl.add_smry_func(res.reportid, mdef["title"], funcname,  val)
        try:
            smry_tbl.generate(self.smry_path)
        except Error as err:
            raise Error("Failed to generate summary table.") from err

    def _add_scatter(self, xdef, ydef, hover_defs=None):
        """
        Create a scatter plot with the metric represented by 'xdef' on the X-axis and the metric
        represented by 'ydef' on the Y-axis using data from 'rsts' which is provided to the class
        during initialisation. Returns the filepath of the generated plot HTML. Arguments are the
        same as in '_DTabBuilder._add_scatter()'.
        """

        for mdef in xdef, ydef:
            mdef["short_unit"] = self._pbuilder.get_base_si_unit(mdef["short_unit"])
            for res in self._rsts:
                res.df[mdef["name"]] = self._pbuilder.base_unit(res.df, mdef["name"])

        super()._add_scatter(xdef, ydef, hover_defs)
        return self._ppaths[-1]

    def _generate_scatter_plots(self, plot_axes):
        """Generate the scatter plots."""

        ppaths = []

        hover_defs = {}
        for reportid, metrics in self._hover_metrics.items():
            hover_defs[reportid] = [self._refres.defs.info[m] for m in metrics]

        for xcolname, ycolname in plot_axes:
            if not all(xcolname in res.df and ycolname in res.df for res in self._rsts):
                _LOG.warning("skipping scatter plot '%s' vs '%s' since not all results have data "
                             "for both.", ycolname, xcolname)
                continue
            xdef = self._refres.defs.info[xcolname]
            ydef = self._refres.defs.info[ycolname]
            ppath = self._add_scatter(xdef, ydef, hover_defs)
            ppaths.append(ppath)
        return ppaths

    def _generate_histograms(self, hist=None, chist=None):
        """Generate the histograms."""

        ppaths = []

        if hist is not None:
            hist = self._tabmetric in set(hist)
        if chist is not None:
            chist = self._tabmetric in set(chist)

        ppaths += self._pbuilder.build_histograms(self._tabmetric, hist, chist)
        return ppaths

    def add_plots(self, plot_axes=None, hist=None, chist=None, hover_defs=None):
        """
        Generate and add plots to the tab.
        Arguments are as follows:
         * plot_axes - tuples of axes to create scatter plots for in the format (xaxis, yaxis).
         * hist - metrics to create histograms for, defaults to 'None'.
         * chist - metrics to create cumulative histograms for, defaults to 'None'.
         * hover_defs - specifies which metrics hovertext in plots should be generated for.
                        Defaults to the metrics given to the constructor as 'hover_metrics'.
        """

        if plot_axes is None and hist is None and chist is None:
            raise Error("BUG: no arguments provided for 'add_plots()', unable to generate plots.")

        if hover_defs is None:
            hover_metrics = self._hover_metrics
        else:
            metric_names = [mdef["name"] for mdef in hover_defs]
            hover_metrics = {reportid: metric_names for reportid in self._rsts}

        # The diagram/histogram transparency level. It is helpful to have some transparency in case
        # there are several test results rendered on the same diagram.
        opacity = 0.8 if len(self._rsts) > 1 else 1

        self._pbuilder = _PlotsBuilder.PlotsBuilder(self._rsts, hover_metrics, opacity,
                                                    self._outdir)

        ppaths = []
        if plot_axes is not None:
            ppaths += self._generate_scatter_plots(plot_axes)

        ppaths += self._generate_histograms(hist, chist)
        self._ppaths = ppaths

    def __init__(self, rsts, outdir, metric_def, basedir=None, hover_metrics=None):
        """
        The class constructor. Arguments as follows:
         * rsts - sets of results containing the data to represent in this tab.
         * outdir - the output directory, in which to create the tab sub-dictionary which will
                    contain plot HTML files and summary table files.
         * metric_def - dictionary containing the definition for the metric represented by this tab.
         * basedir - base directory of the report. All paths should be made relative to this.
                     Defaults to 'outdir'.
         * hover_metrics - a mapping from report_id to metric names which should be included in the
                           hovertext of scatter plots.
        """

        self._tabmetric = metric_def["name"]
        self._rsts = rsts
        self._refres = rsts[0]
        self._pbuilder = None
        self._ppaths = []
        self._hover_metrics = hover_metrics

        reports = {res.reportid: res.df for res in rsts}
        super().__init__(reports, outdir, metric_def, basedir)
