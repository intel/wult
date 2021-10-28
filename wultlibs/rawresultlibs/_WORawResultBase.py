# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module base class for wirte-only raw test result classes.
"""

import os
from helperlibs import FSHelpers
from helperlibs.Exceptions import Error, ErrorExists
from wultlibs.helperlibs import YAML
from wultlibs.rawresultlibs import _CSV, _RawResultBase
from wultlibs.rawresultlibs._RawResultBase import FORMAT_VERSION

class WORawResultBase(_RawResultBase.RawResultBase):
    """This class represents a write-only raw test result."""

    def set_rfilt(self, rfilt):
        """Save row filter value."""
        self._rfilt = rfilt

    def set_rsel(self, rsel):
        """Save row selector value."""
        self._rsel = rsel

    def _init_outdir(self):
        """Initialize the output directory for writing or appending test results."""

        if self.dirpath.exists():
            # Only accept empty output directory.
            paths = (self.dp_path, self.info_path, self.logs_path, self.stats_path, self.descr_path)
            for path in paths:
                if path.exists():
                    raise ErrorExists(f"cannot use path '{self.dirpath}' as the output directory, "
                                      f"it already contains '{path.name}'")
        else:
            try:
                self.dirpath.mkdir(parents=True, exist_ok=True)
                FSHelpers.set_default_perm(self.dirpath)
            except OSError as err:
                raise Error(f"failed to create directory '{self.dirpath}':\n{err}") from None

        self.csv = _CSV.WritableCSV(self.dp_path)

        if self.info_path.exists():
            if not self.info_path.is_file():
                raise Error(f"path '{self.info_path}' exists, but it is not a regular file")
            # Verify that we are going to be able writing to the info file.
            if not os.access(self.info_path, os.W_OK):
                raise Error(f"cannot access '{self.info_path}' for writing")
        else:
            # Create an empty info file in advance.
            try:
                self.info_path.open("tw+", encoding="utf-8").close()
            except OSError as err:
                raise Error(f"failed to create file '{self.info_path}':\n{err}") from None

    def _mangle_eval_expr(self, expr):
        """
        Mangle a python expression that we use for row filters and selectors. Some of the CSV
        file column names may have symbols like '%' (e.g., in 'CC1%'), which cannot be used in
        python expressions, and this method solves the problem.
        """

        if expr is None:
            return None

        expr = str(expr)

        for colname in self.csv.hdr:
            expr = expr.replace(colname, f"dp['{colname}']")
        return expr

    def _get_rsel(self):
        """Get mangled and merged row selector."""

        if not self._mangled_rsel:
            rsel = super()._get_rsel()
            self._mangled_rsel = self._mangle_eval_expr(rsel)
        return self._mangled_rsel

    def _try_filters(self, dp): # pylint: disable=unused-argument
        """
        Verify whether 'dp' passes the filter expression. Returns 'True' if 'dp' would not pass the
        filters because it matches the expression. Otherwise returns 'False'.
        """

        rsel = self._get_rsel()
        passed = False
        try:
            # The 'eval()' expressions use the datapoint argument 'dp'.
            passed = (not rsel) or eval(rsel) # pylint: disable=eval-used
        except SyntaxError as err:
            raise Error(f"failed to evaluate expression '{rsel}'. Make sure you use correct CSV "
                        f"column names, which are also case-sensitive.") from err

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

    def __init__(self, reportid, outdir):
        """
        The class constructor. The arguments are as follows.
          * reportid - reportid of the raw test result.
          * outdir - the output directory to store the raw results at.
        """

        super().__init__(outdir)

        # The writable CSV file object.
        self.csv = None
        self.reportid = reportid
        self._mangled_rsel = None
        self.keep_filtered = False

        self._init_outdir()

        self.info["format_version"] = FORMAT_VERSION
        self.info["reportid"] = reportid

        # Note, this format version assumes that the following elements should be added to
        # 'self.info' later by the owned of this object:
        #  * toolname - name of the tool creating the report.
        #  * toolver - version of the tool creating the report.

    def __del__(self):
        """The destructor."""
        self.close()

    def close(self):
        """Stop the experiment."""

        if getattr(self, "csv", None):
            self.csv.close()
            self.csv = None

    def __enter__(self):
        """Enter the run-time context."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the runtime context."""
        self.close()
