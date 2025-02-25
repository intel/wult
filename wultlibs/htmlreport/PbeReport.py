# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023-2024 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Adam Hawley <adam.james.hawley@intel.com>

"""This module provides API for generating HTML reports for pbe test results."""

from pepclibs.helperlibs import Logging
from statscollectlibs.htmlreport.tabs import TabConfig
from wultlibs import PbeMDC
from wultlibs.htmlreport import _ReportBase
from wultlibs.htmlreport import PbeReportParams
from wulttools.pbe import ToolInfo

_LOG = Logging.getLogger(f"wult.{__name__}")

class PbeReport(_ReportBase.ReportBase):
    """This module provides API for generating HTML reports for pbe test results."""

    def _customise_dtab_cfg(self, dtab_cfg):
        """Customise the data tab configuration 'dtab_cfg' to show 'LDist' on plot axes."""

        new_plots = []
        for plot in dtab_cfg.scatter_plots:
            plot = (self._wp_def, plot[1],)
            new_plots.append(plot)

        dtab_cfg.scatter_plots = new_plots
        dtab_cfg.set_hover_defs({})

    def _customise_tab_cfg(self, tab_cfg):
        """
        Customise the tab configuration 'tab_cfg' to show 'LDist' on plot axes. Recurse through
        all C-tabs and D-tabs to customise their configurations.
        """

        if isinstance(tab_cfg, TabConfig.DTabConfig):
            self._customise_dtab_cfg(tab_cfg)
            return tab_cfg

        if hasattr(tab_cfg, "dtabs"):
            for dtab_cfg in tab_cfg.dtabs:
                self._customise_dtab_cfg(dtab_cfg)

        if hasattr(tab_cfg, "ctabs"):
            for ctab_cfg in tab_cfg.ctabs:
                self._customise_tab_cfg(ctab_cfg)

        return tab_cfg

    def _get_stats_tab_cfgs(self):
        """
        Get the 'pbe' statistics tab configurations. These configurations are based on the default
        tab configuraions provided by 'stats-collect' but they are customised to show 'LDist' on
        the X-axes of plots in the data tabs.
        """

        pbe_cfg = {}
        for stname, tab_cfg in self._stats_rep.get_default_tab_cfgs(self._stats_rsts).items():
            pbe_cfg[stname] = self._customise_tab_cfg(tab_cfg)

        return pbe_cfg

    def generate(self, tab_cfgs=None):
        """
        Override 'super().generate()' to customise the statistics tabs in the report. Arguments are
        the same as in 'wultlibs.htmlreport._ReportBase.ReportBase()'.
        """

        self._load_results()
        for res in self.rsts:
            res.df["Time"] = res.df["Time"] - res.df["Time"].iloc[0]

        if tab_cfgs is None:
            tab_cfgs = self._get_stats_tab_cfgs()
        return super().generate(tab_cfgs)

    def __init__(self, rsts, outdir, report_descr=None, xaxes=None, yaxes=None, logpath=None):
        """
        The class constructor. The arguments are the same as in
        'wultlibs.htmlreport._ReportBase.ReportBase()'.
        """

        args = {"xaxes": xaxes, "yaxes": yaxes}

        for name, default in zip(args, (PbeReportParams.DEFAULT_XAXES,
                                        PbeReportParams.DEFAULT_YAXES)):
            if not args[name]:
                args[name] = default.split(",")

        labels_mdo = PbeMDC.PbeMDC()

        # The 'LDist' metric definition is used to build tab configurations for custom statistics
        # tabs. Assign it to a class property here so that the name does not need to be hard-coded
        # in multiple places.
        self._wp_def = labels_mdo.mdd["LDist"]

        for res in rsts:
            stats_res = res.stats_res
            if not stats_res:
                continue

            for stname in stats_res.info["stinfo"]:
                try:
                    stats_res.info["stinfo"][stname]["paths"]["labels"]
                except KeyError:
                    continue

                stats_res.set_label_defs(stname, labels_mdo.mdd.values())

        super().__init__(rsts, outdir, ToolInfo.TOOLNAME, ToolInfo.VERSION,
                         report_descr=report_descr, xaxes=args["xaxes"], yaxes=args["yaxes"],
                         smry_funcs=PbeReportParams.SMRY_FUNCS, logpath=logpath)
