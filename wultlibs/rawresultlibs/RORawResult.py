# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""This module provides API for reading raw test results."""

import builtins
import re
import logging
from pathlib import Path
import pandas
from pepclibs.helperlibs import YAML
from pepclibs.helperlibs.Exceptions import Error, ErrorNotSupported, ErrorNotFound
from statscollectlibs import DFSummary
from statscollectlibs.rawresultlibs import RORawResult as StatsCollectRes
from statscollectlibs.collector._STCAgent import STINFO
from wultlibs import WultDefs, _WultDefsBase
from wultlibs.rawresultlibs import _RawResultBase

_LOG = logging.getLogger()

# Format version '1.2' contained multiple format versions. It is planned to be removed from the list
# of supported versions in 2025.
_SUPPORTED_FORMAT_VERSIONS = {"1.2", "1.3"}

class RORawResult(_RawResultBase.RawResultBase):
    """This class represents a read-only raw test result."""

    def get_non_numeric_metrics(self, metrics=None):
        """
        Returns the list of non-numeric metrics in the 'metrics' list (all metrics by default).
        """

        if not metrics:
            metrics = self.metrics

        non_numeric = []
        for metric in metrics:
            if self.defs.info[metric]["type"] not in ("int", "float"):
                non_numeric.append(metric)

        return non_numeric

    def get_numeric_metrics(self, metrics=None):
        """
        Returns the list of numeric metrics in the 'metrics' list (all metrics by default).
        """

        if not metrics:
            metrics = self.metrics

        numeric = []
        for metric in metrics:
            if self.defs.info[metric]["type"] in ("int", "float"):
                numeric.append(metric)

        return numeric

    def is_numeric(self, metric):
        """Returns 'True' if metric 'metric' has numeric values, otherwise returns 'False'."""
        return metric in self.get_numeric_metrics(metrics=[metric])

    def _mangle_eval_expr(self, expr):
        """
        Mangle a 'pandas' python expression that we use for row filters and selectors. Some of the
        'pandas.DataFrame' column names may have symbols like '%' (e.g., in 'CC1%'), which cannot be
        used in 'pandas' python expressions, this method solves this problem.
        """

        if expr is None:
            return None

        expr = str(expr)
        for colname in self.metrics:
            expr = expr.replace(colname, f"self.df['{colname}']")
        # The special 'index' name represents the row number (first data row has index '0').
        expr = re.sub("(?!')index(?!')", "self.df.index", expr)
        return expr

    def set_exclude(self, exclude):
        """
        Set the datapoints to exclude: the datapoints matching the 'exclude' expression will be
        excluded from the 'pandas.DataFrame' during the next 'pandas.DataFrame' operation like
        'load_df()'.

        The 'exclude' argument should be a valid pandas python expression that can be used in
        'pandas.eval()'. For example, the '(SilentTime < 10000) and (PC6% == 0)' filter will exclude
        all the datapoints with silent time smaller than 10 usec and zero package C-state #6
        residency. Please, refer to 'pandas.eval()' documentation for more information.
        """

        self._exclude = self._mangle_eval_expr(exclude)

    def set_include(self, include):
        """
        Set the datapoints to include: only the datapoints matching the 'include' expression will be
        added to the 'pandas.DataFrame' during the next 'pandas.DataFrame' operation like
        'load_df()'. The 'include' argument is similar to the 'exclude' argument in the
        'set_exclude()' method.
        """

        self._include = self._mangle_eval_expr(include)

    def set_mexclude(self, regexs):
        """
        Set the metrics to exclude: the metrics with names in 'regexs' (or matching a regular
        expression in 'regexs') will be excluded from the 'pandas.DataFrame' during the next
        'pandas.DataFrame' operation like 'load_df()'.
        """

        if regexs:
            self._mexclude = self.find_metrics(regexs, must_find_all=True)

    def set_minclude(self, regexs):
        """
        Set the metrics to include: only the metrics with names in 'regexs' (or matching a regular
        expression in 'regexs') will be included into the 'pandas.DataFrame' ('self.df') during the
        next 'pandas.DataFrame' operation like 'load_df()'.
        """

        if regexs:
            self._minclude = self.find_metrics(regexs, must_find_all=True)

    def _calc_smry(self, metric, funcnames):
        """
        Helper function for 'calc_smrys()'. Calculate the summary functions in 'funcnames' for
        'metric'. Returns a dictionary with function name - value pairs.
        """

        if not self.is_numeric(metric):
            raise Error(f"unable to compute summaries for non-numeric metric '{metric}'.")

        subdict = DFSummary.calc_col_smry(self.df, metric, funcnames)

        mdef = self.defs.info[metric]
        restype = getattr(builtins, mdef["type"])

        for func, datum in subdict.items():
            # 'calc_col_smry()' can return summary funcs with 'None' values which can't be
            # type-casted.
            if datum is not None:
                subdict[func] = restype(datum)

        return subdict

    def calc_smrys(self, regexs=None, funcnames=None):
        """
        Calculate summary functions specified in 'funcnames' for metrics matching 'regexs', and save
        the result in 'self.smrys'. By default this method calculates the summaries for all metrics
        in the currently loaded 'pandas.DataFrame'.

        The 'regexs' argument should be a list of metrics or regular expressions, which will be
        applied to metrics. The 'funcnames' argument must be a list of function names.

        The result ('self.smrys') is a dictionary of dictionaries. The top level dictionary keys
        are metrics and the sub-dictionary keys are function names.
        """

        if self.df is None:
            self.load_df()

        if not regexs:
            all_metrics = self.metrics
        else:
            all_metrics = self.find_metrics(regexs, must_find_all=True)

        # Exclude metrics with non-numeric data.
        metrics = self.get_numeric_metrics(metrics=all_metrics)

        # Make sure we have some metrics to work with.
        if not metrics:
            msg = "no metrics to calculate summary functions for"
            if all_metrics:
                msg += ".\nThese metrics were excluded because they are not numeric: "
                msg += " ,".join(self.get_non_numeric_metrics(metrics=all_metrics))
            raise ErrorNotFound(msg)

        if not funcnames:
            funcnames = [funcname for funcname, _ in DFSummary.get_smry_funcs()]

        self.smrys = {}
        for metric in metrics:
            if metric in self.df:
                self.smrys[metric] = self._calc_smry(metric, funcnames)

    def _load_csv(self, **kwargs):
        """Read the datapoints CSV file into a 'pandas.DataFrame' and validate it."""

        _LOG.info("Loading test result '%s'.", self.dp_path)

        # Enforce the types we expect.
        dtype = {colname : colinfo["type"] for colname, colinfo in self.defs.info.items()}

        try:
            self.df = pandas.read_csv(self.dp_path, dtype=dtype, **kwargs)
        except Exception as err:
            msg = Error(err).indent(2)
            raise Error(f"failed to load CSV file {self.dp_path}:\n{msg}") from None

        # Check datapoints for too few values.
        if self.df.isnull().values.any():
            raise Error(f"CSV file '{self.dp_path}' include datapoints with too few values (one or "
                        f"more incomplete row).")

        if self.df.empty:
            raise Error(f"no data in CSV file '{self.dp_path}'")

    def _load_df(self, force_reload=False, **kwargs):
        """
        Apply all the filters and selectors to 'self.df'. Load it from the datapoints CSV file if it
        has not been loaded yet. If 'force_reload' is 'True', always load 'self.df' from the CSV
        file.
        """

        dpfilter = self._get_dp_filter()
        metrics = self._get_filtered_metrics(self.metrics)

        load_csv = force_reload or self.df is None

        if not dpfilter:
            if load_csv:
                self._load_csv(usecols=metrics, **kwargs)
            metrics = None
        else:
            # We cannot drop columns yet, because datapoint filter may refer to the columns.
            if load_csv:
                self._load_csv(**kwargs)

        if dpfilter:
            _LOG.debug("applying datapoint filter: %s", dpfilter)
            metrics_str = ", ".join(self.metrics)
            try:
                try:
                    expr = pandas.eval(dpfilter)
                except ValueError as err:
                    # For some reasons on some distros the default "numexpr" engine fails with
                    # various errors, such as:
                    #   * ValueError: data type must provide an itemsize
                    #   * ValueError: unknown type str128
                    #
                    # We are not sure how to properly fix these, but we noticed that often the
                    # "python" engine works fine. Therefore, re-trying with the "python" engine.
                    _LOG.debug("pandas.eval(engine='numexpr') failed: %s\nTrying "
                               "pandas.eval(engine='python')", str(err))
                    expr = pandas.eval(dpfilter, engine="python")
            except Exception as err:
                msg = Error(err).indent(2)
                raise Error(f"failed to evaluate expression '{dpfilter}': {msg}\nMake sure you use "
                            f"correct metric names, which are also case-sensitive. Available "
                            f"metcis are:\n'{metrics_str}'") from err

            try:
                self.df = self.df[expr].reset_index(drop=True)
            except KeyError as err:
                # Example of filter causing this error - just metric name without any operator, like
                # just "CC1%", instead of something like "CC1% > 0".
                raise Error(f"failed to apply expression '{dpfilter}'.\nMake sure you use "
                            f"operator and correct metric names, which are also case-sensitive. "
                            f"Available metrics are:\n{metrics_str}") from err

            if self.df.empty:
                raise Error(f"no data left after applying datapoint filter to CSV file "
                            f"'{self.dp_path}'")

        if metrics:
            _LOG.debug("applying metrics selector: %s", metrics)
            self.df = self.df[metrics]
            if self.df.empty:
                raise Error(f"no datapoints left after applying metric selector(s) to CSV file "
                            f"'{self.dp_path}'")

    def load_df(self, **kwargs):
        """
        If the datapoints CSV file has not been read yet ('self.df' is 'None'), read it into the
        'self.df' 'pandas.DataFrame'. Then apply all the configured filters and selectors to
        'self.df'. The keyword arguments ('kwargs') are passed as is to 'pandas.read_csv()'.
        """

        self._load_df(force_reload=False, **kwargs)

    def reload_df(self, **kwargs):
        """
        Same as 'load_df()', but always reads the datapoints CSV file.
        """

        self._load_df(force_reload=True, **kwargs)

    def find_metrics(self, regexs, must_find_any=True, must_find_all=False):
        """
        Among the list of the metrics of this test result, find metrics that match regular
        expressions in 'regexs'. The arguments are as follows.
          * regexs - an iterable collection or regular expressions to match.
          * must_find_any - if 'True', raise an 'ErrorNotFound' exception in case of no matching
                            metrics. If 'False', just return an empty list in case of no matching
                            metrics.
          * must_find_all - if 'True', raise an 'ErrorNotFound' exception if any of the regular
                            expressions in 'regexs' did not match.
        """

        found = {}
        for regex in regexs:
            matched = False
            for metric in self.metrics:
                try:
                    if re.fullmatch(regex, metric):
                        found[metric] = regex
                        matched = True
                except re.error as err:
                    msg = Error(err).indent(2)
                    raise Error(f"bad regular expression '{regex}':\n{msg}") from err

            if not matched:
                metrics_str = ", ".join(self.metrics)
                msg = f"no matches for metric '{regex}' in the following list of available " \
                      f"metrics:\n  {metrics_str}"
                if must_find_all:
                    raise ErrorNotFound(msg)
                _LOG.debug(msg)

        if not found and must_find_any:
            metrics_str = ", ".join(self.metrics)
            regexs_str = ", ".join(regexs)
            raise ErrorNotFound(f"no matches for the following metric(s):\n  {regexs_str}\n"
                                f"in the following list of available metrics:\n  {metrics_str}")

        return list(found.keys())

    def save(self, dirpath, reportid=None):
        """
        Save the test result at path 'dirpath', optionally change the report ID with 'reportid'.
        """

        dirpath = Path(dirpath)
        if not dirpath.exists():
            _LOG.debug("creating directory '%s", dirpath)
            try:
                dirpath.mkdir(parents=True, exist_ok=False)
            except OSError as err:
                msg = Error(err).indent(2)
                raise Error(f"failed to create directory '{dirpath}':\n{msg}") from None
        elif not dirpath.is_dir():
            raise Error(f"path '{dirpath}' exists and it is not a directory")

        if reportid:
            info = self.info.copy()
            info["reportid"] = reportid
        else:
            info = self.info

        path = dirpath.joinpath(self.info_path.name)
        YAML.dump(info, path)

        path = dirpath.joinpath(self.dp_path.name)
        self.df.to_csv(path, index=False, header=True)

    @staticmethod
    def _convert_col_to_base_unit(df, mdef, base_col_suffix):
        """
        Convert the column of 'df' represented by the metric 'mdef' with "microsecond" units to
        seconds, and return the converted column.
        """

        colname = mdef["name"]

        # This is not generic, but today we have to deal only with microseconds and megahertz, so
        # this is good enough.
        if mdef.get("unit") not in ("microsecond", "nanosecond", "megahertz"):
            return df[colname]

        base_colname = colname + base_col_suffix
        if base_colname in df:
            return df[base_colname]

        if mdef["unit"] == "megahertz":
            df.loc[:, base_colname] = df[colname] * 1000000
        elif mdef["unit"] == "nanosecond":
            df.loc[:, base_colname] = df[colname] / 1000000000
        elif mdef["unit"] == "microsecond":
            df.loc[:, base_colname] = df[colname] / 1000000
        return df[base_colname]

    @staticmethod
    def _convert_mdef_to_base_unit(mdef, base_name_suffix):
        """
        Several defs list "us" as the 'short_unit' which includes the prefix, "u", this method will
        convert that to the base unit 's'. This method accepts a metric definition dictionary 'mdef'
        and returns a new dictionary with both the "short_unit" and "unit" fields adjusted
        accordingly.
        """

        mdef = mdef.copy()

        # This is not generic, but today we have to deal only with microseconds and megahertz, so
        # this is good enough.
        if mdef.get("short_unit") == "us":
            mdef["short_unit"] = "s"
        elif mdef.get("short_unit") == "ns":
            mdef["short_unit"] = "s"
        elif mdef.get("short_unit") == "MHz":
            mdef["short_unit"] = "Hz"

        if mdef.get("unit") == "microsecond":
            mdef["unit"] = "second"
        elif mdef.get("unit") == "megahertz":
            mdef["unit"] = "Hertz"

        mdef["name"] = mdef["name"] + base_name_suffix

        return mdef

    def scale_to_base_units(self, base_col_suffix):
        """Scale datapoints in 'self.df' so that they no longer have any SI prefix."""

        mdefs_to_add = {}
        for col, mdef in self.defs.info.items():
            if col not in self.df:
                continue

            base_colname = col + base_col_suffix
            if base_colname not in self.df:
                self._convert_col_to_base_unit(self.df, mdef, base_col_suffix)

            if base_colname not in self.defs.info:
                mdefs_to_add[base_colname] = self._convert_mdef_to_base_unit(mdef, base_col_suffix)

        self.defs.info.update(mdefs_to_add)

    def _mock_stats_res(self):
        """
        Helper function for the class constructor. Some result directories with 'format_version'
        '1.2', only contain raw statistics files and a 'stats-info.yml' file.

        Populate 'self.stats_res' with a 'stats-collect' 'RORawResult' based on the contents of
        'stats-info.yml'
        """

        tool = f"{self.info['toolname']} v{self.info['toolver']}"

        stats_info_path = self.stats_path / "stats-info.yml"
        self.stats_res = StatsCollectRes.RORawResult(self.dirpath, self.reportid)
        self.stats_res.info_path = self.stats_path / "stats-info.yml"
        self.stats_res.stats_path = self.stats_path

        if stats_info_path.exists():
            stinfo = YAML.load(self.stats_res.info_path)
        else:
            YAML.dump(STINFO, self.stats_path / "stats-info.yml")
            stinfo = STINFO

        self.stats_res.info = {}
        self.stats_res.info["stinfo"] = stinfo

        _LOG.warning("result '%s' was generated with '%s'. It is recommended that you downgrade to "
                     "'%s' if you have any issues.", self.reportid, tool, tool)

    def __init__(self, dirpath, reportid=None):
        """
        The class constructor. The arguments are as follows.
          * dirpath - path to the directory containing the raw test result to open.
          * reportid - override the report ID of the raw test result: the 'reportid' string will be
                       used instead of the report ID stored in 'dirpath/info.yml'. Note, the
                       provided report ID is not verified, so the caller has to make sure is a sane
                       string.

        Note, the constructor does not load the potentially huge test result data into the memory.
        It only loads the 'info.yml' file and figures out which metrics have been measured. The data
        are loaded "on-demand" by 'load_df()' and other methods.
        """

        super().__init__(dirpath)

        # Check few special error cases upfront in order to provide a clear error message:
        # the info and datapoint files should exist and be non-empty.
        for name in ("info_path", "dp_path"):
            attr = getattr(self, name)
            try:
                if not attr.is_file():
                    raise ErrorNotFound(f"'{attr}' does not exist or it is not a regular file")
                if not attr.stat().st_size:
                    raise Error(f"file '{attr}' is empty")
            except OSError as err:
                msg = Error(err).indent(2)
                raise Error(f"failed to access '{attr}':\n{msg}") from err

        self.df = None
        self.smrys = None
        self.metrics = []
        self.metrics_set = set()

        self.info = YAML.load(self.info_path)
        if reportid:
            # Note, we do not verify it here, the caller is supposed to verify.
            self.info["reportid"] = reportid
        if "reportid" not in self.info:
            raise ErrorNotSupported(f"no 'reportid' key found in {self.info_path}")
        self.reportid = self.info["reportid"]

        toolname = self.info.get("toolname")
        if not toolname:
            raise Error(f"bad '{self.info_path}' format - the 'toolname' key is missing")

        toolver = self.info.get("toolver")
        if not toolver:
            raise Error(f"bad '{self.info_path}' format - the 'toolver' key is missing")

        format_ver = self.info.get("format_version")
        if format_ver not in _SUPPORTED_FORMAT_VERSIONS:
            _LOG.warning("result '%s' has format version '%s' which is not supported by this "
                         "version so may cause unexpected behavour. Please use '%s v%s'.",
                         self.reportid, format_ver, toolname, toolver)

        # Read the metrics from the column names in the CSV file.
        try:
            metrics = list(pandas.read_csv(self.dp_path, nrows=0))
        except Exception as err:
            msg = Error(err).indent(2)
            raise Error(f"failed to load CSV file {self.dp_path}:\n{msg}") from None

        if toolname == "wult":
            self.defs = WultDefs.WultDefs(metrics)
        else:
            self.defs = _WultDefsBase.WultDefsBase(toolname)

        # Exclude metrics which are not present in the definitions.
        self.metrics = []
        for metric in metrics:
            if metric in self.defs.info:
                self.metrics.append(metric)

        self.metrics_set = set(self.metrics)

        self.stats_res = None
        if not self.stats_path.exists():
            return

        try:
            self.stats_res = StatsCollectRes.RORawResult(self.stats_path, self.reportid)
        except Error as err:
            if self.info["format_version"] != "1.2":
                raise err

            # 'format_version 1.2' contained several forms of result. Some results contained
            # statistics in a different way which can cause loading statistics to fail. Attempt to
            # load the statistics as they used to be.
            try:
                self._mock_stats_res()
            except Error:
                # If the 'stats-collect' result is malformed. Load the result with no stats but warn
                # the user that there was a problem.
                _LOG.warning("unable to load statistics for '%s':\n%s", self.reportid,
                             err.indent(2))
