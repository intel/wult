# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
#          Adam James Hawley <adam.james.hawley@linux.intel.com>

"""This module contains miscellaneous functions used by various 'statscollecttools' modules."""

import logging
from pathlib import Path
from pepclibs.helperlibs import ProcessManager
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.htmlreport import HTMLReport
from statscollectlibs.htmlreport.tabs import _Tabs, FilePreviewBuilder

_LOG = logging.getLogger()

def get_pman(args):
    """
    Returns the process manager object for host 'hostname'. The returned object should either be
    used with a 'with' statement, or closed with the 'close()' method.
    """

    if args.hostname == "localhost":
        username = privkeypath = timeout = None
    else:
        username = args.username
        privkeypath = args.privkey
        timeout = args.timeout

    return ProcessManager.get_pman(args.hostname, username=username, privkeypath=privkeypath,
                                   timeout=timeout)

def _trim_file(srcpath, dstpath, top, bottom):
    """
    Helper function for 'generate_captured_output_tab()'. Copies the file at 'srcpath' to 'dstpath'
    and removes all but the top 'top' lines and bottom 'bottom' lines.
    """

    try:
        with open(srcpath, "r", encoding="utf-8") as f:
            lines = f.readlines()
            if len(lines) <= top + bottom:
                trimmed_lines = lines
            trimmed_lines = lines[:top] + lines[-bottom:]
    except OSError as err:
        msg = Error(err).indent(2)
        raise Error(f"unable to open captured output file at '{srcpath}':\n{msg}") from None

    try:
        dstpath.parent.mkdir(parents=True, exist_ok=True)
        with open(dstpath, "w", encoding="utf-8") as f:
            f.writelines(trimmed_lines)
    except OSError as err:
        msg = Error(err).indent(2)
        msg = f"unable to write trimmed captured output file at '{dstpath}':\n{msg}"
        raise Error(msg) from None

def generate_captured_output_tab(rsts, outdir):
    """Generate a container tab containing the output captured in 'stats-collect start'."""

    tab_title = "Captured Output"

    _LOG.info("Generating '%s' tab.", tab_title)

    files = {}
    for ftype in ("stdout", "stderr"):
        fp = rsts[0].info.get(ftype)

        if not fp or not all(((res.dirpath / fp).exists() for res in rsts)):
            continue

        srcfp = Path(fp)
        dstfp = srcfp.parent / f"trimmed-{srcfp.name}"
        for res in rsts:
            _trim_file(res.dirpath / srcfp, outdir / res.reportid / dstfp, 16, 32)
        files[ftype] = dstfp

    fpbuilder = FilePreviewBuilder.FilePreviewBuilder(outdir)
    fpreviews = fpbuilder.build_fpreviews({res.reportid: outdir / res.reportid for res in rsts},
                                          files)

    if not fpreviews:
        return None

    dtab = _Tabs.DTabDC(tab_title, fpreviews=fpbuilder.fpreviews)
    return _Tabs.CTabDC(tab_title, tabs=[dtab])

def generate_stc_report(rsts, outdir):
    """Generate a 'stats-collect' report from the results 'rsts' with 'outdir'."""

    rep = HTMLReport.HTMLReport(outdir)
    stats_paths = {res.reportid: res.stats_path for res in rsts}
    stdout_tab = generate_captured_output_tab(rsts, outdir)
    tabs = [stdout_tab] if stdout_tab else None
    rep.generate_report(tabs=tabs, stats_paths=stats_paths, title="stats-collect report")