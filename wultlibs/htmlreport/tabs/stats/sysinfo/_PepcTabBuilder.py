# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""
This module provides the capability of populating a "pepc" info tab to visualise information
collected with the 'pepc' tool.
"""

from wultlibs.htmlreport.tabs.stats.sysinfo import _DTabBuilderBase

_FILES = {
    "pepc cstates info": "sysinfo/pepc_cstates.raw.txt",
    "pepc pstates info": "sysinfo/pepc_pstates.raw.txt"
}

class PepcTabBuilder(_DTabBuilderBase.DTabBuilderBase):
    """
    This class provides the capability of populating a "pepc" info tab to visualise information
    collected with the 'pepc' tool.

    Public method overview:
     * get_tab() - returns a '_Tabs.DTabDC' instance which contains information collected using the
                   'pepc' tool.
    """

    def __init__(self, outdir):
        """Class constructor. Arguments are the same as in 'InfoTabBuilderBase.__init__()'."""

        super().__init__("pepc", outdir, _FILES)
