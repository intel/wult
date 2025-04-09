# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023-2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Antti Laakso <antti.laakso@linux.intel.com>
#         Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""This module implements 'exercise-sut report' command."""

from pathlib import Path
from pepclibs.helperlibs import Logging, Trivial
from wulttools.exercisesut import _Common, _BatchReport

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.wult.{__name__}")

def report_command(args):
    """Implements the 'report' command."""

    if args.list_monikers:
        _Common.list_monikers()
        return

    if not args.respaths:
        _LOG.error_out("please, provide one or multiple paths to be searched for test results")

    with _BatchReport.BatchReport(args.respaths, dry_run=args.dry_run, jobs=args.jobs,
                                  toolpath=args.toolpath, toolopts=args.toolopts,
                                  ignore_errors=args.ignore_errors) as batchreport:
        outdir = args.outdir
        if not outdir:
            outdir = Path(f"{batchreport.toolpath.name}-results")

        diffs = []
        if args.diffs:
            for diff_csv_line in args.diffs:
                diff_monikers = Trivial.split_csv_line(diff_csv_line, dedup=True, keep_empty=True)
                diffs.append(diff_monikers)

        for outpath, respaths in batchreport.group_results(diffs=diffs, include=args.include,
                                                           exclude=args.exclude):
            batchreport.generate_report(respaths, outdir / outpath)
        batchreport.wait()
