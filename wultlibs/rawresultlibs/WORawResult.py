# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module provides API for creating raw wult test results.
"""

from wultlibs.rawresultlibs import _WORawResultBase
from wultlibs.rawresultlibs._WORawResultBase import FORMAT_VERSION # pylint: disable=unused-import

class WultWORawResult(_WORawResultBase.WORawResultBase):
    """This class represents a write-only raw wult test result."""

    def __init__(self, reportid, outdir, toolver, cpunum):
        """
        The class constructor. The arguments are the same as in 'WORawResultBase', except for the
        following.
          * toolver - version of the tool creating the report.
          * cpunum - CPU number associated with this test result (e.g., measured CPU number).
        """

        super().__init__(reportid, outdir, cpunum=cpunum)

        self.info["toolname"] = "wult"
        self.info["toolver"] = toolver
        self.info["cpunum"] = self.cpunum

        # Note, this format version assumes that the following elements should be added to
        # 'self.info' later by the owner of this object:
        #  * devid - ID of the delayed event device
        #  * devdescr - description of the delayed event device

class NdlWORawResult(_WORawResultBase.WORawResultBase):
    """This class represents a write-only raw ndl test result."""

    def __init__(self, reportid, outdir, toolver):
        """
        The class constructor. The arguments are the same as in 'WORawResultBase', except for the
        following.
          * toolver - version of the tool creating the report.
        """

        super().__init__(reportid, outdir)

        self.info["toolname"] = "ndl"
        self.info["toolver"] = toolver
