# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""
This module provides the capability of populating the turbostat statistics tab.
"""

from statscollectlibs.htmlreport.tabs.turbostat import _MCPUL2TabBuilder
from wultlibs.htmlreport.tabs import _Tabs
from wultlibs.htmlreport.tabs.stats.turbostat import _TotalsL2TabBuilder

class TurbostatTabBuilder:
    """
    This class provides the capability of populating the turbostat statistics tab.

    Public methods overview:
    1. Generate a '_Tabs.CTabDC' instance containing turbostat level 2 tabs.
       * 'get_tab()'
    """

    name = "Turbostat"

    def get_tab(self):
        """
        Returns a '_Tabs.CTabDC' instance containing turbostat level 2 tabs:

        1. If 'measured_cpus' was provided to the constructor, a "Measured CPU" container tab will
        be generated containing turbostat tabs which visualise turbostat data for the CPU under
        test.
        2. A "Totals" container tab will be generated containing turbostat tabs which
        visualise the turbostat system summaries.
        """

        l2_tabs = []
        for stab_bldr in self.l2tab_bldrs:
            l2_tabs.append(stab_bldr.get_tab())

        return _Tabs.CTabDC(self.name, l2_tabs)


    def __init__(self, stats_paths, outdir, measured_cpus=None):
        """
        The class constructor. Adding a turbostat statistics container tab will create a "Turbostat"
        sub-directory and store level 2 tabs inside it. Level 2 tabs will represent metrics stored
        in the raw turbostat statistics file using data tabs. Arguments are as follows:
         * stats_paths - dictionary in the format {'reportid': 'statistics_directory_path'}.
           This class will use these directories to locate raw turbostat statistic files.
         * outdir - the output directory in which to create the sub-directory for the turbostat tab.
         * measured_cpus - dictionary in the format {'reportid': 'measured_cpu'} where
                           'measured_cpu' is the CPU that was being tested during the workload. If
                           not provided, the "Measured CPU" tab will not be generated.
        """

        self.l2tab_bldrs = []

        if measured_cpus:
            self.l2tab_bldrs.append(_MCPUL2TabBuilder.MCPUL2TabBuilder(stats_paths,
                                                                       outdir / self.name,
                                                                       outdir, measured_cpus))

        self.l2tab_bldrs.append(_TotalsL2TabBuilder.TotalsL2TabBuilder(stats_paths,
                                                                       outdir / self.name, outdir))
