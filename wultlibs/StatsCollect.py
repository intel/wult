# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module is just a "glue" layer between "WultRunner" and "STCAgent".
"""

import logging
from pepclibs.helperlibs import ClassHelpers
from pepclibs.helperlibs.Exceptions import Error, ErrorNotFound
from statscollectlibs.stcagentlibs import STCAgent, STCHelpers

_LOG = logging.getLogger()

STATS_NAMES = list(STCAgent.DEFAULT_STINFO)
STATS_INFO = STCAgent.DEFAULT_STINFO

def parse_stats(stnames, intervals):
    """Parse user-provided lists of statistics and intervals."""

    stconf = STCHelpers.parse_stnames(stnames)
    if intervals:
        STCHelpers.parse_intervals(intervals, stconf)

    return stconf

class StatsCollect(ClassHelpers.SimpleCloseContext):
    """
    The statistics collector class. Built on top of 'STCAgent', but simplifies the API a little bit
    for wult usage scenario.
    """

    def start(self):
        """Start collecting statistics."""

        _LOG.info("Starting statistics collectors")
        self._stcagent.start()

    def stop(self, sysinfo=True):
        """Stop collecting statistics."""

        _LOG.info("Stopping statistics collectors")
        self._stcagent.stop(sysinfo=sysinfo)

    def apply_stconf(self, stconf):
        """Configure the statistics according to the 'stconf' dictionary contents."""

        if stconf["discover"] or "acpower" in stconf["include"]:
            # Assume that power meter is configured to match the SUT name.
            if self._pman.is_remote:
                devnode = self._pman.hostname
            else:
                devnode = "default"

            try:
                self._stcagent.set_prop("acpower", "devnode", devnode)
            except ErrorNotFound:
                if not stconf["discover"]:
                    raise

        STCHelpers.apply_stconf(self._stcagent, stconf)
        _LOG.info("Configuring the following statistics: %s", ", ".join(stconf["include"]))
        self._stcagent.configure()

    def copy_stats(self):
        """Copy collected statistics and statistics log from remote SUT to the local system."""

        if not self._pman.is_remote:
            return

        loutdir, routdir = self._stcagent.get_outdirs()
        if not routdir:
            # No in-band statistics were collected, so nothing to copy.
            return

        _LOG.debug("copy in-band statistics from '%s:%s' to '%s'",
                   self._pman.hostname, routdir, loutdir)
        _LOG.info("Copying collected statistics from %s", self._pman.hostname)

        # We add trailing slash to the remote directory path in order to make rsync copy the
        # contents of the remote directory, but not the directory itself.
        self._pman.rsync(f"{routdir}/", loutdir, opts="rltD", remotesrc=True, remotedst=False)

        self._pman.rmtree(routdir)

    def __init__(self, pman, res, local_scpath=None, remote_scpath=None):
        """
        The class constructor. The arguments are as follows.
          * pman - the process manager object that defines the host to collect the statistics about.
          * res - the 'WORawResult' object to store the results at.
          * local_scpath - path to the 'stc-agent' python helper tool on the local system.
          * remote_scpath - path to the 'stc-agent' python helper tool on the remote system.
          """

        self._pman = pman
        self._stcagent = STCAgent.STCAgent(pman, local_outdir=res.dirpath,
                                                 local_scpath=local_scpath,
                                                 remote_scpath=remote_scpath)

    def close(self):
        """Close the statistics collector."""
        ClassHelpers.close(self, close_attrs=("_stcagent",), unref_attrs=("_pman",))
