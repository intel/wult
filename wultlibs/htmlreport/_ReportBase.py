# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
#          Vladislav Govtva <vladislav.govtva@intel.com>

"""
This module provides the base class for generating HTML reports for raw test results.
"""

import itertools
import json
import logging
import contextlib
from pathlib import Path
from pepclibs.helperlibs import Trivial, LocalProcessManager, ProjectFiles
from pepclibs.helperlibs.Exceptions import Error, ErrorNotFound
from statscollectlibs.htmlreport import _IntroTable, HTMLReport
from statscollectlibs.htmlreport.tabs import _Tabs
from wultlibs.helperlibs import FSHelpers
from wultlibs.htmlreport import _MetricDTabBuilder

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
            msg = Error(err).indent(2)
            raise Error(f"could not generate report: failed to JSON dump '{descr}' to '{path}':\n"
                        f"{msg}") from None

    def _add_intro_tbl_links(self, label, paths):
        """
        Add links in 'paths' to the 'intro_tbl' dictionary. Arguments are as follows:
            * paths - dictionary in the format {Report ID: Path to Link to}.
            * label - the label that will be shown in the intro table for these links.
        """

        valid_paths = {}
        for res in self.rsts:
            reportid = res.reportid
            path = paths.get(reportid)

            # Do not add links for 'label' if 'paths' does not contain a link for every result or
            # if a path points to somewhere outside of the report directory.
            if path is None or self.outdir not in path.parents:
                return

            # If the path points to inside the report directory then make it relative to the output
            # directory so that the output directory is relocatable. That is, the whole directory
            # can be moved or copied without breaking the link.
            valid_paths[reportid] = path.relative_to(self.outdir)

        row = self._intro_tbl.create_row(label)

        for reportid, path in valid_paths.items():
            row.add_cell(reportid, label, link=path)

    def _prepare_intro_table(self, stats_paths, logs_paths):
        """
        Create the intro table, which is the very first table in the report and it shortly
        summarizes the entire report. The 'stats_paths' should be a dictionary indexed by report ID
        and containing the stats directory path. Similarly, the 'logs_paths' contains paths to the
        logs. Returns the path of the intro table file generated.
        """
        # Add tool information.
        tinfo_row = self._intro_tbl.create_row("Data Collection Tool")
        for res in self.rsts:
            tool_info = f"{res.info['toolname'].capitalize()} version {res.info['toolver']}"
            tinfo_row.add_cell(res.reportid, tool_info)

        # Add run date.
        date_row = self._intro_tbl.create_row("Collection Date")
        for res in self.rsts:
            date_row.add_cell(res.reportid, res.info.get("date"))

        # Add datapoint counts.
        dcount_row = self._intro_tbl.create_row("Datapoints Count")
        for res in self.rsts:
            dcount_row.add_cell(res.reportid, len(res.df.index))

        # Add run duration.
        duration_row = self._intro_tbl.create_row("Duration")
        for res in self.rsts:
            duration_row.add_cell(res.reportid, res.info.get("duration"))

        # Add measurement resolution.
        if all("resolution" in res.info for res in self.rsts):
            dres_row = self._intro_tbl.create_row("Device Resolution")
            for res in self.rsts:
                dres_row.add_cell(res.reportid, f"{res.info['resolution']}ns")

        # Add measured CPU.
        mcpu_row = self._intro_tbl.create_row("Measured CPU")
        for res in self.rsts:
            cpunum = res.info.get("cpunum")
            if cpunum is not None:
                cpunum = str(cpunum)

            mcpu_row.add_cell(res.reportid, cpunum)

        # Add device ID.
        devid_row = self._intro_tbl.create_row("Device ID")
        for res in self.rsts:
            devid_text = res.info.get("devid")
            if devid_text and "devdescr" in res.info:
                devid_text += f" ({res.info['devdescr']})"
            devid_row.add_cell(res.reportid, devid_text)

        # Add links to the stats directories.
        self._add_intro_tbl_links("Statistics", stats_paths)
        # Add links to the logs directories.
        self._add_intro_tbl_links("Logs", logs_paths)

    @staticmethod
    def _copy_dir(srcdir, dstpath):
        """
        Helper function for '_copy_raw_data()'. Copy the 'srcdir' to 'dstpath' and set permissions
        accordingly.
        """

        try:
            FSHelpers.copy_dir(srcdir, dstpath, exist_ok=True, ignore=["html-report"])
            FSHelpers.set_default_perm(dstpath)

            # This block of code helps on SELinux-enabled systems when the output directory
            # ('self.outdir') is exposed via HTTP. In this case, the output directory should
            # have the right SELinux attributes (e.g., 'httpd_user_content_t' in Fedora 35).
            # The raw wult data that we just copied does not have the SELinux attribute, and
            # won't be accessible via HTTPs. Run 'restorecon' tool to fix up the SELinux
            # attributes.
            with LocalProcessManager.LocalProcessManager() as lpman:
                with contextlib.suppress(ErrorNotFound):
                    lpman.run_verify(f"restorecon -R {dstpath}")
        except Error as err:
            msg = Error(err).indent(2)
            raise Error(f"failed to copy raw data to report directory:\n{msg}") from None

    def _copy_raw_data(self):
        """Copy raw test results to the output directory."""

        # Paths to the stats directory.
        stats_paths = {}
        # Paths to the logs directory.
        logs_paths = {}

        for res in self.rsts:
            resdir = res.dirpath
            dstpath = self.outdir / f"raw-{res.reportid}"

            logs_dir = res.logs_path.name
            stats_dir  = res.stats_path.name

            # Before either logs or stats have been copied to 'outdir', assume neither will be.
            logs_dst = resdir / logs_dir
            stats_dst = resdir / stats_dir

            if self.relocatable:
                self._copy_dir(resdir, dstpath)

                # Use the path of the copied raw results rather than the original.
                logs_dst = dstpath / logs_dir
                stats_dst = dstpath / stats_dir
            else:
                try:
                    # Copy only the logs across if the report is not 'relocatable'.
                    dstpath.mkdir(parents=True, exist_ok=True)

                    logs_dst = dstpath / logs_dir
                    if not logs_dst.exists():
                        self._copy_dir(resdir / logs_dir, logs_dst)

                except (OSError, Error) as err:
                    _LOG.warning("unable to copy log files to the generated report: %s", err)
                    logs_dst = resdir / logs_dir

            if res.stats_path.is_dir():
                stats_paths[res.reportid] = stats_dst
            else:
                stats_paths[res.reportid] = None

            if res.logs_path.is_dir():
                # Stats are always copied to 'dstpath'.
                logs_paths[res.reportid] = logs_dst
            else:
                logs_paths[res.reportid] = None

        return stats_paths, logs_paths

    @staticmethod
    def _copy_asset(src, what, dst):
        """
        Copy asset file to the output directory. Arguments are as follows:
         * src - source path of the file to copy.
         * what - a human-readable name for what is being copied.
         * dst - where the file should be copied to.
        """

        asset_path = ProjectFiles.find_project_data("wult", src, what=what)
        FSHelpers.move_copy_link(asset_path, dst, "copy", exist_ok=True)

    def _get_smry_funcs(self, smry_metrics):
        """
        Helper function for '_generate_results_tabs()'. Returns a summary functions dictionary based
        on the metrics in 'smry_metrics'.
        """

        smry_funcs = {}
        for smry_metric in smry_metrics:
            # Add summary functions from 'self._smry_funcs' for each metric in 'smry_metrics'.
            if smry_metric in self._smry_funcs:
                smry_funcs[smry_metric] = self._smry_funcs[smry_metric]

        return smry_funcs

    def _get_axis_def(self, axis, base_col_suffix):
        """
        Get the metric definition for 'axis'. First tries to retrieve the "base metric" (using
        'base_col_suffix') and uses the definition for 'axis' if no "base metric" is found.
        """

        defs = self._refres.defs.info
        base_axis = axis + base_col_suffix
        # Try to add a 'base' metric if it has been calculated, otherwise take the unscaled column.
        return defs[base_axis] if base_axis in self._refres.df else defs[axis]

    def _get_axes_defs(self, axes, base_col_suffix):
        """
        Returns the definition dictionaries for the metrics on the axes in 'axes'. For each axis in
        'axes', tries to find the "base metric" if one has been calculated. Otherwise, uses the axis
        metric.
        """

        plot_defs = []
        for xy_pair in axes:
            xdef = self._get_axis_def(xy_pair[0], base_col_suffix)
            ydef = self._get_axis_def(xy_pair[1], base_col_suffix)
            plot_defs.append((xdef, ydef,))
        return plot_defs

    def _gen_stime_ldist_tab(self, tab_metrics, base_col_suffix, hover_defs):
        """
        Helper method for '_generate_results_tabs()'. Generate a tab for the 'SilentTime' and/or
        'LDist' metrics. Returns 'None', if the tab had to be skipped for some reason.
        """

        defs = self._refres.defs.info

        # Configure what should be included in the 'SilentTime/LDist' tab.
        tab_config = {
            "scatter": [("LDist", "SilentTime")],
            "hist": ["SilentTime", "LDist"],
            "smry_metrics": ["SilentTime", "LDist"],
        }

        # Only include plots with metrics in 'tab_metrics'.
        s_axes = [xypair for xypair in tab_config["scatter"] if set(xypair).issubset(tab_metrics)]
        tab_config["scatter"] = s_axes
        tab_config["hist"] = [metric for metric in tab_config["hist"] if metric in tab_metrics]

        if ("SilentTime" in tab_metrics and "LDist" in tab_metrics):
            tab_mdef = defs.get("SilentTime", defs["LDist"])
            tab_config["title"] = "SilentTime/LDist"
        elif "SilentTime" in tab_metrics:
            tab_mdef = defs["SilentTime"]
            tab_config["title"] = "SilentTime"
        elif "LDist" in tab_metrics:
            tab_mdef = defs["LDist"]
            tab_config["title"] = "LDist"
        else:
            _LOG.debug("skipping 'SilentTime/LDist' tab since neither metric is included as a tab.")
            return None

        s_defs = self._get_axes_defs(tab_config["scatter"], base_col_suffix)
        h_defs = [self._get_axis_def(metric, base_col_suffix) for metric in tab_config["hist"]]

        dtab_bldr = _MetricDTabBuilder.MetricDTabBuilder(self.rsts, self.outdir, tab_mdef)
        dtab_bldr.title = tab_config["title"]
        dtab_bldr.add_plots(s_defs, h_defs, hover_defs=hover_defs)

        smry_metrics = [metric for metric in tab_config["smry_metrics"] if metric in tab_metrics]
        smry_funcs = self._get_smry_funcs(smry_metrics)
        # Only add a summary table if summary metrics were added to 'tab_smry_funcs'.
        if smry_funcs:
            dtab_bldr.add_smrytbl(smry_funcs, self._refres.defs)

        return dtab_bldr.get_tab()

    def _generate_results_tabs(self):
        """
        Generate and return a list of sub-tabs for the results tab. The results tab includes the
        main metrics, such as "WakeLatency". The elements of the returned list are tab dataclass
        objects, such as 'DTabDC'.
        """

        # Scale all results to their base units (i.e. without any SI prefixes) so that 'plotly'
        # can dynamically scale the units in plots.
        base_col_suffix = "_base" # Add this suffix to the names of scaled columns.
        for res in self.rsts:
            res.scale_to_base_units(base_col_suffix)

            _LOG.debug("calculate summary functions for '%s'", res.reportid)
            smry_funcs = ("nzcnt", "max", "99.999%", "99.99%", "99.9%", "99%", "med", "avg", "min",
                          "std")
            res.calc_smrys(regexs=self._smry_metrics, funcnames=smry_funcs)

        plot_axes = [(x, y) for x, y in itertools.product(self.xaxes, self.yaxes) if x != y]

        if self.exclude_xaxes and self.exclude_yaxes:
            x_axes = self._refres.find_metrics(self.exclude_xaxes)
            y_axes = self._refres.find_metrics(self.exclude_yaxes)
            exclude_axes = list(itertools.product(x_axes, y_axes))
            plot_axes = [axes for axes in plot_axes if axes not in exclude_axes]

        dtabs = []
        tab_metrics = [y for _, y in plot_axes]
        tab_metrics += self.chist + self.hist
        tab_metrics = Trivial.list_dedup(tab_metrics)

        # Convert 'self._hov_metrics' to contain definitions for each metric.
        hover_defs = {}
        reports = {res.reportid: res for res in self.rsts}
        for reportid, metrics in self._hov_metrics.items():
            hover_defs[reportid] = [reports[reportid].defs.info[m] for m in metrics]

        for metric in tab_metrics:
            if metric in ("SilentTime", "LDist"):
                continue
            _LOG.info("Generating %s tab.", metric)
            smry_metrics = []
            # Only add plots which have the tab metric on one of the axes.
            axes =  [xypair for xypair in plot_axes if metric in xypair]
            tab_plots = self._get_axes_defs(axes, base_col_suffix)

            smry_metrics += list(set.union(*[set(xypair) for xypair in axes]))
            smry_metrics = Trivial.list_dedup(smry_metrics)

            metric_def = self._refres.defs.info[metric]
            dtab_bldr = _MetricDTabBuilder.MetricDTabBuilder(self.rsts, self.outdir, metric_def)

            smry_funcs = self._get_smry_funcs(smry_metrics)
            # Only add a summary table if summary metrics were added to 'smry_funcs'.
            if smry_funcs:
                dtab_bldr.add_smrytbl(smry_funcs, self._refres.defs)

            metric_def = self._refres.defs.info.get(metric + base_col_suffix, metric_def)
            hist_metrics = [metric] if metric in self.hist else []
            hist_defs = [self._get_axis_def(metric, base_col_suffix) for metric in hist_metrics]
            chist_metrics = [metric] if metric in self.chist else []
            chist_defs = [self._get_axis_def(metric, base_col_suffix) for metric in chist_metrics]
            dtab_bldr.add_plots(tab_plots, hist_defs, chist_defs, hover_defs)

            dtabs.append(dtab_bldr.get_tab())

        if "SilentTime" in tab_metrics or "LDist" in tab_metrics:
            stime_ldist_tab = self._gen_stime_ldist_tab(tab_metrics, base_col_suffix, hover_defs)
            if stime_ldist_tab is not None:
                dtabs.append(stime_ldist_tab)

        return dtabs

    def _generate_report(self):
        """Put together the final HTML report."""

        _LOG.info("Generating the HTML report.")

        # Make sure the output directory exists.
        try:
            self.outdir.mkdir(parents=True, exist_ok=True)
        except OSError as err:
            msg = Error(err).indent(2)
            raise Error(f"failed to create directory '{self.outdir}':\n{msg}") from None

        stats_paths, logs_paths = self._copy_raw_data()
        self._prepare_intro_table(stats_paths, logs_paths)

        results_tabs = self._generate_results_tabs()

        tabs = [_Tabs.CTabDC("Results", results_tabs)]

        toolname = self._refinfo["toolname"].title()

        mcpus = {res.reportid: str(res.info["cpunum"]) for res in self.rsts if "cpunum" in res.info}

        rep = HTMLReport.HTMLReport(self.outdir)
        rep.generate_report(tabs, stats_paths, self._intro_tbl, f"{toolname} Report",
                            self.report_descr, mcpus)

    @staticmethod
    def _mangle_loaded_res(res):
        """
        This method is called for every 'pandas.DataFrame' corresponding to the just loaded CSV
        file. The subclass can override this method to mangle the 'pandas.DataFrame'.
        """

        for metric in res.df:
            defs = res.defs.info.get(metric)
            if not defs:
                continue

            # Some columns should be dropped from 'res.df' if they are "empty", i.e. contain only
            # zero values. For example, the C-state residency columns may be empty. This usually
            # means that the C-state was either disabled or just does not exist.
            if defs.get("drop_empty") and not res.df[metric].any():
                _LOG.debug("dropping empty column '%s'", metric)
                res.df.drop(metric, axis="columns", inplace=True)
                res.metrics_set.remove(metric)

        return res.df

    def _load_results(self):
        """Load the test results from the CSV file and/or apply the metrics selector."""

        _LOG.debug("summaries will be calculated for these metrics: %s",
                   ", ".join(self._smry_metrics))
        _LOG.debug("additional metrics: %s", ", ".join(self._more_metrics))

        for res in self.rsts:
            _LOG.debug("hover metrics: %s", ", ".join(self._hov_metrics[res.reportid]))

            metrics = []
            for metric in self._hov_metrics[res.reportid] + self._more_metrics:
                if metric in res.metrics_set:
                    metrics.append(metric)

            minclude = Trivial.list_dedup(self._smry_metrics + metrics)
            res.set_minclude(minclude)
            res.load_df()

            # We'll be dropping columns and adding temporary columns, so we'll affect the original
            # 'pandas.DataFrame'. This is more efficient than creating copies.
            self._mangle_loaded_res(res)

        # Some metrics from the axes lists could have been dropped, update the lists.
        self._drop_absent_metrics()

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

    def set_hover_metrics(self, regexs):
        """
        This methods allows for specifying metrics that have to be included to the hover text on the
        scatter plot. The 'regexs' argument should be a list of hover text metric regular
        expressions. In other words, each element of the list will be treated as a regular
        expression. Every metric will be matched against this regular expression, and matched
        metrics will be added to the hover text.
        """

        for res in self.rsts:
            self._hov_metrics[res.reportid] = res.find_metrics(regexs, must_find_any=False)

    def _drop_absent_metrics(self):
        """
        Verify that test results provide the metrics in 'xaxes', 'yaxes', 'hist' and 'chist'. Drop
        the absent metrics. Also drop unknown metrics (those not present in the "definitions").
        """

        lists = ("xaxes", "yaxes", "hist", "chist")

        for name in lists:
            res_metrics = set()
            for res in self.rsts:
                res_metrics.update(res.metrics_set)
            intersection = set(getattr(self, name)) & res_metrics
            metrics = []
            for metric in getattr(self, name):
                if metric in intersection:
                    metrics.append(metric)
                else:
                    _LOG.warning("dropping metric '%s' from '%s' because it is not present in any "
                                 "of the results", metric, name)
            setattr(self, name, metrics)

        for name in lists:
            for res in self.rsts:
                metrics = []
                for metric in getattr(self, name):
                    if metric in res.defs.info:
                        metrics.append(metric)
                    else:
                        _LOG.warning("dropping metric '%s' from '%s' because it is not present in "
                                     "the definitions file at '%s'", metric, name, res.defs.path)
            setattr(self, name, metrics)

        for res in self.rsts:
            metrics = []
            for metric in self._hov_metrics[res.reportid]:
                if metric in res.defs.info:
                    metrics.append(metric)
                else:
                    _LOG.warning("dropping metric '%s' from hover text because it is not present "
                                 "in the definitions file at '%s'", metric, res.defs.path)
            self._hov_metrics[res.reportid] = metrics

    def _init_metrics(self):
        """
        Assign default values to the diagram/histogram metrics and remove possible duplication in
        user-provided input.
        """

        for name in ("xaxes", "yaxes", "hist", "chist"):
            if getattr(self, name):
                # Convert list of regular expressions into list of names.
                metrics = self._refres.find_metrics(getattr(self, name))
            else:
                metrics = []
            setattr(self, name, metrics)

        # Ensure '_hov_metrics' dictionary is initialized.
        self.set_hover_metrics(())

        self._drop_absent_metrics()

        # Both X- and Y-axes are required for scatter plots.
        if not self.xaxes or not self.yaxes:
            self.xaxes = self.yaxes = []

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

        if self.report_descr and Path(self.report_descr).is_file():
            try:
                with open(self.report_descr, "r", encoding="UTF-8") as fobj:
                    self.report_descr = fobj.read()
            except OSError as err:
                msg = Error(err).indent(2)
                raise Error(f"failed to read the report description file {self.report_descr}:\n"
                            f"{msg}") from err

        for res in self.rsts:
            if res.dirpath.resolve() == self.outdir.resolve():
                # Don't create report in results directory, use 'html-report' subdirectory instead.
                self.outdir = self.outdir.joinpath("html-report")

    def _init_smry_funcs(self, smry_funcs):
        """
        Assign which summary functions to calculate and include for each metric. Stores the result
        in 'self._smry_funcs'. 'smry_funcs' should be a dictionary containing 'regex':'smry_funcs'
        pairs where 'smry_funcs' is a list of summary functions to calculate and include for
        metrics represented by the regular expression 'regex'.
        """

        self._smry_funcs = {}
        for regex, funcs in smry_funcs.items():
            # Find metrics represented by 'regex'.
            metrics = self._refres.find_metrics([regex], must_find_any=False)

            # If there are no metrics found, move onto the next set of funcs.
            if not metrics:
                continue

            for metric in metrics:
                if metric not in self._smry_funcs:
                    self._smry_funcs[metric] = funcs
                else:
                    # If 'metric' already has funcs, add new funcs from 'funcs' without duplicating.
                    # This handles when a metric is in more than one regex.
                    for func in smry_funcs:
                        if func not in self._smry_funcs[metric]:
                            self._smry_funcs[metric].append(func)

    def __init__(self, rsts, outdir, report_descr=None, xaxes=None, yaxes=None, hist=None,
                 chist=None, exclude_xaxes=None, exclude_yaxes=None, smry_funcs=None):
        """
        The class constructor. The arguments are as follows.
          * rsts - list of 'RORawResult' objects representing the raw test results to generate the
                   HTML report for.
          * outdir - the path at which to store the output directory of the HTML report.
          * report_descr - a string describing this report or a file path containing the
                           description. The description will be put at the top part of the HTML
                           report. It should describe the report in general (e.g. it compares
                           platform A to platform B). By default no title description is added to
                           the HTML report.
          * xaxes - list of regular expressions matching metrics to use for the X-axis of scatter
                    plot diagrams. A scatter plot will be generated for each combination of 'xaxes'
                    and 'yaxes' metric pair (except for pairs from 'exclude_xaxes' and
                    'exclude_yaxes'). Default is the first metric represented by a column in the
                    datapoints CSV file.
          * yaxes - list of regular expressions matching metrics to use for the Y-axis of scatter
                    plot diagrams. Default is the second metric represented by a column in the
                    datapoints CSV file.
          * hist - list of regular expressions matching metrics to create a histogram for. Default
                   is the first metric represented by a column in the datapoints CSV file. An empty
                   string can be used to disable histograms.
          * chist - list of regular expressions matching metrics to create a cumulative histogram
                    for. Default is the first metric represented by a column in the datapoints CSV
                    file. An empty string can be used to disable cumulative histograms.
          * exclude_xaxes - by default all diagrams of X- vs Y-axes combinations will be created.
                            The 'exclude_xaxes' is a list regular expressions matching metrics. A
                            plot will be excluded if its X-axis is in 'exclude_xaxes' and its Y-axis
                            is in 'exclude_yaxes'. This means that this argument, along with
                            'exclude_yaxes', allows for excluding some diagrams from the 'xaxes' and
                            'yaxes' combinations.
          * exclude_yaxes - same as 'exclude_xaxes', but for Y-axes.
          * smry_funcs - a dictionary of 'regex':'smry_funcs' pairs where 'smry_funcs' is a list of
                         summary functions to be calculated for metrics represented by the regular
                         expression 'regex'. Default value of 'None' will not generate any summary
                         tables.
        """

        self.rsts = rsts
        self.outdir = Path(outdir)
        self.report_descr = report_descr
        self.xaxes = xaxes
        self.yaxes = yaxes
        self.exclude_xaxes = exclude_xaxes
        self.exclude_yaxes = exclude_yaxes
        self.hist = hist
        self.chist = chist

        # Users can change this to 'True' to make the reports relocatable. In which case the raw
        # results files will be copied from the test result directories to the output directory.
        self.relocatable = False

        # The first result is the 'reference' result.
        self._refres = rsts[0]
        # The raw reference result information.
        self._refinfo = self._refres.info

        # The intro table which appears at the top of all reports.
        self._intro_tbl = _IntroTable.IntroTable()

        # Names of metrics to provide the summary function values for (e.g., median, 99th
        # percentile). The summaries will show up in the summary tables (one table per metric).
        self._smry_metrics = None
        # Dictionary of 'metric':'smry_funcs' pairs where 'smry_funcs' is a list of summary
        # functions to calculate for 'metric'. Instantiated by 'self._init_smry_funcs()'.
        self._smry_metrics = None
        # Per-test result list of metrics to include into the hover text of the scatter plot.
        # By default only the x and y axis values are included.
        self._hov_metrics = {}
        # Additional metrics to load, if the results contain data for them.
        self._more_metrics = []

        self._validate_init_args()
        self._init_metrics()

        # We'll provide summaries for every metric participating in at least one diagram.
        smry_metrics = Trivial.list_dedup(self.yaxes + self.xaxes + self.hist + self.chist)
        # Summary table includes all test results, but the results may have data for different
        # metrics (e.g. they were collected with different wult versions, using different methods,
        # or on different systems). Therefore, only include metrics common to all test results.
        self._smry_metrics = []
        for metric in smry_metrics:
            for res in rsts:
                if metric not in res.metrics_set:
                    break
            else:
                self._smry_metrics.append(metric)

        if smry_funcs is None:
            smry_funcs = {}
        self._init_smry_funcs(smry_funcs)

        if (self.exclude_xaxes and not self.exclude_yaxes) or \
           (self.exclude_yaxes and not self.exclude_xaxes):
            raise Error("'exclude_xaxes' and 'exclude_yaxes' must both be 'None' or both not be "
                        "'None'")
