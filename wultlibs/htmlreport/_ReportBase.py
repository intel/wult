# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
#          Vladislav Govtva <vladislav.govtva@intel.com>

"""
Provide the base class for generating HTML reports.
"""

import itertools
from pathlib import Path
from pepclibs.helperlibs import Logging, Trivial
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.htmlreport import _IntroTable, HTMLReport
from statscollectlibs.htmlreport.tabs import _Tabs
from statscollectlibs.helperlibs import FSHelpers
from wultlibs.htmlreport import _MetricDTabBuilder

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.wult.{__name__}")

class ReportBase:
    """The base class for generating HTML reports."""

    def _add_intro_tbl_links(self, label, paths):
        """
        Add links in 'paths' to the 'intro_tbl' dictionary. The arguments are as follows.
          * label - the label that will be shown in the intro table for these links.
          * paths - dictionary in the format of '{Report ID: Path to Link to}'.
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
            cpu = res.info.get("cpu")
            if cpu is not None:
                cpu = str(cpu)

            mcpu_row.add_cell(res.reportid, cpu)

        # Add device ID.
        devid_row = self._intro_tbl.create_row("Device ID")
        for res in self.rsts:
            devid_text = res.info.get("devid")
            if devid_text and "devdescr" in res.info:
                devid_text += f" ({res.info['devdescr']})"
            devid_row.add_cell(res.reportid, devid_text)

        # Add links to the raw directories.
        if self.copy_raw:
            self._add_intro_tbl_links("Raw result", self._raw_paths)

        # Add links to the raw statistics directories.
        self._add_intro_tbl_links("Raw statistics", self._raw_stats_paths)

        # Add links to the logs directories.
        self._add_intro_tbl_links("Logs", self._raw_logs_paths)

    def _get_smry_funcs(self, smry_metrics):
        """
        Return the summary functions dictionary based on the metrics in 'smry_metrics'.
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
        Generate a tab for the 'SilentTime' and/or 'LDist' metrics. Return 'None', if the tab had to
        be skipped for some reason.
        """

        mdd = self._refmdd

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
            tab_mdef = mdd.get("SilentTime", mdd["LDist"])
            tab_config["title"] = "SilentTime/LDist"
        elif "SilentTime" in tab_metrics:
            tab_mdef = mdd["SilentTime"]
            tab_config["title"] = "SilentTime"
        elif "LDist" in tab_metrics:
            tab_mdef = mdd["LDist"]
            tab_config["title"] = "LDist"
        else:
            _LOG.debug("skipping 'SilentTime/LDist' tab since neither metric is included as a tab")
            return None

        s_defs = [(mdd[x], mdd[y]) for x, y in tab_config["scatter"]]
        h_defs = [mdd[x] for x in tab_config["hist"]]

        dtab_bldr = _MetricDTabBuilder.MetricDTabBuilder(self.rsts, self.outdir, tab_mdef)
        dtab_bldr.title = tab_config["title"]
        dtab_bldr.add_plots(s_defs, h_defs, hover_defs=hover_defs)

        smry_metrics = [metric for metric in tab_config["smry_metrics"] if metric in tab_metrics]
        smry_funcs = self._get_smry_funcs(smry_metrics)
        # Only add a summary table if summary metrics were added to 'tab_smry_funcs'.
        if smry_funcs:
            dtab_bldr.add_smrytbl(smry_funcs, self._refres.mdo)

        return dtab_bldr.get_tab()

    def _generate_results_tabs(self):
        """
        Generate and return a list of sub-tabs for the results tab. The results tab includes the
        main metrics, such as "WakeLatency". The elements of the returned list are tab dataclass
        objects, such as 'DTabDC'.
        """

        mdd = self._refmdd

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
        hover_mds = []
        for hover_metric in self._hov_metrics:
            for res in self.rsts:
                if hover_metric in self._mdds[res.reportid]:
                    hover_mds.append(self._mdds[res.reportid][hover_metric])

        silenttime_ldist = ("SilentTime", "LDist")
        skip_silenttime_ldist = all(metric in tab_metrics for metric in silenttime_ldist)
        for metric in tab_metrics:
            if skip_silenttime_ldist and metric in silenttime_ldist:
                continue
            _LOG.info("Generating %s tab.", metric)
            smry_metrics = []

            # Only add plots which have the tab metric on one of the axes.
            axes = [xypair for xypair in plot_axes if metric in xypair]
            # Don't generate an empty tab if no diagrams will be generated.
            if not axes:
                continue

            tab_plots = [(mdd[x], mdd[y],) for x, y in axes]

            smry_metrics += list(set.union(*[set(xypair) for xypair in axes]))
            smry_metrics = Trivial.list_dedup(smry_metrics)

            metric_def = self._refmdd[metric]
            dtab_bldr = _MetricDTabBuilder.MetricDTabBuilder(self.rsts, self.outdir, metric_def)

            smry_funcs = self._get_smry_funcs(smry_metrics)
            # Only add a summary table if summary metrics were added to 'smry_funcs'.
            if smry_funcs:
                dtab_bldr.add_smrytbl(smry_funcs, self._refres.mdo)

            hist_defs = [mdd[metric]] if metric in self.hist else []
            chist_defs = [mdd[metric]] if metric in self.chist else []

            dtab_bldr.add_plots(tab_plots, hist_defs, chist_defs, hover_mds)
            dtabs.append(dtab_bldr.get_tab())

        if skip_silenttime_ldist:
            stime_ldist_tab = self._gen_stime_ldist_tab(tab_metrics, hover_mds)
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

        self._prepare_intro_table()

        results_tabs = self._generate_results_tabs()

        tabs = [_Tabs.CTabDC("Results", results_tabs)]

        self._stats_rep.generate_report(tabs=tabs, intro_tbl=self._intro_tbl)

    def _mangle_loaded_res(self, res):
        """
        This method is called for every 'pandas.DataFrame' corresponding to the just loaded CSV
        file. The subclass can override this method to mangle the 'pandas.DataFrame'.
        """

        for metric in res.df:
            md = self._mdds[res.reportid].get(metric)
            if not md:
                continue

            # Some columns should be dropped from 'res.df' if they are "empty", i.e. contain only
            # zero values. For example, the C-state residency columns may be empty. This usually
            # means that the C-state was either disabled or just does not exist.
            if not res.df[metric].any():
                _LOG.debug("dropping empty column '%s' fror result '%s'", metric, res.reportid)
                res.df.drop(metric, axis="columns", inplace=True)
                res.metrics_set.remove(metric)
                del self._mdds[res.reportid][metric]

        return res.df

    def _load_results(self):
        """Load the test results from the CSV file and/or apply the metrics selector."""

        _LOG.debug("hover metrics: %s", ", ".join(self._hov_metrics))

        for res in self.rsts:
            _LOG.debug("summaries will be calculated for these metrics: %s",
                       ", ".join(self._smry_metrics[res.reportid]))
            _LOG.debug("additional metrics: %s", ", ".join(self._more_metrics))

            # Metrics in 'self._more_metrics' are not guaranteed to be present in all results, so
            # filter the metrics for those present in 'res'.
            more_metrics = {metric for metric in self._more_metrics if metric in res.metrics_set}
            minclude = more_metrics.union(self._hov_metrics, self._smry_metrics[res.reportid])

            res.set_minclude(minclude)
            res.load_df()

            # We'll be dropping columns and adding temporary columns, so we'll affect the original
            # 'pandas.DataFrame'. This is more efficient than creating copies.
            self._mangle_loaded_res(res)

        # Some metrics from the axes lists could have been dropped, update the lists.
        self._drop_absent_metrics()

    def _copy_raw_data(self):
        """Copy raw test result or their parts to the output directory."""

        logs_paths = {}
        stats_paths = {}

        for res in self.rsts:
            dstdir = self._raw_paths[res.reportid]

            if self.copy_raw:
                res.copy(dstdir)
            else:
                res.copy_logs(dstdir)

            if res.logs_path:
                logs_paths[res.reportid] = dstdir / res.logs_path.name
            if self.copy_raw and res.stats_path:
                path = dstdir / res.stats_path.name / res.stats_res.stats_path.name
                stats_paths[res.reportid] = path

            if res.stats_res:
                # Copy or link stats-collect logs to the wult logs directory.
                logs_dst = logs_paths[res.reportid] / "stats-collect-logs"
                if self.copy_raw:
                    target = dstdir / res.stats_path.name / res.stats_res.logs_path.name
                    FSHelpers.symlink(logs_dst, target, relative=True)
                else:
                    res.stats_res.copy_logs(logs_dst)

        return logs_paths, stats_paths

    def generate(self):
        """
        Generate the HTML report.

        Important note: this method will modify the input test results in 'self.rsts'. This is done
        for efficiency purposes, to avoid copying the potentially large amounts of data (instances
        of 'pandas.DataFrame').
        """

        # Load the required datapoints into memory.
        self._load_results()

        for res in self.rsts:
            self._raw_paths[res.reportid] = self.outdir / f"raw-{res.reportid}"
        self._raw_logs_paths, self._raw_stats_paths = self._copy_raw_data()

        # Put together the final HTML report.
        self._generate_report()

    def set_hover_metrics(self, regexs):
        """
        Set hover text metrics on the results scatter-plot. The arguments are as follows.
          * regexs - an iterable collection of hover text metric regular expressions.  Every metric
            are matched against these regular expressions, and matched metrics are added to the
            hover text.
        """

        # Note, it is OK if a metric in 'self._hov_metrics' is not present one of the results - it
        # will be excluded from the hover text for that result.
        metrics_set = set()
        for res in self.rsts:
            for metric in res.find_metrics(regexs, must_find_any=False):
                if metric not in metrics_set and metric in self._mdds[res.reportid]:
                    self._hov_metrics.append(metric)

    def _drop_absent_metrics(self):
        """
        Verify that test results provide the metrics in 'xaxes', 'yaxes', 'hist' and 'chist'. Drop
        the absent metrics. Also drop unknown metrics (those not present in the "definitions").
        """

        lists = ("xaxes", "yaxes", "hist", "chist")

        res_metrics = set()
        for res in self.rsts:
            res_metrics.update(res.metrics_set)

        for name in lists:
            metrics = []
            for metric in getattr(self, name):
                if metric in res_metrics:
                    metrics.append(metric)
                else:
                    _LOG.notice("dropping metric '%s' from '%s' because it is not present in any "
                                "of the results", metric, name)
            setattr(self, name, metrics)

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
        Assign which summary functions to calculate and include for each metric. Store the result
        in 'self._smry_funcs'. The arguments are as follows.
          * smry_funcs - a dictionary in the format of '{regex: funcs}', where 'funcs' is a list of
                         summary function names to calculate and add to the summary table for the
                         metrics matching the 'regex' regular expression.
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

    def __init__(self, rsts, outdir, toolname, toolver, report_descr=None, stats_rep=None,
                 xaxes=None, yaxes=None, hist=None, chist=None, exclude_xaxes=None,
                 exclude_yaxes=None, smry_funcs=None, logpath=None):
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
          * stats_rep: A 'statscollectlibs.HTMLReport.HTMLReport' object to use for generating
                       statistics tabs.
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
          * logpath - path to the report generation log file.
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

        # The '_DTabBuilder' module requires the "colname" key in metric definitions.
        self._mdds = {}
        for res in rsts:
            self._mdds[res.reportid] = mdd = {}
            for metric, md in res.mdo.mdd.items():
                mdd[metric] = md.copy()
                mdd[metric]["colname"] = metric

        self._stats_lrsts = []
        for res in self.rsts:
            if not res.stats_path:
                continue
            if res.stats_lres:
                self._stats_lrsts.append(res.stats_lres)

        # Users can change this to 'True' to copy all the raw test results into the output
        # directory.
        self.copy_raw = False

        # The first result is the 'reference' result.
        self._refres = rsts[0]
        self._refmdd = self._mdds[self._refres.reportid]

        # The raw reference result information.
        self._refinfo = self._refres.info

        # The intro table which appears at the top of all reports.
        self._intro_tbl = _IntroTable.IntroTable()

        # List of metric names to be inclued in the hover text of the scatter plots.
        self._hov_metrics = []
        # Additional metrics to load, if the results contain data for them.
        self._more_metrics = []

        # Paths to (copied) raw test result directories in the output directory, and logs/statistics
        # sub-directories in the output directory. The dictionary is indexed by report ID.
        self._raw_paths = {}
        self._raw_logs_paths = {}
        self._raw_stats_paths = {}

        self._validate_init_args()
        self._init_metrics()

        if not stats_rep:
            title = f"{toolname} Report",
            toolname = self._refinfo["toolname"].title()
            stats_rep = HTMLReport.HTMLReport(self._stats_lrsts, title, self.outdir,
                                              logpath=logpath, descr=self.report_descr,
                                              toolname=toolname, toolver=self.toolver)
        self._stats_rep = stats_rep

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
