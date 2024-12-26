# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""API for reading wult, ndl, and pbe raw test results."""

import re
import shutil
import logging
import builtins
from pathlib import Path
import pandas
from pepclibs.helperlibs import YAML
from pepclibs.helperlibs.Exceptions import Error, ErrorNotSupported, ErrorNotFound
from statscollectlibs import DFSummary
from statscollectlibs.rawresultlibs import RORawResult as StatsCollectRes
from wultlibs import WultDefs, PbeDefs, NdlDefs
from wultlibs.rawresultlibs import _RawResultBase

_LOG = logging.getLogger()

_SUPPORTED_FORMAT_VERSIONS = {"1.3"}

class RORawResult(_RawResultBase.RawResultBase):
    """A read-only wult, ndl, or pbe raw test result."""

    def get_non_numeric_metrics(self, metrics=None):
        """
        Return the list of non-numeric metrics in the 'metrics' list (all metrics by default). The
        arguments are as follows.
          * metrics - an iterable collection of metric names to return non-numeric metrics for.
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
        Return the list of numeric metrics in the 'metrics' list (all metrics by default). The
        arguments are as follows.
          * metrics - an iterable collection of metric names to return numeric metrics for.

        """

        if not metrics:
            metrics = self.metrics

        numeric = []
        for metric in metrics:
            if self.defs.info[metric]["type"] in ("int", "float"):
                numeric.append(metric)

        return numeric

    def is_numeric(self, metric):
        """
        Return 'True' if metric 'metric' has numeric values, otherwise returns 'False'. The metric
        name to check.
        """
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
        Set the datapoints exclude filter: the datapoints matching the 'exclude' expression will
        be excluded from the 'pandas.DataFrame' during the next 'pandas.DataFrame' operation like
        'load_df()'. The arguments are as follows.
          * exclude - the datapoints exclude filter expression.

        The 'exclude' argument should be a valid pandas python expression that can be used in
        'pandas.eval()'. For example, the '(SilentTime < 10000) and (PC6% == 0)' filter will exclude
        all the datapoints with silent time smaller than 10 usec and zero package C-state #6
        residency. Please, refer to 'pandas.eval()' documentation for more information.
        """

        self._exclude = self._mangle_eval_expr(exclude)

    def set_include(self, include):
        """
        Set the datapoints include filter: only the datapoints matching the 'include' expression
        will be added to the 'pandas.DataFrame' during the next 'pandas.DataFrame' operation like
        'load_df()'.
          * include - the datapoints include filter expression.

        The 'include' argument is similar to the 'exclude' argument in the 'set_exclude()' method.
        """

        self._include = self._mangle_eval_expr(include)

    def set_mexclude(self, regexs):
        """
        Set the metrics exclude filter: the metrics with names in 'regexs' (or matching a regular
        expression in 'regexs') will be excluded from the 'pandas.DataFrame' during the next
        'pandas.DataFrame' operation like 'load_df()'. The arguments are as follows.
          * regex - the metrics exclude filter regular expression.
        """

        if regexs:
            self._mexclude = self.find_metrics(regexs, must_find_all=True)

    def set_minclude(self, regexs):
        """
        Set the metrics include filter: only the metrics with names in 'regexs' (or matching a
        regular expression in 'regexs') will be included into the 'pandas.DataFrame' ('self.df')
        during the next 'pandas.DataFrame' operation like 'load_df()'. The arguments are as follows.
          * regex - the metrics include filter regular expression.
        """

        if regexs:
            self._minclude = self.find_metrics(regexs, must_find_all=True)

    def _calc_smry(self, metric, funcnames):
        """
        Calculate the summary functions in 'funcnames' for 'metric'. Return a dictionary with
        function name - value pairs.
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
        the result in 'self.smrys'. By default calculate the summaries for all metrics in the
        currently loaded 'pandas.DataFrame'. The arguments are as follows.
          * regexs - an iterable collection of metrics or regular expressions, which will be applied
            to metrics.
          * funcnames - an iterable collection of function names to calculate.

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
        dtype = {colname: colinfo["type"] for colname, colinfo in self.defs.info.items()}

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
                    # For some reasons on some Linux distributions the default "numexpr" engine
                    # fails with various errors, such as:
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
        'self.df'. The arguments are as follows.
          * kwargs - passed as is to 'pandas.read_csv()'.
        """

        self._load_df(force_reload=False, **kwargs)

    def reload_df(self, **kwargs):
        """
        Same as 'load_df()', but unconditionally reads the datapoints CSV file. The arguments are as
        follows.
          * kwargs - passed as is to 'pandas.read_csv()'.
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

    def _copy(self, dirpath, files=None, dirs=None):
        """Copy files from 'files' and dirs from 'dirs' to 'dirpath."""

        if files:
            for path in files:
                try:
                    shutil.copyfile(path, dirpath / path.name)
                except (Error, shutil.Error) as err:
                    errmsg = Error(err).indent(2)
                    raise Error(f"failed to file '{path}' to '{dirpath}':\n{errmsg}") from err

        if dirs:
            for path in dirs:
                try:
                    shutil.copytree(path, dirpath / path.name, dirs_exist_ok=True,
                                    copy_function=shutil.copy)
                except (Error, shutil.Error) as err:
                    errmsg = Error(err).indent(2)
                    raise Error(f"failed to directory '{path}' to '{dirpath}':\n{errmsg}") from err

    @staticmethod
    def _check_info_yml(dirpath):
        """Raise an exception if an 'info.yml' file exists in 'dstdir'."""

        path = dirpath / "info.yml"

        try:
            exists = path.exists()
        except OSError as err:
            msg = Error(err).indent(2)
            raise Error(f"failed to check if '{path}' exists:\n{msg}") from None

        if not exists:
            return

        raise Error(f"the destination directory '{dirpath}' already contains 'info.yml', refusing "
                    f"to overwrite an existing test result")

    @staticmethod
    def _mkdir(dirpath):
        """Create a directory if it does not exist."""

        try:
            exists = dirpath.exists()
            if exists and not dirpath.is_dir():
                raise Error(f"path '{dirpath}' already exists and it is not a directory")
        except OSError as err:
            msg = Error(err).indent(2)
            raise Error(f"failed to check if directory '{dirpath}' exists:\n{msg}") from None

        if exists:
            return

        _LOG.debug("creating directory '%s", dirpath)

        try:
            dirpath.mkdir(parents=True, exist_ok=True)
        except OSError as err:
            msg = Error(err).indent(2)
            raise Error(f"failed to create directory '{dirpath}':\n{msg}") from None

    def copy(self, dirpath):
        """
        Copy the raw test result (self) to path 'dirpath'. The arguments are as follows.
          * dirpath - path to the directory to copy the result to.
        """

        dirpath = Path(dirpath)
        self._mkdir(dirpath)
        self._check_info_yml(dirpath)

        files = (self.info_path, self.dp_path)
        dirs = []
        if self.logs_path_exists:
            dirs.append(self.logs_path)
        if self.stats_path_exists:
            dirs.append(self.stats_path)

        self._copy(dirpath, files=files, dirs=dirs)

    def save(self, dirpath, reportid=None):
        """
        Save the raw test result (self) at path 'dirpath', optionally change the report ID with
        'reportid'. The arguments are as follows.
          * dirpath - path to the directory to save the result at.
          * reportid - new report ID.
        """

        dirpath = Path(dirpath)
        self._mkdir(dirpath)
        self._check_info_yml(dirpath)

        if reportid:
            info = self.info.copy()
            info["reportid"] = reportid
        else:
            info = self.info

        path = dirpath.joinpath(self.info_path.name)
        YAML.dump(info, path)

        path = dirpath.joinpath(self.dp_path.name)
        self.df.to_csv(path, index=False, header=True)

        dirs = []
        if self.logs_path_exists:
            dirs.append(self.logs_path)
        if self.stats_path_exists:
            dirs.append(self.stats_path)

        self._copy(dirpath, dirs=dirs)

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

        # The raw result information dictionary.
        self.info = None
        # The statistics raw results object.
        self.stats_res = None

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
                         "version so may cause unexpected behavior. Please use '%s v%s'.",
                         self.reportid, format_ver, toolname, toolver)

        # Read the metrics from the column names in the CSV file.
        try:
            metrics = list(pandas.read_csv(self.dp_path, nrows=0))
        except Exception as err:
            msg = Error(err).indent(2)
            raise Error(f"failed to load CSV file {self.dp_path}:\n{msg}") from None

        if toolname == "wult":
            self.defs = WultDefs.WultDefs(metrics)
        elif toolname == "pbe":
            self.defs = PbeDefs.PbeDefs()
        elif toolname == "ndl":
            self.defs = NdlDefs.NdlDefs()
        else:
            raise Error(f"unknown tool '{toolname}'")

        # Exclude metrics which are not present in the definitions.
        self.metrics = []
        for metric in metrics:
            if metric in self.defs.info:
                self.metrics.append(metric)

        self.metrics_set = set(self.metrics)

        if self.stats_path_exists:
            self.stats_res = StatsCollectRes.RORawResult(self.stats_path, self.reportid)
