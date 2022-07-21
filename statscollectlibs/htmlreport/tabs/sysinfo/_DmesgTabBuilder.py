# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""
This module provides the capability of populating a "dmesg" SysInfo tab to visualise information
collected with 'dmesg'.
"""

from wultlibs.htmlreport.tabs.stats.sysinfo import _DTabBuilderBase

_FILES = {
    "dmesg": "sysinfo/dmesg.after.raw.txt",
}

class DmesgTabBuilder(_DTabBuilderBase.DTabBuilderBase):
    """
    This class provides the capability of populating a "dmesg" info tab to visualise information
    collected with 'dmesg'.

    Public method overview:
     * get_tab() - returns a '_Tabs.DTabDC' instance which contains information collected using
                   'dmesg'.
    """

    def __init__(self, outdir):
        """Class constructor. Arguments are the same as in 'DTabBuilderBase.__init__()'."""

        super().__init__("dmesg", outdir, _FILES)
