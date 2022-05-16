# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module implements the "WultEventsProvider" class, which provides API to discover, load, and use
various wult delayd event devices and drivers (e.g., the I210 network card).
"""

import logging
import contextlib
from pepclibs.helperlibs import KernelModule, Trivial, ClassHelpers
from pepclibs.helperlibs.Exceptions import Error
from wultlibs.helperlibs import FSHelpers
from wultlibs import Devices

_LOG = logging.getLogger()

class _EventsProviderBase:
    """
    The base class for wult events provider classes.
    """

    def __init__(self, dev, cpunum, pman, ldist=None, intr_focus=None, early_intr=None):
        """
        Initialize a class instance for device 'dev'. The arguments are as follows.
          * dev - the delayed event device object created with 'Devices.WultDevice()'.
          * cpunum - the measured CPU number.
          * pman - the process manager object defining host to operate on.
          * ldist - a pair of numbers specifying the launch distance range. The default value is
                    specific to the delayed event driver.
          * intr_focus - enable inerrupt latency focused measurements ('WakeLatency' is not measured
                         in this case, only 'IntrLatency').
          * early_intr - enable intrrupts before entering the C-state.
        """

        self.dev = dev
        self._cpunum = cpunum
        self._pman = pman
        self._ldist = ldist
        self._intr_focus = intr_focus
        self._early_intr = early_intr

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


class _DrvEventsProvider(_EventsProviderBase):
    """
    The events provider class implementation for devices which are controlled by a wult device
    driver.
    """

    def _unload(self):
        """Unload all the previously loaded wult kernel drivers."""

        # Unload all the possible wult device drivers.
        for drvname in Devices.DRVNAMES:
            drv = KernelModule.KernelModule(drvname, pman=self._pman, dmesg=self.dev.dmesg_obj)
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
                             self._pman.hostmsg, err1)
            raise

    def start(self):
        """Start the latency measurements."""

        with self._pman.open(self._enabled_path, "w") as fobj:
            fobj.write("1")

    def _set_launch_distance(self):
        """Set launch distance limits to driver."""

        try:
            limit_path = self._basedir / "ldist_max_nsec"
            with self._pman.open(limit_path, "r") as fobj:
                ldist_max = fobj.read().strip()

            limit_path = self._basedir / "ldist_min_nsec"
            with self._pman.open(limit_path, "r") as fobj:
                ldist_min = fobj.read().strip()
        except Error as err:
            raise Error(f"failed to read launch distance limit from '{limit_path}'"
                        f"{self._pman.hostmsg}:\n{err}") from err

        ldist_min = Trivial.str_to_num(ldist_min)
        ldist_max = Trivial.str_to_num(ldist_max)
        from_path = self._basedir / "ldist_from_nsec"
        to_path = self._basedir / "ldist_to_nsec"

        for idx, ldist in enumerate(self._ldist):
            if not ldist:
                # Special case: 0 means "use the minimum possible value".
                self._ldist[idx] = ldist_min

        for ldist, ldist_path in zip(self._ldist, [from_path, to_path]):
            if ldist < ldist_min or ldist > ldist_max:
                raise Error(f"launch distance '{ldist}' is out of range, it should be in range of "
                            f"[{ldist_min},{ldist_max}]")
            try:
                with self._pman.open(ldist_path, "w") as fobj:
                    fobj.write(str(ldist))
            except Error as err:
                raise Error(f"can't to change launch disatance range\nfailed to open '{ldist_path}'"
                            f"{self._pman.hostmsg} and write {ldist} to it:\n\t{err}") from err

    def get_resolution(self):
        """Returns resolution of the delayed event devices in nanoseconds."""

        try:
            path = self._basedir / "resolution_nsec"
            with self._pman.open(path, "r") as fobj:
                resolution = fobj.read().strip()
        except Error as err:
            raise Error(f"failed to read the delayed event resolution from '{path}'"
                        f"{self._pman.hostmsg}:\n{err}") from err

        return Trivial.str_to_num(resolution)

    def prepare(self):
        """Prepare to start the measurements."""

        # Unload wult drivers if they were loaded.
        self._unload()

        # Unbind the wult delayed event device from its current driver, if any.
        self._saved_drvname = self.dev.unbind() # pylint: disable=assignment-from-none
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

        if self._intr_focus:
            with self._pman.open(self._intr_focus_path, "w") as fobj:
                fobj.write("1")

        if self._early_intr:
            with self._pman.open(self._early_intr_path, "w") as fobj:
                fobj.write("1")

    def __init__(self, dev, cpunum, pman, ldist=None, intr_focus=None, early_intr=None):
        """
        Initialize a class instance. The arguments are documented in
        '_EventsProviderBase.__init__()'.
        """

        super().__init__(dev, cpunum, pman, ldist=ldist, intr_focus=intr_focus,
                         early_intr=early_intr)

        self._drv = None
        self._saved_drvname = None
        self._basedir = None
        self._enabled_path = None
        self._main_drv = None

        # This is a debugging option that allows to disable automatic wult modules unloading on
        # 'close()'.
        self.unload = True

        self._main_drv = KernelModule.KernelModule("wult", pman=pman, dmesg=dev.dmesg_obj)
        self._drv = KernelModule.KernelModule(self.dev.drvname, pman=pman, dmesg=dev.dmesg_obj)

        mntpoint = FSHelpers.mount_debugfs(pman=pman)
        self._basedir = mntpoint / "wult"
        self._enabled_path = self._basedir / "enabled"
        self._intr_focus_path = self._basedir / "intr_focus"
        self._early_intr_path = self._basedir / "early_intr"

    def close(self):
        """Uninitialize everything (unload kernel drivers, etc)."""

        if getattr(self, "unload", None):
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
            self._saved_drvname = None

        ClassHelpers.close(self, close_attrs=("_main_drv", "_drv"))

        super().close()


def WultEventsProvider(dev, cpunum, pman, ldist=None, intr_focus=None, early_intr=None):
    """
    Create and return an events provider class suitable for device 'dev'. The arguments are the
    same as in '_EventsProviderBase.__init__()'.
    """

    if dev.drvname:
        return _DrvEventsProvider(dev, cpunum, pman, ldist=ldist, intr_focus=intr_focus,
                                  early_intr=early_intr)

    raise Error(f"BUG: unsupported device '{dev.info['name']}'")
