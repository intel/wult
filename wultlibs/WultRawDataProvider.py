# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module implements the "WultRawDataProvider" class, which provides API for reading raw wult
datapoints, as well as intitializing wult devices.
"""

import logging
import contextlib
from pepclibs.helperlibs import KernelModule, Trivial, ClassHelpers
from pepclibs.helperlibs.Exceptions import Error, ErrorTimeOut
from wultlibs.helperlibs import FSHelpers
from wultlibs import Devices, _FTrace, _RawDataProvider

_LOG = logging.getLogger()

class _DrvRawDataProvider(_RawDataProvider.RawDataProviderBase):
    """
    The raw data provider class implementation for devices which are controlled by a wult kernel
    driver.
    """

    def _validate_datapoint(self, fields, vals):
        """
        This is a helper function for 'get_datapoints()' which checks that every raw datapoint
        from the trace buffer has the same fields in the same order.
        """

        if len(fields) != len(self._fields) or len(vals) != len(self._fields) or \
           not all(f1 == f2 for f1, f2 in zip(fields, self._fields)):
            old_fields = ", ".join(self._fields)
            new_fields = ", ".join(fields)
            raise Error(f"the very first raw datapoint has different fields comparing to a new "
                        f"datapointhad\n"
                        f"First datapoint fields count: {len(fields)}\n"
                        f"New datapoint fields count: {len(self._fields)}\n"
                        f"Fist datapoint fields:\n{old_fields}\n"
                        f"New datapoint fields:\n{new_fields}\n\n"
                        f"New datapoint full ftrace line:\n{self._ftrace.raw_line}")

    def get_datapoints(self):
        """
        This generator reads the trace buffer and yields raw datapoints in form of dictionary. The
        dictionary keys are the ftrace field names, the values are the integer values of the fields.
        """

        last_line = None
        yielded_lines = 0

        try:
            for line in self._ftrace.getlines():
                # Wult output format should be: field1=val1 field2=val2, and so on. Parse the line
                # and get the list of (field, val) pairs: [(field1, val1), (field2, val2), ... ].
                try:
                    if not line.msg:
                        raise ValueError
                    pairs = [pair.split("=") for pair in line.msg.split()]
                    fields, vals = zip(*pairs)
                    if len(fields) != len(vals):
                        raise ValueError
                except ValueError:
                    _LOG.debug("unexpected line in ftrace buffer%s:\n%s",
                               self._pman.hostmsg, line.msg)
                    continue

                yielded_lines += 1
                last_line = line.msg

                if self._fields:
                    self._validate_datapoint(fields, vals)
                else:
                    self._fields = fields

                yield dict(zip(fields, [int(val) for val in vals]))
        except ErrorTimeOut as err:
            msg = f"{err}\nCount of wult ftrace lines read so far: {yielded_lines}"
            if last_line:
                msg = f"{msg}\nLast seen wult ftrace line:\n{last_line}"
            raise ErrorTimeOut(msg) from err

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
        """Returns resolution of the delayed event device in nanoseconds."""

        try:
            path = self._basedir / "resolution_nsec"
            with self._pman.open(path, "r") as fobj:
                resolution = fobj.read().strip()
        except Error as err:
            raise Error(f"failed to read the '{self.dev.info['devid']}' delayed event device "
                        f"resolution from '{path}'{self._pman.hostmsg}:\n{err}") from err

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

    def __init__(self, dev, cpunum, pman, timeout=None, ldist=None, intr_focus=None,
                 early_intr=None):
        """
        Initialize a class instance. The arguments are documented in
        '_RawDataProviderBase.__init__()'.
        """

        super().__init__(dev, cpunum, pman, ldist=ldist, intr_focus=intr_focus,
                         early_intr=early_intr)

        self._drv = None
        self._saved_drvname = None
        self._basedir = None
        self._enabled_path = None
        self._main_drv = None
        self._ftrace = None
        self._fields = None

        # This is a debugging option that allows to disable automatic wult modules unloading on
        # 'close()'.
        self.unload = True

        self._main_drv = KernelModule.KernelModule("wult", pman=pman, dmesg=dev.dmesg_obj)
        self._drv = KernelModule.KernelModule(self.dev.drvname, pman=pman, dmesg=dev.dmesg_obj)

        self._ftrace = _FTrace.FTrace(pman=self._pman, timeout=self._timeout)

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

        ClassHelpers.close(self, close_attrs=("_main_drv", "_drv", "_ftrace"))

        super().close()


def WultRawDataProvider(dev, cpunum, pman, timeout=None, ldist=None, intr_focus=None,
                       early_intr=None):
    """
    Create and return a raw data provider class suitable for a delayed event device 'dev'. The
    arguments are the same as in '_RawDataProviderBase.__init__()'.
    """

    if dev.drvname:
        return _DrvRawDataProvider(dev, cpunum, pman, timeout=timeout, ldist=ldist,
                                   intr_focus=intr_focus, early_intr=early_intr)

    raise Error(f"BUG: unsupported device '{dev.info['name']}'")
