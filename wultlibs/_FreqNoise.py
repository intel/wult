# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Tero Kristo <tero.kristo@linux.intel.com>

"""
This module provides a capability of inducing frequent CPU or uncore frequency scaling on the
measured system. On some platforms voltage and frequency scaling causes jitter, and the idea is to
try measuring this jitter by repeatedly driving CPU and uncore frequency up and down.
"""

from pepclibs.helperlibs import LocalProcessManager, ClassHelpers
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.helperlibs import ProcHelpers

class FreqNoise(ClassHelpers.SimpleCloseContext):
    """API to the frequency noise generator tool. See module documentation for more details."""

    def _build_cmdline(self, configs):
        """Build command line string to be passed to the 'wult-freq-helper'."""

        cmdline = ""

        for config in configs:
            ctype = config['type']

            if ctype in ("cpu", "uncore"):
                missing = None
                if 'id' not in config:
                    missing = 'id'
                if 'min' not in config:
                    missing = 'min'
                if 'max' not in config:
                    missing = 'max'

                if missing:
                    raise Error(f"expected '{missing}' in config for type '{ctype}'")
                cid = config['id']
                cmin = config['min']
                cmax = config['max']

                cmdline += f" -s {ctype}:{cid}:{cmin}:{cmax}"
            elif ctype == "sleep":
                if 'val' not in config:
                    raise Error(f"expected 'val' in config for type '{ctype}'")
                cval = config['val']
                cmdline += f" --sleep {cval}"
            else:
                raise Error(f"bad config type: '{ctype}', only 'uncore', 'cpu', 'sleep' supported")

        return cmdline

    def __init__(self, configs, pman=None):
        """
        The class constructor. The arguments are as follows.
          * configs - configuration array for the tool.
          * pman - the process manager object that defines the target host.
        """

        self._pman = pman
        self._fnh_proc = None
        self._fnh_cmdline = None

        if not configs:
            return

        self._fnh_cmdline = self._build_cmdline(configs)

        if not self._pman:
            self._pman = LocalProcessManager.LocalProcessManager()

    def start(self):
        """Start freq noise tool as a background process."""

        if not self._fnh_cmdline:
            return

        cmd = f"wult-freq-helper {self._fnh_cmdline}"
        self._fnh_proc = self._pman.run_async(cmd)

        # Make sure the process did not exit immediately.
        stdout, stderr, exitcode = self._fnh_proc.wait(timeout=1)
        if exitcode is not None:
            msg = self._fnh_proc.get_cmd_failure_msg(stdout, stderr, exitcode)
            raise Error(f"freq-noise tool failed to execute: {msg}{self._pman.hostmsg}")

    def stop(self):
        """Stop the freq noise tool background process."""

        if self._fnh_proc:
            ProcHelpers.kill_pids(self._fnh_proc.pid, kill_children=True, must_die=False,
                                  pman=self._pman)
            self._fnh_proc.close()
            self._fnh_proc = None

    def close(self):
        """Uninitialize the object."""

        self.stop()

        ClassHelpers.close(self, unref_attrs=("_pman",))
