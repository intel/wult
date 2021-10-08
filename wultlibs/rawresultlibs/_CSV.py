# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2020 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module provides API for reading and writing CSV files.
"""

import csv
import logging
from pathlib import Path
from helperlibs.Exceptions import Error

_LOG = logging.getLogger()

class WritableCSV:
    """This class represents a write-only CSV file."""

    def _continue(self):
        """Prepare to continue appending more data to an existing CSV file."""

        try:
            self._fobj = self.path.open("r+", encoding="utf-8")
        except OSError as err:
            raise Error(f"failed to open file '{self.path}':\n{err}")

        try:
            reader = csv.reader(self._fobj)
            self.hdr = next(reader)
            self.initial_rows_cnt = sum(1 for row in reader)
            _LOG.debug("CSV file '%s' information:\n * Header %s\n * Data rows count: %d",
                       self.path, ", ".join(self.hdr), self.initial_rows_cnt)
        except csv.Error as err:
            raise Error(f"failed to read CSV file '{self.path}':\n{err}")
        except StopIteration:
            pass

        # Seek to the end of the file.
        self._fobj.seek(0, 2)

    def _create(self):
        """Create the CSV file."""

        try:
            self._fobj = self.path.open("tw+", encoding="utf-8")
        except OSError as err:
            raise Error(f"failed to create file '{self.path}':\n{err}")

    def _cond_flush(self):
        """
        Flush the buffered CSV file rows if enough of them have been collected in 'self._rowsbuf'.
        """

        if len(self._rowsbuf) >= self._bufsize:
            self.flush()

    def flush(self):
        """Flush the buffered CSV file rows."""

        for row in self._rowsbuf:
            self._fobj.write(row)
            self._fobj.write("\n")
        self._rowsbuf = []

    def add_header(self, hdr):
        """
        Add the CSV header. The 'hdr' argument should be a list of CSV column names.
        """

        if not self.hdr:
            self.hdr = hdr
            self._rowsbuf.append(",".join(hdr))
            self._cond_flush()
            _LOG.debug("CSV header: %s", ", ".join(hdr))
            return

        if list(hdr) != list(self.hdr):
            old_hdr = ", ".join(self.hdr)
            new_hdr = ", ".join(hdr)
            raise Error(f"cannot add the following header to CSV file {self.path}:\n{new_hdr}\n"
                        f"the CSV file already contains a different header:\n{old_hdr}")

    def add_row(self, row):
        """
        Add a row of data to the CSV file. The 'row' argument should be a list of values.
        """

        if not self.hdr:
            raise Error(f"cannot add rows to CSV file {self.path} - the CSV header has not "
                        f"been added yet")

        row_str = ",".join([str(datum)for datum in row])
        if len(row) != len(self.hdr):
            hdr_str = ",".join(self.hdr)
            raise Error(f"failed to add a row with {len(row)} elements to a CSV file with "
                        f"{len(self.hdr)} elements in the header\n"
                        f"CSV file: {self.path}\n"
                        f"CSV header: {hdr_str}\n"
                        f"bad CSV row: {row_str}\n")

        self._rowsbuf.append(row_str)
        self.rows_cnt += 1
        self._cond_flush()

    def __init__(self, path, cont=False):
        """
        The class constructor. The arguments are as follows.
          * path - the CSV file path.
          * cont - if 'path' exists and 'cont' is 'True', then continue appending data to 'path',
                   instead of truncating and overriding 'path', which is the default behavior.
        """

        self.path = Path(path)
        self.hdr = None
        self.initial_rows_cnt = 0
        # How many CSV file rows have been written so far, excluding the CSV header row.
        self.rows_cnt = 0

        self._cont = cont
        # How many CSV file rows to buffer before writing them out.
        self._bufsize = 1024
        self._fobj = None
        self._rowsbuf = []

        if path.is_file() and cont:
            self._continue()
        else:
            self._create()

    def __del__(self):
        """The destructor."""
        self.close()

    def close(self):
        """Stop the experiment."""

        if getattr(self, "_fobj", None):
            self.flush()
            self._fobj.close()
            self._fobj = None

    def __enter__(self):
        """Enter the run-time context."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the runtime context."""
        self.close()
