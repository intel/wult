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
from pepclibs.helperlibs import Trivial, ClassHelpers
from pepclibs.helperlibs.Exceptions import Error, ErrorNotSupported
from wultlibs import _ProgressLine, _Nmcli, _ETFQdisc, _NdlRawDataProvider
from wultlibs.helperlibs import Human
_LOG = logging.getLogger()

class NdlRunner(ClassHelpers.SimpleCloseContext):
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

        timeout = 4.0 + self._ldist[1]/1000000000

        while True:
            stdout, stderr, exitcode = self._prov.ndlrunner.wait(timeout=timeout, lines=[16, None],
                                                                 join=False)
            if exitcode is not None:
                msg = self._prov.ndlrunner.get_cmd_failure_msg(stdout, stderr, exitcode,
                                                               timeout=timeout)
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

    def _collect(self, dpcnt, tlimit):
        """
        Collect datapoints and stop when the CSV file has 'dpcnt' datapoints in total, or when
        collection time exceeds 'tlimit' (value '0' or 'None' means "no limit").
        """

        datapoints = self._get_datapoints()

        # Populate the CSV header first.
        dp = next(datapoints)
        self._res.csv.add_header(dp.keys())

        collected_cnt = 0
        max_rtd = 0
        start_time = time.time()

        for dp in datapoints:
            if tlimit and time.time() - start_time > tlimit:
                break

            max_rtd = max(dp["RTD"], max_rtd)
            _LOG.debug("launch distance: RTD %.2f (max %.2f), LDist %.2f",
                       dp["RTD"], max_rtd, dp["LDist"])

            if not self._res.add_csv_row(dp):
                continue

            collected_cnt += 1
            self._progress.update(collected_cnt, max_rtd)

            if collected_cnt >= dpcnt:
                break

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

        self._prov.start()
        self._res.write_info()

        self._progress.start()
        try:
            self._collect(dpcnt, tlimit)
        except (KeyboardInterrupt, Error) as err:
            self._progress.update(self._progress.dpcnt, self._progress.maxlat, final=True)

            is_ctrl_c = isinstance(err, KeyboardInterrupt)
            if is_ctrl_c:
                # In Linux Ctrl-c prints '^C' on the terminal. Make sure the next output line does
                # not look messy.
                print("\r", end="")
                _LOG.notice("interrupted, stopping the measurements")

            if is_ctrl_c:
                raise

            dmesg = ""
            with contextlib.suppress(Error):
                dmesg = "\n" + self._dev.get_new_dmesg()
            raise Error(f"{err}{dmesg}") from err
        else:
            self._progress.update(self._progress.dpcnt, self._progress.maxlat, final=True)

        self._prov.stop()

        _LOG.info("Finished measuring RTD%s", self._pman.hostmsg)

    def prepare(self):
        """Prepare to start measurements."""

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
        ipaddr = self._netif.get_ipv4_addr(must_get=False)
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

        self._prov.prepare()

        # We use the ETF qdisc for scheduling delayed network packets. Configure it and start the
        # 'phc2sys' process in background in order to keep the host and NIC clocks in sync.

        # Get the TAI offset first.
        stdout, _ = self._pman.run_verify(f"{self._prov.ndlrunner_path} --tai-offset")
        tai_offset = self._get_line(prefix="TAI offset", line=stdout)
        if not Trivial.is_int(tai_offset):
            raise Error(f"unexpected 'ndlrunner --tai-offset' output:\n{stdout}")

        _LOG.info("Configuring the ETF qdisc%s", self._pman.hostmsg)
        self._etfqdisc.configure()
        _LOG.info("Starting NIC-to-system clock synchronization process%s", self._pman.hostmsg)
        self._etfqdisc.start_phc2sys(tai_offset=int(tai_offset))

    def __init__(self, pman, dev, res, ndlrunner_path, ldist=None):
        """
        The class constructor. The arguments are as follows.
          * pman - the process manager object that defines the host to run the measurements on.
          * dev - the network device object to use for measurements (created with
                  'Devices.GetDevice()').
          * res - the 'WORawResult' object to store the results at.
          * ndlrunner_path - path to the 'ndlrunner' helper.
          * ldist - a pair of numbers specifying the launch distance range in nanoseconds (how far
          *         in the future the delayed network packets should be scheduled). Default is
          *         [5000000, 50000000].
        """

        self._pman = pman
        self._dev = dev
        self._res = res
        self._ldist = ldist

        self._netif = self._dev.netif
        self._ifname = self._netif.ifname
        self._ndl_lines = None
        self._prov = None
        self._rtd_path = None
        self._progress = None
        self._etfqdisc = None
        self._nmcli = None

        if not self._ldist:
            self._ldist = [5000000, 50000000]

        self._progress = _ProgressLine.ProgressLine(period=1)

        self._prov = _NdlRawDataProvider.NdlRawDataProvider(dev, ndlrunner_path, pman,
                                                            ldist=self._ldist)

        drvname = self._prov.drvobjs[0].name
        self._rtd_path = self._prov.debugfs_mntpoint.joinpath(f"{drvname}/rtd")
        self._etfqdisc = _ETFQdisc.ETFQdisc(self._netif, pman=pman)

    def close(self):
        """Stop the measurements."""

        if getattr(self, "_netif", None):
            self._netif.down()
        if getattr(self, "_nmcli", None):
            self._nmcli.restore_managed()

        close_attrs = ("_etfqdisc", "_prov", "_nmcli")
        unref_attrs = ("_netif", "_dev", "_pman")
        ClassHelpers.close(self, close_attrs=close_attrs, unref_attrs=unref_attrs)
