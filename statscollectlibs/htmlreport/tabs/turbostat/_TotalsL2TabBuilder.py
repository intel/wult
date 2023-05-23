# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022-2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""
This module provides the capability of populating the "Totals" turbostat level 2 tab.

Please, refer to '_TurbostatL2TabBuilderBase' for more information about level 2 tabs.
"""

from statscollectlibs.dfbuilders import TurbostatDFBuilder
from statscollectlibs.htmlreport.tabs.turbostat import _TurbostatL2TabBuilderBase

class TotalsL2TabBuilder(_TurbostatL2TabBuilderBase.TurbostatL2TabBuilderBase):
    """This class provides the capability of populating the "Totals" turbostat level 2 tab."""

    name = "Totals"

    def _read_stats_file(self, path):
        """
        Returns a 'pandas.DataFrame' containing the data stored in the raw turbostat statistics file
        at 'path'.
        """

        dfbldr = TurbostatDFBuilder.TotalsDFBuilder()
        dfbldr.load_df(path)
        return dfbldr.df

    def _get_tab_hierarchy(self, common_metrics):
        """
        Extends '_get_tab_hierarchy()' from the parent class to add tabs specifically for this
        level 2 turbostat tab as they are not added by 'super()._get_tab_hierarchy()'. Arguments are
        the same as 'super()._get_tab_hierarchy()'.
        """

        harchy = super()._get_tab_hierarchy(common_metrics)

        # Add extra metrics to the metrics in 'harchy' if they are common to all results.
        extra_dtabs = ["PkgWatt", "GFXWatt", "RAMWatt", "PkgTmp"]
        harchy["Temperature / Power"]["dtabs"] += [m for m in extra_dtabs if m in common_metrics]

        # Add uncore frequency D-tab to the "Frequency" C-tab.
        unc_metric = "UncMHz"
        if unc_metric in common_metrics:
            harchy["Frequency"]["dtabs"].append(unc_metric)

        # Add package C-states.
        hw_pkg_cs = self._get_common_cstates(self._cstates["hardware"]["package"])
        harchy["C-states"]["Hardware"]["dtabs"] += [csdef.metric for csdef in hw_pkg_cs]

        # Add module C-states.
        hw_mod_cs = self._get_common_cstates(self._cstates["hardware"]["module"])
        harchy["C-states"]["Hardware"]["dtabs"] += [csdef.metric for csdef in hw_mod_cs]

        return harchy

    def get_tab(self):
        """
        Extends 'super.get_tab()' to populate the descriptions with details on how metrics are
        summarised by turbostat.
        """

        self._defs.mangle_descriptions()
        return super().get_tab()

    def __init__(self, stats_paths, outdir, basedir):
        """
        The class constructor. Adding a "totals" turbostat level 2 tab will create a "Totals"
        sub-directory and store data tabs inside it for metrics stored in the raw turbostat
        statistics file. The arguments are the same as in
        '_TurbostatL2TabBuilderBase.TurbostatL2TabBuilderBase'.
        """

        super().__init__(stats_paths, outdir / self.name, basedir)
