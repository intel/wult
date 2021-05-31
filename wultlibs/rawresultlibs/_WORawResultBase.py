# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2020 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module base class for wirte-only raw test result classes.
"""

import os
from wultlibs.helperlibs import FSHelpers, YAML
from wultlibs.helperlibs.Exceptions import Error, ErrorNotSupported
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

    def _check_can_continue(self):
        """
        Verify if it is OK to continue adding more datapoints to an existing test result."""

        if not self.dp_path.stat().st_size:
            # The datapoints file is empty. It is OK to continue.
            return

        if not self.info_path.is_file():
            raise Error(f"cannot continue a test result at '{self.dirpath}' because it does not "
                        f"have the info file ('{self.info_path}').")

        info = YAML.load(self.info_path)

        if info["format_version"] != FORMAT_VERSION:
            raise ErrorNotSupported(f"report at '{self.dirpath}' uses an unsupported format "
                                    f"version '{info['format_version']}', supported format version "
                                    f"is '{FORMAT_VERSION}'")

        if self.reportid != info["reportid"]:
            raise Error(f"cannot continue writing data belonging to report ID '{self.reportid}'\n"
                        f"to an existing test result directory '{self.dirpath}' with report ID "
                        f"'{info['reportid']}'.\nReport IDs must be the same.")

    def _init_outdir(self):
        """Initialize the output directory for writing or appending test results."""

        if self.dp_path.is_file() and self._cont:
            self._check_can_continue()

        if not self.dirpath.exists():
            try:
                self.dirpath.mkdir(parents=True, exist_ok=True)
                FSHelpers.set_default_perm(self.dirpath)
            except OSError as err:
                raise Error(f"failed to create directory '{self.dirpath}':\n{err}") from None

        self.csv = _CSV.WritableCSV(self.dp_path, cont=self._cont)

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

    def _apply_filter(self, dp):
        """
        Apply filters to the datapoint 'dp'. Returns datapoint 'dp' if filter expression is
        satisfied, otherwise returns 'None'.
        """

        rsel = self._get_rsel()
        try:
            if rsel and not eval(rsel): # pylint: disable=eval-used
                return None
        except SyntaxError as err:
            raise Error("failed to evaluate expression '%s'. Make sure you use correct CSV " \
                        "column names, which are also case-sensitive.", rsel) from err
        return dp

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
        Add datapoint from dictionary 'dp' to CSV file. Datapoint is added only if it fullfills
        filter expressions. Returns 'True' if the row was added to CSV file, returns 'False'
        otherwise.
        """

        if not self._apply_filter(dp):
            return False

        self.csv.add_row(self._get_csv_row(dp))
        return True

    def write_info(self):
        """Write the 'self.info' dictionary to the 'info.yml' file."""

        YAML.dump(self.info, self.info_path)

    def __init__(self, reportid, outdir, cont=False):
        """
        The class constructor. The arguments are as follows.
          * reportid - reportid of the raw test result.
          * outdir - the output directory to store the raw results at.
          * cont - defines what to do if 'outdir' already contains test results. By default the
                   existing 'datapoints.csv' file gets overridden, but when 'cont' is 'True', the
                   existing 'datapoints.csv' file is "continued" instead (new datapoints are
                   appended).
        """

        super().__init__(outdir)

        # The writable CSV file object.
        self.csv = None
        self._cont = cont
        self.reportid = reportid
        self._mangled_rsel = None

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
