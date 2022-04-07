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

import logging
from wultlibs.htmlreport import _ScatterPlot, _Histogram

_LOG = logging.getLogger()


class PlotsBuilder:
    """
    This class provides the capability of generating plots and diagrams using the "Plotly"
    library for Metric Tabs.

    Public method overview:
    1. Build histograms and cumulative histograms.
        * build_histograms()
    2. Build scatter plots.
        * build_scatter()
    """

    def _base_unit(self, df, colname):
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

    def _create_hover_text(self, res, df, xcolname, ycolname):
        """
        Create and return a list containing hover text for every datapoint in the 'pandas.DataFrame'
        'df'.
        """

        _LOG.debug("Preparing hover text for '%s vs %s'", ycolname, xcolname)

        # The loop below creates the following objects.
        #  o colnames - names of the columns to include to the hover text.
        #  o fmts - the hover text format.
        colnames = []
        fmts = []
        for colname in self._hov_metrics[res.reportid]:
            if colname not in df:
                continue
            if colname in (xcolname, ycolname):
                # The X and Y datapoint values will be added automatically.
                continue

            defs = res.defs.info[colname]
            fmt = f"{colname}: {{"
            if defs["type"] == "float":
                fmt += ":.2f"
            fmt += "}"
            unit = defs.get("short_unit")
            if unit and unit not in colname:
                fmt += f"{unit}"

            colnames.append(colname)
            fmts.append(fmt)

        text = []
        fmt = "<br>".join(fmts)

        for row in df[colnames].itertuples(index=False):
            text.append(fmt.format(*row))

        return text

    @staticmethod
    def _get_base_si_unit(unit):
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

    def build_scatter(self, rsts, xmetric, ymetric):
        """
        Create scatter plots with 'xmetric' on the x-axis and 'ymetric' on the y-axis using data
        from 'rsts'. Returns the filepath of the generated plot HTML.
        """

        refdefs = rsts[0].defs
        xaxis_defs = refdefs.info.get(xmetric, {})
        yaxis_defs = refdefs.info.get(ymetric, {})
        xaxis_label = xaxis_defs.get("title", xmetric)
        yaxis_label = yaxis_defs.get("title", xmetric)
        xaxis_fsname = xaxis_defs.get("fsname", xaxis_label)
        yaxis_fsname = yaxis_defs.get("fsname", yaxis_label)
        xaxis_unit = self._get_base_si_unit(xaxis_defs.get("short_unit", ""))
        yaxis_unit = self._get_base_si_unit(yaxis_defs.get("short_unit", ""))

        fname = yaxis_fsname + "-vs-" + xaxis_fsname + ".html"
        outpath = self.outdir / fname

        plot = _ScatterPlot.ScatterPlot(xmetric, ymetric, outpath, xaxis_label=xaxis_label,
                                        yaxis_label=yaxis_label, xaxis_unit=xaxis_unit,
                                        yaxis_unit=yaxis_unit)

        for res in rsts:
            df = plot.reduce_df_density(res.df, res.reportid)
            text = self._create_hover_text(res, df, xmetric, ymetric)
            df[xmetric] = self._base_unit(df, xmetric)
            df[ymetric] = self._base_unit(df, ymetric)
            plot.add_df(df, res.reportid, text)

        plot.generate()
        return outpath

    def _build_histogram(self, rsts, xmetric, xbins, xaxis_label, xaxis_unit):
        """
        Create histograms  with 'xmetric' on the x-axis data from 'rsts'.  Returns the filepath of
        the generated plot HTML.
        """

        ymetric = "Count"
        xmetric_fsname = self._refdefs.info[xmetric]["fsname"]
        fname = ymetric + "-vs-" + xmetric_fsname + ".html"
        outpath = self.outdir / fname

        hst = _Histogram.Histogram(xmetric, outpath, xaxis_label=xaxis_label, xbins=xbins,
                                    xaxis_unit=xaxis_unit)

        for res in rsts:
            df = res.df
            df[xmetric] = self._base_unit(df, xmetric)
            hst.add_df(df, res.reportid)
        hst.generate()
        return outpath

    def _build_chistogram(self, rsts, xmetric, xbins, xaxis_label, xaxis_unit):
        """
        Create cumulative histograms  with 'xmetric' on the x-axis data from 'rsts'.  Returns the
        filepath of the generated plot HTML.
        """

        ymetric = "Percentile"
        xmetric_fsname = self._refdefs.info[xmetric]["fsname"]
        fname = ymetric + "-vs-" + xmetric_fsname + ".html"
        outpath = self.outdir / fname
        chst = _Histogram.Histogram(xmetric, outpath, xaxis_label=xaxis_label,
                                    xaxis_unit=xaxis_unit, xbins=xbins, cumulative=True)
        for res in rsts:
            df = res.df
            df[xmetric] = self._base_unit(df, xmetric)
            chst.add_df(df, res.reportid)
        chst.generate()
        return outpath

    def build_histograms(self, rsts, xmetric, hist=False, chist=False):
        """
        Create histograms and/or cumulative histograms with 'xmetric' on the x-axis using data from
        'rsts'. Returns the filepath of the generated plot HTML.
        """

        def get_xbins(xcolname):
            """Returns the 'xbins' dictinary for plotly's 'Histrogram()' method."""

            xmin, xmax = (float("inf"), -float("inf"))
            for res in rsts:
                # In case of non-numeric column there is only one x-value per bin.
                if not res.is_numeric(xcolname):
                    return {"size" : 1}

                xdata = self._base_unit(res.df, xcolname)
                xmin = min(xmin, xdata.min())
                xmax = max(xmax, xdata.max())

            return {"size" : (xmax - xmin) / 1000}

        xbins = get_xbins(xmetric)

        xaxis_defs = self._refdefs.info.get(xmetric, {})
        xaxis_label = xaxis_defs.get("title", xmetric)
        xaxis_unit = self._get_base_si_unit(xaxis_defs.get("short_unit", ""))

        ppaths = []
        if hist:
            ppaths.append(self._build_histogram(rsts, xmetric, xbins, xaxis_label, xaxis_unit))

        if chist:
            ppaths.append(self._build_chistogram(rsts, xmetric, xbins, xaxis_label, xaxis_unit))
        return ppaths

    def __init__(self, ref_defs, hov_metrics, opacity, outdir):
        """
        The class constructor. The arguments are as follows:
         * ref_defs - Defs dictionary from a 'RORawResult' instance. Used to find the correct units
                      to use in the plots.
         * hov_metrics - a mapping from report_id to metric names which should be included in the
                         hovertext of scatter plots.
         * opacity - opacity of plot points on scatter diagrams.
         * outdir - the directory path which will store the HTML plots.
        """

        self._hov_metrics = hov_metrics
        self._opacity = opacity
        self.outdir = outdir

        # The reference definitions - it contains helpful information about every CSV file column,
        # for example the title, units, and so on.
        self._refdefs = ref_defs
