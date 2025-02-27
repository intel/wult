# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module provides API for managing the 'pbe' driver and reading raw PBE datapoints.
"""

from pepclibs.helperlibs import Logging
from wultlibs import _RawDataProvider

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.wult.{__name__}")

class PbeRawDataProvider(_RawDataProvider.DrvRawDataProviderBase):
    """
    This class provides API for managing the 'pbe' driver and reading raw PBE datapoints.
    """

    def set_ldist(self, ldist):
        """Change launch distance to 'ldist'."""

        with self._pman.open(self._basedir / "ldist_nsec", "w") as fobj:
            fobj.write(f"{ldist}")

    def start(self):
        """Start the measurements."""

        with self._pman.open(self._enable_path, "w") as fobj:
            fobj.write("1")

        self.started = True

    def stop(self):
        """Stop the measurements."""

        with self._pman.open(self._enable_path, "w") as fobj:
            fobj.write("0")

        self.started = False

    def prepare(self):
        """Prepare to start the measurements."""

        super().prepare()
        super()._load_driver()

    def __init__(self, dev, pman, ldist, timeout=None, lcpu=0):
        """
        Initialize a class instance. The arguments are as follows.
          * dev - the device object created with 'Devices.GetDevice()'.
          * pman - the process manager object defining host to operate on.
          * ldist - a pair of numbers specifying the launch distance range in nanoseconds.
          * timeout - the maximum amount of seconds to wait for a raw datapoint. Default is 10
                      seconds.
          * lcpu - the lead CPU. This CPU will set timers and trigger interrupts to wake all other
                   CPUs. By default, uses CPU 0.
        """

        drvinfo = {dev.drvname: {"params": f"cpunum={lcpu}"}}
        super().__init__(dev, pman, ldist, drvinfo=drvinfo, timeout=timeout)

        self.started = False

        self._basedir = self.debugfs_mntpoint / "pbe"
        self._enable_path = self._basedir / "enabled"
