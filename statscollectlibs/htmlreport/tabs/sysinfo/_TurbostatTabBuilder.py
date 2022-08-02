# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""
This module provides the capability of populating a "turbostat" info tab to visualise information
collected with the 'turbostat' tool.
"""

from statscollectlibs.htmlreport.tabs.sysinfo import _DTabBuilderBase

_FILES = {
    "turbostat": "sysinfo/turbostat-d.after.raw.txt"
}

class TurbostatTabBuilder(_DTabBuilderBase.DTabBuilderBase):
    """
    This class provides the capability of populating a "turbostat" info tab to visualise information
    collected with the 'turbostat' tool.

    Public method overview:
     * get_tab() - returns a '_Tabs.DTabDC' instance which contains information collected using the
                   'turbostat' tool.
    """

    def __init__(self, outdir):
        """Class constructor. Arguments are the same as in 'DTabBuilderBase.__init__()'."""

        super().__init__("turbostat", outdir, _FILES)
