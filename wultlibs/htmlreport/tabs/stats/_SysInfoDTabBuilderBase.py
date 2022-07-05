# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""
This module provides the capability of populating a "SysInfo" data tab.

"SysInfo" tabs contain various system information about the systems under test (SUTs).
"""

from wultlibs.htmlreport.tabs import _Tabs

class SysInfoDTabBuilderBase:
    """
    This class provides the capability of populating a "SysInfo" tab.

    Public method overview:
     * get_tab() - returns a '_Tabs.DTabDC' instance which represents system information.
    """

    def get_tab(self):
        """Returns a '_Tabs.DTabDC' instance which represents system information."""

        return _Tabs.DTabDC(self.name)

    def __init__(self, name, outdir):
        """Class constructor."""

        self.name = name
        self.outdir = outdir
