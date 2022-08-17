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
from pepclibs.helperlibs import Trivial, ClassHelpers, Systemctl, Human
from pepclibs.helperlibs.Exceptions import Error, ErrorTimeOut
from statscollectlibs.helperlibs import ProcHelpers
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

        for ldist, ldist_path in zip(reversed(self._ldist), [to_path, from_path]):
            if ldist < ldist_min or ldist > ldist_max:
                ldist = Human.duration_ns(ldist)
                ldist_min = Human.duration_ns(ldist_min)
                ldist_max = Human.duration_ns(ldist_max)
                raise Error(f"launch distance '{ldist}' is out of range, it should be in range of "
                            f"[{ldist_min}, {ldist_max}]")
            try:
                with self._pman.open(ldist_path, "w") as fobj:
                    fobj.write(str(ldist))
            except Error as err:
                raise Error(f"can't to change launch distance range\nfailed to open '{ldist_path}'"
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

        if self._early_intr:
            with self._pman.open(self._early_intr_path, "w") as fobj:
                fobj.write("1")

    def __init__(self, dev, cpunum, pman, timeout=None, ldist=None, early_intr=None):
        """Initialize a class instance. The arguments are the same as in 'WultRawDataProvider'."""

        drvinfo = { "wult" : { "params" : f"cpunum={cpunum}" },
                     dev.drvname : { "params" : None }}
        super().__init__(dev, pman, drvinfo)

        self._timeout = timeout
        self._ldist = ldist
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
                _LOG.warning("failed to start the previously stopped 'irqbalance' service:\n%s",
                             err)

        ClassHelpers.close(self, close_attrs=("_sysctl", "_ftrace"))
        super().close()


class _WultrunnerRawDataProvider(_RawDataProvider.RawDataProviderBase):
    """
    The raw data provider class implementation for devices which are controlled by the 'wultrunner'
    program.
    """

    def _wultrunner_error_prefix(self):
        """
        Forms and returns the starting part of an error message related to a general 'wultrunner'
        process failure.
        """

        return f"the 'wultrunner' process{self._pman.hostmsg}"

    def _get_lines(self):
        """This generator reads the 'wultrunner' helper output and yields it line by line."""

        timeout = 4.0 + self._ldist[1]/1000000000

        while True:
            stdout, stderr, exitcode = self._wultrunner.wait(timeout=timeout, lines=[16, None],
                                                             join=False)
            if exitcode is not None:
                msg = self._wultrunner.get_cmd_failure_msg(stdout, stderr, exitcode,
                                                           timeout=timeout)
                raise Error(f"{self._wultrunner_error_prefix()} has exited unexpectedly\n{msg}")
            if stderr:
                raise Error(f"{self._wultrunner_error_prefix()} printed an error message:\n"
                            f"{''.join(stderr)}")
            if not stdout:
                raise Error(f"{self._wultrunner_error_prefix()} did not provide any output for "
                            f"{timeout} seconds")

            for line in stdout:
                yield line

    def get_datapoints(self):
        """
        This generator receives data from 'wultrunner' and yields datapoints in form of a
        dictionary. The keys are metric names and values are metric values.
        """

        line = None
        yielded_lines = 0
        hdr = None
        types = []

        try:
            for line in self._get_lines():
                line = line.strip()
                vals = Trivial.split_csv_line(line)
                if not hdr:
                    # The very first line is the CSV header.
                    hdr = vals
                    continue

                if len(vals) != len(hdr):
                    raise Error("unexpected line from 'wultrunner'{self._pman.hostmsg}:\n{line}")

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
            msg = f"{err}\nCount of 'wultrunner' lines read so far: {yielded_lines}"
            if line:
                msg = f"{msg}\nLast seen 'wultrunner' line:\n{line}"
            raise ErrorTimeOut(msg) from err

    def _start_wultrunner(self):
        """Start the 'wultrunner' process on the measured system."""

        ldist_str = ",".join([str(val) for val in self._ldist])
        cmd = f"{self._wultrunner_path} -c {self._cpunum} -l {ldist_str} "
        self._wultrunner = self._pman.run_async(cmd)

    def _stop_wultrunner(self):
        """Make 'wultrunner' process to terminate."""

        _LOG.debug("stopping 'wultrunner'")
        self._wultrunner.stdin.write("q\n".encode("utf8"))
        self._wultrunner.stdin.flush()

        _, _, exitcode = self._wultrunner.wait(timeout=5)
        if exitcode is None:
            _LOG.warning("the 'wultrunner' program PID %d%s failed to exit, killing it",
                         self._wultrunner.pid, self._pman.hostmsg)
            ProcHelpers.kill_pids(self._wultrunner.pid, kill_children=True, must_die=False,
                                  pman=self._pman)

        self._wultrunner = None

    def start(self):
        """Start the  measurements."""
        self._start_wultrunner()

    def stop(self):
        """Stop the  measurements."""
        self._stop_wultrunner()

    def prepare(self):
        """Prepare to start the measurements."""

        # Kill stale 'wultrunner' process, if any.
        regex = f"^.*{self._wultrunner_path} .*$"
        ProcHelpers.kill_processes(regex, log=True, name="stale 'wultrunner' process",
                                   pman=self._pman)

    def __init__(self, dev, cpunum, wultrunner_path, pman, timeout=None, ldist=None):
        """Initialize a class instance. The arguments are the same as in 'WultRawDataProvider'."""

        super().__init__(dev, pman)

        self._cpunum = cpunum
        self._wultrunner_path = wultrunner_path
        self._timeout = timeout
        self._ldist = ldist

        self._wultrunner = None
        self._wult_lines = None

        if not timeout:
            self._timeout = 10

        # Validate the 'wultrunner' helper path.
        if not self._pman.is_exe(self._wultrunner_path):
            raise Error(f"bad 'wultrunner' helper path '{self._wultrunner_path}' - does not exist"
                        f"{self._pman.hostmsg} or not an executable file")


def WultRawDataProvider(dev, cpunum, pman, wultrunner_path=None, timeout=None, ldist=None,
                        early_intr=None):
    """
    Create and return a raw data provider class suitable for a delayed event device 'dev'. The
    arguments are the same as in '_RawDataProviderBase.__init__()'.
      * dev - the device object created with 'Devices.GetDevice()'.
      * cpunum - the measured CPU number.
      * pman - the process manager object defining host to operate on.
      * wultrunner_path - path to the 'wultrunner' program.
      * timeout - the maximum amount of seconds to wait for a raw datapoint. Default is 10
                  seconds.
      * ldist - a pair of numbers specifying the launch distance range. The default value is
                specific to the delayed event device.
      * early_intr - enable interrupts before entering the C-state.
    """

    if dev.drvname:
        return _DrvRawDataProvider(dev, cpunum, pman, timeout=timeout, ldist=ldist,
                                   early_intr=early_intr)
    if not wultrunner_path:
        raise Error("BUG: the 'wultrunner' program path was not specified")

    return _WultrunnerRawDataProvider(dev, cpunum, wultrunner_path, pman, timeout=timeout,
                                      ldist=ldist)
