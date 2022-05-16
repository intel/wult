# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module implements the base class for raw data provider classes.
"""

import logging
from pepclibs.helperlibs import ClassHelpers

_LOG = logging.getLogger()

class RawDataProviderBase:
    """
    The base class for raw data provider classes.
    """

    def __init__(self, dev, cpunum, pman, timeout=None, ldist=None, intr_focus=None,
                 early_intr=None):
        """
        Initialize a class instance for device 'dev'. The arguments are as follows.
          * dev - the device object created with 'Devices.WultDevice()'.
          * cpunum - the measured CPU number.
          * pman - the process manager object defining host to operate on.
          * timeout - the maximum amount of seconts to wait for a raw datapoint. Default is 10
                      seconds.
          * ldist - a pair of numbers specifying the launch distance range. The default value is
                    specific to the delayed event device.
          * intr_focus - enable inerrupt latency focused measurements ('WakeLatency' is not measured
                         in this case, only 'IntrLatency').
          * early_intr - enable intrrupts before entering the C-state.
        """

        self.dev = dev
        self._cpunum = cpunum
        self._pman = pman
        self._timoeut = timeout
        self._ldist = ldist
        self._intr_focus = intr_focus
        self._early_intr = early_intr

        if not timeout:
            self._timeout = 10

        msg = f"Using device '{self.dev.info['name']}'{pman.hostmsg}:\n" \
              f" * Device ID: {self.dev.info['devid']}\n" \
              f"   - {self.dev.info['descr']}"
        _LOG.info(msg)

    def close(self):
        """Uninitialize everything."""
        ClassHelpers.close(self, unref_attrs=("dev", "_pman"))

    def __enter__(self):
        """Enter the run-time context."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the runtime context."""
        self.close()
