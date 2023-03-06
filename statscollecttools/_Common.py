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
from pepclibs.helperlibs import ProcessManager
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

def generate_captured_output_tab(rsts, outdir):
    """Generate a container tab containing the output captured in 'stats-collect start'."""

    tab_title = "Captured Output"

    _LOG.info("Generating '%s' tab.", tab_title)

    files = {}
    for ftype in ("stdout", "stderr"):
        fp = rsts[0].info.get(ftype)
        if fp:
            files[ftype] = fp

    fpbuilder = FilePreviewBuilder.FilePreviewBuilder(outdir)
    fpreviews = fpbuilder.build_fpreviews({res.reportid: res.dirpath for res in rsts}, files)

    if not fpreviews:
        return None

    dtab = _Tabs.DTabDC(tab_title, fpreviews=fpbuilder.fpreviews)
    return _Tabs.CTabDC(tab_title, tabs=[dtab])
