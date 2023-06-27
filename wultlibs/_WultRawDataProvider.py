# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module provides API for reading raw wult datapoints, as well as initializing wult devices.
"""

import logging
from pepclibs.helperlibs import Trivial, ClassHelpers, Systemctl, KernelVersion
from pepclibs.helperlibs.Exceptions import Error, ErrorTimeOut, ErrorNotFound
from wultlibs import _FTrace, _RawDataProvider

_LOG = logging.getLogger()

class _WultDrvRawDataProvider(_RawDataProvider.DrvRawDataProviderBase):
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
                        f"datapoint\n"
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

        from_path = self._basedir / "ldist_from_nsec"
        to_path = self._basedir / "ldist_to_nsec"

        for ldist, ldist_path in zip(reversed(self.ldist), [to_path, from_path]):
            try:
                with self._pman.open(ldist_path, "w") as fobj:
                    fobj.write(str(ldist))
            except Error as err:
                raise Error(f"can't to change launch distance range\nfailed to open '{ldist_path}'"
                            f"{self._pman.hostmsg} and write {ldist} to it:\n"
                            f"{err.indent(2)}") from err

    def _get_ldist_limits(self):
        """Returns the min. and max. launch distance supported by the driver."""

        try:
            limit_path = self._basedir / "ldist_min_nsec"
            with self._pman.open(limit_path, "r") as fobj:
                ldist_min = fobj.read().strip()

            limit_path = self._basedir / "ldist_max_nsec"
            with self._pman.open(limit_path, "r") as fobj:
                ldist_max = fobj.read().strip()
        except Error as err:
            raise Error(f"failed to read launch distance limit from '{limit_path}'"
                        f"{self._pman.hostmsg}:\n{err.indent(2)}") from err

        ldist_min = Trivial.str_to_int(ldist_min, what="min. launch distance value")
        if ldist_min < 0:
            raise Error(f"BUG: negative min. launch distance limit value '{ldist_min}'")

        ldist_max = Trivial.str_to_num(ldist_max, what="max. launch distance value")
        if ldist_max < ldist_min:
            raise Error(f"BUG: bad launch distance limit range ['{ldist_min}', '{ldist_max}']")

        return (ldist_min, ldist_max)

    def prepare(self):
        """Prepare to start the measurements."""

        super().prepare()

        # Unbind the wult delayed event device from its current driver, if any.
        self.dev.unbind()

        # Load wult drivers.
        self._load_driver()

        # Bind the delayed event device to its wult driver.
        self.dev.bind()

        self.ldist_limits = self._get_ldist_limits()
        self._adjust_and_validate_ldist()
        self._set_launch_distance()

        try:
            self._sysctl = Systemctl.Systemctl(pman=self._pman)
            msg_fmt = ""
        except ErrorNotFound:
            msg_fmt = f"cannot check if %s service is active, because the 'systemctl' tool " \
                         f"was not found{self._pman.hostmsg}."

        if self.dev.drvname == "wult_igb":
            # The 'irqbalance' service usually causes problems by binding the delayed events (NIC
            # interrupts) to CPUs other than the measured one. Stop the service.
            if not self._sysctl:
                _LOG.notice(msg_fmt, "the 'irqbalance'")
                _LOG.notice("please, make sure 'irqbalance' is disabled")
            else:
                if self._sysctl.is_active("irqbalance"):
                    self._sysctl.stop("irqbalance")
                    _LOG.info("Stopped the 'irqbalance' service")
                    self._stopped_services.append("irqbalance")

        if not self._sysctl:
            _LOG.notice(msg_fmt, "an NTP")
            _LOG.notice("please, make sure NTP is disabled")
        else:
            ntp_services = self._sysctl.stop_ntp()
            if ntp_services:
                self._stopped_services += ntp_services
                for service in ntp_services:
                    _LOG.info("Stopped the '%s' NTP service", service)

    def __init__(self, dev, pman, cpunum, ldist, timeout=None, unload=True):
        """Initialize a class instance. The arguments are the same as in 'WultRawDataProvider'."""

        drvinfo = { "wult" : { "params" : f"cpunum={cpunum}" },
                     dev.drvname : { "params" : None }}
        super().__init__(dev, pman, ldist, drvinfo=drvinfo, timeout=timeout, unload=unload)

        self._ftrace = None
        self._sysctl = None
        self._stopped_services = []

        self._basedir = None
        self._enabled_path = None
        self._fields = None

        self._ftrace = _FTrace.FTrace(pman=self._pman, timeout=self._timeout)

        self._basedir = self.debugfs_mntpoint / "wult"
        self._enabled_path = self._basedir / "enabled"

    def close(self):
        """Uninitialize everything."""

        services = getattr(self, "_stopped_services", [])
        for service in services:
            _LOG.info("Starting previously stopped '%s' service", service)
            try:
                self._sysctl.start(service)
            except Error as err:
                if service != "irqbalance":
                    raise
                # We saw failures here on a system that was running irqbalance, but the user
                # offlined all the CPUs except for CPU0. We were able to stop the service, but could
                # not start it again, probably because there is only one CPU.
                _LOG.warning("failed to start the previously stopped '%s' service:\n%s",
                             service, err.indent(2))

        ClassHelpers.close(self, close_attrs=("_sysctl", "_ftrace"))
        super().close()


class _WultBPFRawDataProvider(_RawDataProvider.HelperRawDataProviderBase):
    """
    The raw data provider class implementation for devices which are controlled by the
    'wult-hrt-helper' program, which includes eBPF code.
    """

    def get_datapoints(self):
        """
        This generator receives data from 'wult-hrt-helper' and yields datapoints in form of a
        dictionary. The keys are metric names and values are metric values.
        """

        line = None
        yielded_lines = 0
        hdr = None
        types = []

        try:
            for line in self._get_lines():
                vals = Trivial.split_csv_line(line)
                if not hdr:
                    # The very first line is the CSV header.
                    hdr = vals
                    continue

                if len(vals) != len(hdr):
                    raise Error(f"unexpected line from '{self._helpername}'{self._pman.hostmsg}:\n"
                                f"{line}")

                if not types:
                    # Figure out the types of various values.
                    for val in vals:
                        if Trivial.is_int(val):
                            types.append(int)
                        elif Trivial.is_float(val):
                            types.append(float)
                        else:
                            types.append(str)

                dp = dict(zip(hdr, [tp(val) for tp, val in zip(types, vals)]))
                yielded_lines += 1
                yield dp
        except ErrorTimeOut as err:
            msg = f"{err}\nCount of '{self._helpername}' lines read so far: {yielded_lines}"
            if line:
                msg = f"{msg}\nLast seen '{self._helpername}' line:\n{line}"
            stderr = self._get_stderr()
            if stderr:
                stderr = Error(stderr).indent(2)
                msg += f"\nStandard error output of '{self._helpername}'\n{stderr}"
            raise ErrorTimeOut(msg) from err
        except Error as err:
            if "Error loading vmlinux BTF" in str(err):
                kver = KernelVersion.get_kver(pman=self._pman)
                if KernelVersion.kver_lt(kver, "5.18"):
                    optname = "CONFIG_DEBUG_INFO"
                else:
                    optname = "CONFIG_DEBUG_INFO_BTF"

                raise Error(f"{err}\nPlease, make sure that your kernel has the '{optname}' "
                            f"configuration option enabled") from err
            raise

    def start(self):
        """Start the measurements."""
        super()._start_helper()

    def stop(self):
        """Stop the measurements."""
        super()._exit_helper()

    def prepare(self):
        """Prepare to start the measurements."""

        super().prepare()

        ldist_str = ",".join([str(val) for val in self.ldist])
        self._helper_opts = f"-c {self._cpunum} -l {ldist_str}"

    def __init__(self, dev, pman, cpunum, ldist, helper_path, timeout=None):
        """Initialize a class instance. The arguments are the same as in 'WultRawDataProvider'."""

        super().__init__(dev, pman, ldist, helper_path=helper_path, timeout=timeout)

        self._cpunum = cpunum

        self._wult_lines = None

def WultRawDataProvider(dev, pman, cpunum, ldist, helper_path=None, timeout=None, unload=True):
    """
    Create and return a raw data provider class suitable for a delayed event device 'dev'. The
    arguments are as follows.
      * dev - the device object created with 'Devices.GetDevice()'.
      * pman - the process manager object defining host to operate on.
      * cpunum - the measured CPU number.
      * ldist - a pair of numbers specifying the launch distance range in nanoseconds.
      * helper_path - path to the 'wult-hrt-helper' program.
      * timeout - the maximum amount of seconds to wait for a raw datapoint. Default is 10
                  seconds.
      * unload - whether or not to unload the kernel driver after finishing measurement.
    """

    if dev.drvname:
        return _WultDrvRawDataProvider(dev, pman, cpunum, ldist, timeout=timeout, unload=unload)
    if not helper_path:
        raise Error("BUG: the 'wult-hrt-helper' program path was not specified")

    return _WultBPFRawDataProvider(dev, pman, cpunum, ldist, helper_path, timeout=timeout)
