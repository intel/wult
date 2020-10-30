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

import datetime
import re
import logging
import contextlib
from collections import OrderedDict
from wultlibs import _common
from wultlibs.helperlibs import Trivial, FSHelpers, KernelModule, KernelVersion, ProcHelpers
from wultlibs.helperlibs import TurbostatParser
from wultlibs.helperlibs.Exceptions import Error, ErrorNotSupported
from wultlibs import Helpers, _ProgressLine, _Nmcli, _NetIface, _ETFQdisc

_LOG = logging.getLogger("main")

class NdlRunner:
    """Run the latency measurements."""

    def _run_post_trigger(self, rtd):
        """Run the post-trigger program."""

        if self._post_trigger_thresh is not None and rtd <= self._post_trigger_thresh:
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

        timeout = 1 + self._ldist[-1]/1000000000

        while True:
            stdout, stderr, exitcode = self._ndlrunner.wait_for_cmd(timeout=timeout, by_line=True,
                                                                    wait_for_exit=False, join=False)
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

    def _get_ts_data(self, dp):
        """
        Read the next turbostat data line from the 'ndlrunner' helper, parse it, and save the
        result in the 'dp' dictionary.
        """

        line = self._get_line(prefix="tsdata")
        tsdata = (self._ts_heading, line)
        parser = TurbostatParser.TurbostatParser(lines=iter(tsdata), cols_regex=self._ts_heading)
        tsdata = next(parser.next())

        # Convert turbostat data into a CSV line.
        for key, val in tsdata["totals"].items():
            if key in self._colmap:
                dp[self._colmap[key]] = val

    def _get_latency(self, dp):
        """
        Read the next latency data line from the 'ndlrunner' helper, parse it, and save the result
        in the 'dp' dictionary.
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

        dp["RTD"] = int(line[0])
        dp["LDist"] = int(line[1])

    def _get_datapoints(self):
        """
        This generator yields datapoints as a dictionary with keys being CSV column names and data
        being values.
        """

        self._ndl_lines = self._get_lines()

        # If turbostat data collection is enabled, the first line will be the table heading.
        if self._run_ts:
            self._ts_heading = self._get_line(prefix="tsheading")

        while True:
            dp = OrderedDict()

            self._get_latency(dp)
            if self._run_ts:
                self._get_ts_data(dp)

            yield dp

    def _start_ndlrunner(self):
        """Start the 'ndlrunner' process on the measured system."""

        regex = f"^.*{self._ndlrunner_bin} .*{self._ifname}.*$"
        ProcHelpers.kill_processes(regex, log=True, name="stale 'ndlrunner' process",
                                   proc=self._proc)

        ldist_str = ",".join([str(val) for val in self._ldist])
        cmd = f"{self._ndlrunner_bin} -l {ldist_str} "
        if self._run_ts:
            col_filter = ",".join(self._colmap.keys())
            cmd += f"-t {self._ts_bin} -f {col_filter} "
        cmd += f"{self._ifname}"

        self._ndlrunner = self._proc.run_async(cmd, shell=True)

    def _collect(self, dpcnt):
        """Collect datapoints and stop when the CSV file has 'dpcnt' datapoints in total."""

        datapoints = self._get_datapoints()

        # Populate the CSV header first.
        dp = next(datapoints)
        self._res.csv.add_header(dp.keys())

        for dp in datapoints:
            self._max_rtd = max(dp["RTD"], self._max_rtd)
            _LOG.debug("launch distance: RTD %d (max %d), LDist %d",
                       dp["RTD"], self._max_rtd, dp["LDist"])

            self._res.csv.add_row(dp.values())

            if self._post_trigger:
                self._run_post_trigger(dp["RTD"])

            self._progress.update(self._res.csv.rows_cnt, self._max_rtd)
            dpcnt -= 1
            if dpcnt <= 0:
                break

    def run(self, dpcnt=1000000):
        """
        Start the measurements. The arguments are as follows.
          * dpcnt - count of datapoints to collect.
        """

        dpcnt = Helpers.get_dpcnt(self._res, dpcnt)
        if not dpcnt:
            return

        _LOG.info("Start measuring RTD%s, collecting %d datapoints",
                  self._proc.hostmsg, dpcnt)

        self._start_ndlrunner()
        self._res.write_info()

        self._progress.start()
        try:
            self._collect(dpcnt)
        finally:
            self._progress.update(self._res.csv.rows_cnt, self._max_rtd, final=True)

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
        self._netif = _NetIface.NetIface(self._ifname, proc=self._proc)
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

    def set_post_trigger(self, path, thresh=None):
        """
        Configure the post-trigger - a program that has to be executed after a datapoint is
        collected. The arguments are as follows.
          * path - path to the executable program to run. The program will be executed with the
            '--latency <value>' option, where '<value>' is the observed latency value in
            nanoseconds.
          * thresh - the post-trigger threshold. By default, the trigger program is executed on evey
            datapoint. But if a threshold is provided, the trigger program will be executed only
            when latency exceeds the threshold.
        """

        if not FSHelpers.isexe(path, proc=self._proc):
            raise Error(f"file '{path}' does not exist or it is not an executalbe file")

        self._post_trigger = path
        if thresh is not None:
            if not Trivial.is_int(thresh):
                raise Error(f"bad post-trigger threshold value '{thresh}', should be an integer "
                            f"amount of nanoseconds")
            self._post_trigger_thresh = int(thresh)

    def _build_colmap(self):
        """Build and return the turbostat -> CSV column names map."""

        self._colmap = {}

        # Build the turbostat -> CSV column names map.
        cmd = f"{self._ts_bin} -l"
        stdout, _ = self._proc.run_verify(cmd)
        for key in Trivial.split_csv_line(stdout):
            if key == "Busy%":
                self._colmap[key] = "CC0%"
            elif key.startswith("CPU%c"):
                self._colmap[key] = f"CC{key[5:]}%"
            elif key.startswith("Pkg%pc"):
                self._colmap[key] = f"PC{key[6:]}%"

    def _get_turbostat_version(self):
        """Returns turbostat version string."""

        cmd = f"{self._ts_bin} -v"
        _, stderr = self._proc.run_verify(cmd)
        matchobj = re.match(r".+ (\d\d\.\d\d\.\d\d) .+", stderr)
        if not matchobj:
            raise Error(f"failed to get turbostat version.\nExecuted: {cmd}{self._proc.hostmsg}\n"
                        f"Got: {stderr}")

        return matchobj.group(1)

    def _cstate_stats_init(self):
        """Initialize information related to C-state statistics and the 'turbostat' tool."""

        if self._run_ts is False:
            if not self._ts_bin:
                return
            raise Error("path to 'turbostat' tool given, but C-state statistics collection is "
                        "disabled")

        if not self._ts_bin:
            self._ts_bin = FSHelpers.which("turbostat", default=None, proc=self._proc)

        if not self._ts_bin:
            msg = f"cannot collect C-state statistics: the 'turbostat' tool was not found" \
                  f"{self._proc.hostmsg}"
            if self._run_ts is True:
                raise ErrorNotSupported(msg)

            self._run_ts = False
            _LOG.info(msg)
            return

        # Make sure turbostat version is '19.08.31' or newer. Turbostat versions are dates (e.g.,
        # version '19.03.20' is Mar 20 2019), so we can use the 'datetime' module to compare the
        # versions.
        version = self._get_turbostat_version()
        vdate = (int(val) for val in version.split("."))
        if datetime.datetime(*vdate) < datetime.datetime(19, 8, 31):
            msg = f"cannot collect C-state statistics: too old turbostat version '{version}', " \
                  f"use turbostat version '19.08.31' or newer\n(checked {self._ts_bin}" \
                  f"{self._proc.hostmsg}"
            if self._run_ts:
                raise ErrorNotSupported(msg)

            self._run_ts = False
            _LOG.info(msg)
        else:
            self._run_ts = True
            self._build_colmap()

    def _verify_input_args(self):
        """Verify and adjust the constructor input arguments."""

        if not self._ldist:
            self._ldist = "5000, 10000"

        self._ldist = _common.validate_ldist(self._ldist)

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

    def __init__(self, proc, ifname, res, ndlrunner_bin, cstats=None, ts_bin=None, ldist=None):
        """
        The class constructor. The arguments are as follows.
          * proc - the 'Proc' or 'SSH' object that defines the host to run the measurements on.
          * ifname - the network interface name to use for measuring the latency.
          * res - the 'WORawResult' object to store the results at.
          * ndlrunner_bin - path to the 'ndlrunner' helper.
          * cstats - True: collect C-state statistics, fail if 'turbostat' not found.
                     None: collect C-state statistics, only if 'turbostat' is found.
                     False: do not collect C-state statistics.
          * ts_bin - path to the 'turbostat' tool, default is just "turbostat".
          * ldist - for how far in the future the delayed network packets should be scheduled in
                    microseconds. Default is [5000, 10000] microseconds.
        """

        self._proc = proc
        self._ifname = ifname
        self._res = res
        self._ndlrunner_bin = ndlrunner_bin
        self._run_ts = cstats
        self._ts_bin = ts_bin
        self._ldist = ldist
        self._ts_heading = ""

        self._ndl_lines = None
        self._drv = None
        self._rtd_path = None
        self._ndlrunner = None
        self._colmap = None
        self._progress = None
        self._max_rtd = 0
        self._post_trigger = None
        self._post_trigger_thresh = None
        self._etfqdisc = None
        self._nmcli = None
        self._netif = None

        self._verify_input_args()
        self._cstate_stats_init()

        self._progress = _ProgressLine.ProgressLine(period=1)
        self._drv = KernelModule.KernelModule(proc, "ndl")

        mntpath = FSHelpers.mount_debugfs(proc=proc)
        self._rtd_path = mntpath.joinpath(f"{self._drv.name}/rtd")
        self._etfqdisc = _ETFQdisc.ETFQdisc(ifname, proc=proc)

    def close(self):
        """Stop the measurements."""

        if getattr(self, "_etfqdisc", None):
            self._etfqdisc.close()

        if getattr(self, "_ndlrunner", None):
            self._stop_ndlrunner()

        if getattr(self, "_netif", None):
            self._netif.down()
            self._netif.close()

        if getattr(self, "_nmcli", None):
            self._nmcli.restore_managed()
            self._nmcli.close()

        if getattr(self, "_proc", None):
            self._proc = None

        # Unload our driver.
        if getattr(self, "_drv", None):
            self._drv.unload()

    def __enter__(self):
        """Enter the run-time context."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the runtime context."""
        self.close()
