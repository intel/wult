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

from pepclibs.helperlibs import Trivial
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.htmlreport import _SummaryTable
from statscollectlibs.htmlreport.tabs import _DTabBuilder

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

    def add_smrytbl(self, smry_funcs, defs):
        """
        Overrides 'super().add_smrytbl()', refer to that method for more information. Results have
        summaries pre-calculated therefore we do not have to calculate them in this method as the
        parent class does.
        """

        # Summaries are calculated only for numeric metrics. Tab metric name is represented by
        # 'smrytblpath.name', this should come first if it is included in 'smry_funcs'.
        tab_metric = self._tabmdef["name"]
        if tab_metric in smry_funcs and self._refres.is_numeric(tab_metric):
            metrics = [tab_metric]
        else:
            metrics = []

        metrics += [metric for metric in smry_funcs if self._refres.is_numeric(metric)]

        # Dedupe the list so that each metric only appears once.
        deduped_mdefs = [defs.info[metric] for metric in Trivial.list_dedup(metrics)]

        self._smrytbl = _SummaryTable.SummaryTable()

        for mdef in deduped_mdefs:
            # Create row in the summary table for each metric.
            fmt = "{:.2f}" if mdef["type"] == "float" else None
            self._smrytbl.add_metric(mdef["title"], mdef["short_unit"], mdef["descr"], fmt)

            # Select only those functions that are present in at least one test result. For example,
            # 'std' will not be present if the result has only one datapoint. If no results have a
            # value for 'std', we need to exclude the 'std' function entirely.
            funcs = []
            for funcname in smry_funcs[mdef["name"]]:
                if any(res.smrys[mdef["name"]].get(funcname) is not None for res in self._rsts):
                    funcs.append(funcname)

            # Populate each row with summary functions for each result.
            for res in self._rsts:
                for funcname in funcs:
                    if mdef["name"] in res.smrys:
                        val = res.smrys[mdef["name"]][funcname]
                    else:
                        val = None
                    self._smrytbl.add_smry_func(res.reportid, mdef["title"], funcname, val)
        try:
            self._smrytbl.generate(self.smry_path)
        except Error as err:
            raise Error("Failed to generate summary table.") from err

    def _add_histogram(self, mdef, cumulative=False, xbins=None):
        """Extends 'super()._add_histogram()' by adding custom binning."""

        if xbins is None:
            # Calculate custom bins.
            xmin, xmax = (float("inf"), -float("inf"))
            for res in self._rsts:
                if not mdef["name"] in res.df:
                    continue

                # In case of non-numeric column there is only one x-value per bin.
                if not res.is_numeric(mdef["name"]):
                    return {"size" : 1}

                xdata = res.df[mdef["name"]]
                xmin = min(xmin, xdata.min())
                xmax = max(xmax, xdata.max())

            xbins = {"size" : (xmax - xmin) / 1000}

        return super()._add_histogram(mdef, cumulative, xbins)

    def __init__(self, rsts, outdir, metric_def, basedir=None):
        """
        The class constructor. Arguments as follows:
         * rsts - sets of results containing the data to represent in this tab.
         * outdir - the output directory, in which to create the tab sub-dictionary which will
                    contain plot HTML files and summary table files.
         * metric_def - dictionary containing the definition for the metric represented by this tab.
         * basedir - base directory of the report. All paths should be made relative to this.
                     Defaults to 'outdir'.
        """

        self._tabmdef = metric_def
        self._rsts = rsts
        self._refres = rsts[0]

        reports = {res.reportid: res.df for res in rsts}
        super().__init__(reports, outdir, metric_def, basedir)
