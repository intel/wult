# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023-2024 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Adam Hawley <adam.james.hawley@intel.com>

"""This module provides API for generating HTML reports for pbe test results."""

from pepclibs.helperlibs import Logging
from statscollectlibs.result import LoadedResult
from statscollectlibs.htmlreport import HTMLReport
from wultlibs import PbeMDC
from wultlibs.htmlreport import _ReportBase
from wultlibs.htmlreport import PbeReportParams
from wulttools.pbe import ToolInfo

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.wult.{__name__}")

class PbeReport(_ReportBase.ReportBase):
    """This module provides API for generating HTML reports for pbe test results."""

    def generate(self):
        """
        Override 'super().generate()' to customise the statistics tabs in the report. Arguments are
        the same as in 'wultlibs.htmlreport._ReportBase.ReportBase()'.
        """

        self._load_results()
        for res in self.rsts:
            res.df["Time"] = res.df["Time"] - res.df["Time"].iloc[0]

        return super().generate()

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

        mdo = PbeMDC.PbeMDC()

        stats_lrsts: list[LoadedResult.LoadedResult] = []
        for res in rsts:
            if not res.stats_lres:
                continue
            res.stats_lres.set_ldd(mdo.mdd)
            stats_lrsts.append(res.stats_lres)

        # TODO: I see inconsistency: in some places res.info["toolname"] is used, in others
        # 'ToolInfo.TOOLNAME' is used. Similar for tool version. Should be cleaned up.
        title = f"{ToolInfo.TOOLNAME} Report",
        stats_rep = HTMLReport.HTMLReport(stats_lrsts, title, outdir,
                                          logpath=logpath, descr=report_descr,
                                          toolname=ToolInfo.TOOLNAME, toolver=ToolInfo.VERSION,
                                          xmetric="LDist")

        # TODO: the "xaxes" and "yaxes" do not seem to be relevant to pbe. Somehow rework this.
        super().__init__(rsts, outdir, ToolInfo.TOOLNAME, ToolInfo.VERSION,
                         report_descr=report_descr, stats_rep=stats_rep, xaxes=args["xaxes"],
                         yaxes=args["yaxes"], smry_funcs=PbeReportParams.SMRY_FUNCS,
                         logpath=logpath)
