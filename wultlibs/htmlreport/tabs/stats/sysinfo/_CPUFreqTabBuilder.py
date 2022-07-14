# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""
This module provides the capability of populating a "cpufreq" SysInfo tab to visualise information
collected from '/sys/devices/system/cpu/cpufreq'.
"""

from wultlibs.htmlreport.tabs.stats.sysinfo import _DTabBuilderBase

_FILES = {
    "cpufreq": "sysinfo/sys-cpufreq.after.raw.txt"
}

class CPUFreqTabBuilder(_DTabBuilderBase.DTabBuilderBase):
    """
    This class provides the capability of populating a "cpufreq" info tab to visualise information
    collected from '/sys/devices/system/cpu/cpufreq'.

    Public method overview:
     * get_tab() - returns a '_Tabs.DTabDC' instance which contains the collected information.
    """

    def __init__(self, outdir):
        """Class constructor. Arguments are the same as in 'DTabBuilderBase.__init__()'."""

        super().__init__("cpufreq", outdir, _FILES)
