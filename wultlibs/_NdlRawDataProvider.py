# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module implements the "NdlRawDataProvider" class, which provides API for reading raw ndl
data.
"""

import logging
import contextlib
from pepclibs.helperlibs.Exceptions import Error
from wultlibs import _RawDataProvider
from wultlibs.helperlibs import ProcHelpers

_LOG = logging.getLogger()

class NdlRawDataProvider(_RawDataProvider.DrvRawDataProviderBase):
    """
    The raw data provider class implementation the ndl tool.
    """

    def _start_ndlrunner(self):
        """Start the 'ndlrunner' process on the measured system."""

        ldist_str = ",".join([str(val) for val in self._ldist])
        cmd = f"{self.ndlrunner_path} -l {ldist_str} "
        cmd += f"{self._ifname}"

        self.ndlrunner = self._pman.run_async(cmd)

    def _stop_ndlrunner(self):
        """Make 'ndlrunner' process to terminate."""

        _LOG.debug("stopping 'ndlrunner'")
        self.ndlrunner.stdin.write("q\n".encode("utf8"))
        self.ndlrunner.stdin.flush()

        _, _, exitcode = self.ndlrunner.wait(timeout=5)
        if exitcode is None:
            _LOG.warning("the 'ndlrunner' program PID %d%s failed to exit, killing it",
                         self.ndlrunner.pid, self._pman.hostmsg)
            ProcHelpers.kill_pids(self.ndlrunner.pid, kill_children=True, must_die=False,
                                  pman=self._pman)

    def start(self):
        """Start the  measurements."""
        self._start_ndlrunner()

    def stop(self):
        """Stop the  measurements."""
        self._stop_ndlrunner()

    def prepare(self):
        """Prepare to start the measurements."""

        # Unload the ndl driver if it is loaded.
        self._unload(everything=True)
        # Load the ndl driver.
        self._load()

        # Kill stale 'ndlrunner' process, if any.
        regex = f"^.*{self.ndlrunner_path} .*{self._ifname}.*$"
        ProcHelpers.kill_processes(regex, log=True, name="stale 'ndlrunner' process",
                                   pman=self._pman)

    def __init__(self, dev, ndlrunner_path, pman, timeout=None, ldist=None):
        """
        Initialize a class instance. The arguments are as follows.
          * dev - the device object created with 'Devices.GetDevice()'.
          * ndlrunner_path - path to the 'ndlrunner' helper.
          * pman - the process manager object defining host to operate on.
          * timeout - the maximum amount of seconds to wait for a raw datapoint. Default is 10
                      seconds.
          * ldist - a pair of numbers specifying the launch distance range.
        """

        drvinfo = {dev.drvname : {"params" : f"ifname={dev.netif.ifname}"}}
        super().__init__(dev, pman, drvinfo)

        self.ndlrunner_path = ndlrunner_path
        self._timeout = timeout
        self._ldist = ldist

        self.ndlrunner = None
        self._ifname = self.dev.netif.ifname

        if not timeout:
            self._timeout = 10

        # Validate the 'ndlrunner' helper path.
        if not self._pman.is_exe(self.ndlrunner_path):
            raise Error(f"bad 'ndlrunner' helper path '{self.ndlrunner_path}' - does not exist"
                        f"{self._pman.hostmsg} or not an executable file")

    def close(self):
        """Stop the measurements."""

        if getattr(self, "_ndlrunner", None):
            with contextlib.suppress(Error):
                self._stop_ndlrunner()
            self.ndlrunner = None

        super().close()
