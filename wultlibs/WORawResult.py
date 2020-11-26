# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2020 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module provides API for creating raw wult test results.
"""

from wultlibs.helperlibs.Exceptions import Error
from wultlibs import _WORawResultBase, _Common
from wultlibs._WORawResultBase import FORMAT_VERSION # pylint: disable=unused-import

class WultWORawResult(_WORawResultBase.WORawResultBase):
    """This class represents a write-only raw wult test result."""

    def _check_can_continue(self):
        """Same as 'WORawResultBase._check_can_continue()'. Just adds 'cpunum' check."""

        super()._check_can_continue()

        if self.cpunum != self.info.get("cpunum", self.cpunum):
            raise Error(f"cannot continue writing CPU '{self.cpunum}' data to an existing test "
                        f"result directory\n'{self.dirpath}' containing CPU '{self.info['cpunum']}'"
                        f" data.\nCPU numbers must be the same.")

    def __init__(self, reportid, outdir, toolver, cpunum, cont=False):
        """
        The class constructor. The arguments are the same as in 'WORawResultBase', except for the
        following.
          * toolver - version of the tool creating the report.
          * cpunum - the to measure (Linux logical CPU number, e.g. like in '/proc/cpuinfo').
        """

        self.cpunum = None

        super().__init__(reportid, outdir, cont=cont)

        self.cpunum = _Common.validate_cpunum(cpunum)

        self.info["toolname"] = "wult"
        self.info["toolver"] = toolver
        self.info["cpunum"] = self.cpunum

        # Note, this format version assumes that the following elements should be added to
        # 'self.info' later by the owner of this object:
        #  * devid - ID of the delayed event device
        #  * devdescr - description of the delayed event device

class NdlWORawResult(_WORawResultBase.WORawResultBase):
    """This class represents a write-only raw ndl test result."""

    def __init__(self, reportid, outdir, toolver, cont=False):
        """
        The class constructor. The arguments are the same as in 'WORawResultBase', except for the
        following.
          * toolver - version of the tool creating the report.
        """

        super().__init__(reportid, outdir, cont=cont)

        self.info["toolname"] = "ndl"
        self.info["toolver"] = toolver
