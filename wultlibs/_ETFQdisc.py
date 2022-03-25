# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module provides API for configuring the ETF (Earliest Tx time First) qdisc (queuing
discipline).
"""

import re
import logging
from pepclibs.helperlibs import ToolChecker, Procs
from pepclibs.helperlibs.Exceptions import Error
from wultlibs.helperlibs import KernelVersion, ProcHelpers

_LOG = logging.getLogger()

class ETFQdisc():
    """
    This module provides API for configuring the ETF (Earliest Tx time First) qdisc (queuing
    discipline).
    """

    def reset_root_qdisc(self):
        """Reset root qdisc to defaults."""

        # Reset the qdisc of the network interface to default. The command may fail, for example if
        # the configuration is already "default", so ignore the errors.
        self._proc.run(f"tc qdisc del dev {self._ifname} root")

    def configured(self):
        """Return 'True' if network ETF qdisc has been configured."""

        cmd = f"tc qdisc show dev {self._ifname}"
        stdout, _ = self._proc.run_verify(cmd)
        if not stdout or "qdisc etf " not in stdout:
            return False
        return True

    def _run_tc_cmd(self, cmd):
        """This is a helper for running a 'tc' command specified in 'cmd'."""

        stdout, stderr, exitcode = self._proc.run(cmd)
        if exitcode:
            errmsg = self._proc.cmd_failed_msg(cmd, stdout, stderr, exitcode)
            errors = ("Operation not supported", "Specified qdisc not found")
            if any(err in stderr for err in errors):
                errmsg += "\n\n"
                pkgname = self._tchk.tool_to_pkg("sch_etf.ko")
                if pkgname:
                    kver = KernelVersion.get_kver(proc=self._proc)
                    errmsg += f"Try to install package '{pkgname}'{self._proc.hostmsg}\n"      \
                              f"Currently running kernel version is '{kver}', make sure the\n" \
                              f"installed '{pkgname}' also has version '{kver}'.\n"
                errmsg += "If you are running a custom kernel (as opposed to the vanilla OS\n" \
                          "kernel), ensure your kernel has the following features enabled:\n"    \
                          "* QoS / fair queuing (CONFIG_NET_SCHED)\n"                            \
                          "* Multi-queue priority scheduler (CONFIG_NET_SCH_MQPRIO)\n"           \
                          "* Earliest TxTime First (CONFIG_NET_SCH_ETF)\n"                       \
                          "* Netfilter (CONFIG_NETFILTER_NETLINK)\n"                             \
                          "And related modules, such as 'sch_etf' and 'sch_mqprio',\n"           \
                          "loaded if needed."

            elif "Unknown qdisc \"etf\"" in stderr:
                errmsg += self._old_tc_err_msg

            raise Error(errmsg)

        return stdout, stderr, exitcode

    def start_phc2sys(self, sync_period=5, tai_offset=37):
        """
        Start the 'phc2sys' process in order to synchronize the host and NIC time. The arguments are
        as follows.
          * sync_period - how often to synchronize (every 5 seconds).
          * tai_offset - current TAI offset in seconds (TAI time - real time).
        """

        # Kill a possibly stale 'phc2sys' process.
        ProcHelpers.kill_processes(r"^phc2sys .*", log=True, name="stale 'phc2sys' processes",
                                   proc=self._proc)

        freq = 1.0 / sync_period
        cmd = f"phc2sys -s CLOCK_REALTIME -c {self._ifname} -R {freq:.5} -O {tai_offset}"
        self._phc2sys_proc = self._proc.run_async(cmd)

        # Make sure the process did not exit immediately.
        stdout, stderr, exitcode = self._phc2sys_proc.wait(timeout=1)
        if exitcode is not None:
            raise Error("can't synchronize the NIC and system clocks, 'phc2sys' exited:\n%s"
                        % self._phc2sys_proc.cmd_failed_msg(stdout, stderr, exitcode))

    def configure(self):
        """Configure the ETF qdisc."""

        _LOG.debug("setting up ETF qdisc with handover delta %d nanoseconds", self._handover_delta)

        stdout, _ = self._proc.run_verify("%s -V" % self._tc_bin)
        match = re.match(r"^tc utility, iproute2-(ss)?(.*)$", stdout.strip())
        if not match:
            raise Error(f"failed to parse version number of the 'tc' tool{self._proc.hostmsg}")

        # 'tc' version numbering changed from date based (e.g. "tc utility, iproute2-ss180129") to
        # regular version numbering corresponding to kernel version (e.g. "tc utility,
        # iproute2-5.8.0") Any version with new style is new enough.
        if match.group(1) == "ss" and int(match.group(2)) < 181023:
            raise Error(self._old_tc_err_msg)

        self.reset_root_qdisc()

        cmd = f"{self._tc_bin} qdisc replace dev {self._ifname} parent root handle 100 mqprio " \
              f"num_tc 3 map 2 2 1 0 2 2 2 2 2 2 2 2 2 2 2 2 queues 1@0 1@1 2@2 hw 0"
        self._run_tc_cmd(cmd)

        cmd = f"{self._tc_bin} qdisc add dev {self._ifname} parent 100:1 etf offload clockid " \
              f"CLOCK_TAI delta {self._handover_delta}"
        self._run_tc_cmd(cmd)

        # Here is the behavior we observed in kernel version 4.19: resetting the qdisc resets the
        # NIC, and the carrier disappears for some time. Let's wait for it to appear.
        _LOG.debug("waiting for carrier on network interface '%s'%s", self._ifname,
                   self._proc.hostmsg)
        self._netif.wait_for_carrier(10)

    def __init__(self, netif, tc_bin="tc", handover_delta=500000, phc2sys_bin="phc2sys",
                 proc=None):
        """
        Class constructor. The arguments are as follows.
          * netif - the 'NetIface' object of network device used for measurements.
          * tc_bin - path to the 'tc' tool that should be used for setting up the ETF qdisc.
          * handover_delta - the qdisc delta - the time offset in microseconds when the qdisc hands
                             the packet over to the network driver.
          * phc2sys_bin - path to the 'phc2sys' tool that will be run in background and periodically
                          synchronize the host and NIC clock.
          * proc - the 'Proc' or 'SSH' object that defines the host to configure the ETF qdisc on
                   (default is the local host). This object will keep a 'proc' reference and use it
                   in various methods.

        Note about phc2sys.

        When ETF qdisc offloads packets to the NIC, it is important to keep host and NIC times in
        sync, because Linux kernel API accept absolute time values to send the packets at, and these
        values are passed down to the NIC as-is. If NIC's time is different, the packets will be
        sent at incorrect time or just dropped causing errors like "missing deadline".
        """

        self._proc = proc
        self._netif = netif
        self._ifname = netif.ifname

        self._close_proc = proc is None

        self._tchk = None
        self._tc_bin = None

        self._phc2sys_bin = None
        self._phc2sys_proc = None

        self._handover_delta = None
        self._old_tc_err_msg = None

        if not self._proc:
            self._proc = Procs.Proc()

        self._handover_delta = int(handover_delta * 1000)

        self._tchk = ToolChecker.ToolChecker(proc=self._proc)

        self._tc_bin = self._tchk.check_tool(tc_bin)
        self._phc2sys_bin = self._tchk.check_tool(phc2sys_bin)

        self._old_tc_err_msg = f"the 'tc' tool installed{self._proc.hostmsg} is not new enough " \
                               f"and does not support the ETF qdisc.\nPlease, install 'tc' " \
                               f"version '181023' or greater.\nThe 'tc' tool is part of the " \
                               f"'iproute2' project. Run 'tc -V' to check its version."

    def close(self):
        """Stop the measurements."""

        if getattr(self, "_phc2sys_proc", None):
            _LOG.debug("killing the the phc2sys process PID %d%s",
                       self._phc2sys_proc.pid, self._proc.hostmsg)
            ProcHelpers.kill_pids(self._phc2sys_proc.pid, kill_children=True, must_die=False,
                                  proc=self._proc)
            self._phc2sys_proc = None

        for attr in ("_tchk",):
            obj = getattr(self, attr, None)
            if obj:
                obj.close()
                setattr(self, attr, None)

        for attr in ("_netif", "_proc",):
            obj = getattr(self, attr, None)
            if obj:
                if getattr(self, f"_close{attr}", False):
                    getattr(obj, "close")()
                setattr(self, attr, None)

    def __enter__(self):
        """Enter the runtime context."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the runtime context."""
        self.close()
