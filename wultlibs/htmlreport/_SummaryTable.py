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
This module provides the functionality for generating summary table dictionaries for HTML reports.
"""

from pepclibs.helperlibs.Exceptions import Error, ErrorExists, ErrorNotFound
from wultlibs import DFSummary


class SummaryTable:
    """
    This module provides the functionality for generating summary table dictionaries for HTML
    reports.

    The HTML summary table has the following format:

    | Title                     | Result Report ID 1 | Result Report ID 2 |
    |---------------------------|--------------------|--------------------|
    | Metric | Smry Func Name 1 | Smry Func Val 1    | Smry Func Val 1    |
    |        | Smry Func Name 2 | Smry Func Val 2    | Smry Func Val 2    |
    |--------|------------------|--------------------|--------------------|
    | Metric | Smry Func Name 1 | Smry Func Val 3    | Smry Func Val 3    |

    Public methods overview:
    1. Add metrics to the summary table.
       * 'add_metric()'
    2. Populate summary function cells by adding summary function names and values.
       * 'add_smry_func()'
    3. Generate the dictionary representing the summary table.
       * 'generate()'
    """

    def add_metric(self, metricname, unit=None, description=None, fmt="{}"):
        """
        Add a new metric to the summary table. Arguments are as follows:
         * metricname - name of the metric being added.
         * unit - unit the metric is measured in e.g. "s".
         * description - description of the metric (will be shown as hovertext).
         * fmt - format string. Decides how values will be formatted in the table.
        """

        if metricname in self.smrytbl["title"]:
            raise ErrorExists(f"Unable to add metric '{metricname}' as it has already been added.")

        self._units[metricname] = unit
        self._formats[metricname] = fmt

        self.smrytbl["title"][metricname] = {
            "metric": f"{metricname}, {unit}" if unit else metricname,
            "descr": description if description else "",
            "funcs": {}
        }

    def add_smry_func(self, reportid, metric, funcname, val):
        """
        Add summary functions to the summary table. Arguments are as follows:
         * reportid - the reportid of the results which this summary function summarises.
         * metric - name of the metric which this function summarises.
         * funcname - what kind of summary has been calculated. E.g. 'max', 'min' etc.
         * val - raw value of the summary function calculation.
        """

        if metric not in self.smrytbl["title"]:
            raise ErrorNotFound(f"Trying to add a summary function calculation for a metric which "
                                f"has not yet been added. Please add metric '{metric}' with "
                                f"'_SummaryTable.add_metric()'.")

        if reportid not in self.smrytbl["funcs"]:
            self.smrytbl["funcs"][reportid] = {}

        if metric not in self.smrytbl["funcs"][reportid]:
            self.smrytbl["funcs"][reportid][metric] = {}

        formatted_val = self._formats[metric].format(val)

        self.smrytbl["funcs"][reportid][metric][funcname] = {
            "raw_val": val,
            "formatted_val": formatted_val,
        }

        if funcname not in self.smrytbl["title"][metric]["funcs"]:
            func_descr = DFSummary.get_smry_func_descr(funcname)
            self.smrytbl["title"][metric]["funcs"][funcname] = func_descr

    def _get_hovertext(self, val, reportid, metric, funcname):
        """
        Generate hovertext for a summary function value. If this value is part of the reference set,
        the hovertext will reflect this. Otherwise, the hovertext will show the relative change
        between this value and the reference result. Arguments are as follows:
         * val - the raw value of the summary function.
         * reportid - the name of the column this value is contained by.
         * metric - the metric which this value is summarising.
         * funcname - the function which this value represents.
        """

        ref_reportid = next(iter(self.smrytbl["funcs"]))

        if reportid == ref_reportid:
            return "This is the reference result, other results are compared to this one."

        if metric not in self.smrytbl["funcs"][ref_reportid]:
            raise Error(f"Metric '{metric}' not added for reference set '{ref_reportid}'. Please "
                        f"add summary calculations with 'SummaryTable.add_smry_func_val()'.")

        if funcname not in self.smrytbl["funcs"][ref_reportid][metric]:
            raise Error(f"Calculation for function '{funcname}' for metric '{metric}' in set "
                        f"'{reportid}' not added. Please add summary calculation with "
                        f"'SummaryTable.add_smry_func_val()'.")

        ref_fdict = self.smrytbl["funcs"][ref_reportid][metric][funcname]
        change = val - ref_fdict["raw_val"]
        if ref_fdict["raw_val"]:
            percent = (change / ref_fdict["raw_val"]) * 100
        else:
            percent = change
        change = self._formats[metric].format(change) + self._units.get(metric, "")
        percent = f"{percent:.1f}%"
        return f"Change: {change} ({percent})"

    def generate(self):
        """
        Generate the finalised report summary table dictionary. The finalised dictionary has the
        following structure:

        {
            "title": {
                metric: {
                    "metric": metric_name (+ metric_unit),
                    "coldescr": metric_description,
                    "funcs": {
                        func_name: func_value
                    }
                }
            },
            "funcs": {
                reportid: {
                    metric: {
                        func_name: {
                            "raw_val": raw_val,
                            "formatted_val": formatted_val,
                            "hovertext": hovertext
                        }
                    }
                }
            }
        }
        """

        # Calculate hovertext now that all reference calculations have been added.
        for name, subdict in self.smrytbl["funcs"].items():
            for metric, mdict in subdict.items():
                for funcname, fdict in mdict.items():
                    fdict["hovertext"] = self._get_hovertext(fdict["raw_val"], name, metric,
                                                             funcname)
        return self.smrytbl

    def __init__(self):
        """The class constructor."""

        self.smrytbl = {}
        self.smrytbl["title"] = {}
        self.smrytbl["funcs"] = {}

        # A dictionary mapping from metric name to metric unit.
        self._units = {}
        # A dictionary mapping from metric name to metric format string.
        self._formats = {}
