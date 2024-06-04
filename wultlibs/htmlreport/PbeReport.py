# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Adam Hawley <adam.james.hawley@intel.com>

"""This module provides API for generating HTML reports for pbe test results."""

import logging
from wultlibs import PbeDefs
from wultlibs.htmlreport import _ReportBase
from wultlibs.htmlreport import PbeReportParams
from wulttools.pbe import ToolInfo

_LOG = logging.getLogger()

class PbeReport(_ReportBase.ReportBase):
    """This module provides API for generating HTML reports for pbe test results."""

    def _get_acpower_cfg(self, def_acpower_cfg):
        """Customise the default 'AC Power' tab configuration to show 'WakePeriod' on plot axes."""

        new_plots = []
        for plot in def_acpower_cfg.scatter_plots:
            new_plots.append((self._wp_def, plot[1],))

        def_acpower_cfg.scatter_plots = new_plots
        return def_acpower_cfg

    def _get_tstat_dtab_cfg(self, dtab_cfg):
        """
        Customise the default 'turbostat' data tab configuration to show 'WakePeriod' on plot axes.
        """

        new_plots = []
        for plot in dtab_cfg.scatter_plots:
            plot = (self._wp_def, plot[1],)
            new_plots.append(plot)
        dtab_cfg.scatter_plots = new_plots
        dtab_cfg.set_hover_defs({})

    def _get_tstat_cfg(self, tab_cfg):
        """Customise the default 'Turbostat' tab configuration to show 'WakePeriod' on plot axes."""

        if hasattr(tab_cfg, "dtabs"):
            for dtab_cfg in tab_cfg.dtabs:
                self._get_tstat_dtab_cfg(dtab_cfg)

        if hasattr(tab_cfg, "ctabs"):
            for ctab_cfg in tab_cfg.ctabs:
                self._get_tstat_cfg(ctab_cfg)

        return tab_cfg

    def _get_ipmi_cfg(self, tab_cfg):
        """Customise the default 'IPMI' tab configuration to show 'WakePeriod' on plot axes."""

        for ctab_cfg in tab_cfg.ctabs:
            for dtab_cfg in ctab_cfg.dtabs:
                new_plots = []
                for plot in dtab_cfg.scatter_plots:
                    p = (self._wp_def, plot[1],)
                    new_plots.append(p)
                dtab_cfg.scatter_plots = new_plots
                dtab_cfg.set_hover_defs({})
        return tab_cfg

    def _get_pbe_cfgs(self):
        """Get the default 'pbe' statistics tab configurations."""

        def_tab_cfgs = self._stats_rep.get_default_tab_cfgs(self._stats_rsts)
        tab_cfgs = {}
        tab_cfgs["acpower"] = self._get_acpower_cfg(def_tab_cfgs["acpower"])
        tab_cfgs["turbostat"] = self._get_tstat_cfg(def_tab_cfgs["turbostat"])
        try:
            tab_cfgs["ipmi-oob"] = self._get_ipmi_cfg(def_tab_cfgs["ipmi-oob"])
        except KeyError:
            _LOG.debug("no 'ipmi-oob' data found so skipping 'ipmi' tab")

        return tab_cfgs

    def generate(self, tab_cfgs=None):
        """Override 'super().generate()' to customise the statistics tabs in the report."""

        self._load_results()
        for res in self.rsts:
            res.df["Time"] = res.df["Time"] - res.df["Time"].iloc[0]

        if tab_cfgs is None:
            tab_cfgs = self._get_pbe_cfgs()
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

        labels_defs = PbeDefs.PbeDefs()

        # The 'WakePeriod' metric definition is used to build tab configurations for custom
        # statistics tabs. Assign it to a class property here so that the name does not need to be
        # hard-coded in multiple places.
        self._wp_def = labels_defs.info["WakePeriod"]

        for res in rsts:
            stats_res = res.stats_res
            for stname in stats_res.info["stinfo"]:
                try:
                    stats_res.info["stinfo"][stname]["paths"]["labels"]
                except KeyError:
                    continue

                stats_res.set_label_defs(stname, labels_defs.info.values())

        super().__init__(rsts, outdir, ToolInfo.TOOLNAME, ToolInfo.VERSION,
                         report_descr=report_descr, xaxes=args["xaxes"], yaxes=args["yaxes"],
                         smry_funcs=PbeReportParams.SMRY_FUNCS, logpath=logpath)
