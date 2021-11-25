# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
#          Vladislav Govtva <vladislav.govtva@intel.com>

"""
This module the base class for generating HTML reports for raw test results.
"""

import logging
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List
from pepclibs.helperlibs import Trivial, FSHelpers
from pepclibs.helperlibs.Exceptions import Error
from wultlibs.helperlibs import Jinja2
from wultlibs.rawresultlibs import RORawResult
from wultlibs.reportlibs import _PlotsBuilder

_LOG = logging.getLogger()

@dataclass
class Tab:
    """
    This class defines what is expected by the Jinja templates when adding a tab to the
    report.

    Jinja templates read from Tab objects to populate tabs in the report. Here is how it is done:
     1. The tab selector (the button you click to open a tab) is created with 'label' as the text in
        the button and 'id' as the HTML element ID.
     2. If 'Tab.tabs' is populated with child tabs, the template recursively adds these tabs.
     3. Depending on the 'category' of tab chosen, the template uses a different macro to populate
        the tab. The macro will be passed the dictionary 'mdata'.
    """

    # HTML tab element ID.
    id: str
    # Label for the tab selector.
    label: str
    # Child tabs (each child tab is of type 'Tab').
    tabs: List['Tab'] = None
    # If a 'category' is defined, it is used to populate the tab using the correct macro.
    # Possible values include 'metric', 'info' or None.
    category: str = None
    # Macros which populate the tab content will be provided the 'mdata' dictionary.
    mdata: Dict = None

