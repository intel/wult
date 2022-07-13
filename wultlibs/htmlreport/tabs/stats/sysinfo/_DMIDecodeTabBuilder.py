# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""
This module provides the capability of populating a "dmidecode" SysInfo tab to visualise information
collected with 'dmidecode'.
"""

from wultlibs.htmlreport.tabs.stats.sysinfo import _DTabBuilderBase

_FILES = {
    "dmidecode": "sysinfo/dmidecode.raw.txt",
    "dmidecode -u": "sysinfo/dmidecode-u.raw.txt"
}

class DMIDecodeTabBuilder(_DTabBuilderBase.DTabBuilderBase):
    """
    This class provides the capability of populating a "dmidecode" info tab to visualise information
    collected with 'dmidecode'.

    Public method overview:
     * get_tab() - returns a '_Tabs.DTabDC' instance which contains information collected using the
                   'dmidecode'.
    """

    def __init__(self, outdir):
        """Class constructor. Arguments are the same as in 'InfoTabBuilderBase.__init__()'."""

        super().__init__("dmidecode", outdir, _FILES)
