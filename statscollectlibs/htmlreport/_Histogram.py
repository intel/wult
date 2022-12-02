# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
#          Vladislav Govtva <vladislav.govtva@intel.com>
#          Adam Hawley <adam.james.hawley@intel.com>

"""This module provides the functionality for producing plotly histograms."""

import plotly
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.htmlreport import _Plot


class Histogram(_Plot.Plot):
    """This class provides the functionality to generate plotly histograms."""

    def add_df(self, df, name, hover_template=None):
        """
        Overrides the 'add_df' function in the base class 'Plot'. See more details in
        'Plot.add_df()'.
        """

        try:
            if self.cumulative:
                gobj = plotly.graph_objs.Histogram(x=df[self.xcolname], name=name, xbins=self.xbins,
                                                    cumulative=dict(enabled=True),
                                                    histnorm="percent", opacity=self.opacity)
            else:
                gobj = plotly.graph_objs.Histogram(x=df[self.xcolname], name=name, xbins=self.xbins,
                                                   opacity=self.opacity,
                                                   hovertemplate=hover_template, customdata=df)
        except Exception as err:
            msg = Error(err).indent(2)
            raise Error(f"failed to create histogram 'count-vs-{self.xcolname}':\n{msg}") from err

        self._gobjs.append(gobj)

    def __init__(self, xcolname, outpath, xaxis_label=None, xaxis_unit=None, opacity=None,
                 xbins=None, cumulative=False):
        """
        The class constructor. The arguments are a subset of the constructor of the 'Plot()'  class
        except for the following:
         * xbins - argument is passed to plotly histogram "graph object" constructor for custom
                   binning.
         * cumulative - boolean which dictates whether the histogram is cumulative or not. If it
                        is, the Y-axis will show a percentile rather than a count.
        """

        self.xbins = xbins
        self.cumulative = cumulative

        if cumulative:
            ycolname = "Percentile"
            yaxis_unit = "%"
        else:
            ycolname = "Count"
            yaxis_unit = None

        super().__init__(xcolname, ycolname, outpath, xaxis_label=xaxis_label,
                         xaxis_unit=xaxis_unit, yaxis_unit=yaxis_unit, opacity=opacity)
