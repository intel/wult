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
import plotly
from wultlibs.htmlreport import _Plot

# List of diagram markers that we use in scatter plots.
_SCATTERPLOT_MARKERS = ['circle', 'square', 'diamond', 'cross', 'triangle-up', 'pentagon']

class ScatterPlot(_Plot.Plot):
    """This class provides the functionality to generate plotly scatter plots."""

    def add_df(self, df, name, hover_text=None):
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
                                            text=hover_text, opacity=self.opacity,
                                            marker=marker, mode="markers", name=name)
        self._gobjs.append(gobj)

    def __init__(self, xcolname, ycolname, outpath, xaxis_label=None, yaxis_label=None,
                 xaxis_unit=None, yaxis_unit=None, opacity=None):
        """The class constructor. The arguments are the same as in 'Plot()'."""

        super().__init__(xcolname, ycolname, outpath, xaxis_label=xaxis_label,
                         yaxis_label=yaxis_label, xaxis_unit=xaxis_unit, yaxis_unit=yaxis_unit,
                         opacity=opacity)

        self._markers = itertools.cycle(_SCATTERPLOT_MARKERS)
