# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
#          Vladislav Govtva <vladislav.govtva@intel.com>

"""
This module provides the capability of generating plots and diagrams using the "Plotly" library for
Metric Tabs.
"""

import logging
import numpy
import pandas
from wultlibs.htmlreport import _ScatterPlot, _Histogram

_LOG = logging.getLogger()


def _colname_to_fname(colname):
    """
    Turn column name 'colname' into a file name, replacing problematic characters that browsers
    may refuse.
    """

    return colname.replace("%", "_pcnt").replace("/", "-to-")

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
            df[base_colname] = df[colname] / 1000000
        return df[base_colname]

    def _create_hover_text(self, res, df, xcolname, ycolname):
        """
        Create and return a list containing hover text for every datapoint in the 'df' dataframe.
        """

        _LOG.debug("Preparing hover text for '%s vs %s'", xcolname, ycolname)

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
    def _reduce_df_density(res, xcolname, ycolname):
        """
        This function reduces the density of the dataframe belonging to the test result 'res'. The
        density reduction is only used for the scatter plot. The problem it solves is that that
        there are thousands and thousands of "uninteresting" datapoints per one "interesting"
        datapoint (an outlier). And if the total amount of datapoints is huge (say, 10000000), a web
        browser simply cannot show it because the plot is too large (gigabytes). So what we are
        trying to do is to:
        1. Split the scatter plot on NxN squares, where N is the bins count.
        2. Calculate how many datapoints each square contains (the 2D histogram).
        3. If a square has few datapoints, these are outliers, we leave them alone. "Few" is defined
           by the "low threshold" value.
        4. The for the squares containing many datapoints, we do the reduction. We basically drop
           the datapoints and leave maximum "high threshold" amount of datapoints. And we try to
           scale the amount of datapoints left proportionally to the original value between the
           values of ("low threshold", "high threshold").
        """

        def _map_non_numeric(colname):
            """
            In order to reduce density for a non-numeric column, we need to map that column to
            unique numbers, find datapoints to keep, and then reduce the dataframe. This function
            does exactly that - maps a non-numeric column 'colname' to unique numbers and returns
            the corresponding pandas series object.
            """

            if not res.is_numeric(colname):
                num_rmap = {name : idx for idx, name in enumerate(df[colname].unique())}
                return df[colname].map(num_rmap)

            return df[colname]

        lo_thresh = 20
        hi_thresh = 200
        bins_cnt = 100

        _LOG.info("Reducing density for report ID '%s', diagram '%s-vs-%s'",
                  res.reportid, ycolname, xcolname)

        # Create a new dataframe with just the X- and Y-columns, which we'll be reducing. It should
        # be a bit more optimal than reducing the bigger original dataframe.
        df = res.df[[xcolname, ycolname]]

        xdata = _map_non_numeric(xcolname)
        ydata = _map_non_numeric(ycolname)

        # Crete a histogram for the columns in question.
        hist, xbins, ybins = numpy.histogram2d(xdata, ydata, bins_cnt)
        # Turn the histogram into a dataframe.
        hist = pandas.DataFrame(hist, dtype=int)

        hist_max = hist.max().max()
        if hist_max <= lo_thresh:
            _LOG.debug("cancel density reduction: max frequency for '%s vs %s' is %d, but scaling "
                       "threshold is %d", xcolname, ycolname, hist_max, lo_thresh)
            return res.df

        # The histogram scaling factor.
        factor = hi_thresh / hist_max

        # Scale the histogram down. Do not change the buckets with few datapoints (< lo_thresh),
        # scale down all the other buckets so that they would have maximum 'hi_thresh' datapoints.
        scaling_func = lambda f: max(int(f * factor), lo_thresh) if f > lo_thresh else f
        hist = hist.applymap(scaling_func)

        # Create a copy of the histogram, but populate it with zeroes.
        cur_hist = pandas.DataFrame(0, columns=hist.columns, index=hist.index)

        # Calculate bin indexes for all the X and Y values in the dataframe.
        xindeces = numpy.digitize(xdata, xbins[:-1])
        yindeces = numpy.digitize(ydata, ybins[:-1])

        # This is how many datapoints we are going to have in the reduced dataframe.
        reduced_datapoints_cnt = hist.values.sum()
        _LOG.debug("reduced datapoints count is %d", reduced_datapoints_cnt)

        # Here we'll store 'df' indexes of the rows that will be included into the resulting
        # reduced dataframe.
        copy_cols = []

        for idx in range(0, len(df)):
            xidx = xindeces[idx] - 1
            yidx = yindeces[idx] - 1

            if cur_hist.at[xidx, yidx] >= hist.at[xidx, yidx]:
                continue

            cur_hist.at[xidx, yidx] += 1
            copy_cols.append(idx)

        # Include all the colums in reduced version of the dataframe.
        return res.df.loc[copy_cols]

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
        xaxis_unit = self._get_base_si_unit(xaxis_defs.get("short_unit", ""))
        yaxis_unit = self._get_base_si_unit(yaxis_defs.get("short_unit", ""))

        fname = _colname_to_fname(ymetric) + "-vs-" + _colname_to_fname(xmetric) + ".html"
        outpath = self.outdir / fname

        plot = _ScatterPlot.ScatterPlot(xmetric, ymetric, outpath, xaxis_label=xaxis_label,
                                        yaxis_label=yaxis_label, xaxis_unit=xaxis_unit,
                                        yaxis_unit=yaxis_unit)

        for res in rsts:
            df = self._reduce_df_density(res, xmetric, ymetric)
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
        _LOG.info("Generating histogram: %s vs %s.", xmetric, ymetric)
        fname = _colname_to_fname(ymetric) + "-vs-" + _colname_to_fname(xmetric) + ".html"
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
        fname = _colname_to_fname(ymetric) + "-vs-" + _colname_to_fname(xmetric) + ".html"
        outpath = self.outdir / fname
        _LOG.info("Generating cumulative histogram: %s vs %s.", xmetric, ymetric)
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
