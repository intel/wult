# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module is just a "glue" layer between "WultRunner" and "StatsCollect".
"""

import logging
from pepclibs.helperlibs import ClassHelpers
from statscollectlibs.collector import StatsCollect, STCHelpers

_LOG = logging.getLogger()

STATS_NAMES = list(StatsCollect.DEFAULT_STINFO)
STATS_INFO = StatsCollect.DEFAULT_STINFO

def parse_stats(stnames, intervals):
    """Parse user-provided lists of statistics and intervals."""

    stconf = STCHelpers.parse_stnames(stnames)
    if intervals:
        STCHelpers.parse_intervals(intervals, stconf)

    return stconf

class WultStatsCollect(ClassHelpers.SimpleCloseContext):
    """
    The statistics collector class. Built on top of 'StatsCollect', but simplifies the API a little
    bit for wult usage scenario.
    """

    def set_stcagent_path(self, local_path=None, remote_path=None):
        """
        Confugure the 'stc-agent' program path. The arguments are as follows.
          * local_path - path to the 'stc-agent' program on the local system.
          * remote_path - path to the 'stc-agent' program on the remote system.
        """

        self._stcoll.set_stcagent_path(local_path=local_path, remote_path=remote_path)

    def get_enabled_stats(self):
        """Return the list of enabled statistic names."""

        return self._stcoll.get_enabled_stats()

    def set_prop(self, stname, name, value):
        """Set 'stname' statistic collector's property 'name' to value 'value'."""

        return self._stcoll.set_prop(stname, name, value)

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

        STCHelpers.apply_stconf(self._stcoll, stconf)
        _LOG.info("Configuring the following statistics: %s", ", ".join(stconf["include"]))
        self._stcoll.configure()

    def copy_stats(self):
        """Copy collected statistics and statistics log from remote SUT to the local system."""

        _LOG.info("Copying collected statistics from %s", self._pman.hostname)
        self._stcoll.copy_remote_data()

    def __init__(self, pman, outdir):
        """
        The class constructor. The arguments are as follows.
          * pman - the process manager object that defines the host to collect the statistics about.
          * outdir - path to the output directory.
          """

        self._pman = pman
        self._stcoll = StatsCollect.StatsCollect(pman, local_outdir=outdir)

    def close(self):
        """Close the statistics collector."""
        ClassHelpers.close(self, close_attrs=("_stcoll",), unref_attrs=("_pman",))
