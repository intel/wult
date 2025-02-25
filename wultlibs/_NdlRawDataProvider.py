# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module implements the "NdlRawDataProvider" class, which provides API for reading raw ndl
data.
"""

import contextlib
from pepclibs.helperlibs import Trivial, ClassHelpers
from pepclibs.helperlibs.Exceptions import Error, ErrorNotSupported
from wultlibs import _RawDataProvider, _ETFQdisc, _Nmcli

_LOG = Logging.getLogger(f"wult.{__name__}")

class NdlRawDataProvider(_RawDataProvider.DrvRawDataProviderBase,
                         _RawDataProvider.HelperRawDataProviderBase):
    """
    The raw data provider class implementation for the ndl tool.
    """

    def _unexpected_line_error_prefix(self, line):
        """
        Forms and returns the starting part of an error message related to an unexpected line
        received from the 'ndl-helper' process.
        """

        msg = f"received the following unexpected line from {self._error_pfx()}:\n{line}"
        stderr = self._get_stderr()
        if stderr:
            stderr = Error(stderr).indent(2)
            msg += f"\nStandard error output of '{self._helpername}':\n{stderr}"

        return msg

    def _get_line(self, prefix="", line=None):
        """Read, validate, and return the next 'ndl-helper' line."""

        if not line:
            line = next(self._ndl_lines)
        prefix = f"ndl-helper: {prefix}: "
        if not line.startswith(prefix):
            msg = self._unexpected_line_error_prefix(line)
            raise Error(f"{msg}\nExpected a line with the following prefix instead:\n{prefix}")
        return line[len(prefix):]

    def _get_latency(self):
        """
        Read the next latency data line from the 'ndl-helper' helper, parse it, and return the
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
        This generator receives data from 'ndl-helper' and yields datapoints in form of a
        dictionary. The keys are metric names and values are metric values.
        """

        self._ndl_lines = self._get_lines()

        while True:
            yield self._get_latency()

    def start(self):
        """Start the measurements."""
        super()._start_helper()

    def stop(self):
        """Stop the  measurements."""

        super()._exit_helper()

        self._etfqdisc.stop_phc2sys()
        self._netif.down()
        if self._nmcli:
            self._nmcli.restore_managed()

    def prepare(self):
        """Prepare to start the measurements."""

        super().prepare()

        ldist_str = ",".join([str(val) for val in self.ldist])
        self._helper_opts = f"-C {self._cpunum} -l {ldist_str}"
        if self._cbuf_size:
            self._helper_opts += f" --trash-cpu-cache {self._cbuf_size}"
        self._helper_opts += f" {self._netif.ifname}"

        try:
            self._nmcli = _Nmcli.Nmcli(pman=self._pman)
        except ErrorNotSupported:
            pass
        else:
            # We have to configure the I210 network interface in a special way, but if it is managed
            # by NetworkManager, the configuration may get reset at any point. Therefore, detach the
            # network interface from NetworkManager.
            _LOG.info("Detaching network interface '%s' from NetworkManager%s",
                      self._netif.ifname, self._pman.hostmsg)
            self._nmcli.unmanage(self._netif.ifname)

        # Ensure the network interface exists and has carrier. It must be brought up before we can
        # check the carrier status.
        self._netif.up()
        self._netif.wait_for_carrier(10)

        # Make sure the network interface has an IP address.
        ipaddr = self._netif.get_ipv4_addr(must_get=False)
        if ipaddr:
            _LOG.debug("network interface '%s'%s has IP address '%s'",
                       self._netif.ifname, self._pman.hostmsg, ipaddr)
        else:
            ipaddr = self._netif.get_unique_ipv4_addr()
            ipaddr += "/16"
            self._netif.set_ipv4_addr(ipaddr)
            # Ensure the IP was set.
            self._netif.get_ipv4_addr()
            _LOG.info("Assigned IP address '%s' to interface '%s'%s",
                      ipaddr, self._netif.ifname, self._pman.hostmsg)


        # Load the ndl driver.
        self._load_driver()

        # We use the ETF qdisc for scheduling delayed network packets. Configure it and start the
        # 'phc2sys' process in background in order to keep the host and NIC clocks in sync.

        # Get the TAI offset first.
        stdout, _ = self._pman.run_verify(f"{self._helper_path} --tai-offset")
        tai_offset = self._get_line(prefix="TAI offset", line=stdout)
        if not Trivial.is_int(tai_offset):
            raise Error(f"unexpected 'ndl-helper --tai-offset' output:\n{stdout}")

        _LOG.info("Configuring the ETF qdisc%s", self._pman.hostmsg)
        self._etfqdisc.configure()
        _LOG.info("Starting NIC-to-system clock synchronization process%s", self._pman.hostmsg)
        self._etfqdisc.start_phc2sys(tai_offset=int(tai_offset))

    def __init__(self, dev, pman, cpunum, ldist, ndlhelper_path, timeout=None, cbuf_size=0):
        """
        Initialize a class instance. The arguments are as follows.
          * dev - the device object created with 'Devices.GetDevice()'.
          * pman - the process manager object defining host to operate on.
          * cpunum - CPU number to send delayed packets from.
          * ldist - a pair of numbers specifying the launch distance range in nanoseconds.
          * ndlhelper_path - path to the 'ndl-helper' helper.
          * timeout - the maximum amount of seconds to wait for a raw datapoint. Default is 10
                      seconds.
          * cbuf_size - CPU cache trashing buffer size.
        """

        drvinfo = {dev.drvname : {"params" : f"ifname={dev.netif.ifname}"}}
        super().__init__(dev, pman, ldist, drvinfo=drvinfo, helper_path=ndlhelper_path,
                         timeout=timeout)

        self._cpunum = cpunum
        self._helper_path = ndlhelper_path
        self._netif = self.dev.netif
        self._cbuf_size= cbuf_size

        self._ndl_lines = None
        self._etfqdisc = None
        self._nmcli = None

        # Validate the 'ndl-helper' helper path.
        if not self._pman.is_exe(self._helper_path):
            raise Error(f"bad 'ndl-helper' helper path '{self._helper_path}' - does not exist"
                        f"{self._pman.hostmsg} or not an executable file")

        self._etfqdisc = _ETFQdisc.ETFQdisc(self._netif, pman=self._pman)

    def close(self):
        """Stop the measurements."""

        if getattr(self, "_netif", None):
            with contextlib.suppress(Error):
                self._netif.down()

        if getattr(self, "_nmcli", None):
            with contextlib.suppress(Error):
                self._nmcli.restore_managed()

        unref_attrs = ("_netif",)
        close_attrs = ("_etfqdisc", "_nmcli")
        ClassHelpers.close(self, close_attrs=close_attrs, unref_attrs=unref_attrs)

        super().close()
