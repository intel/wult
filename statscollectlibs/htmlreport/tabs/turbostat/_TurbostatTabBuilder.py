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

from statscollectlibs.htmlreport.tabs import _Tabs
from statscollectlibs.htmlreport.tabs.turbostat import _MCPUL2TabBuilder, _TotalsL2TabBuilder

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


    def __init__(self, rsts, outdir):
        """
        The class constructor. Adding a turbostat statistics container tab will create a "Turbostat"
        sub-directory and store level 2 tabs inside it. Level 2 tabs will represent metrics stored
        in the raw turbostat statistics file using data tabs. Arguments are as follows:
         * rsts - a list of 'RORawResult' instances for different results with statistics which
                  should be included in the turbostat tabs.
         * outdir - the output directory in which to create the sub-directory for the turbostat tab.
        """

        self.l2tab_bldrs = []

        self.l2tab_bldrs.append(_MCPUL2TabBuilder.MCPUL2TabBuilder(rsts, outdir / self.name,
                                                                   outdir))

        self.l2tab_bldrs.append(_TotalsL2TabBuilder.TotalsL2TabBuilder(rsts, outdir / self.name,
                                                                       outdir))
