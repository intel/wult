# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023-2024 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Adam Hawley <adam.james.hawley@intel.com>

"""This module provides API for generating HTML reports for pbe test results."""

import logging
import pandas
from statscollectlibs.htmlreport.tabs import TabConfig
from wultlibs import PbeDefs
from wultlibs.htmlreport import _ReportBase
from wultlibs.htmlreport import PbeReportParams
from wulttools.pbe import ToolInfo

_LOG = logging.getLogger()

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

    def _compat_wake_period(self, rsts):
        """
        Versions of 'pbe' <= 0.2.0 used "Wake Period" as the metric to represent what is now
        known as "Launch Distance". Rename the "WakePeriod" column in 'rsts' to "LDist". Once
        support for v0.2.0 results is dropped, this method can be removed.
        """

        for res in rsts:
            wper_colname = "WakePeriod"
            ldist_colname = "LDist"
            colnames = list(pandas.read_csv(res.dp_path, nrows=0))

            # The initial release of 'pbe' was version 0.2.0, so only 1 version is affected.
            if res.info.get("toolver") != "0.2.0" or wper_colname not in colnames:
                continue

            _LOG.notice(f"renaming '{wper_colname}' to '{ldist_colname}' in the result at '%s'",
                        res.dp_path)
            res.metrics = []
            for colname in colnames:
                if colname == wper_colname:
                    res.metrics.append(ldist_colname)
                elif colname in res.defs.info:
                    res.metrics.append(colname)

            res.metrics_set = set(res.metrics)
            res.load_df()
            res.df.rename(columns={wper_colname: ldist_colname}, inplace=True)

        return rsts

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

        # The 'LDist' metric definition is used to build tab configurations for custom statistcs
        # tabs. Assign it to a class property here so that the name does not need to be hard-coded
        # in multiple places.
        self._wp_def = labels_defs.info["LDist"]

        for res in rsts:
            stats_res = res.stats_res
            if not stats_res:
                continue

            for stname in stats_res.info["stinfo"]:
                try:
                    stats_res.info["stinfo"][stname]["paths"]["labels"]
                except KeyError:
                    continue

                stats_res.set_label_defs(stname, labels_defs.info.values())

        rsts = self._compat_wake_period(rsts)

        super().__init__(rsts, outdir, ToolInfo.TOOLNAME, ToolInfo.VERSION,
                         report_descr=report_descr, xaxes=args["xaxes"], yaxes=args["yaxes"],
                         smry_funcs=PbeReportParams.SMRY_FUNCS, logpath=logpath)
