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

    def _read_stats_file(self, path):
        """
        Returns a 'pandas.DataFrame' containing the data stored in the raw turbostat statistics file
        at 'path'.
        """

        dfbldr = TurbostatDFBuilder.MCPUDFBuilder(self._statdir_to_mcpu[path.parent])
        dfbldr.load_df(path)
        return dfbldr.df

    def __init__(self, rsts, outdir, basedir):
        """
        The class constructor. Adding a "measured CPU" turbostat level 2 tab will create a
        "MeasuredCPU" sub-directory and store data tabs inside it for metrics stored in the raw
        turbostat statistics files for each measured CPU. The arguments are the same as in
        '_TurbostatL2TabBuilder.TurbostatL2TabBuilder'.
        """

        self._statdir_to_mcpu = {}
        for res in rsts:
            if "cpunum" in res.info:
                self._statdir_to_mcpu[res.stats_path] = str(res.info["cpunum"])

        super().__init__(rsts, outdir / self.name, basedir)
