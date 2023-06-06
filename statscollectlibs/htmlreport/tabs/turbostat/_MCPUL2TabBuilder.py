# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""
This module provides the capability of populating the "Measured CPU" turbostat level 2 tab.

Please, refer to '_TurbostatL2TabBuilderBase' for more information about level 2 tabs.
"""

from statscollectlibs.dfbuilders import TurbostatDFBuilder
from statscollectlibs.htmlreport.tabs.turbostat import _TurbostatL2TabBuilderBase

class MCPUL2TabBuilder(_TurbostatL2TabBuilderBase.TurbostatL2TabBuilderBase):
    """
    This class provides the capability of populating the "Measured CPU" turbostat level 2 tab.
    """

    name = "Measured CPU"

    def __init__(self, rsts, outdir, basedir):
        """
        The class constructor. Adding a "measured CPU" turbostat level 2 tab will create a
        "MeasuredCPU" sub-directory and store data tabs inside it for metrics stored in the raw
        turbostat statistics files for each measured CPU. Arguments are as follows:
         * rsts - a list of 'RORawResult' instances for which data should be included in the built
                  tab.
         * outdir - the output directory in which to create the sub-directory for the built tab.
         * basedir - base directory of the report. All asset paths will be made relative to this.
        """

        dfs = {}
        for res in rsts:
            if "turbostat" not in res.info["stinfo"]:
                continue

            cpunum = res.info.get("cpunum", None)
            if cpunum is None:
                continue

            mcpu = str(res.info["cpunum"])
            dfs[res.reportid] = res.load_stat("turbostat", TurbostatDFBuilder.MCPUDFBuilder(mcpu),
                                              "turbostat.raw.txt")

        super().__init__(dfs, outdir / self.name, basedir)
