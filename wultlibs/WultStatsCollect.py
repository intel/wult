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
from pepclibs.helperlibs.Exceptions import Error, ErrorNotFound
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

class WultStatsCollect(ClassHelpers.SimpleCloseContext):
    """
    The statistics collector class. Built on top of 'StatsCollect', but simplifies the API a little
    bit for wult usage scenario.
    """

    def start(self):
        """Start collecting statistics."""

        _LOG.info("Starting statistics collectors")
        self._stcoll.start()

    def stop(self, sysinfo=True):
        """Stop collecting statistics."""

        _LOG.info("Stopping statistics collectors")
        self._stcoll.stop(sysinfo=sysinfo)

    def apply_stconf(self, stconf):
        """Configure the statistics according to the 'stconf' dictionary contents."""

        if stconf["discover"] or "acpower" in stconf["include"]:
            # Assume that power meter is configured to match the SUT name.
            if self._pman.is_remote:
                devnode = self._pman.hostname
            else:
                devnode = "default"

            try:
                self._stcoll.set_prop("acpower", "devnode", devnode)
            except ErrorNotFound:
                if not stconf["discover"]:
                    raise

        StatsHelpers.apply_stconf(self._stcoll, stconf)
        _LOG.info("Configuring the following statistics: %s", ", ".join(stconf["include"]))
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
                   self._pman.hostname, self._routdir, self._loutdir)
        _LOG.info("Copying collected statistics from %s", self._pman.hostname)

        # We add trailing slash to the remote directory path in order to make rsync copy the
        # contents of the remote directory, but not the directory itself.
        self._pman.rsync(f"{routdir}/", self._loutdir, opts="rltD", remotesrc=True, remotedst=False)

        self._pman.rmtree(self._routdir)

    def __init__(self, pman, res, local_scpath=None, remote_scpath=None):
        """
        The class constructor. The arguments are as follows.
          * pman - the process manager object that defines the host to collect the statistics about.
          * res - the 'WORawResult' object to store the results at.
          * local_scpath - path to the 'stats-collect' python helper tool on the local system.
          * remote_scpath - path to the 'stats-collect' python helper tool on the remote system.
          """

        self._pman = pman
        self._stcoll = None
        # Local and remote output directories.
        self._loutdir = res.dirpath
        self._routdir = None

        # Create the local statistics collector data and log directories.
        try:
            self._loutdir.mkdir(exist_ok=True)
        except OSError as err:
            raise Error(f"failed to create directory '{self._loutdir}': {err}") from None

        self._routdir = self._pman.mkdtemp(prefix="wult-stats-collect-")

        self._stcoll = StatsCollect.StatsCollect(pman, local_outdir=self._loutdir.resolve(),
                                                 remote_outdir=self._routdir,
                                                 local_scpath=local_scpath,
                                                 remote_scpath=remote_scpath)

    def close(self):
        """Close the statistics collector."""
        ClassHelpers.close(self, close_attrs=("_stcoll",), unref_attrs=("_pman",))
