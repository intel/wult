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
from pepclibs.helperlibs import Trivial, ClassHelpers
from pepclibs.helperlibs.Exceptions import Error
from wultlibs import _RawDataProvider, _ETFQdisc
from wultlibs.helperlibs import ProcHelpers

_LOG = logging.getLogger()

class NdlRawDataProvider(_RawDataProvider.DrvRawDataProviderBase):
    """
    The raw data provider class implementation the ndl tool.
    """

    def _ndlrunner_error_prefix(self):
        """
        Forms and returns the starting part of an error message related to a general 'ndlrunner'
        process failure.
        """

        return f"the 'ndlrunner' process{self._pman.hostmsg}"

    def _unexpected_line_error_prefix(self, line):
        """
        Forms and returns the starting part of an error message related to an unexpected line
        recieved from the 'ndlrunner' process.
        """

        return f"received the following unexpected line from {self._ndlrunner_error_prefix()}:\n" \
               f"{line}"

    def _start_ndlrunner(self):
        """Start the 'ndlrunner' process on the measured system."""

        ldist_str = ",".join([str(val) for val in self._ldist])
        cmd = f"{self._ndlrunner_path} -l {ldist_str} "
        cmd += f"{self.dev.netif.ifname}"

        self._ndlrunner = self._pman.run_async(cmd)

    def _stop_ndlrunner(self):
        """Make 'ndlrunner' process to terminate."""

        _LOG.debug("stopping 'ndlrunner'")
        self._ndlrunner.stdin.write("q\n".encode("utf8"))
        self._ndlrunner.stdin.flush()

        _, _, exitcode = self._ndlrunner.wait(timeout=5)
        if exitcode is None:
            _LOG.warning("the 'ndlrunner' program PID %d%s failed to exit, killing it",
                         self._ndlrunner.pid, self._pman.hostmsg)
            ProcHelpers.kill_pids(self._ndlrunner.pid, kill_children=True, must_die=False,
                                  pman=self._pman)

        self._ndlrunner = None

    def _get_lines(self):
        """This generator reads the 'ndlrunner' helper output and yields it line by line."""

        timeout = 4.0 + self._ldist[1]/1000000000

        while True:
            stdout, stderr, exitcode = self._ndlrunner.wait(timeout=timeout, lines=[16, None],
                                                            join=False)
            if exitcode is not None:
                msg = self._ndlrunner.get_cmd_failure_msg(stdout, stderr, exitcode, timeout=timeout)
                raise Error(f"{self._ndlrunner_error_prefix()} has exited unexpectedly\n{msg}")
            if stderr:
                raise Error(f"{self._ndlrunner_error_prefix()} printed an error message:\n"
                            f"{''.join(stderr)}")
            if not stdout:
                raise Error(f"{self._ndlrunner_error_prefix()} did not provide any output for "
                            f"{timeout} seconds")

            for line in stdout:
                yield line

    def _get_line(self, prefix="", line=None):
        """Read, validate, and return the next 'ndlrunner' line."""

        if not line:
            line = next(self._ndl_lines)
        prefix = f"ndlrunner: {prefix}: "
        if not line.startswith(prefix):
            msg = self._unexpected_line_error_prefix(line)
            raise Error(f"{msg}\nExpected a line with the following prefix instead:\n{prefix}")
        return line[len(prefix):]

    def _get_latency(self):
        """
        Read the next latency data line from the 'ndlrunner' helper, parse it, and return the
        resulting dictionary.
        """

        line = self._get_line(prefix="datapoint")
        line = Trivial.split_csv_line(line)

        if len(line) != 2:
            msg = self._unexpected_line_error_prefix(line)
            raise Error(f"{msg}\nExpected 2 comma-separated integers, got {len(line)}")

        for val in line:
            if not Trivial.is_int(val):
                msg = self._unexpected_line_error_prefix(line)
                raise Error(f"{msg}\n: Expected 2 comma-separated integers, got a non-integer "
                            f"'{val}'")

        # Convert nanoseconds to microseconds.
        line = [int(val)/1000 for val in line]
        return {"RTD" : line[0], "LDist" : line[1]}

    def get_datapoints(self):
        """
        This generator receives data from 'ndlrunner' and yields datapoints in form of a dictionary.
        The keys are metric names and values are metric values.
        """

        self._ndl_lines = self._get_lines()

        while True:
            yield self._get_latency()

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
        regex = f"^.*{self._ndlrunner_path} .*{self.dev.netif.ifname}.*$"
        ProcHelpers.kill_processes(regex, log=True, name="stale 'ndlrunner' process",
                                   pman=self._pman)

        # We use the ETF qdisc for scheduling delayed network packets. Configure it and start the
        # 'phc2sys' process in background in order to keep the host and NIC clocks in sync.

        # Get the TAI offset first.
        stdout, _ = self._pman.run_verify(f"{self._ndlrunner_path} --tai-offset")
        tai_offset = self._get_line(prefix="TAI offset", line=stdout)
        if not Trivial.is_int(tai_offset):
            raise Error(f"unexpected 'ndlrunner --tai-offset' output:\n{stdout}")

        _LOG.info("Configuring the ETF qdisc%s", self._pman.hostmsg)
        self._etfqdisc.configure()
        _LOG.info("Starting NIC-to-system clock synchronization process%s", self._pman.hostmsg)
        self._etfqdisc.start_phc2sys(tai_offset=int(tai_offset))

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

        self._ndlrunner_path = ndlrunner_path
        self._timeout = timeout
        self._ldist = ldist

        self._ndlrunner = None
        self._ndl_lines = None
        self._etfqdisc = None

        if not timeout:
            self._timeout = 10

        # Validate the 'ndlrunner' helper path.
        if not self._pman.is_exe(self._ndlrunner_path):
            raise Error(f"bad 'ndlrunner' helper path '{self._ndlrunner_path}' - does not exist"
                        f"{self._pman.hostmsg} or not an executable file")

        self._etfqdisc = _ETFQdisc.ETFQdisc(self.dev.netif, pman=self._pman)

    def close(self):
        """Stop the measurements."""

        if getattr(self, "_ndlrunner", None):
            with contextlib.suppress(Error):
                self._stop_ndlrunner()
            self._ndlrunner = None

        close_attrs = ("_etfqdisc",)
        ClassHelpers.close(self, close_attrs=close_attrs)

        super().close()
