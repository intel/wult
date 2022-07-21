# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""
This module provides the capability of populating a "cpuidle" SysInfo tab to visualise information
collected from '/sys/devices/system/cpu/cpuidle'.
"""

from statscollectlibs.htmlreport.tabs.sysinfo import _DTabBuilderBase

_FILES = {
    "cpuidle": "sysinfo/sys-cpuidle.after.raw.txt"
}

class CPUIdleTabBuilder(_DTabBuilderBase.DTabBuilderBase):
    """
    This class provides the capability of populating a "cpuidle" info tab to visualise information
    collected from '/sys/devices/system/cpu/cpuidle'.

    Public method overview:
     * get_tab() - returns a '_Tabs.DTabDC' instance which contains the collected information.
    """

    def __init__(self, outdir):
        """Class constructor. Arguments are the same as in 'DTabBuilderBase.__init__()'."""

        super().__init__("cpuidle", outdir, _FILES)
