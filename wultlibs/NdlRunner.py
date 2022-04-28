# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module implements the main ndl functionality - runs the measurement experiments and saves the
result.
"""

import time
import logging
import contextlib
from pepclibs.helperlibs import Trivial, KernelModule, ClassHelpers
from pepclibs.helperlibs.Exceptions import Error, ErrorNotSupported
from wultlibs import _ProgressLine, _Nmcli, _ETFQdisc
from wultlibs.helperlibs import KernelVersion, ProcHelpers, Human, FSHelpers

_LOG = logging.getLogger()

class NdlRunner:
    """Run the latency measurements."""

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

    def _get_lines(self):
        """This generator to reads the 'ndlrunner' helper output and yields it line by line."""

        timeout = 1.0 + self._ldist[1]/1000000000

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
        Read the next latency data line from the 'ndlrunner' helper, parse it, and ireturn the
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

    def _get_datapoints(self):
        """
        This generator yields datapoints as a dictionary with keys being CSV column names and data
        being values.
        """

        self._ndl_lines = self._get_lines()

        while True:
            yield self._get_latency()

    def _start_ndlrunner(self):
        """Start the 'ndlrunner' process on the measured system."""

        regex = f"^.*{self._ndlrunner_bin} .*{self._ifname}.*$"
        ProcHelpers.kill_processes(regex, log=True, name="stale 'ndlrunner' process",
                                   pman=self._pman)

        ldist_str = ",".join([str(val) for val in self._ldist])
        cmd = f"{self._ndlrunner_bin} -l {ldist_str} "
        cmd += f"{self._ifname}"

        self._ndlrunner = self._pman.run_async(cmd)

    def _collect(self, dpcnt, tlimit):
        """
        Collect datapoints and stop when the CSV file has 'dpcnt' datapoints in total, or when
        collection time exceeds 'tlimit' (value '0' or 'None' means "no limit"). Returns count of
        collected datapoints. If the filters were configured, the returned value counts only those
        datapoints that passed the filters.
        """

        datapoints = self._get_datapoints()

        # Populate the CSV header first.
        dp = next(datapoints)
        self._res.csv.add_header(dp.keys())

        collected_cnt = 0
        start_time = time.time()
        for dp in datapoints:
            if tlimit and time.time() - start_time > tlimit:
                break

            self._max_rtd = max(dp["RTD"], self._max_rtd)
            _LOG.debug("launch distance: RTD %.2f (max %.2f), LDist %.2f",
                       dp["RTD"], self._max_rtd, dp["LDist"])

            if not self._res.add_csv_row(dp):
                continue

            collected_cnt += 1
            self._progress.update(collected_cnt, self._max_rtd)

            if collected_cnt >= dpcnt:
                break

        return collected_cnt

    def run(self, dpcnt=1000000, tlimit=None):
        """
        Start the measurements. The arguments are as follows.
          * dpcnt - count of datapoints to collect.
          * tlimit - the measurements time limit in seconds.
        """

        msg = f"Start measuring RTD{self._pman.hostmsg}, collecting {dpcnt} datapoints"
        if tlimit:
            msg += f", time limit is {Human.duration(tlimit)}"
        _LOG.info(msg)

        self._start_ndlrunner()
        self._res.write_info()

        self._progress.start()
        collected_cnt = 0
        try:
            collected_cnt = self._collect(dpcnt, tlimit)
        finally:
            self._progress.update(collected_cnt, self._max_rtd, final=True)

        self._stop_ndlrunner()

        _LOG.info("Finished measuring RTD%s", self._pman.hostmsg)

    def prepare(self):
        """Prepare to start measurements."""

        # Ensure the kernel is fresh enough.
        kver = KernelVersion.get_kver(pman=self._pman)
        if KernelVersion.kver_lt(kver, "5.1-rc1"):
            raise Error(f"version of the running kernel{self._pman.hostmsg} is {kver}, but it "
                        f"does not support the ETF qdisc.\nPlease, use kernel version 5.1 or "
                        f"newer")

        try:
            self._nmcli = _Nmcli.Nmcli(pman=self._pman)
        except ErrorNotSupported:
            pass
        else:
            # We have to configure the I210 network interface in a special way, but if it is managed
            # by NetworkManager, the configuration may get reset at any point. Therefore, detach the
            # network interface from NetworkManager.
            _LOG.info("Detaching network interface '%s' from NetworkManager%s",
                      self._ifname, self._pman.hostmsg)
            self._nmcli.unmanage(self._ifname)

        # Ensure the interface exists and has carrier. It must be brought up before we can check the
        # carrier status.
        self._netif.up()
        self._netif.wait_for_carrier(10)

        # Make sure the network interface has an IP address.
        ipaddr = self._netif.get_ipv4_addr(default=None)
        if ipaddr:
            _LOG.debug("network interface '%s'%s has IP address '%s'",
                       self._ifname, self._pman.hostmsg, ipaddr)
        else:
            ipaddr = self._netif.get_unique_ipv4_addr()
            ipaddr += "/16"
            self._netif.set_ipv4_addr(ipaddr)
            # Ensure the IP was set.
            self._netif.get_ipv4_addr()
            _LOG.info("Assigned IP address '%s' to interface '%s'%s",
                      ipaddr, self._ifname, self._pman.hostmsg)

        self._drv.load(unload=True, opts=f"ifname={self._ifname}")

        # We use the ETF qdisc for scheduling delayed network packets. Configure it and start the
        # 'phc2sys' process in background in order to keep the host and NIC clocks in sync.

        # Get the TAI offset first.
        stdout, _ = self._pman.run_verify(f"{self._ndlrunner_bin} --tai-offset")
        tai_offset = self._get_line(prefix="TAI offset", line=stdout)
        if not Trivial.is_int(tai_offset):
            raise Error(f"unexpected 'ndlrunner --tai-offset' output:\n{stdout}")

        _LOG.info("Configuring the ETF qdisc%s", self._pman.hostmsg)
        self._etfqdisc.configure()
        _LOG.info("Starting NIC-to-system clock synchronization process%s", self._pman.hostmsg)
        self._etfqdisc.start_phc2sys(tai_offset=int(tai_offset))

    def _verify_input_args(self):
        """Verify and adjust the constructor input arguments."""

        # Validate the 'ndlrunner' helper path.
        if not self._pman.is_exe(self._ndlrunner_bin):
            raise Error(f"bad 'ndlrunner' helper path '{self._ndlrunner_bin}' - does not exist"
                        f"{self._pman.hostmsg} or not an executable file")

    def _stop_ndlrunner(self):
        """Make 'ndlrunner' process to terminate."""

        ndlrunner = self._ndlrunner
        self._ndlrunner = None
        with contextlib.suppress(Error):
            ndlrunner.stdin.write("q\n".encode("utf8"))
            ndlrunner.stdin.flush()

        _, _, exitcode = ndlrunner.wait(timeout=5)
        if exitcode is None:
            _LOG.warning("the 'ndlrunner' program PID %d%s failed to exit, killing it",
                         ndlrunner.pid, self._pman.hostmsg)
            ProcHelpers.kill_pids(ndlrunner.pid, kill_children=True, must_die=False,
                                  pman=self._pman)

    def __init__(self, pman, netif, res, ndlrunner_bin, ldist=None):
        """
        The class constructor. The arguments are as follows.
          * pman - the process manager object that defines the host to run the measurements on.
          * netif - the 'NetIface' object of network device used for measurements.
          * res - the 'WORawResult' object to store the results at.
          * ndlrunner_bin - path to the 'ndlrunner' helper.
          * ldist - a pair of numbers specifying the launch distance range in nanoseconds (how far
          *         in the future the delayed network packets should be scheduled). Default is
          *         [5000000, 50000000].
        """

        self._pman = pman
        self._netif = netif
        self._res = res
        self._ndlrunner_bin = ndlrunner_bin
        self._ldist = ldist
        self._ifname = netif.ifname

        self._ndl_lines = None
        self._drv = None
        self._rtd_path = None
        self._ndlrunner = None
        self._progress = None
        self._max_rtd = 0
        self._etfqdisc = None
        self._nmcli = None

        if not self._ldist:
            self._ldist = [5000000, 50000000]

        self._verify_input_args()

        self._progress = _ProgressLine.ProgressLine(period=1)
        self._drv = KernelModule.KernelModule("ndl", pman=pman)

        mntpath = FSHelpers.mount_debugfs(pman=pman)
        self._rtd_path = mntpath.joinpath(f"{self._drv.name}/rtd")
        self._etfqdisc = _ETFQdisc.ETFQdisc(netif, pman=pman)

    def close(self):
        """Stop the measurements."""

        if getattr(self, "_ndlrunner", None):
            self._stop_ndlrunner()
        if getattr(self, "_netif", None):
            self._netif.down()
        if getattr(self, "_nmcli", None):
            self._nmcli.restore_managed()
        if getattr(self, "_drv", None):
            self._drv.unload()

        unref_attrs = ("_ndlrunner", "_netif", "_nmcli", "_drv", "_pman")
        close_attrs = ("_etfqdisc", "_nmcli")
        ClassHelpers.close(self, unref_attrs=unref_attrs, close_attrs=close_attrs)

    def __enter__(self):
        """Enter the run-time context."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the runtime context."""
        self.close()
