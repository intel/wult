# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module contains the base class for the raw test result classes.

A raw test result is a directory containing the following files.
 * info.yml - a YAML file containing miscellaneous test information, such as the report ID.
 * logs - optional directory containing wult run logs.
 * stats - optional directory containing various statistics, such as 'lscpu'.
"""

from pathlib import Path
from pepclibs.helperlibs.Exceptions import Error

# The latest supported raw results format version.
FORMAT_VERSION = "1.2"

class RawResultBase:
    """Base class for the test result classes."""

    def __init__(self, dirpath):
        """The class constructor. The 'dirpath' argument is path raw test result directory."""

        self.reportid = None
        # This dictionary represents the info file.
        self.info = {}

        if not dirpath:
            raise Error("raw test results directory path was not specified")

        self.dirpath = Path(dirpath)

        if self.dirpath.exists() and not self.dirpath.is_dir():
            raise Error(f"path '{self.dirpath}' is not a directory")

        self.info_path = self.dirpath.joinpath("info.yml")
        self.logs_path = self.dirpath.joinpath("logs")
        self.stats_path = self.dirpath.joinpath("stats")

        if self.info_path.exists() and not self.info_path.is_file():
            raise Error(f"path '{self.info_path}' exists, but it is not a regular file")

        for name in ("logs_path", "stats_path"):
            path = getattr(self, name)
            if path.exists() and not path.is_dir():
                raise Error(f"path '{path}' exists, but it is not a directory")
