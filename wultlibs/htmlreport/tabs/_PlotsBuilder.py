# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
#          Vladislav Govtva <vladislav.govtva@intel.com>

"""
This module provides the capability of generating plots and diagrams using the "Plotly" library for
Metric Tabs.
"""

class PlotsBuilder:
    """
    This class provides the capability of generating plots and diagrams using the "Plotly"
    library for Metric Tabs.
    """

    def base_unit(self, df, colname):
        """
        Convert columns with 'microsecond' units to seconds, and return the converted column.
        """

        # This is not generic, but today we have to deal only with microseconds, so this is good
        # enough.
        if self._refdefs.info[colname].get("unit") != "microsecond":
            return df[colname]

        base_colname = f"{colname}_base"
        if base_colname not in df:
            df.loc[:, base_colname] = df[colname] / 1000000
        return df[base_colname]

    @staticmethod
    def get_base_si_unit(unit):
        """
        Plotly will handle SI unit prefixes therefore we should provide only the base unit.
        Several defs list 'us' as the 'short_unit' which includes the prefix so should be
        reduced to just the base unit 's'.
        """

        # This is not generic, but today we have to deal only with microseconds, so this is good
        # enough.
        if unit == "us":
            return "s"
        return unit

    def __init__(self, rsts, hov_metrics, opacity, outdir):
        """
        The class constructor. The arguments are as follows:
         * rsts - list of 'RORawResult' objects representing the raw test results to generate the
                  plots for.
         * hov_metrics - a mapping from report_id to metric names which should be included in the
                         hovertext of scatter plots.
         * opacity - opacity of plot points on scatter diagrams.
         * outdir - the directory path which will store the HTML plots.
        """

        self._hov_metrics = hov_metrics
        self._opacity = opacity
        self.outdir = outdir

        self._rsts = rsts
        # The reference definitions - it contains helpful information about every CSV file column,
        # for example the title, units, and so on.
        self._refdefs = rsts[0].defs
