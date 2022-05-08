# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
#          Vladislav Govtva <vladislav.govtva@intel.com>
#          Adam Hawley <adam.james.hawley@intel.com>

"""This module provides the common defaults and logic for producing plotly diagrams."""

import logging
import plotly
from pandas.core.dtypes.common import is_numeric_dtype
from pepclibs.helperlibs.Exceptions import Error

# Default plotly diagram layout configuration.

_FONTFMT = {"family" : "Arial, sans-serif",
            "size"   : 18,
            "color"  : "black"}

_AXIS = {"hoverformat" : ".4s",
         "showline"  : True,
         "showgrid"  : True,
         "titlefont" : _FONTFMT,
         "ticks"     : "outside",
         "tickwidth" : 1,
         "tickformat" : ".3s",
         "showticklabels" : True,
         "linewidth" : 1,
         "linecolor" : "black",
         "zeroline" : True,
         "zerolinewidth" : 1,
         "zerolinecolor" : "black"}

_LEGEND = {"font"    : {"size" : 14},
           "bgcolor" : "#E2E2E2",
           "borderwidth" : 2,
           "bordercolor" : "#FFFFFF"}

_LOG = logging.getLogger()

class Plot:
    """This class provides the common defaults and logic for producing plotly diagrams."""

    def get_hover_text(self, hov_defs, df):
        """
        Create and return a list containing hover text for every datapoint in the 'pandas.DataFrame'
        'df'. Arguments are as follows:
         * hov_defs - a list of definitions dictionaries which represent metrics for which hovertext
                      should be generated.
         * df - the 'pandas.DataFrame' which contains the datapoints to label.
        """

        _LOG.debug("Preparing hover text for '%s vs %s'", self.ycolname, self.xcolname)

        # The loop below creates the following objects.
        #  o colnames - names of the columns to include to the hover text.
        #  o fmts - the hover text format.
        colnames = []
        fmts = []
        for mdef in hov_defs:
            colname = mdef["metric"]
            if colname not in df:
                continue
            if colname in (self.xcolname, self.ycolname):
                # The X and Y datapoint values will be added automatically.
                continue

            fmt = f"{colname}: {{"
            if mdef.get("type") == "float":
                fmt += ":.2f"
            fmt += "}"
            unit = mdef.get("short_unit")
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
    def _is_numeric_col(df, colname):
        """
        Returns 'True' if column 'colname' in 'pandas.DataFrame' 'df' consists of numerical data,
        otherwise returns 'False'.  Helper for child classes to dictate styling based on whether a
        column is numeric or not.
        """

        # Pandas 'is_numeric_dtype' function returns 'True' if the column datatype is numeric or a
        # boolean.  This function returns the same as the pandas function unless the datatype is a
        # boolean, in which case it returns False.
        return is_numeric_dtype(df[colname]) and df[colname].dtype != 'bool'

    def add_df(self, df, name, hover_text=None):
        """
        Add a single 'pandas.DataFrame' of data to the plot.
         * df - 'pandas.DataFrame' containing the data to be plotted for that test run.
         * name - plots with multiple sets of data will include a legend indicating which plot
                  points are from which set of data. This 'name' parameter will be used to label
                  the data given when this function is called.
         * hover_text - hover text elements associated with each (x,y) pair. If a single string, the
                        same string appears over all the data points. If an array of string, the
                        items are mapped in order to the this trace's (x,y) coordinates.
        """

        raise NotImplementedError()

    def generate(self):
        """
        Generates a plotly diagram based on the data in all instances of 'pandas.DataFrame' saved
        with 'self.add_df()'. Then saves it to a file at the output path 'self.outpath'.
        """

        try:
            fig = plotly.graph_objs.Figure(data=self._gobjs, layout=self._layout)
            if hasattr(fig, "update_layout") and fig.update_layout:
                # In plotly version 4 the default theme has changed. The old theme is called
                # 'plotly_white'. Use it to maintain consistent look for plotly v3 and v4.
                fig.update_layout(template="plotly_white")

            _LOG.info("Generating plot: %s vs %s.", self.yaxis_label, self.xaxis_label)
            plotly.offline.plot(fig, filename=str(self.outpath), auto_open=False,
                                config={"showLink" : False})
        except Exception as err:
            raise Error(f"failed to create the '{self.outpath}' diagram:\n{err}") from err

    def _configure_layout(self):
        """
        Creates and returns a plotly layout configuration using the parameters provided to the
        constructor.
        """

        xaxis = {**_AXIS,
                 "ticksuffix": self.xaxis_unit,
                 "title": self.xaxis_label}

        # The default axis configuration uses an SI prefix for units (e.g. ms, ks, etc.).  For
        # percent values, just round the value to 3 significant figures and do not include an SI
        # prefix.
        if self.xaxis_unit == "%":
            xaxis["tickformat"] = ".3r"

        yaxis = {**_AXIS,
                 "ticksuffix": self.yaxis_unit,
                 "title": self.yaxis_label}

        # See comment above regarding SI prefixes. Here we do the same but for the Y-axis.
        if self.yaxis_unit == "%":
            yaxis["tickformat"] = ".3r"

        layout = {"showlegend"  : True,
                  "hovermode"   : "closest",
                  "xaxis"   : xaxis,
                  "yaxis"   : yaxis,
                  "barmode" : "overlay",
                  "bargap"  : 0,
                  "legend"  : _LEGEND}
        return layout

    def __init__(self, xcolname, ycolname, outpath, xaxis_label=None, yaxis_label=None,
                 xaxis_unit=None, yaxis_unit=None, opacity=None):
        """
        The class constructor. The arguments are as follows.
         * xcolname - name of the column to use as the X-axis.
         * ycolname - name of the column to use as the Y-axis.
         * outpath - desired filepath of resultant plot HTML.
         * xaxis_label - label which describes the data plotted on the X-axis.
         * yaxis_label - label which describes the data plotted on the Y-axis.
         * xaxis_unit - the unit provided will be appended as a suffix to datapoints and along the
                        X-axis.
         * yaxis_unit - same as 'xaxis_unit', but for Y-axis.
         * opacity - opacity of the plotly trace, will be passed directly to plotly. Can be
                     used for overriding the project default value.
        """

        self.xcolname = xcolname
        self.ycolname = ycolname
        self.outpath = outpath

        # 'gobjs' contains plotly "Graph Objects". This attribute stores the data from each
        # 'self.add_df()' call. Then the data is aggregated for the final diagram during the
        # 'self.generate()' stage.
        self._gobjs = []

        self.xaxis_label = xaxis_label if xaxis_label else xcolname
        self.yaxis_label = yaxis_label if yaxis_label else ycolname
        self.xaxis_unit = xaxis_unit if xaxis_unit else ""
        self.yaxis_unit = yaxis_unit if yaxis_unit else ""
        self.opacity = opacity if opacity else 0.8

        self._layout = self._configure_layout()
