# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2020 Intel Corporation
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
from wultlibs.helperlibs import Trivial, FSHelpers, KernelModule, KernelVersion, ProcHelpers, Human
from wultlibs.helperlibs.Exceptions import Error, ErrorNotSupported
from wultlibs import _ProgressLine, _Nmcli, _ETFQdisc

_LOG = logging.getLogger()

class NdlRunner:
    """Run the latency measurements."""

    def _run_post_trigger(self, rtd):
        """Run the post-trigger program."""

        if self._post_trigger_range and \
           rtd < self._post_trigger_range[0] or \
           rtd > self._post_trigger_range[1]:
            return

        self._proc.run_verify(f"{self._post_trigger} --latency {rtd}")

    def _ndlrunner_error_prefix(self):
        """
        Forms and returns the starting part of an error message related to a general 'ndlrunner'
        process failure.
        """

        return f"the 'ndlrunner' process{self._proc.hostmsg}"

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
            stdout, stderr, exitcode = self._ndlrunner.wait_for_cmd(timeout=timeout, by_line=True,
                                                                    lines=[16, None], join=False)
            if exitcode is not None:
                msg = self._ndlrunner.cmd_failed_msg(stdout, stderr, exitcode, timeout)
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
                                   proc=self._proc)

        ldist_str = ",".join([str(val) for val in self._ldist])
        cmd = f"{self._ndlrunner_bin} -l {ldist_str} "
        cmd += f"{self._ifname}"

        self._ndlrunner = self._proc.run_async(cmd)

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

            if self._post_trigger:
                self._run_post_trigger(dp["RTD"])

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

        msg = f"Start measuring RTD{self._proc.hostmsg}, collecting {dpcnt} datapoints"
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

        _LOG.info("Finished measuring RTD%s", self._proc.hostmsg)

    def prepare(self):
        """Prepare to start measurements."""

        # Ensure the kernel is fresh enough.
        kver = KernelVersion.get_kver(proc=self._proc)
        if KernelVersion.kver_lt(kver, "5.1-rc1"):
            raise Error(f"version of the running kernel{self._proc.hostmsg} is {kver}, but it "
                        f"does not support the ETF qdisc.\nPlease, use kernel version 5.1 or "
                        f"newer")

        try:
            self._nmcli = _Nmcli.Nmcli(proc=self._proc)
        except ErrorNotSupported:
            pass
        else:
            # We have to configure the I210 network interface in a special way, but if it is managed
            # by NetworkManager, the configuration may get reset at any point. Therefore, detach the
            # network interface from NetworkManager.
            _LOG.info("Detaching network interface '%s' from NetworkManager%s",
                      self._ifname, self._proc.hostmsg)
            self._nmcli.unmanage(self._ifname)

        # Ensure the interface exists and has carrier. It must be brought up before we can check the
        # carrier status.
        self._netif.up()
        self._netif.wait_for_carrier(10)

        # Make sure the network interface has an IP address.
        ipaddr = self._netif.get_ipv4_addr(default=None)
        if ipaddr:
            _LOG.debug("network interface '%s'%s has IP address '%s'",
                       self._ifname, self._proc.hostmsg, ipaddr)
        else:
            ipaddr = self._netif.get_unique_ipv4_addr()
            ipaddr += "/16"
            self._netif.set_ipv4_addr(ipaddr)
            # Ensure the IP was set.
            self._netif.get_ipv4_addr()
            _LOG.info("Assigned IP address '%s' to interface '%s'%s",
                      ipaddr, self._ifname, self._proc.hostmsg)

        self._drv.load(unload=True, opts=f"ifname={self._ifname}")

        # We use the ETF qdisc for scheduling delayed network packets. Configure it and start the
        # 'phc2sys' process in background in order to keep the host and NIC clocks in sync.

        # Get the TAI offset first.
        stdout, _ = self._proc.run_verify(f"{self._ndlrunner_bin} --tai-offset")
        tai_offset = self._get_line(prefix="TAI offset", line=stdout)
        if not Trivial.is_int(tai_offset):
            raise Error(f"unexpected 'ndlrunner --tai-offset' output:\n{stdout}")

        _LOG.info("Configuring the ETF qdisc%s", self._proc.hostmsg)
        self._etfqdisc.configure()
        _LOG.info("Starting NIC-to-system clock synchronization process%s", self._proc.hostmsg)
        self._etfqdisc.start_phc2sys(tai_offset=int(tai_offset))

    def set_post_trigger(self, path, trange=None):
        """
        Configure the post-trigger - a program that has to be executed after a datapoint is
        collected. The arguments are as follows.
          * path - path to the executable program to run. The program will be executed with the
            '--latency <value>' option, where '<value>' is the observed latency value in
            nanoseconds.
          * trange - the post-trigger range. By default, the trigger program is executed on every
            datapoint. But if a range is provided, the trigger program will be executed only when
            RTD is in trigger range.
        """

        if not FSHelpers.isexe(path, proc=self._proc):
            raise Error(f"file '{path}' does not exist or it is not an executable file")

        self._post_trigger = path
        self._post_trigger_range = trange

    def _verify_input_args(self):
        """Verify and adjust the constructor input arguments."""

        # Validate the 'ndlrunner' helper path.
        if not FSHelpers.isexe(self._ndlrunner_bin, proc=self._proc):
            raise Error(f"bad 'ndlrunner' helper path '{self._ndlrunner_bin}' - does not exist"
                        f"{self._proc.hostmsg} or not an executable file")

    def _stop_ndlrunner(self):
        """Make 'ndlrunner' process to terminate."""

        ndlrunner = self._ndlrunner
        self._ndlrunner = None
        with contextlib.suppress(Error):
            ndlrunner.stdin.write("q\n".encode("utf8"))
            ndlrunner.stdin.flush()

        _, _, exitcode = ndlrunner.wait_for_cmd(timeout=5)
        if exitcode is None:
            _LOG.warning("the 'ndlrunner' program PID %d%s failed to exit, killing it",
                         ndlrunner.pid, self._proc.hostmsg)
            ProcHelpers.kill_pids(ndlrunner.pid, kill_children=True, must_die=False,
                                  proc=self._proc)

    def __init__(self, proc, netif, res, ndlrunner_bin, ldist=None):
        """
        The class constructor. The arguments are as follows.
          * proc - the 'Proc' or 'SSH' object that defines the host to run the measurements on.
          * netif - the 'NetIface' object of network device used for measurements.
          * res - the 'WORawResult' object to store the results at.
          * ndlrunner_bin - path to the 'ndlrunner' helper.
          * ldist - a pair of numbers specifying the launch distance range in nanoseconds (how far
          *         in the future the delayed network packets should be scheduled). Default is
          *         [5000000, 50000000].
        """

        self._proc = proc
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
        self._post_trigger = None
        self._etfqdisc = None
        self._nmcli = None
        self._post_trigger_range = []

        if not self._ldist:
            self._ldist = [5000000, 50000000]

        self._verify_input_args()

        self._progress = _ProgressLine.ProgressLine(period=1)
        self._drv = KernelModule.KernelModule(proc, "ndl")

        mntpath = FSHelpers.mount_debugfs(proc=proc)
        self._rtd_path = mntpath.joinpath(f"{self._drv.name}/rtd")
        self._etfqdisc = _ETFQdisc.ETFQdisc(netif, proc=proc)

    def close(self):
        """Stop the measurements."""

        if getattr(self, "_etfqdisc", None):
            self._etfqdisc.close()
            self._etfqdisc = None

        if getattr(self, "_ndlrunner", None):
            self._stop_ndlrunner()
            self._ndlrunner = None

        if getattr(self, "_netif", None):
            self._netif.down()
            self._netif = None

        if getattr(self, "_nmcli", None):
            self._nmcli.restore_managed()
            self._nmcli.close()
            self._nmcli = None

        if getattr(self, "_proc", None):
            self._proc = None

        # Unload our driver.
        if getattr(self, "_drv", None):
            self._drv.unload()
            self._drv = None

    def __enter__(self):
        """Enter the run-time context."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the runtime context."""
        self.close()
