# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Vladislav Govtva <vladislav.govtva@intel.com>
#          Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module provides API for generating HTML reports for ndl test results.
"""

from wultlibs.htmlreport import _ReportBase
from wultlibs.htmlreport import NdlReportParams

class NdlReport(_ReportBase.ReportBase):
    """This module provides API for generating HTML reports for ndl test results."""

    def __init__(self, rsts, outdir, title_descr=None, xaxes=None, yaxes=None, hist=None,
                 chist=None):
        """The class constructor. The arguments are the same as in 'HTMLReportBase()'."""

        args = {"xaxes": xaxes, "yaxes": yaxes, "hist": hist, "chist": chist}

        for name, default in zip(args, (NdlReportParams.DEFAULT_XAXES,
                                        NdlReportParams.DEFAULT_YAXES,
                                        NdlReportParams.DEFAULT_HIST,
                                        NdlReportParams.DEFAULT_CHIST)):
            if not args[name]:
                args[name] = default.split(",")

        super().__init__(rsts, outdir, title_descr=title_descr, xaxes=args["xaxes"],
                         yaxes=args["yaxes"], hist=args["hist"], chist=args["chist"],
                         smry_funcs=NdlReportParams.SMRY_FUNCS)
