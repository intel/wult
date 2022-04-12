# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module is just a "glue" layer between "WultRunner" and "StatsCollect".
"""

import logging
from pepclibs.helperlibs import ClassHelpers
from pepclibs.helperlibs.Exceptions import Error
from wultlibs.statscollectlibs import StatsCollect, StatsHelpers

_LOG = logging.getLogger()

STATS_NAMES = list(StatsCollect.DEFAULT_STINFO)
STATS_INFO = StatsCollect.DEFAULT_STINFO

def parse_stats(stnames, intervals):
    """Parse user-provided lists of statistics and intervals."""

    stconf = StatsHelpers.parse_stnames(stnames)
    if intervals:
        StatsHelpers.parse_intervals(intervals, stconf)

    return stconf

class WultStatsCollect:
    """
    The statistics collector class. Built on top of 'StatsCollect', but simplifies the API a little
    bit for wult usage scenario.
    """

    def start(self):
        """Start collecting statistics."""

        self._stcoll.start()

    def stop(self):
        """Stop collecting statistics."""

        self._stcoll.stop()

    def apply_stconf(self, stconf):
        """Configure the statistics according to the 'stconf' dictionary contents."""

        if stconf["discover"] or "acpower" in stconf["include"]:
            # Assume that power meter is configured to match the SUT name.
            if self._pman.is_remote:
                devnode = self._pman.hostname
            else:
                devnode = "default"
            self._stcoll.set_prop("acpower", "devnode", devnode)

        StatsHelpers.apply_stconf(self._stcoll, stconf)
        self._stcoll.configure()

    def copy_stats(self):
        """Copy collected statistics and statistics log from remote SUT to the local system."""

        if not self._pman.is_remote:
            return

        _, routdir = self._stcoll.get_outdirs()
        if not routdir:
            # No in-band statistics were collected, so nothing to copy.
            return

        _LOG.debug("copy in-band statistics from '%s:%s' to '%s'",
                   self._pman.hostname, routdir, self._outdir)

        # We add trailing slash to the remote directory path in order to make rsync copy the
        # contents of the remote directory, but not the directory itself.
        self._pman.rsync(f"{routdir}/", self._outdir, opts="rltD", remotesrc=True, remotedst=False)

    def __init__(self, pman, res):
        """
        The class constructor. The arguments are as follows.
          * pman - the process manager object that defines the host to collect the statistics about.
          * res - the 'WORawResult' object to store the results at.
          """

        self._pman = pman
        self._outdir = res.dirpath
        self._stcoll = None

        # Create the local statistics collector data and log directories.
        try:
            path = self._outdir
            path.mkdir(exist_ok=True)
        except OSError as err:
            raise Error(f"failed to create directory '{path}': {err}") from None

        self._stcoll = StatsCollect.StatsCollect(pman, local_outdir=self._outdir.resolve())

    def close(self):
        """Close the statistics collector."""
        ClassHelpers.close(self, unref_attrs=("_pman",), close_attrs=("_stcoll",))

    def __enter__(self):
        """Enter the run-time context."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the runtime context."""
        self.close()
