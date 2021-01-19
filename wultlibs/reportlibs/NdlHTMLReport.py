# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2020 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Vladislav Govtva <vladislav.govtva@intel.com>
#          Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module provides API for generating HTML reports for ndl test results.
"""

from wultlibs.reportlibs import _HTMLReportBase
from wultlibs.helperlibs import Trivial

DEFAULT_XAXES = "LDist"
DEFAULT_YAXES = DEFAULT_HIST = DEFAULT_CHIST = "RTD"

class NdlHTMLReport(_HTMLReportBase.HTMLReportBase):
    """This module provides API for generating HTML reports for ndl test results."""

    def _mangle_loaded_res(self, res):
        """
        Drop 'res.df' dataframe columns corresponding to C-states with no residency. Presumably this
        C-state was either disabled or just does not exist.
        """

        for colname in res.df:
            if colname not in self._cs_colnames:
                continue
            # Drop the corresponding C-state percentage column if no CPU cycles were spent in
            # it.
            if not res.df[colname].any():
                res.df.drop(colname, axis="columns", inplace=True)

        return super()._mangle_loaded_res(res)

    def __init__(self, rsts, outdir, title_descr=None, xaxes=None, yaxes=None, hist=None,
                 chist=None):
        """The class constructor. The arguments are the same as in 'HTMLReportBase()'."""

        args = {"xaxes": xaxes, "yaxes": yaxes, "hist": hist, "chist": chist}

        for name, default in zip(args, (DEFAULT_XAXES, DEFAULT_YAXES, DEFAULT_HIST, DEFAULT_CHIST)):
            if not args[name]:
                args[name] = default.split(",")

        super().__init__(rsts, outdir, title_descr=title_descr, xaxes=args["xaxes"],
                         yaxes=args["yaxes"], hist=args["hist"], chist=args["chist"])

        # Column names representing C-state residency.
        self._cs_colnames = set()

        for res in rsts:
            for colname in res.defs.get_csres_colnames():
                # Form the list of column names representing C-state residency. We'll need to load
                # them in order to detect C-states with no residency.
                self._cs_colnames.add(colname)
                self._more_colnames.append(colname)

        self._more_colnames = Trivial.list_dedup(self._more_colnames)
