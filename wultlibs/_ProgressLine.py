# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module implements the measurement progress line.
"""

import sys
import time
import logging

_LOG = logging.getLogger()

class _ProgressLineBase:
    """This the base class for tool-specific progress line classes."""

    def start(self):
        """Start tracking the progress."""

        self._start_ts = self._last_ts = time.time()

    def get_duration(self):
        """Returns the overall measurements duration in seconds."""
        return time.time() - self._start_ts

    def _update(self, final, time_now=None):
        """
        The common part of the 'update()' method. Returns 'True' if the progress line update is
        needed, returns 'fals otherwise.
        """

        if not self.enabled:
            return False

        if final:
            if not self._printed:
                return False
            self._end = "\n"
            self._printed = False
        else:
            if time_now is None:
                time_now = time.time()
            if time_now - self._last_ts < self.period:
                return False
            self._end = ""

        return True

    def __init__(self, period=1):
        """
        The class constructor. The arguments are as follows.
          * period - how often the progress should be updated, seconds.
        """

        self.period = period
        self.enabled = None

        # Time when progress was last updated.
        self._last_ts = None
        # Time when the measurements have started.
        self._start_ts = None
        # Whether progress information was printed at least once.
        self._printed = False
        # The ending of the progress line (empty line or '\n' for the final print).
        self._end = ""

        if _LOG.getEffectiveLevel() > logging.INFO or not sys.stdout.isatty():
            self.enabled = False
        else:
            self.enabled = True

class WultProgressLine(_ProgressLineBase):
    """
    Wult tool progress line.
    """

    def update(self, dpcnt, maxlat, final=False):
        """
        Update the progress. The arguments are as follows.
          * dpcnt - how many datapoints were collected so far.
          * maxlat - the maximum latency value so far.
          * final - if 'True', all datapoints were collected and this is the last progress update.
        """

        time_now = time.time()
        if not self._update(final, time_now):
            return

        self._last_ts = time_now
        rate = dpcnt / (self._last_ts - self._start_ts)
        print(f"\rDatapoints: {dpcnt}, max. latency: {maxlat:.2f} us, "
              f"rate: {rate:.2f} datapoints/sec", end=self._end, flush=True)

        self._printed = True
        self.dpcnt = dpcnt
        self.maxlat = maxlat

    def __init__(self, period=1):
        """
        The class constructor. The arguments are the same as in '_ProgressLineBase().__init__()'.
        """

        super().__init__(period=period)

        # Last printed datapoints count.
        self.dpcnt = 0
        # Last printed latency.
        self.maxlat = 0

class NdlProgressLine(WultProgressLine):
    """
    Ndl tool progress line (same as 'wult' tool progress line).
    """
