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
from pepclibs.helperlibs import Trivial, ClassHelpers, Systemctl
from pepclibs.helperlibs.Exceptions import Error, ErrorTimeOut
from wultlibs import _FTrace, _RawDataProvider

_LOG = logging.getLogger()

class _DrvRawDataProvider(_RawDataProvider.DrvRawDataProviderBase):
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

    def start(self):
        """Start the measurements."""

        with self._pman.open(self._enabled_path, "w") as fobj:
            fobj.write("1")

    def stop(self):
        """Stop the measurements."""

        with self._pman.open(self._enabled_path, "w") as fobj:
            fobj.write("0")

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

    def prepare(self):
        """Prepare to start the measurements."""

        if self.dev.drvname == "wult_igb":
            # The 'irqbalance' service usually causes problems by binding the delayed events (NIC
            # interrupts) to CPUs different form the measured one. Stop the service.
            self._sysctl = Systemctl.Systemctl(pman=self._pman)
            if self._sysctl.is_active("irqbalance"):
                _LOG.info("Stopping the 'irqbalance' service")
                self._sysctl.stop("irqbalance")
                self._irqbalance_stopped = True

        # Unload wult drivers if they were loaded.
        self._unload(everything=True)

        # Unbind the wult delayed event device from its current driver, if any.
        self.dev.unbind()

        # Load wult drivers.
        self._load()

        # Bind the delayed event device to its wult driver.
        self.dev.bind()

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
        Initialize a class instance. The arguments are as follows.
          * dev - the device object created with 'Devices.GetDevice()'.
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

        drvinfo = { "wult" : { "params" : f"cpunum={cpunum}" },
                     dev.drvname : { "params" : None }}
        super().__init__(dev, pman, drvinfo)

        self._timeout = timeout
        self._ldist = ldist
        self._intr_focus = intr_focus
        self._early_intr = early_intr

        self._ftrace = None
        self._sysctl = None
        self._irqbalance_stopped = False

        self._basedir = None
        self._enabled_path = None
        self._fields = None

        if not timeout:
            self._timeout = 10

        self._ftrace = _FTrace.FTrace(pman=self._pman, timeout=self._timeout)

        self._basedir = self.debugfs_mntpoint / "wult"
        self._enabled_path = self._basedir / "enabled"
        self._intr_focus_path = self._basedir / "intr_focus"
        self._early_intr_path = self._basedir / "early_intr"

    def close(self):
        """Uninitialize everything."""

        if getattr(self, "_irqbalance_stopped"):
            _LOG.info("Starting the previously stopped 'irqbalance' service")
            try:
                self._sysctl.start("irqbalance")
            except Error as err:
                # We saw failures here on a system that was running irqbalance, but the user
                # offlined all the CPUs except for CPU0. We were able to stop the service, but could
                # not start it again, probably because there is only one CPU.
                _LOG.warning("failed to start the previously stoopped 'irqbalance' service:\n%s",
                             err)

        ClassHelpers.close(self, close_attrs=("_sysctl", "_ftrace"))
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
