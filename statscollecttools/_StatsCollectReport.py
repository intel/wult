# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Adam Hawley <adam.james.hawley@intel.com>

"""
This module includes the "report" 'stats-collect' command implementation.
"""

from pepclibs.helperlibs import YAML
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.htmlreport import HTMLReport

def report_command(args):
    """Implements the 'report' command."""

    # Dictionary to reflecting 'info.yml' contents.
    infos = {}

    # Dictionary to reflecting 'datapoints.csv' contents.
    stats_paths = {}

    for respath in args.respaths:
        info_path = respath / "info.yml"
        if not info_path.is_file():
            raise Error(f"unable to open info file '{info_path}'")
        info_yml = YAML.load(info_path)

        reportid = info_yml.get("reportid", f"report-{len(infos)}")
        infos[reportid] = info_yml

        stats_path = respath / "stats"
        if not stats_path.is_dir():
            raise Error(f"unable to find statistics directory '{stats_path}'")
        stats_paths[reportid] = stats_path

    if not args.outdir:
        args.outdir = args.respaths[0] / "html-report"

    rep = HTMLReport.HTMLReport(args.outdir)
    rep.generate_report(stats_paths=stats_paths, title="stats-collect report")