class HTMLReportBase:
    """This is the base class for generating HTML reports for raw test results."""

    def _prepare_intro_table(self, stats_paths, logs_paths, descr_paths):
        """
        Create the intro table, which is the very first table in the report and it shortly
        summarizes the entire report. The 'stats_paths' should be a dictionary indexed by report ID
        and containing the stats directory path. Similarly, the 'logs_paths' and 'descr_paths'
        contains paths to the logs and the test result description files.
        """

        intro_tbl = {}
        intro_tbl["Title"] = {}
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

        # Add links to the stats directories.
        if stats_paths:
            key = "stats"
            intro_tbl["Title"][key] = "Statistics"
            for res in self.rsts:
                path = stats_paths.get(res.reportid, "Not available")
                intro_tbl[res.reportid][key] = path

        # Add links to the logs directories.
        if logs_paths:
            key = "logs"
            intro_tbl["Title"][key] = "Logs"
            for res in self.rsts:
                path = logs_paths.get(res.reportid, "Not available")
                intro_tbl[res.reportid][key] = path

        # Add links to the descriptions.
        if descr_paths:
            key = "descr"
            intro_tbl["Title"][key] = "Test description"
            for res in self.rsts:
                path = descr_paths.get(res.reportid, "Not available")
                intro_tbl[res.reportid][key] = path

        return intro_tbl

    def _prepare_smrys_tables(self, pinfos):
        """
        Summaries table includes values like average and median values for a single metric (column).
        It "summarizes" the metric. This function creates summaries table for each metrics included
        in 'pinfos' list.
        """

        if not pinfos:
            return {}

        smrys_tbl = {}
        smrys_tbl["Title"] = {}
        for res in self.rsts:
            smrys_tbl[res.reportid] = {}

        for pinfo in pinfos:
            for colname in (pinfo.colname, pinfo.xcolname):
                if colname in smrys_tbl["Title"]:
                    continue

                # Skip non-numeric columns, as summaries are calculated only for numeric columns.
                if not self.rsts[0].is_numeric(colname):
                    continue

                # Each column name is represented by a row in the summary table. Fill the "Title"
                # column.
                title_dict = smrys_tbl["Title"][colname] = {}
                defs = self._refres.defs.info[colname]

                title_dict["colname"] = colname
                unit = defs.get("short_unit", "")
                if unit:
                    title_dict["colname"] += f", {unit}"
                title_dict["coldescr"] = defs["descr"]

                title_dict["funcs"] = {}
                for funcname in self._smry_funcs:
                    # Select only those functions that are present in all test results. For example,
                    # 'std' will not be present if the result has only one datapoint. In this case,
                    # we need to exclude the 'std' function.
                    if all(res.smrys[colname].get(funcname) for res in self.rsts):
                        title_dict["funcs"][funcname] = RORawResult.get_smry_func_descr(funcname)

                # Now fill the values for each result.
                for res in self.rsts:
                    res_dict = smrys_tbl[res.reportid][colname] = {}
                    res_dict["funcs"] = {}

                    for funcname in title_dict["funcs"]:
                        val = res.smrys[colname][funcname]
                        fmt = "{}"
                        if defs["type"] == "float":
                            fmt = "{:.2f}"

                        fdict = res_dict["funcs"][funcname] = {}
                        fdict["val"] = fmt.format(val)
                        fdict["raw_val"] = val

                        if self._refres.reportid == res.reportid:
                            fdict["hovertext"] = "This is the reference result, other results " \
                                                 "are compared to this one."
                            continue

                        ref_fdict = smrys_tbl[self._refres.reportid][colname]["funcs"][funcname]
                        change = val - ref_fdict["raw_val"]
                        if ref_fdict["raw_val"]:
                            percent = (change / ref_fdict["raw_val"]) * 100
                        else:
                            percent = change
                        change = fmt.format(change) + unit
                        percent = "{:.1f}%".format(percent)
                        fdict["hovertext"] = f"Change: {change} ({percent})"

        return smrys_tbl

    def _copy_raw_data(self):
        """Copy raw test results to the output directory."""

        # Paths to the stats directory.
        stats_paths = {}
        # Paths to the logs directory.
        logs_paths = {}
        # Paths to test reports' description files.
        descr_paths = {}

        for res in self.rsts:
            srcpath = res.dirpath
            resrootdir = "raw-" + res.reportid
            dstpath = self.outdir.joinpath(resrootdir)

            if self.relocatable == "copy":
                FSHelpers.copy_dir(srcpath, dstpath, exist_ok=True, ignore=["html-report"])
                FSHelpers.set_default_perm(dstpath)
            else:
                FSHelpers.move_copy_link(srcpath, dstpath, action="symlink", exist_ok=True)

            if res.stats_path.is_dir():
                hlink = f"<a href=\"{resrootdir}/{res.stats_path.name}\">Statistics</a>"
                stats_paths[res.reportid] = hlink
            if res.logs_path.is_dir():
                hlink = f"<a href=\"{resrootdir}/{res.logs_path.name}\">Logs</a>"
                logs_paths[res.reportid] = hlink
            if res.descr_path.is_file():
                hlink = f"<a href=\"{resrootdir}/{res.descr_path.name}\">Test description</a>"
                descr_paths[res.reportid] = hlink

        return stats_paths, logs_paths, descr_paths

    def _copy_asset(self, src, action, descr):
        """Copy asset file to the output directory or create symlink."""

        asset_path = FSHelpers.find_app_data(self._projname, src, descr=descr)
        dstpath = self.outdir.joinpath(src)
        FSHelpers.move_copy_link(asset_path, dstpath, action, exist_ok=True)

    def _generate_metric_tabs(self, all_pinfos):
        """
        Generate Tabs which contain the plots in 'all_pinfos'. These Tabs are then used to populate
        the Jinja templates and resultantly the HTML report.
        """

        tabs = []
        for colname, pinfos in all_pinfos.items():
            smrys_tbl = self._prepare_smrys_tables(pinfos)

            # Build plot paths 'ppaths' (relative to the output directory).
            ppaths = []
            for pinfo in pinfos:
                p = self._plotsdir.joinpath(pinfo.fname)
                ppaths.append(p.relative_to(self.outdir))

            metric_data = {}
            metric_data["smrys_tbl"] = smrys_tbl
            metric_data["ppaths"] = ppaths
            metric_data["colname"] = colname
            metric_data["title_descr"] = self.title_descr
            tabs.append(Tab(id=colname, label=colname, category="metric", mdata=metric_data))
        return tabs

    def _generate_report(self):
        """Put together the final HTML report."""

        _LOG.info("Generating the HTML report.")

        # Make sure the output directory exists.
        try:
            self.outdir.mkdir(parents=True, exist_ok=True)
        except OSError as err:
            raise Error(f"failed to create directory '{self.outdir}': {err}") from None

        # Copy raw data and assets according to 'self.relocatable'.
        stats_paths, logs_paths, descr_paths = self._copy_raw_data()
        for path, descr in self._assets:
            self._copy_asset(Path(path), self.relocatable, descr)

        # Always copy 'css/style.css' as it is so small.
        self._copy_asset(Path("css/style.css"), "copy", "HTML report CSS file")

        # Find the template paths.
        templdir = FSHelpers.find_app_data(self._projname, Path("templates"),
                                           descr="HTML report Jinja2 templates")

        jenv = Jinja2.build_jenv(templdir, trim_blocks=True, lstrip_blocks=True)
        jenv.globals["intro_tbl"] = self._prepare_intro_table(stats_paths, logs_paths, descr_paths)
        jenv.globals["toolname"] = self._refinfo["toolname"]

        all_pinfos = self._pinfos
        if not self._pinfos:
            # This may happen if there are no diagrams to plot. In this case we still want to
            # generate an HTML report, but without diagrams.
            _LOG.warning("no diagrams to plot")
            all_pinfos = {"Dummy" : {}}

        metric_tabs = self._generate_metric_tabs(all_pinfos)

        tabs = []
        tabs.append(Tab(id="Results", label="Results", tabs=metric_tabs))
        # 'tab_container' acts as a global store of tabs.
        jenv.globals["tab_container"] = {"tabs": tabs}

        templfile = outfile = "index.html"
        Jinja2.render_template(jenv, Path(templfile), outfile=self.outdir.joinpath(outfile))

    def _calc_smrys(self):
        """Calculate summaries that we are going to show in the summary table."""

        for res in self.rsts:
            _LOG.debug("calculate summary functions for '%s'", res.reportid)
            res.calc_smrys(regexs=self._smry_colnames, funcnames=self._smry_funcs)

    def _mangle_loaded_res(self, res): # pylint: disable=no-self-use, unused-argument
        """
        This method is called for every dataframe corresponding to the just loaded CSV file. The
        subclass can override this method to mangle the dataframe.
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

        # Update columns lists in case some of the columns were removed from the loaded dataframe.
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
            # dataframe. This is more efficient than creating copies.
            self._mangle_loaded_res(res)

        # Some columns from the axes lists could have been dropped, update the lists.
        self._drop_absent_colnames()

    def generate(self):
        """Generate the HTML report and store the result in 'self.outdir'.

        Important note: this method will modify the input test results in 'self.rsts'. This is done
        for effeciency purposes, to avoid copying the potentially large amounts of data (pandas
        dataframes).
        """

        if self.relocatable not in ("copy", "symlink"):
            raise Error("bad 'relocatable' value, use one of: copy, symlink")

        # Load the required datapoints into memory.
        self._load_results()

        # Calculate the summaries for the datapoints, like min. and max. values.
        self._calc_smrys()

        try:
            self._plotsdir.mkdir(parents=True, exist_ok=True)
        except OSError as err:
            raise Error(f"failed to create directory '{self._plotsdir}': {err}") from None

        # Generate the plots.
        self._pinfos = self._pbuilder.generate_plots()

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
        'self._assets' defines the assets which should be copied into or linked to from the output
        directory. The list is in the format: (path_to_asset, asset_description).
        """

        self._assets = [
            ("bootstrap/css/bootstrap.min.css", "Bootstrap CSS file"),
            ("bootstrap/css/bootstrap.min.css.map", "Bootstrap CSS source map"),
            ("bootstrap/js/bootstrap.min.js", "Bootstrap js file"),
            ("bootstrap/js/bootstrap.min.js.map", "Bootstrap js source map"),
            ("bootstrap/LICENSE", "Bootstrap usage License"),
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
                with open(self.title_descr, "r") as fobj:
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
        self.hist = hist
        self.chist = chist

        self._projname = "wult"
        self._plotsdir = self.outdir.joinpath("plots")
        self._pbuilder = None

        # Users can change this to 'copy' to make the reports relocatable. In which case the raw
        # results and report assets such as CSS and JS files will be copied from the test result
        # directories to the output directory.
        self.relocatable = "symlink"

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
        # Plot information dictionaries. This is a dictionary of of lists, each list containing
        # sub-dictionaries describing a single plot. The lists of sub-dictionaries are grouped by
        # the "X" and "Y" axis column names, because later plots with the same "Y" and "Y" axes will
        # go to the same HTML page.
        self._pinfos = {}
        # Per-test result list of column names to include into the hover text of the scatter plot.
        # By default only the x and y axis values are included.
        self._hov_colnames = {}
        # Additional columns to load, if they exist in the CSV file.
        self._more_colnames = []

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
        self._validate_init_args()

        self._pbuilder = _PlotsBuilder.PlotsBuilder(self.rsts, self._plotsdir, self.xaxes,
                                                    self.yaxes, self.hist, self.chist,
                                                    exclude_xaxes, exclude_yaxes,
                                                    self._hov_colnames)
