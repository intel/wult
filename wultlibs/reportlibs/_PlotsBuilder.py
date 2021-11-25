# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
#          Vladislav Govtva <vladislav.govtva@intel.com>

"""
This module provides the capability of generating plots and diagrams using the "Plotly" library.
"""

import itertools
import logging
import numpy
import pandas
import plotly
from pepclibs.helperlibs import Trivial
from pepclibs.helperlibs.Exceptions import Error

_LOG = logging.getLogger()

# List of diagram markers that we use in scatter plots.
_SCATTERPLOT_MARKERS = ['circle', 'square', 'diamond', 'cross', 'triangle-up', 'pentagon']

def _colname_to_fname(colname):
    """
    Turn column name 'colname' into a file name, replacing problematic characters that browsers
    may refuse.
    """

    return colname.replace("%", "_pcnt").replace("/", "-to-")

class PlotsBuilder:
    """
    This class provides the capability of generating plots and diagrams using the "Plotly"
    library.
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

    def _create_diagram_axis_info(self, axis, pinfo):
        """Configure axis information dictionary for plotly's 'Figure()' method."""

        nkey = f"{axis}colname"
        colname = pinfo[nkey]
        defs = self._refdefs.info.get(colname, {})
        title = defs.get("title", colname)

        fontfmt = {"family" : "Arial, sans-serif",
                   "size"   : 18,
                   "color"  : "black"}

        axis = {"showline"  : True,
                "showgrid"  : True,
                "title"     : title,
                "titlefont" : fontfmt,
                "ticks"     : "outside",
                "tickwidth" : 1,
                "showticklabels" : True,
                "linewidth" : 1,
                "linecolor" : "black",
                "zeroline" : True,
                "zerolinewidth" : 1,
                "zerolinecolor" : "black"}

        if defs.get("unit") == "microsecond":
            axis["tickformat"] = ".3s"
            axis["ticksuffix"] = "s"
            axis["hoverformat"] = ".4s"
        elif colname == "Percentile":
            axis["ticksuffix"] = "%"

        if defs and not self.rsts[0].is_numeric(colname):
            axis["type"] = "category"
            axis["autorange"] = False
            axis["categoryorder"] = "category ascending"

        return axis

    def _add_pinfo(self, xcolname, ycolname, is_hist=False):
        """Add information about a plot to 'self._create_diagrams'."""

        pinfo = {}
        pinfo["xcolname"] = xcolname
        pinfo["ycolname"] = ycolname
        pinfo["fname"] = _colname_to_fname(pinfo['ycolname']) + "-vs-" + \
                         _colname_to_fname(pinfo['xcolname']) + ".html"

        if is_hist:
            colname = xcolname
        else:
            colname = ycolname

        pinfo["colname"] = colname

        if colname not in self._pinfos:
            self._pinfos[colname] = []
        self._pinfos[colname].append(pinfo)

        return pinfo

    def _create_hover_text(self, res, df, pinfo):
        """
        Create and return a list containing hover text for every datapoint in the 'df' dataframe.
        """

        xcolname, ycolname = pinfo["xcolname"], pinfo["ycolname"]
        _LOG.debug("Preparing hover text for '%s vs %s'", xcolname, ycolname)

        # The loop below creates the following objects.
        #  o colnames - names of the columns to include to the hover text.
        #  o fmts - the hover text format.
        colnames = []
        fmts = []
        for colname in self._hov_colnames[res.reportid]:
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

    def _create_diagram(self, gobjs, pinfo):
        """Put the 'gobjs' objects to a single plot and save it in the output directory."""

        xaxis = self._create_diagram_axis_info("x", pinfo)
        yaxis = self._create_diagram_axis_info("y", pinfo)

        legend_format = {"font"    : {"size" : 14},
                         "bgcolor" : "#E2E2E2",
                         "borderwidth" : 2,
                         "bordercolor" : "#FFFFFF"}

        layout = {"showlegend"  : True,
                  "hovermode"   : "closest",
                  "xaxis"   : xaxis,
                  "yaxis"   : yaxis,
                  "barmode" : "overlay",
                  "bargap"  : 0,
                  "legend"  : legend_format}

        fpath = self.outdir.joinpath(pinfo["fname"])

        try:
            fig = plotly.graph_objs.Figure(data=gobjs, layout=layout)
            if hasattr(fig, "update_layout") and fig.update_layout:
                # In plotly version 4 the default theme has changed. The old theme is called
                # 'plotly_white'. Use it to maintain consistent look for plotly v3 and v4.
                fig.update_layout(template="plotly_white")
            plotly.offline.plot(fig, filename=str(fpath), auto_open=False,
                                config={"showLink" : False})
        except Exception as err:
            raise Error(f"failed to create the '{pinfo['fname']}' diagram:\n{err}") from err

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

    def _generate_scatter_plots(self):
        """Generate the scatter plots."""

        plot_axes = [(x, y) for x, y in itertools.product(self.xaxes, self.yaxes) if x != y]

        if self.exclude_xaxes and self.exclude_yaxes:
            x_axes = self._refres.find_colnames([self.exclude_xaxes])
            y_axes = self._refres.find_colnames([self.exclude_yaxes])
            exclude_axes = list(itertools.product(x_axes, y_axes))
            plot_axes = [axes for axes in plot_axes if axes not in exclude_axes]

        for xcolname, ycolname in plot_axes:
            _LOG.info("Generating scatter plot: %s vs %s.", xcolname, ycolname)

            pinfo = self._add_pinfo(xcolname, ycolname, is_hist=False)
            markers = itertools.cycle(_SCATTERPLOT_MARKERS)
            gobjs = []

            for res in self.rsts:
                df = self._reduce_df_density(res, xcolname, ycolname)

                # How many datapoints were included into the scatter plot.
                pinfo["sp_datapoints_cnt"] = len(df.index)

                text = self._create_hover_text(res, df, pinfo)

                # Non-numeric columns will have only few unique values, e.g. 'ReqState' might have
                # "C1", "C1E" and "C6". Using dotted markers for such data will have 3 thin lines
                # which is hard to see. Improve it by using line markers to turn lines into wider
                # "bars".
                if all((res.is_numeric(xcolname), res.is_numeric(ycolname))):
                    marker_size = 4
                    marker_symbol = next(markers)
                else:
                    marker_size = 30
                    marker_symbol = "line-ns"

                marker = {"size" : marker_size, "symbol" : marker_symbol, "opacity" : self._opacity}
                try:
                    gobj = plotly.graph_objs.Scattergl(x=self._base_unit(df, xcolname),
                                                       y=self._base_unit(df, ycolname),
                                                       opacity=self._opacity,
                                                       text=text, mode="markers",
                                                       name=res.reportid, marker=marker)
                except Exception as err:
                    raise Error(f"failed to create scatter plot '{ycolname}-vs-{xcolname}':\n"
                                f"{err}") from err
                gobjs.append(gobj)

            self._create_diagram(gobjs, pinfo)

    def _generate_histograms(self):
        """Generate the scatter plots."""

        def get_xbins(xcolname):
            """Returns the 'xbins' dictinary for plotly's 'Histrogram()' method."""

            xmin, xmax = (float("inf"), -float("inf"))
            for res in self.rsts:
                # In case of non-numeric column there is only one x-value per bin.
                if not res.is_numeric(xcolname):
                    return {"size" : 1}

                xdata = self._base_unit(res.df, xcolname)
                xmin = min(xmin, xdata.min())
                xmax = max(xmax, xdata.max())

            return {"size" : (xmax - xmin) / 1000}

        xcolnames = Trivial.list_dedup(self.hist + self.chist)
        hist_set = set(self.hist)
        chist_set = set(self.chist)

        for xcolname in xcolnames:
            if xcolname in hist_set:
                ycolname = "Count"
                pinfo = self._add_pinfo(xcolname, ycolname, is_hist=True)
                _LOG.info("Generating histogram: %s vs %s.", xcolname, ycolname)
                gobjs = []
                xbins = get_xbins(xcolname)
                for res in self.rsts:
                    xdata = self._base_unit(res.df, xcolname)
                    try:
                        gobj = plotly.graph_objs.Histogram(x=xdata, name=res.reportid, xbins=xbins,
                                                           opacity=self._opacity)
                    except Exception as err:
                        raise Error(f"failed to create histogram '{ycolname}-vs-{xcolname}':\n"
                                    f"{err}") from err
                    gobjs.append(gobj)

                self._create_diagram(gobjs, pinfo)

            if xcolname in chist_set:
                ycolname = "Percentile"
                _LOG.info("Generating cumulative histogram: %s vs %s.", xcolname, ycolname)
                pinfo = self._add_pinfo(xcolname, ycolname, is_hist=True)
                gobjs = []
                if xcolname not in hist_set:
                    xbins = get_xbins(xcolname)
                for res in self.rsts:
                    xdata = self._base_unit(res.df, xcolname)
                    try:
                        gobj = plotly.graph_objs.Histogram(x=xdata, name=res.reportid, xbins=xbins,
                                                           cumulative=dict(enabled=True),
                                                           histnorm="percent",
                                                           opacity=self._opacity)
                    except Exception as err:
                        raise Error(f"failed to create cumulative histogram "
                                    f"'{ycolname}-vs-{xcolname}':\n{err}") from err
                    gobjs.append(gobj)

                self._create_diagram(gobjs, pinfo)

    def generate_plots(self):
        """
        Generate plots according to the arguments passed to the class constructor. This method
        generates HTML plots for the results 'self.rsts' in the output directory 'self.outdir'. Both
        of these class attributes are included in the group of arguments passed to the class
        constructor.
        """

        self._generate_scatter_plots()
        self._generate_histograms()
        return self._pinfos

    def __init__(self, rsts, outdir, xaxes, yaxes, hist, chist, exclude_xaxes, exclude_yaxes,
                 hov_colnames):
        """
        The class constructor. The arguments are the same as for 'HTMLReportBase.init()' except for
        'outdir' which is the directory path which will store the HTML plots.
        """

        self.rsts = rsts
        self.outdir = outdir
        self.xaxes = xaxes
        self.yaxes = yaxes
        self.hist = hist
        self.chist = chist
        self.exclude_xaxes = exclude_xaxes
        self.exclude_yaxes = exclude_yaxes
        self._hov_colnames = hov_colnames

        if (self.exclude_xaxes and not self.exclude_yaxes) or \
           (self.exclude_yaxes and not self.exclude_xaxes):
            raise Error("'exclude_xaxes' and 'exclude_yaxes' must both be 'None' or both not be "
                        "'None'")

        # Plot information dictionaries. This is a dictionary of of lists, each list containing
        # sub-dictionaries describing a single plot. The lists of sub-dictionaries are grouped by
        # the "X" and "Y" axis column names, because later plots with the same "Y" and "Y" axes will
        # go to the same HTML page.
        self._pinfos = {}
        # The first result is the 'reference' result.
        self._refres = rsts[0]
        # The diagram/histogram transparency level. It is helpful to have some transparency in case
        # there are several test results rendered on the same diagram.
        self._opacity = 0.8 if len(self.rsts) > 1 else 1
        # The reference definitions - it contains helpful information about every CSV file column,
        # for example the title, units, and so on.
        self._refdefs = self._refres.defs
