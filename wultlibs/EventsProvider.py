# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2020 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module implements the "EventsProvider" class, which provides an easy to use API to discover,
load, and use various delayed event devices and drivers (e.g., the I210 network card).
"""

import logging
import contextlib
from wultlibs.helperlibs import FSHelpers, KernelModule, Trivial
from wultlibs.helperlibs.Exceptions import Error
from wultlibs import Devices

_LOG = logging.getLogger()

class EventsProvider:
    """
    This class provides an easy to use API for using the kernel wult framework: finding and loading
    delayed event provider drivers, starting the measurements, etc.
    """

    def _unload(self):
        """Unload all the previously loaded wult kernel drivers."""

        # Unload all the possible wult device drivers.
        for drvname in Devices.DRVNAMES:
            drv = KernelModule.KernelModule(self._proc, drvname)
            drv.unload()
            drv.close()

        self._main_drv.unload()

    def _load(self): # pylint: disable=arguments-differ
        """Load all the necessary Linux drivers."""

        # Load the main driver ('wult').
        self._main_drv.load(opts=f"cpunum={self._cpunum}")

        # Load the delayed event driver ('wult').
        try:
            self._drv.load()
        except Error:
            try:
                self._main_drv.unload()
            except Error as err1:
                _LOG.warning("failed to unload module '%s'%s:\n%s", self._main_drv.name,
                             self._proc.hostmsg, err1)
            raise

    def start(self):
        """Start the latency measurements."""

        # Sanity check.
        if not FSHelpers.exists(self._enable_path, proc=self._proc):
            raise Error(f"path {self._enable_path} does not exist{self._proc.hostmsg}")

        self._proc.run_verify(f"echo 1 > {self._enable_path}", shell=True)

    def _set_launch_distance(self):
        """Set launch distance limits to driver."""

        try:
            limit_path = self._basedir / "ldist_max_nsec"
            with self._proc.open(limit_path, "r") as fobj:
                ldist_max = fobj.read().strip()

            limit_path = self._basedir / "ldist_min_nsec"
            with self._proc.open(limit_path, "r") as fobj:
                ldist_min = fobj.read().strip()
        except Error as err:
            raise Error(f"failed to read launch distance limit from '{limit_path}'"
                        f"{self._proc.hostmsg}:\n{err}")

        ldist_min = Trivial.str_to_num(ldist_min)
        ldist_max = Trivial.str_to_num(ldist_max)
        from_path = self._basedir / "ldist_from_nsec"
        to_path = self._basedir / "ldist_to_nsec"

        for ldist, ldist_path in zip(self._ldist, [from_path, to_path]):
            if ldist < ldist_min or ldist > ldist_max:
                raise Error(f"launch distance '{ldist}' is out of range, it should be in range of "
                            f"[{ldist_min},{ldist_max}]")
            if not FSHelpers.exists(ldist_path, proc=self._proc):
                raise Error(f"path i'{ldist_path}' does not exist{self._proc.hostmsg}")
            # open()/write() doesn't work for this file when done over SSH.
            self._proc.run_verify(f"echo {ldist} > {ldist_path}", shell=True)

    def get_resolution(self):
        """Returns resolution of the delayed event devices in nanoseconds."""

        try:
            path = self._basedir / "resolution_nsec"
            with self._proc.open(path, "r") as fobj:
                resolution = fobj.read().strip()
        except Error as err:
            raise Error(f"failed to read the delayed event reslolution from '{path}'"
                        f"{self._proc.hostmsg}:\n{err}")

        return Trivial.str_to_num(resolution)

    def prepare(self):
        """Prepare to start the measurements."""

        self._main_drv.dmesg = self.dmesg
        self._drv.dmesg = self.dmesg
        self.dev.dmesg = self.dmesg

        # Unload wult drivers if they were loaded.
        self._unload()

        # Unbind the wult delayed event device from its current driver, if any.
        self._saved_drvname = self.dev.unbind()
        if self._saved_drvname:
            if self.unload:
                word = "Temporarily unbinded"
            else:
                word = "Unbinded"
            _LOG.info("%s device '%s' from driver '%s'",
                      word, self.dev.info["devid"], self._saved_drvname)

        # Load wult drivers.
        self._load()

        # Bind the delayed event device to its wult driver.
        _LOG.info("Binding device '%s' to driver '%s'",
                  self.dev.info["devid"], self.dev.drvname)
        self.dev.bind(self.dev.drvname)

        if self._ldist:
            self._set_launch_distance()

    def close(self):
        """Uninitialize everything (unload kernel drivers, etc)."""

        if getattr(self, "_proc", None):
            self._proc = None
        else:
            return

        if self.unload:
            if getattr(self, "_drv", None):
                with contextlib.suppress(Error):
                    self._drv.unload()

            if getattr(self, "_main_drv", None):
                with contextlib.suppress(Error):
                    self._main_drv.unload()

            # Bind the device back to the original driver.
            saved_drvname = getattr(self, "_saved_drvname", None)
            if saved_drvname and saved_drvname != self.dev.drvname:
                _LOG.info("Binding device '%s' back to driver '%s'",
                          self.dev.info["devid"], self._saved_drvname)
                try:
                    self.dev.bind(self._saved_drvname)
                except Error as err:
                    _LOG.error("failed to bind device '%s' back to driver '%s':\n %s",
                               self.dev.info["devid"], self._saved_drvname, err)

    def __init__(self, devid, cpunum, proc, ldist=None, force=False):
        """
        Initialize a class instance for a PCI device 'devid'. The arguments are as follows.
          * devid - the device "ID", which can be a PCI address or a network interface name.
          * cpunum - the measured CPU number.
          * proc - the host to operate on. This object will keep a 'proc' reference and use it in
                   various methods
          * ldist - a pair of numbers specifying the launch distance range. The default value is
                    specific to the delayed event driver.
          * force - initialize measurement device, even if it is already in use.
        """

        self._cpunum = cpunum
        self._proc = proc
        self._ldist = ldist
        self._drv = None
        self._saved_drvname = None
        self.dev = None
        self._basedir = None
        self._enable_path = None
        self._main_drv = None

        # This is a debugging option that allows to disable automatic wult modules unloading on
        # 'close()'.
        self.unload = True
        # Whether kernel messages should be monitored. They are very useful if something goes wrong.
        self.dmesg = True

        self.dev = Devices.WultDevice(devid, cpunum, proc, force=force)

        self._main_drv = KernelModule.KernelModule(proc, "wult")
        self._drv = KernelModule.KernelModule(proc, self.dev.drvname)

        mntpoint = FSHelpers.mount_debugfs(proc=proc)
        self._basedir = mntpoint / "wult"
        self._enable_path = self._basedir /"enabled"

        msg = f"Compatible device '{self.dev.info['name']}'{proc.hostmsg}:\n" \
              f" * Device ID: {self.dev.info['devid']}\n" \
              f"   - {self.dev.info['descr']}"
        _LOG.info(msg)

    def __enter__(self):
        """Enter the run-time context."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the runtime context."""
        self.close()
