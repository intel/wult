# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
#          Vladislav Govtva <vladislav.govtva@intel.com>

"""
This module provides the base class for generating HTML reports for raw test results.
"""

import dataclasses
import itertools
import json
import logging
from pathlib import Path
from pepclibs.helperlibs import Trivial, FSHelpers
from pepclibs.helperlibs.Exceptions import Error, ErrorNotFound
from wultlibs import Deploy
from wultlibs.htmlreport.tabs import _MetricTabBuilder, _Tabs
from wultlibs.htmlreport.tabs.stats import _ACPowerTabBuilder, _IPMITabBuilder
from wultlibs.htmlreport.tabs.stats.turbostat import _TurbostatTabBuilder

_LOG = logging.getLogger()

class ReportBase:
    """This is the base class for generating HTML reports for raw test results."""

    @staticmethod
    def _dump_json(obj, path, descr):
        """
        Helper function wrapping 'json.dump' operation with a standardised error message so that the
        error messages are consistent. Arguments are as follows:
         * obj - Python object to dump to JSON.
         * path - path to create JSON file at.
         * descr - description of object being dumped.
        """
        try:
            with open(path, "w", encoding="utf-8") as fobj:
                json.dump(obj, fobj, default=str)
        except Exception as err:
            raise Error(f"could not generate report: failed to JSON dump '{descr}' to '{path}':"
                        f"{err}") from None

    def _prepare_intro_table(self, stats_paths, logs_paths, descr_paths):
        """
        Create the intro table, which is the very first table in the report and it shortly
        summarizes the entire report. The 'stats_paths' should be a dictionary indexed by report ID
        and containing the stats directory path. Similarly, the 'logs_paths' and 'descr_paths'
        contains paths to the logs and the test result description files.
        """

        intro_tbl = {}
        intro_tbl["Title"] = {}
        # Keys of values to turn into links (e.g. paths).
        link_keys = []
        for res in self.rsts:
            intro_tbl[res.reportid] = {}

        # Add tool information.
        key = "tool_info"
        intro_tbl["Title"][key] = "Data collection tool"
        for res in self.rsts:
            intro_tbl[res.reportid][key] = f"{res.info['toolname'].capitalize()} version " \
                                         f"{res.info['toolver']}"

        # Add datapoint counts.
        key = "datapoints_cnt"
        intro_tbl["Title"][key] = "Datapoints Count"
        for res in self.rsts:
            intro_tbl[res.reportid][key] = len(res.df.index)

        # Add measurement resolution.
        for res in self.rsts:
            key = "device_resolution"
            resolution = res.info.get("resolution")
            if resolution:
                intro_tbl["Title"][key] = "Device Resolution"
                intro_tbl[res.reportid][key] = f"{resolution}ns"

        def add_intro_tbl_links(key, title, paths):
            """
            Add links in 'paths' to the 'intro_tbl' dictionary. Arguments are as follows:
             * paths - dictionary in the format {Report ID: Path to Link to}.
             * key - the key which will be used to store the links in the 'intro_tbl' dictionary.
             * title - the label that will be shown in the intro table for these links.
            """

            if not paths:
                return

            intro_tbl["Title"][key] = title
            link_keys.append(key)

            for res in self.rsts:
                path = paths.get(res.reportid, None)
                if path:
                    if self.outdir not in path.parents:
                        # If the path points to somewhere outside of the report directory, don't
                        # include it in the intro table.
                        path = None
                    else:
                        # If the path points to inside the report directory then make it relative to
                        # the output directory so that the output directory is relocatable. That is,
                        # the whole directory can be moved or copied without breaking the link.
                        path = path.relative_to(self.outdir)

                intro_tbl[res.reportid][key] = path

        # Add links to the stats directories.
        add_intro_tbl_links("stats", "Statistics", stats_paths)
        # Add links to the logs directories.
        add_intro_tbl_links("logs", "Logs", logs_paths)
        # Add links to the descriptions.
        add_intro_tbl_links("descr", "Test Description", descr_paths)

        intro_tbl["link_keys"] = link_keys

        return intro_tbl

    def _copy_raw_data(self):
        """Copy raw test results to the output directory."""

        # Paths to the stats directory.
        stats_paths = {}
        # Paths to the logs directory.
        logs_paths = {}
        # Paths to test reports' description files.
        descr_paths = {}

        for res in self.rsts:
            resdir = res.dirpath

            if self.relocatable:
                dstpath = self.outdir / f"raw-{res.reportid}"
                try:
                    FSHelpers.copy_dir(resdir, dstpath, exist_ok=True, ignore=["html-report"])
                    FSHelpers.set_default_perm(dstpath)
                except Error as err:
                    raise Error(f"failed to copy raw data to report directory: {err}") from None

                # Use the path of the copied raw results rather than the original.
                resdir = dstpath

            if res.stats_path.is_dir():
                stats_paths[res.reportid] = resdir / res.stats_path.name
            else:
                stats_paths[res.reportid] = None

            if res.logs_path.is_dir():
                logs_paths[res.reportid] = resdir / res.logs_path.name
            else:
                logs_paths[res.reportid] = None

            if res.descr_path.is_file():
                descr_paths[res.reportid] = resdir / res.descr_path.name

        return stats_paths, logs_paths, descr_paths

    def _copy_asset(self, src, descr, dst):
        """
        Copy asset file to the output directory. Arguments are as follows:
         * src - source path of the file to copy.
         * descr - description of the file which is being copied.
         * dst - where the file should be copied to.
        """

        asset_path = Deploy.find_app_data(self._projname, src, descr=descr)
        FSHelpers.move_copy_link(asset_path, dst, "copy", exist_ok=True)

    def _generate_metric_tabs(self):
        """Generate 'Metric Tabs' which contain the plots and summary tables for each metric."""

        for res in self.rsts:
            _LOG.debug("calculate summary functions for '%s'", res.reportid)
            res.calc_smrys(regexs=self._smry_colnames, funcnames=self._smry_funcs)

        plot_axes = [(x, y) for x, y in itertools.product(self.xaxes, self.yaxes) if x != y]

        if self.exclude_xaxes and self.exclude_yaxes:
            x_axes = self._refres.find_colnames([self.exclude_xaxes])
            y_axes = self._refres.find_colnames([self.exclude_yaxes])
            exclude_axes = list(itertools.product(x_axes, y_axes))
            plot_axes = [axes for axes in plot_axes if axes not in exclude_axes]

        dtabs = []
        tab_metrics = [y for _, y in plot_axes]
        tab_metrics += self.chist + self.hist
        tab_metrics = Trivial.list_dedup(tab_metrics)

        for metric in tab_metrics:
            _LOG.info("Generating %s tab.", metric)

            tab_plots = []
            smry_metrics = []
            for axes in plot_axes:
                if metric in axes:
                    # Only add plots which have the tab metric on one of the axes.
                    tab_plots.append(axes)
                    # Only add metrics shown in the diagrams to the summary table.
                    smry_metrics += axes

            smry_metrics = Trivial.list_dedup(smry_metrics)

            dtab_bldr = _MetricTabBuilder.MetricTabBuilder(metric, self.rsts, self.outdir)
            dtab_bldr.add_smrytbl(smry_metrics, self._smry_funcs)
            dtab_bldr.add_plots(tab_plots, self.hist, self.chist, self._hov_colnames)
            dtabs.append(dtab_bldr.get_tab())

        return dtabs

    def _generate_stats_tabs(self, stats_paths):
        """
        Generate statistics tabs using the appropriate tab generator for each statistic.
        'stats_paths' is a dictionary mapping in the format: {Report ID: Stats directory path} where
        the stats directory path is the directory to check for raw statistics files.
        """

        _LOG.info("Generating statistics tabs.")

        mcpus = {res.reportid: str(res.info["cpunum"]) for res in self.rsts if "cpunum" in res.info}

        tab_builders = {
            _ACPowerTabBuilder.ACPowerTabBuilder: {},
            _TurbostatTabBuilder.TurbostatTabBuilder: {"measured_cpus": mcpus},
            _IPMITabBuilder.IPMITabBuilder: {}
        }

        tabs = []

        for tab_builder, args in tab_builders.items():
            try:
                tbldr = tab_builder(stats_paths, self.outdir, **args)
            except ErrorNotFound as err:
                _LOG.info("Skipping '%s' tab as '%s' statistics not found for all reports.",
                          tab_builder.name, tab_builder.name)
                _LOG.debug(err)
                continue

            _LOG.info("Generating '%s' tab.", tbldr.name)
            try:
                tabs.append(tbldr.get_tab())
            except Error as err:
                _LOG.info("Skipping '%s' statistics: %s", tab_builder.name, err)
                continue

        return tabs

    def _generate_report(self):
        """Put together the final HTML report."""

        _LOG.info("Generating the HTML report.")

        # Make sure the output directory exists.
        try:
            self.outdir.mkdir(parents=True, exist_ok=True)
        except OSError as err:
            raise Error(f"failed to create directory '{self.outdir}': {err}") from None

        # Copy raw data and assets.
        stats_paths, logs_paths, descr_paths = self._copy_raw_data()
        for src, descr in self._assets:
            self._copy_asset(Path(src), descr, self.outdir / src)

        # 'report_info' stores data used by the Javascript to generate the main report page
        # including the intro table, the file path of the tabs JSON dump and the toolname.
        report_info = {}
        report_info["intro_tbl"] = self._prepare_intro_table(stats_paths, logs_paths, descr_paths)
        report_info["toolname"] = self._refinfo["toolname"].title()

        metric_tabs = self._generate_metric_tabs()

        try:
            stats_tabs = self._generate_stats_tabs(stats_paths)
        except Error as err:
            _LOG.info("Error occurred during statistics tabs generation: %s", err)
            stats_tabs = []

        tabs = []
        # Convert Dataclasses to dictionaries so that they are JSON serialisable.
        tabs.append(dataclasses.asdict(_Tabs.CTabDC("Results", metric_tabs)))

        if stats_tabs:
            tabs.append(dataclasses.asdict(_Tabs.CTabDC("Stats", tabs=stats_tabs)))
        else:
            _LOG.info("All statistics have been skipped therefore the report will not contain a "
                      "'Stats' tab.")

        tabs_path = self.outdir / "tabs.json"
        self._dump_json(tabs, tabs_path, "tab container")

        report_info["tab_file"] = str(tabs_path.relative_to(self.outdir))
        rinfo_path = self.outdir / "report_info.json"
        self._dump_json(report_info, rinfo_path, "report information dictionary")

        self._copy_asset("js/index.html", "root HTML page of the report.",
                         self.outdir / "index.html")

    def _mangle_loaded_res(self, res): # pylint: disable=no-self-use, unused-argument
        """
        This method is called for every 'pandas.DataFrame' corresponding to the just loaded CSV
        file. The subclass can override this method to mangle the 'pandas.DataFrame'.
        """

        for colname in res.df:
            defs = res.defs.info.get(colname)
            if not defs:
                continue

            # Some columns should be dropped if they are "empty", i.e., contain only zero values.
            # For example, the C-state residency columns may be empty. This usually means that the
            # C-state was either disabled or just does not exist.
            if defs.get("drop_empty") and not res.df[colname].any():
                _LOG.debug("dropping empty column '%s'", colname)
                res.df.drop(colname, axis="columns", inplace=True)

        # Update columns lists in case some of the columns were removed from the loaded
        # 'pandas.Dataframe'.
        for name in ("_smry_colnames", "xaxes", "yaxes", "hist", "chist"):
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

        _LOG.debug("summaries will be calculated for these columns: %s",
                   ", ".join(self._smry_colnames))
        _LOG.debug("additional colnames: %s", ", ".join(self._more_colnames))

        for res in self.rsts:
            _LOG.debug("hover colnames: %s", ", ".join(self._hov_colnames[res.reportid]))

            colnames = []
            for colname in self._hov_colnames[res.reportid] + self._more_colnames:
                if colname in res.colnames_set:
                    colnames.append(colname)

            csel = Trivial.list_dedup(self._smry_colnames + colnames)
            res.set_csel(csel)
            res.load_df()

            # We'll be dropping columns and adding temporary columns, so we'll affect the original
            # 'pandas.DataFrame'. This is more efficient than creating copies.
            self._mangle_loaded_res(res)

        # Some columns from the axes lists could have been dropped, update the lists.
        self._drop_absent_colnames()

    def generate(self):
        """Generate the HTML report and store the result in 'self.outdir'.

        Important note: this method will modify the input test results in 'self.rsts'. This is done
        for effeciency purposes, to avoid copying the potentially large amounts of data
        (instances of 'pandas.DataFrame').
        """

        # Load the required datapoints into memory.
        self._load_results()

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

    def _drop_absent_colnames(self):
        """
        Verify that test results provide the columns in 'xaxes', 'yaxes', 'hist' and 'chist'. Drop
        the absent columns. Also drop uknown columns (those not present in the "definitions").
        """

        lists = ("xaxes", "yaxes", "hist", "chist")

        for name in lists:
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

        for name in lists:
            for res in self.rsts:
                colnames = []
                for colname in getattr(self, name):
                    if colname in res.defs.info:
                        colnames.append(colname)
                    else:
                        _LOG.warning("dropping column '%s' from '%s' because it is not present in "
                                     "the definitions file at '%s'", colname, name, res.defs.path)
            setattr(self, name, colnames)

        for res in self.rsts:
            colnames = []
            for colname in self._hov_colnames[res.reportid]:
                if colname in res.defs.info:
                    colnames.append(colname)
                else:
                    _LOG.warning("dropping column '%s' from hover text because it is not present "
                                 "in the definitions file at '%s'", colname, res.defs.path)
            self._hov_colnames[res.reportid] = colnames

    def _init_colnames(self):
        """
        Assign default values to the diagram/histogram column names and remove possible
        duplication in user-provided input.
        """

        for name in ("xaxes", "yaxes", "hist", "chist"):
            if getattr(self, name):
                # Convert list of regular expressions into list of names.
                colnames = self._refres.find_colnames(getattr(self, name))
            else:
                colnames = []
            setattr(self, name, colnames)

        # Ensure '_hov_colnames' dictionary is initialized.
        self.set_hover_colnames(())

        self._drop_absent_colnames()

        # Both X- and Y-axes are required for scatter plots.
        if not self.xaxes or not self.yaxes:
            self.xaxes = self.yaxes = []

    def _init_assets(self):
        """
        'Assets' are the CSS and JS files which supplement the HTML which makes up the report.
        'self._assets' defines the assets which should be copied into the output directory. The list
        is in the format: (path_to_asset, asset_description).
        """

        self._assets = [
            ("js/dist/main.js", "bundled JavaScript"),
            ("js/dist/main.css", "bundled CSS"),
            ("js/dist/main.js.LICENSE.txt", "bundled dependency licenses"),
        ]

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
                with open(self.title_descr, "r", encoding="UTF-8") as fobj:
                    self.title_descr = fobj.read()
            except OSError as err:
                raise Error(f"failed to read the report description file {self.title_descr}:\n"
                            f"{err}") from err

        for res in self.rsts:
            if res.dirpath.resolve() == self.outdir.resolve():
                # Don't create report in results directory, use 'html-report' subdirectory instead.
                self.outdir = self.outdir.joinpath("html-report")

    def __init__(self, rsts, outdir, title_descr=None, xaxes=None, yaxes=None, hist=None,
                 chist=None, exclude_xaxes=None, exclude_yaxes=None):
        """
        The class constructor. The arguments are as follows.
          * rsts - list of 'RORawResult' objects representing the raw test results to generate the
                   HTML report for.
          * outdir - the output directory path to store the HTML report at.
          * title_descr - a string describing this report or a file path containing the description.
          *               The description will be put at the top part of the HTML report. It should
          *               describe the report in general (e.g., it compares platform A to platform
          *               B). By default no title description is added to the HTML report.
          * xaxes - list of regular expressions matching datapoints CSV file column names to use for
                    the X axis of scatter plot diagrams. A scatter plot will be generated for each
                    combination of 'xaxes' and 'yaxes' column name pair (except for the pairs in
                    'exclude_xaxes'/'exclude_yaxes'). Default is the first column in the datapoints
                    CSV file.
          * yaxes - list of regular expressions matching datapoints CSV file column names to use for
                    the Y axis of scatter plot diagrams. Default is the second column in the
                    datapoints CSV file.
          * hist - list of regular expressions matching datapoints CSV file column names to create a
                   histogram for. Default is the first column in the datapoints CSV file. An empty
                   string can be used to disable histograms.
          * chist - list of regular expressions matching datapoints CSV file column names to create
                    a cumulative histogram for. Default is he first column in the datapoints CSV
                    file. An empty string can be used to disable cumulative histograms.
          * exclude_xaxes - by default all diagrams of X- vs Y-axes combinations will be created.
                            The 'exclude_xaxes' is a list regular expressions matching datapoints
                            CSV file column names. There will be no scatter plot for each
                            combinations of 'exclude_xaxes' and 'exclude_yaxes'. In other words,
                            this argument along with 'exclude_yaxes' allows for excluding some
                            diagrams from the 'xaxes' and 'yaxes' combinations.
          * exclude_yaxes - same as 'exclude_xaxes', but for Y-axes.
        """

        self.rsts = rsts
        self.outdir = Path(outdir)
        self.title_descr = title_descr
        self.xaxes = xaxes
        self.yaxes = yaxes
        self.exclude_xaxes = exclude_xaxes
        self.exclude_yaxes = exclude_yaxes
        self.hist = hist
        self.chist = chist

        self._projname = "wult"

        # Users can change this to 'True' to make the reports relocatable. In which case the raw
        # results files will be copied from the test result directories to the output directory.
        self.relocatable = False

        # The first result is the 'reference' result.
        self._refres = rsts[0]
        # The raw reference result information.
        self._refinfo = self._refres.info

        # Names of columns in the datapoints CSV file to provide the summary function values for
        # (e.g., median, 99th percentile). The summaries will show up in the summary tables (one
        # table per metric).
        self._smry_colnames = None
        # List of functions to provide in the summary tables.
        self._smry_funcs = ("nzcnt", "max", "99.999%", "99.99%", "99.9%", "99%", "med", "avg",
                            "min", "std")
        # Per-test result list of column names to include into the hover text of the scatter plot.
        # By default only the x and y axis values are included.
        self._hov_colnames = {}
        # Additional columns to load, if they exist in the CSV file.
        self._more_colnames = []

        self._validate_init_args()
        self._init_colnames()

        # We'll provide summaries for every column participating in at least one diagram.
        smry_colnames = Trivial.list_dedup(self.yaxes + self.xaxes + self.hist + self.chist)
        # Summary functions table includes all test results, but the results may have a bit
        # different set of column names (e.g., they were collected with different wult versions # or
        # using different methods, or on different systems). Therefore, include only common columns
        # into it.
        self._smry_colnames = []
        for colname in smry_colnames:
            for res in rsts:
                if colname not in res.colnames_set:
                    break
            else:
                self._smry_colnames.append(colname)

        self._init_assets()

        if (self.exclude_xaxes and not self.exclude_yaxes) or \
           (self.exclude_yaxes and not self.exclude_xaxes):
            raise Error("'exclude_xaxes' and 'exclude_yaxes' must both be 'None' or both not be "
                        "'None'")
