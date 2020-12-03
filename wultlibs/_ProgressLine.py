# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2020 Intel Corporation
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

class ProgressLine:
    """This class implements the measurement progress line."""

    def start(self):
        """Start tracking the progress."""

        self._start_ts = self._last_ts = time.time()

    def update(self, dpcnt, maxlat, final=False):
        """
        Update the progress. The arguments are as follows.
          * dpcnt - how many datapoints were collected so far.
          * maxlat - the maximum latency value so far.
          * final - if 'True', all datapoints were collected and this is the last progress update.
        """

        if not self.enabled:
            return

        if final:
            if not self._printed:
                return
            end = "\n"
            self._printed = False
        else:
            if time.time() - self._last_ts < self.period:
                return
            end = ""

        self._last_ts = time.time()
        rate = dpcnt / (time.time() - self._start_ts)
        print(f"\rDatapoints: {dpcnt}, max. latency: {maxlat} ns, "
              f"rate: {rate:.2f} datapoints/sec\r", end=end, flush=True)
        self._printed = True

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

        if _LOG.getEffectiveLevel() > logging.INFO or not sys.stdout.isatty():
            self.enabled = False
        else:
            self.enabled = True
