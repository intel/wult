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
from pepclibs.helperlibs import ClassHelpers
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

    with pman.run_async(cmd) as proc:
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

class Runner(ClassHelpers.SimpleCloseContext):
    """
    This class provides the capability to execute a given command on a SUT and control the
    simultaneous collection of statistics.
    """

    def run(self, cmd, tlimit=None):
        """
        Run command 'cmd' and collect statistics about the SUT during command execution. Arguments
        are as follows:
         * cmd - the command to run on the SUT during statistics collection.
         * tlimit - the time limit to execute 'cmd' in seconds.
        """

        if self._stcoll:
            self._stcoll.start()

        stdout, stderr = run_command(cmd, self._pman, tlimit)

        if self._stcoll:
            self._stcoll.stop()
            self._stcoll.finalize()

        for ftype, txt in [("stdout", stdout,), ("stderr", stderr,)]:
            if not txt:
                continue
            fpath = self.res.logs_path / f"cmd-{ftype}.log.txt"
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(txt)
            self.res.info[ftype] = fpath.relative_to(self.res.dirpath)

        self.res.write_info()

    def __init__(self, res, pman, stcoll=None):
        """
        Class constructor. Arguments are as follows:
         * res - 'WORawResult' instance to store the results in.
         * pman - the process manager object that defines the host to run the measurements on.
         * stcoll - the 'StatsCollect' object to use for collecting statistics. No statistics
                    are collected by default.
        """

        self.res = res
        self._pman = pman
        self._stcoll = stcoll

    def close(self):
        """Close the runner."""
        ClassHelpers.close(self, unref_attrs=("_pman",))
