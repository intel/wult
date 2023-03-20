# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022-2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
#          Adam Hawley <adam.james.hawley@intel.com>

"""
This module provides the capability to execute a given command on a SUT and control the simultaneous
collection of statistics.
"""

import logging
from statscollectlibs.helperlibs import ProcHelpers

_LOG = logging.getLogger()

def run_command(cmd, pman, tlimit):
    """Run the command."""

    _LOG.info("Running the following command%s: %s", pman.hostmsg, cmd)

    if not tlimit:
        run_forever = True
        tlimit = 4 * 60 * 60
    else:
        run_forever = False

    proc = pman.run_async(cmd)

    while True:
        stdout, stderr, exitcode = proc.wait(timeout=tlimit)
        if exitcode is not None:
            break

        if run_forever:
            continue

        _LOG.notice("statistics collection stopped because the time limit was reached before "
                    "the command finished executing.")
        ProcHelpers.kill_pids(proc.pid, kill_children=True, must_die=True, pman=pman)

    return stdout, stderr
