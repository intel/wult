# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module provides API for write-only raw test results.
"""

import os
import shutil
import contextlib
from pepclibs.helperlibs import Logging, YAML, ClassHelpers
from pepclibs.helperlibs.Exceptions import Error, ErrorExists
from wultlibs.helperlibs import Human
from wultlibs.result import _CSV, _RawResultBase
from wultlibs.result._RawResultBase import FORMAT_VERSION

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.wult.{__name__}")

class WORawResult(_RawResultBase.RawResultBase, ClassHelpers.SimpleCloseContext):
    """This class represents a write-only raw test result."""

    def set_exclude(self, exclude):
        """Save the 'exclude' value, which describes which datapoints to exclude."""
        self._exclude = exclude

    def set_include(self, include):
        """Save the 'include' value, which describes which datapoints to include."""
        self._include = include

    def _init_outdir(self):
        """Initialize the output directory for writing or appending test results."""

        if self.dirpath.exists():
            # Only accept empty output directory.
            paths = (self.dp_path, self.info_path, self.logs_path, self.stats_path)
            for path in paths:
                if path.exists():
                    raise ErrorExists(f"cannot use path '{self.dirpath}' as the output directory, "
                                      f"it already contains '{path.name}'")
            self._created_paths = paths
        else:
            try:
                self.dirpath.mkdir(parents=True, exist_ok=True)
                self._created_paths.append(self.dirpath)
                _LOG.info("Created result directory '%s'", self.dirpath)
            except OSError as err:
                raise Error(f"failed to create directory '{self.dirpath}':\n{err}") from None

        self.csv = _CSV.WritableCSV(self.dp_path)

        # Create an empty info file in advance.
        try:
            with self.info_path.open("tw+", encoding="utf-8"):
                pass
        except OSError as err:
            raise Error(f"failed to create file '{self.info_path}':\n{err}") from None

    def _mangle_eval_expr(self, expr):
        """
        Mangle a python expression that we use for row filters and selectors. Some of the CSV
        file column names may have symbols like '%' (e.g., in 'CC1%'), which cannot be used in
        python expressions, and this method solves this problem.

        Also, 'CC1%' are 'CC1Derived%' are effectively the same thing so make sure that if the
        filter includes 'CC1%', but it is absent in the CSV, then 'CC1Derived%' is used instead (if
        it is present in the CSV file).
        """

        if expr is None:
            return None

        expr = str(expr)

        for replaced, replacement in (("CC1%", "CC1Derived%"), ("CC1Derived%", "CC1%")):
            if replaced in expr and replaced not in self.csv.hdr:
                expr = expr.replace(replaced, replacement)
                _LOG.notice("metric '%s' was not found, replacing it with '%s', new filter: '%s'",
                            replaced, replacement, expr)
                break

        for colname in self.csv.hdr:
            expr = expr.replace(colname, f"dp['{colname}']")
        return expr

    def _get_dp_filter(self):
        """
        Get the datapoint filter expression. See 'super()._get_dp_filter()' for more details.
        """

        if not self._mangled_dpfilter:
            dpfilter = super()._get_dp_filter()
            self._mangled_dpfilter = self._mangle_eval_expr(dpfilter)
        return self._mangled_dpfilter

    def _try_filters(self, dp): # pylint: disable=unused-argument
        """
        Verify whether 'dp' passes the filter expression. Returns 'True' if 'dp' would not pass the
        filters because it matches the expression. Otherwise returns 'False'.
        """

        dpfilter = self._get_dp_filter()
        if not dpfilter:
            return True

        passed = False
        try:
            # The 'eval()' expressions use the datapoint argument 'dp'.
            passed = eval(dpfilter) # pylint: disable=eval-used
        except Exception as err:
            raise Error(f"failed to evaluate expression '{dpfilter}'. Make sure you use correct "
                        f"metric names, which are also case-sensitive. The filter was failing on "
                        f"datapoint:\n{Human.dict2str(dp)}") from err

        return passed

    def _get_csv_row(self, dp):
        """
        Form CSV row from datapoint dictionary values in 'dp'. Make C-state percentage values nicer
        to read by saving only two most significant decimals. Returns the CSV row as a list.
        """

        row = []
        for key in self.csv.hdr:
            val = dp[key]
            if "%" in key:
                val =  f"{val:.2f}"
            row.append(val)

        return row

    def add_csv_row(self, dp):
        """
        Apply filters to the 'dp' datapoint and possibly add it to the CSV file. The 'dp' argument
        should be a dictionary with keys being the CSV column names, and values being the column
        value. If 'self.keep_filtered' is 'False', the datapoint is added to the CSV file only if it
        passes the filters ('dp' does not match the filter expression). If 'self.keep_filtered' is
        'True', the datapoint is added to the CSV file regardless of whether it passes the filters
        or not.

        The return value is the same as in 'try_filters()' function: returns 'True' if 'dp' passes
        the filters, otherwise returns 'False'.
        """

        passed = self._try_filters(dp)
        if passed or self.keep_filtered:
            self.csv.add_row(self._get_csv_row(dp))

        return passed

    def write_info(self):
        """Write the 'self.info' dictionary to the 'info.yml' file."""

        YAML.dump(self.info, self.info_path)

    def __init__(self, toolname, toolver, reportid, outdir, cpu=None):
        """
        The class constructor. The arguments are as follows.
          * toolname - name of the tool creating the report.
          * toolver - version of the tool creating the report.
          * reportid - reportid of the raw test result.
          * outdir - the output directory to store the raw results at.
          * cpu - CPU number associated with this test result (e.g., measured CPU number).
        """

        self.cpu = cpu

        super().__init__(outdir)

        # The writable CSV file object.
        self.csv = None
        self.reportid = reportid
        self._mangled_dpfilter = None
        self.keep_filtered = False
        self._created_paths = []

        self._init_outdir()

        self.info["toolname"] = toolname
        self.info["toolver"] = toolver
        if cpu is not None:
            self.info["cpu"] = self.cpu
        self.info["format_version"] = FORMAT_VERSION
        self.info["reportid"] = reportid

        # Note, this format version assumes that the following elements should be added to
        # 'self.info' later by the owner of this object:
        #  * toolname - name of the tool creating the report.
        #  * toolver - version of the tool creating the report.

    def close(self):
        """Stop the experiment."""

        if getattr(self, "csv", None):
            self.csv.close()
            self.csv = None

        # Remove results if no datapoints was collected.
        dp_path = getattr(self, "dp_path", None)
        paths = []
        if (not dp_path or not dp_path.exists()) or dp_path.stat().st_size == 0:
            paths = getattr(self, "_created_paths", [])

        if paths:
            _LOG.info("No data was collected so the following paths which were created will be "
                      "deleted:\n  - %s", "\n  - ".join(str(path) for path in self._created_paths))

        for path in paths:
            if not path.exists():
                continue
            with contextlib.suppress(Exception):
                if path.is_dir():
                    shutil.rmtree(path)
                elif path.is_file():
                    os.remove(path)
