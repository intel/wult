# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""
This module provides the capability of populating a "lspci" SysInfo tab to visualise information
collected with 'lspci'.
"""

from statscollectlibs.htmlreport.tabs.sysinfo import _SysInfoTabBuilderBase

_FILES = {
    "lspci": "sysinfo/lspci.raw.txt",
    "lspci -vvv": "sysinfo/lspci-vvv.raw.txt"
}

class LspciTabBuilder(_SysInfoTabBuilderBase.SysInfoTabBuilderBase):
    """
    This class provides the capability of populating a "lspci" info tab to visualise information
    collected with 'lspci'.

    Public method overview:
     * get_tab() - returns a '_Tabs.DTabDC' instance which contains information collected using
                   'lspci'.
    """

    def __init__(self, outdir):
        """Class constructor. Arguments are the same as in '_SysInfoTabBuilderBase.__init__()'."""

        super().__init__("lspci", outdir, _FILES)
