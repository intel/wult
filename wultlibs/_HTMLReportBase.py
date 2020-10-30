# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2020 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
#          Vladislav Govtva <vladislav.govtva@intel.com>

"""
This module the base class for generating HTML reports for raw test results.
"""

import shutil
import logging
import itertools
from pathlib import Path
from collections import OrderedDict
import numpy
import pandas
import plotly
from wultlibs.helperlibs import Trivial, FSHelpers, Jinja2
from wultlibs.helperlibs.Exceptions import Error
from wultlibs import RORawResult

_LOG = logging.getLogger("main")

# List of diagram markers that we use in scatter plots.
_SCATTERPLOT_MARKERS = ['circle', 'square', 'diamond', 'cross', 'triangle-up', 'pentagon']

class HTMLReportBase:
    """This is the base class for generating HTML reports for raw test results."""

    def _prepare_summary_table(self, raw_stats_paths, descr_paths):
        """
        Create the test report summary table. The 'raw_stats_paths' should be a dictionary
        indexed by report ID and containing the raw statistics directory path. Similarly, the
        'descr_paths' contains paths to the test result description files.
        """

        sum_tbl = OrderedDict()
        sum_tbl["Title"] = OrderedDict()
        for res in self.rsts:
            sum_tbl[res.reportid] = OrderedDict()

        # Add tool information.
        key = "tool_info"
        sum_tbl["Title"][key] = "Data collection tool"
        for res in self.rsts:
            sum_tbl[res.reportid][key] = f"{res.info['toolname'].capitalize()} version " \
                                         f"{res.info['toolver']}"

        # Add datapoint counts.
        key = "datapoints_cnt"
        sum_tbl["Title"][key] = "Datapoints Count"
        for res in self.rsts:
            sum_tbl[res.reportid][key] = len(res.df.index)

        # Add measurement resolution.
        for res in self.rsts:
            key = "device_resolution"
            resolution = res.info.get("resolution")
            if resolution:
                sum_tbl["Title"][key] = "Device Resolution"
                sum_tbl[res.reportid][key] = f"{resolution}ns"

        # Add links to the raw statistics directories.
        if raw_stats_paths:
            key = "raw_stats"
            sum_tbl["Title"][key] = "Raw statistics"
            for res in self.rsts:
                path = raw_stats_paths.get(res.reportid, "Not available")
                sum_tbl[res.reportid][key] = path

        # Add links to the descriptions.
        if descr_paths:
            key = "descr"
            sum_tbl["Title"][key] = "Test description"
            for res in self.rsts:
                path = descr_paths.get(res.reportid, "Not available")
                sum_tbl[res.reportid][key] = path

        return sum_tbl

    def _prepare_links_table(self):
        """Creates the links table which refers to HTML sub-pages."""

        links_tbl = OrderedDict()
        for colname in itertools.islice(self._pinfos, 1, None):
            links_tbl[colname] = {}
            links_tbl[colname]["name"] = f"{colname}"
            fname = colname.replace("%", "_pcnt") + ".html"
            links_tbl[colname]["fname"] = fname
            links_tbl[colname]["hlink"] = f"<a href=\"{fname}\">{colname}</a>"

        return links_tbl

    def _prepare_stats_table(self, pinfos):
        """Create the statistics table for metrics included in plots in 'pinfos' list."""

        stats_tbl = OrderedDict()
        stats_tbl["Title"] = OrderedDict()
        for res in self.rsts:
            stats_tbl[res.reportid] = OrderedDict()

        for pinfo in pinfos:
            for colname in (pinfo["colname"], pinfo["xcolname"]):
                if colname in stats_tbl["Title"]:
                    continue

                # Each column name is represented by a row in the statistics table. Fill the "Title"
                # column.
                title_dict = stats_tbl["Title"][colname] = OrderedDict()
                defs = self._refdefs.info[colname]

                if defs.get("unit") == "nanosecond":
                    # Convert nanoseconds to microseconds.
                    unit = "us"
                else:
                    unit = defs.get("short_unit", "")

                title_dict["colname"] = colname
                if unit:
                    title_dict["colname"] += f", {unit}"
                title_dict["coldescr"] = defs["descr"]

                title_dict["funcs"] = OrderedDict()
                for funcname in self._stats_funcs:
                    if funcname in self.rsts[0].cstats[colname]:
                        title_dict["funcs"][funcname] = RORawResult.get_stat_func_descr(funcname)

                # Now fill the values for each result.
                for res in self.rsts:
                    res_dict = stats_tbl[res.reportid][colname] = OrderedDict()
                    res_dict["funcs"] = OrderedDict()

                    for funcname in title_dict["funcs"]:
                        val = res.cstats[colname][funcname]
                        fmt = "{}"
                        if defs.get("unit") == "nanosecond" and "index" not in funcname:
                            val /= 1000
                            fmt = "{:.2f}"
                        if defs["type"] == "float":
                            fmt = "{:.2f}"

                        fdict = res_dict["funcs"][funcname] = OrderedDict()
                        fdict["val"] = fmt.format(val)
                        fdict["raw_val"] = val

                        if self._refres.reportid == res.reportid:
                            fdict["hovertext"] = "This is the reference result, other results " \
                                                 "are compared to this one."
                            continue

                        ref_fdict = stats_tbl[self._refres.reportid][colname]["funcs"][funcname]
                        change = val - ref_fdict["raw_val"]
                        if ref_fdict["raw_val"]:
                            percent = (change / ref_fdict["raw_val"]) * 100
                        else:
                            percent = change
                        change = fmt.format(change) + unit
                        percent = "{:.1f}%".format(percent)
                        fdict["hovertext"] = f"Change: {change} ({percent})"

        return stats_tbl

    def _copy_raw_data(self):
        """Copy raw test results to the output directory."""

        # Paths to the raw statistics.
        raw_stats_paths = {}
        # Paths to test reports' description files.
        descr_paths = {}

        for res in self.rsts:
            srcpath = res.dirpath
            resrootdir = "raw-" + res.reportid
            dstpath = self.outdir.joinpath(resrootdir)

            if self.relocatable:
                action = "copy"
            else:
                action = "symlink"
            FSHelpers.move_copy_link(srcpath, dstpath, action=action, exist_ok=True)

            if res.stats_path.is_dir():
                hlink = f"<a href=\"{resrootdir}/{res.stats_path.name}\">Raw statistics</a>"
                raw_stats_paths[res.reportid] = hlink
            if res.descr_path.is_file():
                hlink = f"<a href=\"{resrootdir}/{res.descr_path.name}\">Test description</a>"
                descr_paths[res.reportid] = hlink

        return raw_stats_paths, descr_paths

    def _generate_report(self):
        """Put together the final HTML report."""

        _LOG.info("Generating the HTML report.")

        # Make sure the output directory exists.
        try:
            self.outdir.mkdir(parents=True, exist_ok=True)
        except OSError as err:
            raise Error(f"failed to create directory '{self.outdir}': {err}")

        raw_stats_paths, descr_paths = self._copy_raw_data()

        # Find the styles and templates paths.
        templdir = FSHelpers.search_for_app_data("wult", Path("templates"),
                                                 pathdescr="HTML report Jinja2 templates")
        csspath = FSHelpers.search_for_app_data("wult", Path("css/style.css"),
                                                pathdescr="HTML report CSS file")

        # Copy the styles file to the output directory.
        dstpath = self.outdir.joinpath("style.css")
        try:
            shutil.copyfile(csspath, dstpath)
        except OSError as err:
            raise Error(f"failed to copy CSS file from '{csspath}' to '{dstpath}':\n{err}")

        # The summary table is only included into the main HTML page.
        sum_tbl = self._prepare_summary_table(raw_stats_paths, descr_paths)
        links_tbl = self._prepare_links_table()

        # Each column name gets its own HTML page.
        for colname, pinfos in self._pinfos.items():
            stats_tbl = self._prepare_stats_table(pinfos)

            # Render the template.
            jenv = Jinja2.build_jenv(templdir, trim_blocks=True, lstrip_blocks=True)
            jenv.globals["stats_tbl"] = stats_tbl
            jenv.globals["pinfos"] = pinfos
            jenv.globals["colname"] = colname
            jenv.globals["title_descr"] = self.title_descr
            jenv.globals["toolname"] = self._refinfo["toolname"]

            if sum_tbl:
                jenv.globals["sum_tbl"] = sum_tbl
                jenv.globals["links_tbl"] = links_tbl
                templfile = outfile = "index.html"
                sum_tbl = None
            else:
                templfile = "metric.html"
                outfile = links_tbl[colname]["fname"]

            Jinja2.render_template(jenv, Path(templfile), outfile=self.outdir.joinpath(outfile))

    def _add_pinfo(self, xcolname, ycolname, is_hist=False):
        """Add information about a plot to 'self._create_diagrams'."""

        pinfo = {}
        pinfo["xcolname"] = xcolname
        pinfo["ycolname"] = ycolname
        pinfo["fname"] = f"{pinfo['ycolname']}-vs-{pinfo['xcolname']}.html"
        # C-state residency column names contain the '%' caracter, which is not allowed in HTML page
        # file name.
        pinfo["fname"] = pinfo["fname"].replace("%", "_pcnt")

        if is_hist:
            colname = xcolname
        else:
            colname = ycolname

        pinfo["colname"] = colname

        if colname not in self._pinfos:
            self._pinfos[colname] = []
        self._pinfos[colname].append(pinfo)

        return pinfo

    def _base_unit(self, df, colname):
        """
        If the unit of column 'colname' of the 'df' datafram uses a prefix like 'nano', then return
        the column converted into base units.
        """

        # This is not generic, but today we have to deal only with nanoseconds, so this is good
        # enough.
        if self._refdefs.info[colname].get("unit") != "nanosecond":
            return df[colname]

        base_colname = f"{colname}_base"
        if base_colname not in df:
            df[base_colname] = df[colname] / 1000000000
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

        if defs.get("unit") == "nanosecond":
            axis["tickformat"] = ".3s"
            axis["ticksuffix"] = "s"
            axis["hoverformat"] = ".4s"
        elif colname == "Percentile":
            axis["ticksuffix"] = "%"

        return axis

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

        outdir = self.outdir.joinpath("plots")
        try:
            outdir.mkdir(parents=True, exist_ok=True)
        except OSError as err:
            raise Error(f"failed to create directory '{outdir}': {err}")

        fpath = outdir.joinpath(pinfo["fname"])

        try:
            fig = plotly.graph_objs.Figure(data=gobjs, layout=layout)
            if hasattr(fig, "update_layout") and fig.update_layout:
                # In plotly version 4 the default theme has changed. The old theme is called
                # 'plotly_white'. Use it to maintain consistent look for plotly v3 and v4.
                fig.update_layout(template="plotly_white")
            plotly.offline.plot(fig, filename=str(fpath), auto_open=False,
                                config={"showLink" : False})
        except Exception as err:
            raise Error(f"failed to create the '{pinfo['fname']}' diagram:\n{err}")

        pinfo["path"] = str(fpath.relative_to(self.outdir))

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

        lo_thresh = 20
        hi_thresh = 200
        bins_cnt = 100

        _LOG.info("Reducing density for report ID '%s', diagram '%s-vs-%s'",
                  res.reportid, ycolname, xcolname)

        # Crete a histogram for the columns in question.
        hist, xbins, ybins = numpy.histogram2d(res.df[xcolname], res.df[ycolname], bins_cnt)
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
        xindeces = numpy.digitize(res.df[xcolname], xbins[:-1])
        yindeces = numpy.digitize(res.df[ycolname], ybins[:-1])

        # This is how many datapoints we are going to have in the reduced dataframe.
        reduced_datapoints_cnt = hist.values.sum()
        _LOG.debug("reduced datapoints count is %d", reduced_datapoints_cnt)

        # Here we'll store 'res.df' indexes of the rows that will be included into the resulting
        # reduced dataframe.
        copy_cols = []

        for col in res.df.itertuples(index=True):
            xidx = xindeces[col.Index] - 1
            yidx = yindeces[col.Index] - 1

            if cur_hist.at[xidx, yidx] >= hist.at[xidx, yidx]:
                continue

            cur_hist.at[xidx, yidx] += 1
            copy_cols.append(col.Index)

        return res.df.loc[copy_cols]

    def _generate_scatter_plots(self):
        """Generate the scatter plots."""

        for xcolname, ycolname in itertools.product(self.xaxes, self.yaxes):
            _LOG.info("Generating scatter plot: %s vs %s.", xcolname, ycolname)

            pinfo = self._add_pinfo(xcolname, ycolname, is_hist=False)
            markers = itertools.cycle(_SCATTERPLOT_MARKERS)
            gobjs = []

            for res in self.rsts:
                df = self._reduce_df_density(res, xcolname, ycolname)

                # How many datapoints were included into the scatter plot.
                pinfo["sp_datapoints_cnt"] = len(df.index)

                text = self._create_hover_text(res, df, pinfo)
                marker = {"size" : 4, "symbol" : next(markers), "opacity" : self._opacity}
                try:
                    gobj = plotly.graph_objs.Scattergl(x=self._base_unit(df, xcolname),
                                                       y=self._base_unit(df, ycolname),
                                                       opacity=self._opacity,
                                                       text=text, mode="markers",
                                                       name=res.reportid, marker=marker)
                except Exception as err:
                    raise Error(f"failed to create scatter plot '{ycolname}-vs-{xcolname}':\n{err}")
                gobjs.append(gobj)

            self._create_diagram(gobjs, pinfo)

    def _generate_histograms(self):
        """Generate the scatter plots."""

        def get_xbins(xcolname):
            """Returns the 'xbins' dictinary for plotly's 'Histrogram()' method."""

            xmin, xmax = (float("inf"), -float("inf"))
            for res in self.rsts:
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
                        raise Error(f"failed to create histogram "
                                    f"'{ycolname}-vs-{xcolname}':\n{err}")
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
                                    f"'{ycolname}-vs-{xcolname}':\n{err}")
                    gobjs.append(gobj)

                self._create_diagram(gobjs, pinfo)

    def _calc_stats(self):
        """Calculate statistics that we are going to show in the report table."""

        for res in self.rsts:
            _LOG.info("Calculate statistics for '%s'", res.reportid)
            res.calc_stats(regexs=self._stats_colnames, funcnames=self._stats_funcs)

    def _mangle_loaded_res(self, res): # pylint: disable=no-self-use, unused-argument
        """
        This method is called for every dataframe corresponding to the just loaded CSV file. The
        subclass can override this method to mangle the dataframe.
        """

        # Update columns lists in case some of the columns were removed from the loaded dataframe.
        for name in ("_stats_colnames", "xaxes", "yaxes", "hist", "chist"):
            colnames = []
            for colname in getattr(self, name):
                if colname in res.df:
                    colnames.append(colname)
            setattr(self, name, colnames)

        for name in ("_hov_colnames", ):
            colnames = []
            val = getattr(self, name)
            for colname in val[res.reportid]:
                if colname in res.df:
                    colnames.append(colname)
            val[res.reportid] = colnames
        return res.df

    def _load_results(self):
        """Load the test results from the CSV file and/or apply the columns selector."""

        _LOG.debug("stats colnames: %s", ", ".join(self._stats_colnames))
        _LOG.debug("additional colnames: %s", ", ".join(self._more_colnames))

        for res in self.rsts:
            _LOG.debug("hover colnames: %s", ", ".join(self._hov_colnames[res.reportid]))

            colnames = []
            for colname in self._hov_colnames[res.reportid] + self._more_colnames:
                if colname in res.colnames_set:
                    colnames.append(colname)

            csel = Trivial.list_dedup(self._stats_colnames + colnames)
            res.clear_filts()
            res.set_csel(csel)
            res.load_df()

            # We'll be dropping columns and adding temporary columns, so we'll affect the original
            # dataframe. This is more effecient than creating copies.
            self._mangle_loaded_res(res)

    def generate(self):
        """Generate the HTML report and store the result in 'self.outdir'.

        Important note: this method will modify the input test results in 'self.rsts'. This is done
        for effeciency purposes, to avoid copying the potentially large amounts of data (pandas
        dataframes).
        """

        # Load the required datapoints into memory.
        self._load_results()

        # Calculate datapoints statistics, like min. and max. values.
        self._calc_stats()

        # Generate the plots.
        self._generate_scatter_plots()
        self._generate_histograms()

        # Put together the final HTML report.
        self._generate_report()

    def set_hover_colnames(self, regexs):
        """
        This methods allows for specifying CSV file column names that have to be included to the
        hover test on the scatter plot. The 'regexs' argument should be a list of hover text colum
        name regular expressions. In other words, each element of the list will be treated as a
        regular expression. Every CSV colum name will be matched against this regular expression,
        and matched column names will be added to the hover text.
        """

        for res in self.rsts:
            self._hov_colnames[res.reportid] = res.find_colnames(regexs, must_find_any=False)

    def _init_colnames(self):
        """
        Assign default values to the diagram/histogram column names and remove possible
        duplication in user-provided input.
        """

        for name in ("xaxes", "yaxes", "hist", "chist"):
            val = getattr(self, name, None)
            if val is not None:
                if val:
                    # Convert list of regular expressions into list of names.
                    colnames = self._refres.find_colnames(getattr(self, name))
                else:
                    colnames = []
                setattr(self, name, colnames)
            else:
                # Set the default values.
                colnames = iter(self._refdefs.info)
                col1 = next(colnames)
                col2 = next(colnames)

                if name != "yaxes":
                    setattr(self, name, [col1])
                else:
                    setattr(self, name, [col2])

        # At this point we've got the list of column names based on the first test result. But if
        # there are multiple test results, we should find the largest common subset, in case other
        # test results are missing some of the columns present in the first (reference) test result.
        for name in ("xaxes", "yaxes", "hist", "chist"):
            intersection = set(getattr(self, name))
            for res in self.rsts:
                intersection = intersection & res.colnames_set
            colnames = []
            for colname in getattr(self, name):
                if colname in intersection:
                    colnames.append(colname)
                else:
                    _LOG.warning("dropping column '%s' from '%s' because it is not present in one "
                                 "of the results", colname, name)
                setattr(self, name, colnames)

        # Verify that we have at least one X-column and Y-column.
        if not self.xaxes or not self.yaxes:
            if not self.xaxes:
                name = "X"
            else:
                name = "Y"
            raise Error(f"the {name} axis column list is empty")

    def _validate_init_args(self):
        """Validate the class constructor input arguments."""

        if self.outdir.exists() and not self.outdir.is_dir():
            raise Error(f"path '{self.outdir}' already exists and it is not a directory")

        # Ensure that results are compatible.
        rname, rver = self._refinfo["toolname"], self._refinfo["toolver"]
        for res in self.rsts:
            name, ver = res.info["toolname"], res.info["toolver"]
            if name != rname:
                raise Error(f"the following test results are not compatible:\n"
                            f"1. {self._refres.dirpath}: created by '{rname}'\n"
                            f"2. {res.dirpath}: created by '{name}'\n"
                            f"Cannot put incompatible results to the same report")
            if ver != rver:
                _LOG.warning("the following test results may be not compatible:\n"
                             "1. %s: created by '%s' version '%s'\n"
                             "2. %s: created by '%s' version '%s'",
                             self._refres.dirpath, rname, rver, res.dirpath, name, ver)

        # Ensure the report IDs are unique.
        reportids = set()
        for res in self.rsts:
            reportid = res.reportid
            if reportid in reportids:
                # Try to construct a unique report ID.
                for idx in range(1, 20):
                    new_reportid = f"{reportid}-{idx:02}"
                    if new_reportid not in reportids:
                        _LOG.warning("duplicate reportid '%s', using '%s' instead",
                                     reportid, new_reportid)
                        res.reportid = new_reportid
                        break
                else:
                    raise Error(f"too many duplicate report IDs, e.g., '{reportid}' is problematic")

            reportids.add(res.reportid)

        if self.title_descr and Path(self.title_descr).is_file():
            try:
                with open(self.title_descr, "r") as fobj:
                    self.title_descr = fobj.read()
            except OSError as err:
                raise Error(f"failed to read the report description file {self.title_descr}: {err}")

        for res in self.rsts:
            if res.dirpath.resolve() == self.outdir.resolve():
                # Don't create report in results directory, use 'html-report' subdirectory instead.
                self.outdir = self.outdir.joinpath("html-report")

    def __init__(self, rsts, outdir, title_descr=None, xaxes=None, yaxes=None, hist=None,
                 chist=None):
        """
        The class constructor. The arguments are as follows.
          * rsts - list of 'RORawResult' objects representing the raw test results to generate the
                   HTML report for.
          * outdir - the output directory path to store the HTML report at.
          * title_descr - a string describing this report or a file path containing the description.
          *               The description will be put at the top part of the HTML report. It should
          *               describe the report in general (e.g., it compares platform A to platform
          *               B). By default no title description is added to the HTML report.
          * xaxes - list of datapoints CSV file column names to use on the X axis. Default is the
                    first column in the datapoints CSV file.
          * yaxes - list of datapoints CSV file column names to use on the Y axis. Default is
                    'WakeLatency'. Default is the second column in the datapoints CSV file.
          * hist - list of datapoints CSV file column names to create a histogram for. Default is
                   the first column in the datapoints CSV file. And empty string can be used to
                   disable histograms.
          * chist - list of datapoints CSV file column names to create a cumulative histogram for.
                    Default is he first column in the datapoints CSV file. And empty string can be
                    used to disable cumulative histograms.
        """

        self.rsts = rsts
        self.outdir = Path(outdir)
        self.title_descr = title_descr
        self.xaxes = xaxes
        self.yaxes = yaxes
        self.hist = hist
        self.chist = chist

        # Users can change this to make the reports relocatable. In this case the statistics and
        # other stuff will be copied from the test result directories to the output directory. By
        # default symlinks are used.
        self.relocatable = True

        # The first result is the 'reference' result.
        self._refres = rsts[0]
        # The reference definitions - it contains helpful information about every CSV file column,
        # for example the title, units, and so on.
        self._refdefs = self._refres.defs
        # The raw reference result information.
        self._refinfo = self._refres.info

        # Names of columns in the datapoints CSV file to provide the statistics for. The statistics
        # will show up in the statistics table included into the report.
        self._stats_colnames = None
        # List of functions to provide in the statistics column.
        self._stats_funcs = ("nzcnt", "max", "99.999%", "99.99%", "99.9%", "99%", "med", "avg",
                             "min", "std")
        # The diagram/histogram transparency level. It is helpful to have some transparency in case
        # there are several test results rendered on the same diagram.
        self._opacity = 0.8 if len(self.rsts) > 1 else 1
        # Plot information dictionaries. This is a dictionary of of lists, each list containing
        # sub-dictionaries describing a single plot. The lists of sub-dictionaries are grouped by
        # the X" and "Y" axis column names, because later plots with the same "Y" and "Y" axes will
        # go to the same HTML page.
        self._pinfos = OrderedDict()
        # Per-test result List of column names to include into the hover text of the scatter plot.
        # By default only the x and y axis values are included.
        self._hov_colnames = {}
        # Additional columns to load, if they exist in the CSV file.
        self._more_colnames = []

        self._init_colnames()

        # We'll provide statistics for every column participating in at least one diagram.
        stats_colnames = Trivial.list_dedup(self.yaxes + self.xaxes + self.hist + self.chist)
        # Since statistics table is global, include only common columns into it.
        self._stats_colnames = []
        for colname in stats_colnames:
            for res in rsts:
                if colname not in res.colnames_set:
                    break
            else:
                self._stats_colnames.append(colname)

        self._validate_init_args()
