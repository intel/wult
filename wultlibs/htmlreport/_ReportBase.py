# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2023 Intel Corporation
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
from pathlib import Path
from pepclibs.helperlibs import Trivial, ProjectFiles
from pepclibs.helperlibs.Exceptions import Error
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

    def _copy_results(self):
        """Copies each result directory into the report directory."""

        stats_paths = {}
        logs_paths = {}

        for res in self.rsts:
            srcdir = res.dirpath
            dstdir = self.outdir / f"raw-{res.reportid}"

            HTMLReport.copy_dir(srcdir, dstdir)
            logs_paths[res.reportid] = dstdir / res.logs_path.relative_to(res.dirpath)

            stats_path = dstdir / res.stats_path.relative_to(res.dirpath)
            if stats_path.exists():
                stats_paths[res.reportid] = stats_path

        return stats_paths, logs_paths

    def _copy_logs(self):
        """Copies the log files for each result into the report directory."""

        logs_paths = {}

        for res in self.rsts:
            dstdir = self.outdir / f"raw-{res.reportid}"

            try:
                dstdir.mkdir(parents=True, exist_ok=True)
                logs_path = res.logs_path.relative_to(res.dirpath)
                HTMLReport.copy_dir(res.dirpath / logs_path, dstdir / logs_path)
                logs_paths[res.reportid] = dstdir / res.logs_path.relative_to(res.dirpath)
            except (OSError, Error) as err:
                _LOG.warning("unable to copy log files to the generated report: %s", err)

        return logs_paths

    def _copy_raw_data(self):
        """
        Helper function for '_prepare_intro_table()'. Copies result data into the report directory.
        """

        if self.relocatable:
            stats_paths, logs_paths = self._copy_results()
        else:
            logs_paths = self._copy_logs()
            stats_paths = {}

        for res in self.rsts:
            if res.stats_res:
                logs_dst = logs_paths[res.reportid] / "stats-collect-logs"
                HTMLReport.copy_dir(res.stats_res.logs_path, logs_dst)

        return stats_paths, logs_paths

    def _add_intro_tbl_links(self, label, paths):
        """
        Add links in 'paths' to the 'intro_tbl' dictionary. Arguments are as follows:
         * label - the label that will be shown in the intro table for these links.
         * paths - dictionary in the format {Report ID: Path to Link to}.
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

    def _prepare_intro_table(self):
        """
        Create the intro table, which is the very first table in the report and it shortly
        summarizes the entire report. Returns the path of the intro table file generated.
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

        stats_paths, logs_paths = self._copy_raw_data()

        # Add links to the stats directories.
        self._add_intro_tbl_links("Statistics", stats_paths)

        # Add links to the logs directories.
        self._add_intro_tbl_links("Logs", logs_paths)

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

        # Hard-code the order summary functions will appear in summary tables.
        funcs = ["max", "99.999%", "99.99%", "99.9%", "99%", "med", "avg", "std", "min"]

        smry_funcs = {}
        for metric in smry_metrics:
            # Add summary functions from 'self._smry_funcs' for each metric in 'smry_metrics'.
            if metric in self._smry_funcs:
                smry_funcs[metric] = [func for func in funcs if func in self._smry_funcs[metric]]

        return smry_funcs

    def _gen_stime_ldist_tab(self, tab_metrics, hover_defs):
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

        s_defs = [(defs[x], defs[y]) for x,y in tab_config["scatter"]]
        h_defs = [defs[x] for x in tab_config["hist"]]

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

        defs = self._refres.defs.info

        for res in self.rsts:
            _LOG.debug("calculate summary functions for '%s'", res.reportid)
            smry_funcs = ("nzcnt", "max", "99.999%", "99.99%", "99.9%", "99%", "med", "avg", "min",
                          "std")
            res.calc_smrys(regexs=self._smry_metrics[res.reportid], funcnames=smry_funcs)

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

        silenttime_ldist = ("SilentTime", "LDist")
        skip_silenttime_ldist = all(metric in tab_metrics for metric in silenttime_ldist)
        for metric in tab_metrics:
            if skip_silenttime_ldist and metric in silenttime_ldist:
                continue
            _LOG.info("Generating %s tab.", metric)
            smry_metrics = []

            # Only add plots which have the tab metric on one of the axes.
            axes =  [xypair for xypair in plot_axes if metric in xypair]
            # Don't generate an empty tab if no diagrams will be generated.
            if not axes:
                continue

            tab_plots = [(defs[x], defs[y],) for x,y in axes]

            smry_metrics += list(set.union(*[set(xypair) for xypair in axes]))
            smry_metrics = Trivial.list_dedup(smry_metrics)

            metric_def = self._refres.defs.info[metric]
            dtab_bldr = _MetricDTabBuilder.MetricDTabBuilder(self.rsts, self.outdir, metric_def)

            smry_funcs = self._get_smry_funcs(smry_metrics)
            # Only add a summary table if summary metrics were added to 'smry_funcs'.
            if smry_funcs:
                dtab_bldr.add_smrytbl(smry_funcs, self._refres.defs)

            hist_defs = [defs[metric]] if metric in self.hist else []
            chist_defs = [defs[metric]] if metric in self.chist else []

            dtab_bldr.add_plots(tab_plots, hist_defs, chist_defs, hover_defs)
            dtabs.append(dtab_bldr.get_tab())

        if skip_silenttime_ldist:
            stime_ldist_tab = self._gen_stime_ldist_tab(tab_metrics, hover_defs)
            if stime_ldist_tab is not None:
                dtabs.append(stime_ldist_tab)

        return dtabs

    def _generate_report(self, tab_cfgs):
        """Put together the final HTML report."""

        _LOG.info("Generating the HTML report.")

        # Make sure the output directory exists.
        try:
            self.outdir.mkdir(parents=True, exist_ok=True)
        except OSError as err:
            msg = Error(err).indent(2)
            raise Error(f"failed to create directory '{self.outdir}':\n{msg}") from None

        self._prepare_intro_table()

        results_tabs = self._generate_results_tabs()

        tabs = [_Tabs.CTabDC("Results", results_tabs)]

        toolname = self._refinfo["toolname"].title()

        self._stats_rep.generate_report(tabs=tabs, rsts=self._stats_rsts, intro_tbl=self._intro_tbl,
                                        title=f"{toolname} Report", descr=self.report_descr,
                                        toolname=self.toolname, toolver=self.toolver,
                                        tab_cfgs=tab_cfgs)

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

        for res in self.rsts:
            _LOG.debug("summaries will be calculated for these metrics: %s",
                       ", ".join(self._smry_metrics[res.reportid]))
            _LOG.debug("additional metrics: %s", ", ".join(self._more_metrics))

            _LOG.debug("hover metrics: %s", ", ".join(self._hov_metrics[res.reportid]))

            # Metrics in 'self._more_metrics' are not guaranteed to be present in all results, so
            # filter the metrics for those present in 'res'.
            more_metrics = {metric for metric in self._more_metrics if metric in res.metrics_set}
            minclude = more_metrics.union(self._hov_metrics[res.reportid],
                                          self._smry_metrics[res.reportid])

            res.set_minclude(minclude)
            res.load_df()

            # We'll be dropping columns and adding temporary columns, so we'll affect the original
            # 'pandas.DataFrame'. This is more efficient than creating copies.
            self._mangle_loaded_res(res)

        # Some metrics from the axes lists could have been dropped, update the lists.
        self._drop_absent_metrics()

    def generate(self, tab_cfgs=None):
        """
        Generate the HTML report and store the result in 'self.outdir'.

        Optionally provide 'tab_cfgs', a dictionary in the format '{stname: TabConfig}',
        where 'TabConfig' is an instance of 'statscollectlibs.htmlreport.tabs.TabConfig.CTabConfig',
        to overwrite the tab configurations used to generate statistics tabs. By default, no custom
        configurations will be used so the default statistics tabs will be generated.

        Important note: this method will modify the input test results in 'self.rsts'. This is done
        for effeciency purposes, to avoid copying the potentially large amounts of data
        (instances of 'pandas.DataFrame').
        """

        # Load the required datapoints into memory.
        self._load_results()

        # Put together the final HTML report.
        self._generate_report(tab_cfgs)


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
            union = set(getattr(self, name)) | res_metrics
            metrics = []
            for metric in getattr(self, name):
                if metric in union:
                    metrics.append(metric)
                else:
                    _LOG.notice("dropping metric '%s' from '%s' because it is not present in any "
                                "of the results", metric, name)
            setattr(self, name, metrics)

        for res in self.rsts:
            metrics = []
            for metric in self._hov_metrics[res.reportid]:
                if metric in res.defs.info:
                    metrics.append(metric)
                else:
                    _LOG.notice("dropping metric '%s' from hover text because it is not present "
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

        HTMLReport.validate_outdir(self.outdir)

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

        HTMLReport.reportids_dedup(self.rsts)

        if self.report_descr and Path(self.report_descr).is_file():
            try:
                with open(self.report_descr, "r", encoding="UTF-8") as fobj:
                    self.report_descr = fobj.read()
            except OSError as err:
                msg = Error(err).indent(2)
                raise Error(f"failed to read the report description file {self.report_descr}:\n"
                            f"{msg}") from err

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
                    for func in funcs:
                        if func not in self._smry_funcs[metric]:
                            self._smry_funcs[metric].append(func)

    def __init__(self, rsts, outdir, toolname, toolver, report_descr=None, xaxes=None, yaxes=None,
                 hist=None, chist=None, exclude_xaxes=None, exclude_yaxes=None, smry_funcs=None,
                 logpath=None):
        """
        The class constructor. The arguments are as follows.
          * rsts - list of 'RORawResult' objects representing the raw test results to generate the
                   HTML report for.
          * outdir - the path at which to store the output directory of the HTML report.
          * toolname - the name of the tool used to generate the report.
          * toolver - the version of the tool used to generate the report.
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
          * the path to the report generation log file.
        """

        self.rsts = rsts
        self.outdir = Path(outdir)
        self.toolname = toolname
        self.toolver = toolver
        self.report_descr = report_descr
        self.xaxes = xaxes
        self.yaxes = yaxes
        self.exclude_xaxes = exclude_xaxes
        self.exclude_yaxes = exclude_yaxes
        self.hist = hist
        self.chist = chist

        # This class is implemented by adding tabs to the 'HTMLReport' class provided by
        # 'stats-collect'. Instantiate 'stats_rep' now so that child classes can use features of
        # 'HTMLReport' specific to those reports.
        self._stats_rep = HTMLReport.HTMLReport(self.outdir, logpath=logpath)

        self._stats_rsts = []
        for res in self.rsts:
            if not res.stats_path.exists():
                continue
            if res.stats_res:
                self._stats_rsts.append(res.stats_res)

        # Users can change this to 'True' to make the reports relocatable. In which case the raw
        # results files will be copied from the test result directories to the output directory.
        self.relocatable = False

        # The first result is the 'reference' result.
        self._refres = rsts[0]
        # The raw reference result information.
        self._refinfo = self._refres.info

        # The intro table which appears at the top of all reports.
        self._intro_tbl = _IntroTable.IntroTable()

        # Dictionary in the format {'reportid': 'hov_metrics'} where 'hov_metrics' is a list of
        # metrics to include in the hover text of 'reportid' datapoints on scatter plots. By default
        # only the x and y axis values are included, but can be modified using 'set_hover_metrics()'
        self._hov_metrics = {}
        # Additional metrics to load, if the results contain data for them.
        self._more_metrics = []

        self._validate_init_args()
        self._init_metrics()

        # Dictionary in the format {'reportid': 'smry_metrics'} where 'smry_metrics is a list of
        # metrics to provide the summary function values for (e.g., median, 99th percentile). The
        # summaries will show up in the summary tables (one table per metric).
        self._smry_metrics = {}
        diag_metrics = Trivial.list_dedup(self.yaxes + self.xaxes + self.hist + self.chist)
        for res in self.rsts:
            self._smry_metrics[res.reportid] = [m for m in diag_metrics if m in res.metrics_set]

        # Dictionary in the format {'metric':'smry_funcs'} where 'smry_funcs' is a list of summary
        # functions to calculate for 'metric'. Instantiated by 'self._init_smry_funcs()'.
        self._smry_funcs = None
        if smry_funcs is None:
            smry_funcs = {}
        self._init_smry_funcs(smry_funcs)

        if (self.exclude_xaxes and not self.exclude_yaxes) or \
           (self.exclude_yaxes and not self.exclude_xaxes):
            raise Error("'exclude_xaxes' and 'exclude_yaxes' must both be 'None' or both not be "
                        "'None'")
