# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2020 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module provides API for reading raw test results.
"""

import re
import logging
import builtins
from pathlib import Path
import numpy
import pandas
from wultlibs.helperlibs import YAML, Trivial
from wultlibs.helperlibs.Exceptions import Error, ErrorNotSupported, ErrorNotFound
from wultlibs.rawresultlibs import _RawResultBase
from wultlibs import Defs

_LOG = logging.getLogger()

# Summary function names and titles.
_SMRY_FUNCS = {"min"       : "the minimum value",
               "min_index" : "index of the minimum value",
               "max"       : "the maximum value",
               "max_index" : "index of the maximum value",
               "avg"       : "the average value",
               "med"       : "the median value",
               "std"       : "standard deviation",
               "N%"        : "N-th percentile, 0 < N < 100",
               "nzcnt"     : "datapoints with non-zero value"}

def get_smry_funcs():
    """
    Yields all the supported summary function names along with short description as a tuple.
    """

    for funcname, descr in _SMRY_FUNCS.items():
        yield funcname, descr

def _get_percentile(funcname):
    """
    Parses and validates the percentile statistics function name (e.g., "99%") and returns the
    percent value (99).
    """

    percent = Trivial.str_to_num(funcname[:-1])
    if percent <= 0 or percent >= 100:
        raise Error(f"bad percentile number in '{funcname}', should be in range of "
                    f"(0, 100)")
    return percent

def get_smry_func_descr(funcname):
    """Returns description for a summary function 'funcname'."""

    if funcname in _SMRY_FUNCS:
        return _SMRY_FUNCS[funcname]

    if "%" in funcname:
        percent = _get_percentile(funcname)
        return f"{percent}-th percentile"

    funcnames = ", ".join([fname for fname, _ in get_smry_funcs()])
    raise Error(f"unknown function name '{funcname}', supported names are:\n{funcnames}")

class RORawResult(_RawResultBase.RawResultBase):
    """This class represents a read-only raw test result."""

    def get_non_numeric_colnames(self, colnames=None):
        """
        Returns the list of non-numeric colnames in the 'colnames' list (all colnames by default).
        """

        if not colnames:
            if self.df is None:
                self.load_df()
            colnames = list(self.df)

        non_numeric = []
        for colname in colnames:
            if self.defs.info[colname]["type"] not in ("int", "float"):
                non_numeric.append(colname)

        return non_numeric

    def get_numeric_colnames(self, colnames=None):
        """
        Returns the list of non-numeric colnames in the 'colnames' list (all colnames by default).
        """

        if not colnames:
            if self.df is None:
                self.load_df()
            colnames = list(self.df)

        numeric = []
        for colname in colnames:
            if self.defs.info[colname]["type"] in ("int", "float"):
                numeric.append(colname)

        return numeric

    def is_numeric(self, colname):
        """Returns 'True' if column 'colname' has numeric values, otherwise returns 'False'."""
        return colname in self.get_numeric_colnames(colnames=[colname])

    def _mangle_eval_expr(self, expr):
        """
        Mangle a pandas python expression that we use for row filters and selectors. Some of the CSV
        file column names may have symbols like '%' (e.g., in 'CC1%'), which cannot be used in
        pandas python expressions, and this method solves the problem.
        """

        if expr is None:
            return None

        expr = str(expr)
        for colname in self.colnames:
            expr = expr.replace(colname, f"self.df['{colname}']")
        # The special 'index' name represents the row number (first data row has index '0').
        expr = re.sub("(?!')index(?!')", f"self.df.index", expr)
        return expr

    def set_rfilt(self, rfilt):
        """
        Set the rows filter: the CSV rows matching the 'rfilt' expression will be excluded from the
        dataframe during the next dataframe operation like 'load_df()'. Use 'None' to disable rows
        filter.

        The 'rfilt' argument should be a valid pandas python expression that can be used in
        'pandas.eval()'. For example, the '(SilentTime < 10000) and (PC6% == 0)' filter will exclude
        all the datapoints with silent time smaller than 10 usec and zero package C-state #6
        residency. Please, refer to 'pandas.eval()' documentation for more information.
        """

        self._rfilt = self._mangle_eval_expr(rfilt)

    def set_rsel(self, rsel):
        """
        Set the rows selector: only the CSV rows matching the 'rsel' expression will be added to the
        dataframe during the next dataframe operation like 'load_df()'. The 'rsel' argument is
        similar to the 'rfilt' argument in the 'set_rfilt()' method.
        """

        self._rsel = self._mangle_eval_expr(rsel)

    def set_cfilt(self, regexs):
        """
        Set the columns filter: the CSV columns with names in 'regexs' (or matching a regular
        expression in 'regexs') will be excluded from the dataframe during the next dataframe
        operation like 'load_df()'. Use 'None' to disable columns filter.
        """

        if regexs:
            self._cfilt = self.find_colnames(regexs, must_find_all=True)

    def set_csel(self, regexs):
        """
        Set the columns selector: only the CSV columns with names in 'regexs' (or matching a regular
        expression in 'regexs') will be included into the dataframe ('self.df') during the next
        dataframe operation like 'load_df()'. Use 'None' to disable the selector.
        """

        if regexs:
            self._csel = self.find_colnames(regexs, must_find_all=True)

    def clear_filts(self):
        """Clear all the filters and selectors for both rows and columns."""

        self._rfilt = None
        self._cfilt = None
        self._rsel = None
        self._csel = None

    def _get_rsel(self):
        """Merge row filter and selector and return the result."""

        expr = None

        if self._rsel:
            if self._rfilt:
                expr = f"({self._rsel}) and not ({self._rfilt})"
            else:
                expr = self._rsel
        else:
            if self._rfilt:
                expr = f"not ({self._rfilt})"
            else:
                expr = None

        return expr

    def _get_csel(self):
        """Merge column filter and selector and return the result."""

        if not self._csel and not self._cfilt:
            return None

        csel = self._csel
        if self._csel is None:
            csel = self.colnames

        cfilt = self._cfilt
        if self._cfilt is None:
            cfilt = []

        result = []
        cfilt_set = set(cfilt)
        for colname in csel:
            if colname not in cfilt_set:
                result.append(colname)

        return result

    def _calc_smrys(self, colname, funcnames, all_funcs):
        """
        Calculate summary functions 'funcnames' for column 'colname' and return the resulting
        dictionary. Note, 'smrys' comes from "summaries".
        """

        fmap = {"min" : "idxmin", "min_index" : "idxmin", "max" : "idxmax", "max_index" : "idxmax",
                "avg" : "mean", "med" : "median", "std" : "std"}
        smrys = {}

        for funcname in funcnames:
            restype = None
            coldef = self.defs.info[colname]

            # We do not the description, calling this method just to let it validate the function
            # name.
            get_smry_func_descr(funcname)

            fname = funcname
            if fname.endswith("%"):
                fname = "N%"
            if coldef["default_funcs"] != "all" and not all_funcs:
                # Skip functions that are not in the "default functions" list for this column.
                if funcname not in coldef["default_funcs"]:
                    # Take into account that defs may contain 'N%' that matches all percentiles.
                    if not (funcname.endswith("%") and "N%" in coldef["default_funcs"]):
                        continue

            if funcname in smrys:
                continue

            if funcname in fmap:
                # Other summaries can be handled in a generic way.
                datum = getattr(self.df[colname], fmap[funcname])()
            elif funcname == "nzcnt":
                datum = (self.df[colname] != 0).sum()
                restype = int
            else:
                # Handle percentiles separately.
                if funcname == "N%":
                    # Assume 99% by default.
                    funcname = "99%"
                percent = _get_percentile(funcname)
                datum = self.df[colname].quantile(percent / 100)

            if numpy.isnan(datum):
                continue

            # Min/max are a bit special.
            if fmap.get(funcname, "").startswith("idx"):
                # Datum is the index, not the actual value.
                idx_funcname = f"{funcname[0:3]}_index"
                funcname = funcname[0:3]
                if "idx" not in funcname:
                    # This makes sure that the order is the same as in 'funcnames'.
                    smrys[funcname] = None
                smrys[idx_funcname] = datum
                datum = self.df.loc[datum, colname]

            if not restype:
                restype = getattr(builtins, coldef["type"])
            smrys[funcname] = restype(datum)

        return smrys

    def calc_smrys(self, regexs=None, funcnames=None, all_funcs=False):
        """
        Calculate summary functions specified in 'funcnames' for columns matching 'regexs', and
        save the result in 'self.smrys'. By default this method calculates the summaries for all
        columns in the currently loaded dataframe and uses the default functions functions.

        The 'regexs' argument should be a list of column names or regular expressions, which will be
        applied to column names. The 'funcnames' argument must be a list of function names.

        Each column has the "default functions" associated with this column. These are just function
        names which generally make sense for this column. By default ('all_funcs' is 'False'), this
        method uses only the default functions. If, for example, 'funcnames' specifies the 'avg'
        function, and 'avg' function is not in the default functions list for the 'SilentTime'
        column, it will not be applied (will be skipped). So the result ('self.smrys') will not
        include 'avg' for 'SilentTime'. However, if 'avg' is in the list of default functions for
        the 'WakeLatency' column, and it was specified in 'funcnames', it will be applied and will
        show up in the result.

        The 'all_funcs' flag changes this behavior and disables the logic where we look at the
        default functions. If 'all_funcs' is 'True', this method will calculate all the functions in
        'funcnames' for all columns without looking at the default functions list.

        The result ('self.smrys') is a dictionary of dictionaries. The top level dictionary keys
        are column names and the sub-dictionary keys are function names.
        """

        if self.df is None:
            self.load_df()

        if not regexs:
            all_colnames = list(self.df)
        else:
            all_colnames = self.find_colnames(regexs, must_find_all=True)

        # Exclude columns with non-numeric data.
        colnames = self.get_numeric_colnames(colnames=all_colnames)

        # Make sure we have some columns to work with.
        if not colnames:
            msg = "no columns to calculate summary functions for"
            if all_colnames:
                msg += ".\nThese columns were excluded because they are not numeric: "
                msg += " ,".join(self.get_non_numeric_colnames(colnames=all_colnames))
            raise ErrorNotFound(msg)

        if not funcnames:
            funcnames = list(_SMRY_FUNCS.keys())

        # Turn 'N%' into 99%, 99.9%, 99.99%, and 99.999%.
        fnames = []
        for fname in funcnames:
            if fname != "N%":
                fnames.append(fname)
            else:
                fnames += ["99%", "99.9%", "99.99%", "99.999%"]

        self.smrys = {}
        for colname in colnames:
            subdict = self._calc_smrys(colname, fnames, all_funcs)
            if subdict:
                self.smrys[colname] = subdict

    def _load_csv(self, **kwargs):
        """Read the datapoints CSV file into a pandas dataframe and validate it."""

        _LOG.info("Loading test result '%s'.", self.dp_path)

        # Enforce the types we expect.
        dtype = {colname : colinfo["type"] for colname, colinfo in self.defs.info.items()}

        try:
            self.df = pandas.read_csv(self.dp_path, dtype=dtype, **kwargs)
        except Exception as err:
            raise Error(f"failed to load CSV file {self.dp_path}:\n{err}")

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

        rsel = self._get_rsel()
        csel = self._get_csel()

        if not rsel:
            if force_reload or self.df is None:
                self._load_csv(usecols=csel, **kwargs)
            csel = None
        else:
            # We cannot drop columns yet, because rows selector may refer the columns.
            if force_reload or self.df is None:
                self._load_csv(**kwargs)

        if rsel:
            _LOG.debug("applying rows selector: %s", rsel)
            expr = pandas.eval(rsel)
            self.df = self.df[expr].reset_index(drop=True)
            if self.df.empty:
                raise Error(f"no data left after applying row selector(s) to CSV file "
                            f"'{self.dp_path}'")

        if csel:
            _LOG.debug("applying columns selector: %s", csel)
            self.df = self.df[csel]
            if self.df.empty:
                raise Error(f"no data left after applying column selector(s) to CSV file "
                            f"'{self.dp_path}'")

        # Previously the CSV file had time in nanoseconds, but from version 1.1 onwards, time is
        # saved in microseconds. Convert time to microseconds if we are dealing with old data
        # format.
        if self.info["format_version"] < "1.1":
            for colname in self.df:
                defs = self.defs.info.get(colname)
                if defs and defs.get("unit") == "microsecond":
                    self.df[colname] = self.df[colname] / 1000

    def load_df(self, **kwargs):
        """
        If the datapoints CSV file has not been read yet ('self.df' is 'None'), read it into the
        'self.df' pandas dataframe. Then apply all the configured filters and selectors to
        'self.df'. The keyword arguments ('kwargs') are passed as is to 'pandas.read_csv()'.
        """

        self._load_df(force_reload=False, **kwargs)

    def reload_df(self, **kwargs):
        """
        Same as 'load_df()', but always reads the datapoints CSV file.
        """

        self._load_df(force_reload=True, **kwargs)

    def find_colnames(self, regexs, must_find_any=True, must_find_all=False):
        """
        Among the list of the column names of this test result, find column names that match regular
        expressions in 'regexs'. The arguments are as follows.
          * regexs - an iterable collection or regular expressions to match.
          * must_find_any - if 'True', raise an 'ErrorNotFound' exception in case of no matching
                            columns. If 'False', just return an empty list in case of no matching
                            columns.
          * must_find_all - if 'True', raise an 'ErrorNotFound' exception if any of the regular
                            expressions in 'regexs' did not match.
        """

        found = {}
        for regex in regexs:
            matched = False
            for colname in self.colnames:
                try:
                    if re.match(regex, colname):
                        found[colname] = regex
                        matched = True
                except re.error as err:
                    raise Error(f"bad regular expression '{regex}': {err}")

            if not matched:
                colnames_str = ", ".join(self.colnames)
                msg = f"no matches for column '{regex}' in the following list of available " \
                      f"columns:\n  {colnames_str}"
                if must_find_all:
                    raise ErrorNotFound(msg)
                _LOG.debug(msg)

        if not found and must_find_any:
            colnames_str = ", ".join(self.colnames)
            regexs_str = ", ".join(regexs)
            raise ErrorNotFound(f"no matches for the following column name(s):\n  {regexs_str}\n"
                                f"in the following list of available columns:\n  {colnames_str}")

        return list(found.keys())

    def _read_colnames(self):
        """Read the datapoints CSV file header, fetch and validate its column names."""

        try:
            colnames = list(pandas.read_csv(self.dp_path, nrows=0))
        except Exception as err:
            raise Error(f"failed to load CSV file {self.dp_path}:\n{err}")

        self.defs.populate_cstates(colnames)

        self._ignored_colnames = set(colnames) - set(self.defs.info.keys())
        if self._ignored_colnames:
            _LOG.warning("ignoring the following unknown column names in '%s':\n%s",
                         self.dp_path, ", ".join(self._ignored_colnames))

        for colname in colnames:
            if colname not in self._ignored_colnames:
                self.colnames.append(colname)

        self.colnames_set = set(self.colnames)

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
                raise Error(f"failed to create directory '{dirpath}':\n{err}")
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

    def _get_toolname(self):
        """
        Figure out what tool created this result. Very old results did not contain this information
        in the info file.
        """

        try:
            colnames = list(pandas.read_csv(self.dp_path, nrows=0))
        except Exception as err:
            raise Error(f"failed to load CSV file '{self.dp_path}':\n{err}")

        if "RTD" in colnames:
            return "ndl"
        if "WakeLatency" in colnames:
            return "wult"

        raise Error(f"unrecognized test results in '{self.dp_path}' - neither wult nor ndl")

    def _get_toolver(self):
        """
        Figure out version of the tool that created this result. Very old results did not contain
        this information in the info file.
        """

        toolname = self.info["toolname"]
        if toolname == "wult":
            return "1.4"
        if toolname == "ndl":
            return "1.1"

        raise Error(f"failed to figure out which '{toolname}' tool version has created test result "
                    f"at '{self.dp_path}'")

    def __init__(self, dirpath, reportid=None):
        """
        The class constructor. The arguments are as follows.
          * dirpath - path to the directory containing the raw test result to open.
          * reportid - override the report ID of the raw test result: the 'reportid' string will be
                       used instead of the report ID stored in 'dirpath/info.yml'. Note, the
                       provided report ID is not verified, so the caller has to make sure is a sane
                       string.

        Note, the constructor does not load the potentially huge test result data into the memory.
        It only loads the 'info.yml' file and figures out the colum names list. The data are loaded
        "on-demand" by the 'load_df()' and other methods.
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
                raise Error(f"failed to access '{attr}': {err}")

        # The row and column filters and selectors.
        self._rfilt = None
        self._cfilt = None
        self._rsel = None
        self._csel = None

        # Unknown columns in the CSV file.
        self._ignored_colnames = None

        self.df = None
        self.smrys = None
        self.colnames = []
        self.colnames_set = set()

        self.info = YAML.load(self.info_path)
        if reportid:
            # Note, we do not verify it here, the caller is supposed to verify.
            self.info["reportid"] = reportid
        if "reportid" not in self.info:
            raise ErrorNotSupported(f"no 'reportid' key found in {self.info_path}")
        self.reportid = self.info["reportid"]

        toolname = self.info.get("toolname")
        if not toolname:
            self.info["toolname"] = self._get_toolname()

        toolver = self.info.get("toolver")
        if not toolver:
            self.info["toolver"] = self._get_toolver()

        self.defs = Defs.Defs(self.info["toolname"])

        # All column names in the CSV file.
        self._read_colnames()
