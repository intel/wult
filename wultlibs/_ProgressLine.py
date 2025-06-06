# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
Provide an API for displaying measurement progress line.
"""

from __future__ import annotations # Remove when switching to Python 3.10+.

import sys
import time
from pepclibs.helperlibs import Logging
from wultlibs.helperlibs import Human

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.wult.{__name__}")

class _ProgressLineBase:
    """Base class for progress line implementations used by specific tools."""

    def __init__(self, period: float = 1):
        """
        Initialize a class instance.

        Args:
            period: Interval in seconds between progress updates.

        Disable progress updates if the logging level is higher than INFO.
        """

        self.period = period
        self.enabled = True
        self._isatty = sys.stdout.isatty()

        # Time when progress was last updated.
        self._last_ts = 0.0
        # Time when the measurements have started.
        self._start_ts = 0.0
        # Whether progress information was printed at least once.
        self._printed = False
        # The ending of the progress line (empty line or '\n' for the final print).
        self._end = ""
        # Saved logger prerix.
        self._prefix = ""

        if _LOG.getEffectiveLevel() > Logging.INFO:
            self.enabled = False

    def start(self):
        """Begin tracking the progress line."""

        # Make sure logging message are prefixed with a newline. E.g., if there is a warning, it
        # starts with a new line.
        # TODO: needed only in case of "\r"
        main_logger = Logging.getLogger(Logging.MAIN_LOGGER_NAME)

        self._prefix = main_logger.prefix
        main_logger.set_prefix(f"\n{self._prefix}")

        self._start_ts = self._last_ts = time.time()

    def get_duration(self):
        """Return the total duration of the measurements in seconds."""

        return time.time() - self._start_ts

    def _update(self, final: bool, time_now: float | None = None) -> bool:
        """
        Determine if the progress line should be updated.

        Args:
            final: Whether this is the final update.
            time_now: The current time, or None to use the current system time.

        Returns:
            bool: True if the progress line should be updated, False otherwise.
        """

        if not self.enabled:
            return False

        if final:
            Logging.getLogger(Logging.MAIN_LOGGER_NAME).set_prefix(self._prefix)
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

class WultProgressLine(_ProgressLineBase):
    """
    Progress line class for the Wult tool.
    """

    def __init__(self, period=1):
        """
        The class constructor.
        """

        super().__init__(period=period)

        # Last printed datapoints count.
        self.dpcnt = 0
        # Last printed latency.
        self.maxlat = 0

    def update(self, dpcnt: int, maxlat: float, final: bool = False):
        """
        Update the progress line with the current datapoint count and maximum latency.

        Args:
            dpcnt: Number of datapoints collected so far.
            maxlat: Maximum latency value observed so far (in microseconds).
            final: Set to True for the final progress update after all datapoints are collected.
        """

        time_now = time.time()
        if not self._update(final, time_now):
            return

        self._last_ts = time_now
        rate = dpcnt / (self._last_ts - self._start_ts)

        msg = f"Datapoints: {dpcnt}, max. latency: {maxlat:.2f} us, rate: {rate:.2f} datapoints/sec"

        # Overwrite the previous progress line when printing to a terminal or if the logger uses
        # colored output. Assume that the logger is connected to the same output stream as
        # 'print()', and assume that if the output is colored, it is either a terminal or
        # intentionally treated as a terminal.
        if self._isatty or _LOG.colored:
            print("\r" + msg, end=self._end, flush=True)
        else:
            print(msg, flush=True)

        self._printed = True
        self.dpcnt = dpcnt
        self.maxlat = maxlat

class NdlProgressLine(WultProgressLine):
    """
    Progress line class for the ndl tool.
    """

class PbeProgressLine(_ProgressLineBase):
    """
    Progress line class for the pbe tool.
    """

    def __init__(self):
        """
        The class constructor.
        """

        super().__init__(period=1)

        # Last printed launch distance.
        self.ldist = None

    NSEC_PER_SEC = 1000000000

    def update(self, ldist: int):
        """
        Update the progress line with the current launch distance.

        Args:
            ldist: Current measured launch distance in nanoseconds.
        """

        time_now = time.time()
        if not self._update(False, time_now):
            return

        hldist = Human.num2si(ldist, unit="ns")
        rate = int(self.NSEC_PER_SEC / ldist)
        duration = Human.duration(self.get_duration())

        msg = f"Tot. time: {duration}, ldist: {hldist} ({rate} intr/s)"
        if self._isatty or _LOG.colored:
            print("\r" + msg, end=self._end, flush=True)
        else:
            print(msg, flush=True)

        self._printed = True
        self.ldist = ldist
