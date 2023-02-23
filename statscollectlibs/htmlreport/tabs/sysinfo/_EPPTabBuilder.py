# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""
This module provides the capability of populating an "x86_energy_perf_policy" SysInfo tab to
visualise various system information.
"""

from statscollectlibs.htmlreport.tabs.sysinfo import _SysInfoTabBuilderBase

_FILES = {
    "x86_energy_perf_policy": "sysinfo/x86_energy_perf_policy.after.raw.txt",
}

class EPPTabBuilder(_SysInfoTabBuilderBase.SysInfoTabBuilderBase):
    """
    This class provides the capability of populating an "x86_energy_perf_policy" SysInfo tab to
    visualise various system information.

    Public method overview:
     * get_tab() - returns a '_Tabs.DTabDC' instance which contains various system information.
    """

    def __init__(self, outdir):
        """Class constructor. Arguments are the same as in 'DTabBuilderBase.__init__()'."""

        super().__init__("x86_energy_perf_policy", outdir, _FILES)
