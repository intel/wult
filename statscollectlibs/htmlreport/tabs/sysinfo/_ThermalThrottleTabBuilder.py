# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""
This module provides the capability of populating a "thermal_throttle" SysInfo tab to visualise
information collected from '/sys/devices/system/cpu/thermal_throttle'.
"""

from statscollectlibs.htmlreport.tabs.sysinfo import _SysInfoTabBuilderBase

_FILES = {"thermal throttle": "sysinfo/sys-thermal_throttle.after.raw.txt"}

class ThermalThrottleTabBuilder(_SysInfoTabBuilderBase.SysInfoTabBuilderBase):
    """
    This class provides the capability of populating a "thermal_throttle" info tab to visualise
    information collected from '/sys/devices/system/cpu/thermal_throttle'.

    Public method overview:
     * get_tab() - returns a '_Tabs.DTabDC' instance which contains the collected information.
    """

    def __init__(self, outdir, stats_paths):
        """Class constructor. Arguments are the same as in 'DTabBuilderBase.__init__()'."""

        super().__init__("thermal_throttle", outdir, _FILES, stats_paths)
