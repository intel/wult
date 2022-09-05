# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
#          Vladislav Govtva <vladislav.govtva@intel.com>
#          Adam Hawley <adam.james.hawley@intel.com>

"""This module provides the functionality for producing plotly scatter plots."""

import itertools
import logging
import numpy
import pandas
import plotly
from statscollectlibs.htmlreport import _Plot

# List of diagram markers that we use in scatter plots.
_SCATTERPLOT_MARKERS = ['circle', 'square', 'diamond', 'cross', 'triangle-up', 'pentagon']

_LOG = logging.getLogger()

class ScatterPlot(_Plot.Plot):
    """This class provides the functionality to generate plotly scatter plots."""

    def reduce_df_density(self, rawdf, reportid):
        """
        This function reduces the density of the 'pandas.DataFrame' 'rawdf'. The problem it solves
        is that that there are thousands and thousands of "uninteresting" datapoints per one
        "interesting" datapoint (an outlier). And if the total amount of datapoints is huge (say,
        10000000), a web browser simply cannot show it because the plot is too large (gigabytes). So
        what we are trying to do is to:
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
            unique numbers, find datapoints to keep, and then reduce the 'pandas.DataFrame'. This
            function does exactly that - maps a non-numeric column 'colname' to unique numbers and
            returns the corresponding pandas series object.
            """

            if not self._is_numeric_col(df, colname):
                num_rmap = {name : idx for idx, name in enumerate(df[colname].unique())}
                return df[colname].map(num_rmap)

            return df[colname]

        lo_thresh = 20
        hi_thresh = 200
        bins_cnt = 100

        _LOG.info("Reducing density for report ID '%s', diagram '%s vs %s'",
                  reportid, self.yaxis_label, self.xaxis_label)

        # Create a new 'pandas.DataFrame' with just the X- and Y-columns, which we'll be reducing.
        # It should be a bit more optimal than reducing the bigger original 'pandas.DataFrame'.
        df = rawdf[[self.xcolname, self.ycolname]]

        xdata = _map_non_numeric(self.xcolname)
        ydata = _map_non_numeric(self.ycolname)

        # Crete a histogram for the columns in question.
        hist, xbins, ybins = numpy.histogram2d(xdata, ydata, bins_cnt)
        # Turn the histogram into a 'pandas.DataFrame'.
        hist = pandas.DataFrame(hist, dtype=int)

        hist_max = hist.max().max()
        if hist_max <= lo_thresh:
            _LOG.debug("cancel density reduction: max frequency for '%s vs %s' is %d, but scaling "
                       "threshold is %d", self.yaxis_label, self.xaxis_label, hist_max, lo_thresh)
            return rawdf

        # The histogram scaling factor.
        factor = hi_thresh / hist_max

        # Scale the histogram down. Do not change the buckets with few datapoints (< lo_thresh),
        # scale down all the other buckets so that they would have maximum 'hi_thresh' datapoints.
        scaling_func = lambda f: max(int(f * factor), lo_thresh) if f > lo_thresh else f
        hist = hist.applymap(scaling_func)

        # Create a copy of the histogram, but populate it with zeroes.
        cur_hist = pandas.DataFrame(0, columns=hist.columns, index=hist.index)

        # Calculate bin indexes for all the X and Y values in the 'pandas.DataFrame'.
        xindeces = numpy.digitize(xdata, xbins[:-1])
        yindeces = numpy.digitize(ydata, ybins[:-1])

        # This is how many datapoints we are going to have in the reduced 'pandas.DataFrame'.
        reduced_datapoints_cnt = hist.values.sum()
        _LOG.debug("reduced datapoints count is %d", reduced_datapoints_cnt)

        # Here we'll store 'df' indexes of the rows that will be included into the resulting
        # reduced 'pandas.DataFrame'.
        copy_cols = []

        for idx in range(0, len(df)):
            xidx = xindeces[idx] - 1
            yidx = yindeces[idx] - 1

            if cur_hist.at[xidx, yidx] >= hist.at[xidx, yidx]:
                continue

            cur_hist.at[xidx, yidx] += 1
            copy_cols.append(idx)

        # Include all the columns in reduced version of the 'pandas.DataFrame'.
        return rawdf.loc[copy_cols]

    def add_df(self, df, name, hover_template=None):
        """
        Overrides the 'add_df' function in the base class 'Plot'. See more details in
        'Plot.add_df()'.
        """

        # Non-numeric columns will have only few unique values, e.g. 'ReqState' might have
        # "C1", "C1E" and "C6". Using dotted markers for such data will have 3 thin lines
        # which is hard to see. Improve it by using line markers to turn lines into wider
        # "bars".
        if self._is_numeric_col(df, self.xcolname) and self._is_numeric_col(df, self.ycolname):
            marker_size = 4
            marker_symbol = next(self._markers)
        else:
            marker_size = 30
            marker_symbol = "line-ns"

        marker = {"size" : marker_size, "symbol" : marker_symbol, "opacity" : self.opacity}
        gobj = plotly.graph_objs.Scattergl(x=df[self.xcolname], y=df[self.ycolname],
                                           hovertemplate=hover_template, customdata=df,
                                           opacity=self.opacity, marker=marker, mode="markers",
                                           name=name)
        self._gobjs.append(gobj)

    def __init__(self, xcolname, ycolname, outpath, xaxis_label=None, yaxis_label=None,
                 xaxis_unit=None, yaxis_unit=None, opacity=None):
        """The class constructor. The arguments are the same as in 'Plot()'."""

        super().__init__(xcolname, ycolname, outpath, xaxis_label=xaxis_label,
                         yaxis_label=yaxis_label, xaxis_unit=xaxis_unit, yaxis_unit=yaxis_unit,
                         opacity=opacity)

        self._markers = itertools.cycle(_SCATTERPLOT_MARKERS)
