# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""This module provides the API for creating raw stats-collect test results."""

import time
import os
from pepclibs.helperlibs import YAML
from pepclibs.helperlibs.Exceptions import Error, ErrorExists
from statscollectlibs.helperlibs import FSHelpers
from statscollectlibs.rawresultlibs import _RawResultBase

class WORawResult(_RawResultBase.RawResultBase):
    """This class represents a write-only raw test result."""

    def _init_outdir(self):
        """Initialize the output directory for writing or appending test results."""

        if self.dirpath.exists():
            # Only accept empty output directory.
            paths = (self.info_path, self.logs_path, self.stats_path)
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

    def write_info(self):
        """Write the 'self.info' dictionary to the 'info.yml' file."""

        YAML.dump(self.info, self.info_path)

    def __init__(self, reportid, outdir, toolver, cpunum, cmd):
        """
        The class constructor. The arguments are as follows.
          * reportid - reportid of the raw test result.
          * outdir - the output directory to store the raw results at.
          * toolver - version of the tool creating the report.
          * cpunum - CPU number associated with this test result (e.g., measured CPU number).
          * cmd - the command executed during statistics collection.
        """

        super().__init__(outdir)

        self.reportid = reportid
        self.cpunum = cpunum

        self._init_outdir()

        self.info["format_version"] = _RawResultBase.FORMAT_VERSION
        self.info["reportid"] = reportid
        self.info["toolname"] = "stats-collect"
        self.info["toolver"] = toolver
        self.info["cpunum"] = self.cpunum
        self.info["cmd"] = cmd
        self.info["date"] = time.strftime("%d %b %Y")
