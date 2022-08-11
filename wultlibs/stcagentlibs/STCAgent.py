# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module provides API for collecting SUT statistics.
"""

import time
import socket
import logging
import contextlib
from pathlib import Path
from pepclibs.helperlibs import LocalProcessManager, Trivial, ClassHelpers
from pepclibs.helperlibs.Exceptions import Error, ErrorExists, ErrorNotFound
from wultlibs.helperlibs import KernelVersion, ProcHelpers, RemoteHelpers
from statscollectlibs.stcagentlibs import SysInfo

_LOG = logging.getLogger()

# The message delimiter used by 'stc-agent'.
_DELIMITER = "--\n".encode("utf-8")

# The default statistics information. This dictionary is used by the '_Collector' class by default,
# but users can provide a custom dictionary of similar structure to override the defaults.
#
# * interval: normally a statistics collector is a program that wakes up periodically and collects
#             some data. The 'interval' key is the wake up period in seconds.
# * fallible: some collectors are known to be not so stable, and this flag tells 'stc-agent' to
#             ignore failures of this statistics collector. Default value is 'False'.
# * inband: 'True' the statistics collector is "in band" and 'False' if it is "out-of-band". The
#           former means that the collector runs on the SUT, and the latter means that it runs on a
#           separate host and collects statistics via an out-of-band channel, e.g., by talking to
#           the BMC module. Default value is 'True'.
# * enabled: 'True' if the statistics collector is enabled, otherwise 'False'. Default value is
#            'True'.
# * toolpath: path to the tool to collect the statistics. By default just the tool name (e.g.,
#             turbostat), in which case 'stc-agent' will assume the tool is in '$PATH'. But
#             users can modify this field and specify full path to the tool.
# * description: the statistics collector description.
# * props: a sub-dictionary containing various collector-specific properties.
#
# Here are the currently supported properties.
#
# ipmi:
#     bmchost: name or address of the BMC host to read IPMI data from.
#     bmcuser: name of the BMC user to use when talking to the BMC host (same as 'ipmitool -U').
#     bmcpwd: BMC password to use when talking to the BMC host (same as 'ipmitool -P').
# acpower:
#     devnode: the power meter device node to use for reading power consumption data.
#     pmtype: the power meter type.
#
# The 'sysinfo' statistics are special - this is just a bunch of information about the SUT collected
# before and after the workload. Sysinfo includes stuff like the '/proc/cpuinfo' contents, the
# 'lspci' output, and more.
#
DEFAULT_STINFO = {
    "sysinfo" : {
        "interval": None,
        "toolpath": None,
        "description" : "Not really a statiscics collector, but just a script that saves all sorts "
                        "of information about the SUT (e.g., 'dmesg', 'lspci -vvv' and 'dmidecode' "
                        "output, and more). One snapshot of the SUT information is taken before "
                        "the workload, and the other snapshot is taken after the workload. The "
                        "second snapshot, however, includes only the information that could "
                        "potentially change while the workload was running (e.g., 'dmesg' may "
                        "include new messages).",
    },
    "turbostat" : {
        "interval": 5,
        "toolpath": "turbostat",
        "description": "Periodically run the 'turbostat' tool and collect C-state residency, "
                       "average CPU frequency, RAPL data, and more.",
    },
    "ipmi": {
        "interval": 5,
        "fallible": True,
        "inband": False,
        "toolpath": "ipmi-helper",
        "description": "Periodically run 'ipmitool' to collect platform IPMI data, such as fans "
                       "speed, CPU temperature, etc. The data are collected by running 'ipmitool' "
                       "outside of the SUT (out of band), so that 'ipmitool' talks to SUT's BMC "
                       "module via the network. This is supposedly better than running 'ipmitool' "
                       "on the SUT (in-band), because it does not add to CPU load.",
        "props" : {
            "bmchost" : None,
            "bmcuser" : None,
            "bmcpwd" : None,
        }
    },
    "ipmi-inband": {
        "interval": 5,
        "fallible": True,
        "toolpath": "ipmi-helper",
        "description": "Same as the 'ipmi' statistics, but the data are collected by running "
                       "'ipmitool' on the SUT (in-band).",
    },
    "acpower": {
        "interval": 1,
        "inband": False,
        "toolpath": "yokotool",
        "description": "Collect SUT wall socket power consumption from an external Yokogawa power "
                       "meter using 'yokotool'.",
        "props" : {
            "devnode" : None,
            "pmtype" : None,
        }
    },
}

class SCReplyError(Error):
    """This exception is raised when 'stc-agent' replies that a commant has failed."""

def _check_stname(stname):
    """Verify that 'stname' is a known statistic name."""

    if stname not in DEFAULT_STINFO:
        avail_stnames = ", ".join(DEFAULT_STINFO)
        raise Error(f"unknown statistic name '{stname}', the known names are: {avail_stnames}")

def _check_stnames(stnames):
    """Verify that statistics in the 'stnames' list are legit."""

    for stname in stnames:
        _check_stname(stname)

def _set_stinfo_defaults(stinfo):
    """Add default keys to the statistics description dictionary."""

    for info in stinfo.values():
        if "enabled" not in info:
            info["enabled"] = True
        if "inband" not in info:
            info["inband"] = True
        if "fallible" not in info:
            info["fallible"] = False
        if "props" not in info:
            info["props"] = {}

def _separate_inb_vs_oob(stnames):
    """
    Splits the list of statistics names 'stnames' on two sets - the in-band and the out-of-band
    statistics. Returns a tuple of those two sets.
    """

    inb_stnames = set()
    oob_stnames = set()
    for stname in stnames:
        _check_stname(stname)

        if DEFAULT_STINFO[stname]["inband"]:
            inb_stnames.add(stname)
        else:
            oob_stnames.add(stname)

    return (inb_stnames, oob_stnames)

def _get_max_interval(stinfo):
    """
    Returns the maximum statistics collection interval value for all enabled statistics in
    'stinfo'.
    """

    intervals = []
    for info in stinfo.values():
        if info["enabled"] and info["interval"] is not None:
            intervals.append(info["interval"])

    if intervals:
        return max(intervals)

    return 0

class STCAgent(ClassHelpers.SimpleCloseContext):
    """
    This class provides API for collecting SUT statistics, such as 'turbostat' data and AC power.

    The usage model of this class is as follows.
      1. Create an object. This will run 'stc-agent' on the SUT (in-band statistics collection) and
         the local host (out-of-band collection). 'stc-agent' is just an agent that listens for
         commands on a Unix socket. The commands are like "start collecting", "stop collecting",
         "set properties", etc. 'stc-agent' runs various collectors.

         Example of "in-band" collectors: acpower, ipmi. These tools run on the local system, but
         collect information about the remote system.
      2. Optionally set the list of statistics collectors that are going to be used by running the
         'set_disabled_stats()', 'set_enabled_stats()'.
      3. Optionally set tool path and properties for certain statistics using 'set_prop()' and
         'set_toolpath()'.
      4. Optionally discover the available statistics by running the 'discover()' method. Once the
         discovery is finished, re-run 'set_enabled_stats()' to enable the discovered statistics.
      5. Run the 'configure()' method to configure the statistics collectors.
      6. Run 'start()' to start collecting the statistics. Supposedly after the 'start()' method is
         finished, you run a workload on the SUT.
      7. Run 'stop()' to stop collecting the statistics. You can repeat the start/stop cycles and
         re-configure the collectors between the cycles.
    """

    def start(self):
        """Start collecting the statistics."""

        self._inbcoll.start()
        if self._oobcoll:
            self._oobcoll.start()

    def stop(self, sysinfo=True):
        """Stop collecting the statistics."""

        self._inbcoll.stop(sysinfo=sysinfo)
        if self._oobcoll:
            self._oobcoll.stop(sysinfo=sysinfo)

    def get_max_interval(self):
        """
        Returns the longest currently configured interval value. If all statistics are disabled,
        returns 0.
        """

        inb_max_interval = _get_max_interval(self._inbcoll.stinfo)
        if self._oobcoll:
            oob_max_interval = _get_max_interval(self._oobcoll.stinfo)
        else:
            oob_max_interval = 0

        return max(inb_max_interval, oob_max_interval)

    def set_disabled_stats(self, stnames):
        """Disable statistics in 'stnames'."""

        _check_stnames(stnames)
        inb_stnames, oob_stnames = _separate_inb_vs_oob(stnames)

        for stname in inb_stnames:
            self._inbcoll.stinfo[stname]["enabled"] = False
        if self._oobcoll:
            for stname in oob_stnames:
                self._oobcoll.stinfo[stname]["enabled"] = False

    def set_enabled_stats(self, stnames):
        """Enable statistics in 'stnames' and disable all other statistics."""

        _check_stnames(stnames)
        inb_stnames, oob_stnames = _separate_inb_vs_oob(stnames)

        for stname, stinfo in self._inbcoll.stinfo.items():
            stinfo["enabled"] = stname in inb_stnames
        if self._oobcoll:
            for stname, stinfo in self._oobcoll.stinfo.items():
                stinfo["enabled"] = stname in oob_stnames

    def get_enabled_stats(self):
        """Return the list of enabled statistic names."""

        stnames = self._inbcoll.get_enabled_stats()
        if self._oobcoll:
            stnames |= self._oobcoll.get_enabled_stats()

        return stnames

    def _handle_conflicting_stats(self):
        """
        Some statistic collectors are mutually exclusive, for example "ipmi" and "ipmi-inband". This
        function handles situations when both collectors are requested.
        """

        if not self._oobcoll:
            return

        if self._inbcoll.stinfo["ipmi-inband"]["enabled"] and \
           self._oobcoll.stinfo["ipmi"]["enabled"]:
            # IPMI in-band and out-of-band collect the same information, but 'ipmi' is supposedly
            # less intrusive.
            _LOG.info("Disabling 'ipmi-inband' statistics in favor of 'ipmi'")
            self._inbcoll.stinfo["ipmi-inband"]["enabled"] = False

    def set_intervals(self, intervals):
        """
        Set intervals for statistics collectors. The 'intervals' argument should be a dictionary
        with statistics collector names as keys and the collection interval as the value. This
        method should be called prior to the 'configure()' method. By default the statistics
        collectors use intervals from the 'DEFAULT_STINFO' statistics description dictionary.

        Returns a dictionary similar to 'intervals', but only including enabled statistics and
        possibly rounded interval values as 'float' type.
        """

        _check_stnames(intervals.keys())
        inb_stnames, oob_stnames = _separate_inb_vs_oob(intervals.keys())

        inb_intervals = {stname: intervals[stname] for stname in inb_stnames}
        oob_intervals = {stname: intervals[stname] for stname in oob_stnames}

        intervals = self._inbcoll.set_intervals(inb_intervals)
        if self._oobcoll:
            intervals.update(self._oobcoll.set_intervals(oob_intervals))
        return intervals

    def _get_stinfo(self, stname):
        """Get statistics description dictionary for the 'stname' statistics."""

        if stname in self._inbcoll.stinfo:
            return self._inbcoll.stinfo[stname]

        if self._oobcoll:
            return self._oobcoll.stinfo[stname]

        raise ErrorNotFound(f"statistics '{stname}' is not available")

    def get_toolpath(self, stname):
        """
        Get currently configured path to the tool collecting the 'stname' statistics. The path is on
        the same host where 'stc-agent' runs (local host for out-of-band statistics, the SUT for
        in-band statistics.
        """

        _check_stname(stname)

        stinfo = self._get_stinfo(stname)
        return stinfo["toolpath"]

    def set_toolpath(self, stname, path):
        """
        Set path to the tool collecting the 'stname' statistics to 'path'. The path is supposed to
        be on the same host where 'stc-agent' runs (local host for out-of-band statistics, the SUT
        for in-band statistics.
        """

        _check_stname(stname)

        stinfo = self._get_stinfo(stname)
        stinfo["toolpath"] = path

    def get_outdirs(self):
        """
        Returns the output directory paths in form of a tuple of 2 elements:
        ('local_outdir', 'remote_outdir').
        """

        loutdir = None
        if self._oobcoll:
            loutdir = self._oobcoll.outdir

        return (loutdir, self._inbcoll.outdir)

    def set_prop(self, stname, name, value):
        """Set 'stname' statistic collector's property 'name' to value 'value'."""

        _check_stname(stname)

        stinfo = self._get_stinfo(stname)

        if name not in stinfo["props"]:
            msg = f"unknown property '{name}' for the '{stname}' statistics"
            if stinfo["props"]:
                msg += f", known properties are: {', '.join(stinfo['props'])}"
            raise Error(msg)

        stinfo["props"][name] = str(value)

    def configure(self):
        """
        Configure the statistics collectors. This method should be called after statistics collector
        configuration changes. Prior to calling this method, you can (but do not have to) use the
        following methods.
         * 'discover()' - to discover the list of statistics that can be collected.
         * 'set_disabled_stats()' and 'set_enabled_stats()' prior to to enable /disable certain
            statistics.
         * 'set_intervals()' - to configure the statistics collectors' intervals.
         * 'set_prop()' - to configure statistics collectors' properties.
         * 'set_toolpath()' - to configure statistics collectors' tools paths.
        """

        self._handle_conflicting_stats()

        self._inbcoll.configure()
        if self._oobcoll:
            self._oobcoll.configure()

    def discover(self):
        """
        Discover and return set of statistics that can be collected for SUT. This method probes all
        non-disabled statistics collectors. Prior to calling this method, you can (but do not have
        to) use the following methods.
         * 'set_disabled_stats()' and 'set_enabled_stats()' prior to to enable /disable certain
            statistics.
         * 'set_intervals()' - to configure the statistics collectors' intervals.
         * 'set_prop()' - to configure statistics collectors' properties.
         * 'set_toolpath()' - to configure statistics collectors' tools paths.
        """

        stnames = self._inbcoll.discover()
        if self._oobcoll:
            stnames |= self._oobcoll.discover()
        return stnames

    def __init__(self, pman, local_outdir=None, remote_outdir=None, local_scpath=None,
                 remote_scpath=None):
        """
        Initialize a class instance. The arguments are as follows.
          * pman - the process manager object associated with the SUT (the host to collect the
                   statistics for). Note, a reference to the 'pman' object will be saved and it will
                   be used in various methods, so it has to be kept connected. The reference will be
                   dropped once the 'close()' method is invoked.
          * local_outdir - output directory path on the local host for storing the local
                           'stc-agent' logs and results (the collected statistics). The out-of-band
                           statistics are always collected by the local 'stc-agent' instance, so
                           it's logs and results will be stored in 'local_outdir'. However, if the
                           SUT is the local host, the in-band 'stc-agent' logs and results are
                           stored in the 'local_outdir' directory, and the out-of-band 'stc-agent'
                           is not used at all.
          * remote_outdir - output directory path on the remote host (the SUT) for storing the
                            remote 'stc-agent' logs and results (the collected statistics). If the
                            SUT is a remote host, the 'remote_outdir' will be used for 'stc-agent'
                            logs and in-band statistics. Otherwise, this path won't be used at all.
          * local_scpath - path to 'stc-agent' on the local host.
          * remote_scpath - path to 'stc-agent' on the remote host (the SUT).

        The collected statistics will be stored in the 'stats' sub-directory of the output
        directory, the 'stc-agent' logs will be stored in the 'logs' sub-directory. Use
        'get_outdirs()' method to get the output directories.

        If the an output directory was not provided and instead, was created by 'STCAgent', the
        directory gets removed in the 'close()' method.
        """

        self._pman = pman

        # The in-band and out-of-band statistics collector objects.
        self._inbcoll = None
        self._oobcoll = None

        if local_outdir:
            local_outdir = Path(local_outdir)
            if not local_outdir.is_absolute():
                raise Error(f"path '{local_outdir}' is not absolute.\nPlease, provide absolute "
                            f"path for local output directory")
        if remote_outdir:
            remote_outdir = Path(remote_outdir)
            if not remote_outdir.is_absolute():
                raise Error(f"path '{remote_outdir}' is not absolute.\nPlease, provide absolute "
                            f"path for remote output directory")

        if pman.is_remote:
            inb_outdir = remote_outdir
            oob_outdir = local_outdir
            inb_scpath = remote_scpath
            oob_scpath = local_scpath
        else:
            inb_outdir = local_outdir
            oob_outdir = -1 # Just a bogus value, should not be used.
            inb_scpath = local_scpath
            oob_scpath = -1

        self._inbcoll = _InBandCollector(pman, outdir=inb_outdir, scpath=inb_scpath)
        # Do not create the out-of-band collector if 'pman' represents the local host. Out-of-band
        # collectors by definition run on a host different to the SUT.
        if pman.is_remote:
            self._oobcoll = _OutOfBandCollector(pman.hostname, outdir=oob_outdir, scpath=oob_scpath)

    def close(self):
        """Close the statistics collector."""
        ClassHelpers.close(self, close_attrs=("_oobcoll", "_inbcoll"), unref_attrs=("_pman",))

class _Collector(ClassHelpers.SimpleCloseContext):
    """
    The base statistics collector class, contains the parts shared between the inband and
    out-of-band collectors.
    """

    def _connect(self):
        """Connect to 'stc-agent'."""

        try:
            if self._ssht_port:
                # Connect to 'stc-agent' via the SSH tunnel.
                self._sock = socket.create_connection(("localhost", self._ssht_port))
                self._sock.settimeout(self._timeout)
            else:
                # Connect to 'stc-agent' direcly via the Unix socket file.
                self._sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                self._sock.connect(self._uspath)
        except socket.error as err:
            raise Error(f"cannot connect to 'stc-agent' at {self._sc_id}:\n{err}") from err

        _LOG.debug("connected to 'stc-agent' at %s", self._sc_id)

    def _disconnect(self):
        """Disconnect from 'stc-agent'."""

        assert self._sock

        try:
            self._sock.shutdown(socket.SHUT_RDWR)
            self._sock.close()
            self._sock = None
        except socket.error as err:
            raise Error(f"cannot disconnect from 'stc-agent' at {self._sc_id}: {err}") from err

        _LOG.debug("disconnected from 'stc-agent' at %s", self._sc_id)

    def _send_msg(self, msg):
        """Send a message to 'stc-agent'."""

        buf = msg.encode("utf-8") + _DELIMITER
        total = 0

        while total < len(buf):
            sent = self._sock.send(buf[total:])
            if sent == 0:
                raise Error(f"'stc-agent' at {self._sc_id} closed the connection")
            total += sent

    def _recv_msg(self):
        """
        Receive a message from 'stc-agent'. Returns 'None' if the remote side closed the connection,
        returns the received message otherwise.
        """

        msg = bytes()

        starttime = time.time()
        while time.time() - starttime < self._timeout:
            buf = self._sock.recv(1)
            if not buf:
                raise Error(f"'stc-agent' at {self._sc_id} closed the connection")

            # This inefficient, but good enough for our small messages.
            msg += buf
            if msg[-len(_DELIMITER):] == _DELIMITER:
                return msg[:-len(_DELIMITER)].decode("utf-8")

        raise Error(f"time out waiting for the 'stc-agent' response at {self._sc_id}")

    def _send_command(self, cmd, arg=None):
        """Send a command to 'stc-agent', verify and return the response."""

        if arg:
            cmd += " " + arg

        sc_str = f"'stc-agent' at {self._sc_id}"
        check_log_msg = f"Check 'stc-agent' log file{self._pman.hostmsg}':\n{self._logpath}"

        _LOG.debug("sending the following command to %s:\n%s", sc_str, cmd)

        try:
            self._send_msg(cmd)
        except (Error, socket.error) as err:
            raise Error(f"failed to send the following message to "
                        f"{sc_str}:\n{cmd}\n{err}\n{check_log_msg}") from err

        try:
            msg = self._recv_msg()
        except (Error, socket.error) as err:
            raise Error(f"failed receiving the reply to the following command from {sc_str}: "
                        f"{cmd}\n{err}\n{check_log_msg}") from err

        if msg == "OK":
            return None

        if msg.startswith("OK "):
            return msg[3:]

        raise SCReplyError(f"{sc_str} did not respond with 'OK' to the following command:\n{cmd}"
                           f"\nInstead, the response was the following:\n{msg}\n{check_log_msg}")

    def _set_collector_property(self, name, prop, value):
        """Set the 'prop' property of the 'name' statistic collector to the 'value' value."""

        if value is not None:
            self._send_command("set-collector-property", arg=f"{name} {prop} {value}")

    def set_intervals(self, intervals):
        """
        Set intervals for statistics collectors. The 'intervals' argument should be a dictionary
        with statistics collector names as keys and the collection interval as the value. This
        method should be called prior to the 'configure()' method. By default the statistics
        collectors use intervals from the 'DEFAULT_STINFO' statistics description dictionary.
        Returns a dictionary of the same structure as 'interval', but with interval values that will
        actually be used for all the statistics collectors.
        """

        # Convert intervals to strings and get rid of the trailing ".0" from the final string.
        for stname, interval in intervals.items():
            if not Trivial.is_float(interval):
                raise Error(f"bad interval value '{interval}' for '{stname}' statistics")
            self.stinfo[stname]["interval"] = float(interval)

        actual = {}
        for stname, stinfo in self.stinfo.items():
            if stinfo.get("interval"):
                actual[stname] = stinfo.get("interval")

        return actual

    def _ensure_min_collect_time(self):
        """
        This method makes sure all statistics collector made progress and collected at least one
        piece of statistics.
        """

        if not self._start_time:
            raise Error("statistics collection did not start yet")

        max_interval = _get_max_interval(self.stinfo)
        if max_interval == 0:
            return

        # Add some margin of safety.
        max_interval += 1

        if "ipmi" in self.stinfo and self.stinfo["ipmi"]["enabled"]:
            # IPMI may be very slow sometimes, so give it at least 10 seconds.
            max_interval = max(10, max_interval)

        delta = time.time() - self._start_time
        if delta < max_interval:
            _LOG.debug("enforcing minimum %f secs collection time, sleeping %f secs",
                       max_interval, max_interval - delta)
            time.sleep(max_interval - delta)

    def start(self, sysinfo=True):
        """Start collecting the statistics."""

        stnames = self.get_enabled_stats()

        if "sysinfo" in stnames:
            stnames.remove("sysinfo")
            if sysinfo:
                _LOG.info("Collecting %s system information", self._sutname)
                SysInfo.collect_before(self._statsdir / "sysinfo", self._pman)

        if not stnames:
            return

        self._send_command("start")
        self._start_time = time.time()

    def stop(self, sysinfo=True):
        """Stop collecting the statistics."""

        stnames = self.get_enabled_stats()

        if "sysinfo" in stnames:
            stnames.remove("sysinfo")
            if sysinfo:
                _LOG.info("Collecting more %s system information", self._sutname)
                SysInfo.collect_after(self._statsdir / "sysinfo", self._pman)

        if not stnames:
            return

        self._ensure_min_collect_time()
        self._send_command("stop")
        self._start_time = None

    def _get_failed_collectors(self):
        """
        Requests failed statistics names from 'stc-agent' and returns their names in form of a
        'set()'.
        """

        result = self._send_command("get-failed-collectors")
        if not result:
            _LOG.debug("no collectors failed")
            return set()

        result = result.split(",")
        _LOG.debug("the following collectors failed: %s", ", ".join(result))
        return set(result)

    def _init_paths(self):
        """Helper function for '_start_stc_agent()' that discovers and initializes various paths."""

        # Discover path to 'stc-agent'.
        if not self.scpath:
            self.scpath = self._pman.which("stc-agent")

        is_root = ProcHelpers.is_root(pman=self._pman)

        if not self._unshare_path and is_root:
            # Unshare is used for running 'stc-agent' in a separate PID namespace. We do this
            # because when the PID 1 process of the namespace is killed, all other processes get
            # automatically killed. This helps to easily and reliably clean up processes upon exit.
            # But creating a PID namespace requires 'root'.
            self._unshare_path = self._pman.which("unshare", must_find=False)
            if not self._unshare_path:
                _LOG.warning("the 'unshare' tool is missing%s, it is recommended to have it "
                             "installed. This tool is part of the 'util-linux' project",
                             self._pman.hostmsg)

        if not self._nice_path and is_root:
            # We are trying to run 'stc-agent' with high priority, because we want the statistics to
            # be collected at steady intervals. The 'nice' tool helps changing the priority of the
            # process.
            self._nice_path = self._pman.which("nice", must_find=False)
            if not self._nice_path:
                _LOG.warning("the 'nice' tool is missing%s, it is recommended to have it "
                             "installed. This tool is part of the 'coreutils' project",
                             self._pman.hostmsg)

    def _fetch_stat_collect_socket_path(self):
        """
        This is a helper for '_start_stc_agent()'. When 'stc-agent' starts, it prints unix socket
        path it is listening for connections on. This functions parses 'stc-agent' output and
        fetches the socket path.
        """

        # Spend max. 5 secs waiting for 'stc-agent' to startup and print the socket file path.
        attempts = 0
        while not self._uspath and attempts < 5:
            _, _, exitcode = self._sc.wait(timeout=1, capture_output=False)
            attempts += 1

            logdata = logerr = None
            try:
                with self._pman.open(self._logpath, "r") as fobj:
                    logdata = fobj.read()
            except Error as logerr:
                pass

            if exitcode is not None:
                msg = self._pman.get_cmd_failure_msg(self._cmd, logdata, None, exitcode)
                if not logdata:
                    msg += f"\nCheck '{self._logpath}'{self._pman.hostmsg} for details"
                raise Error(msg)

            if not logdata:
                # The log file has not been created yet or has no data yet.
                continue

            # Search for the socket file path in the log.
            pfx = "Listening on Unix socket "
            for line in logdata.splitlines():
                if line.startswith(pfx):
                    self._uspath = line.strip()[len(pfx):]
                    break

        if self._uspath:
            _LOG.debug("stc-agent PID: %d, socket file path: %s", self._sc.pid, self._uspath)

            self._sc_id = f"{self._pman.hostname}:{self._uspath}"
            msg = f"stc-agent (PID {self._sc.pid}) that reported it is listening on Unix " \
                  f"socket {self._uspath}{self._pman.hostmsg}"

            try:
                if self._pman.is_socket(Path(self._uspath)):
                    return
            except Error as err:
                msg = f"{msg}\nBut checking the file path failed: {err}"
            else:
                msg = f"{msg}\nBut this is not a Unix socket file"
        else:
            # Failed to extract socket file path.
            if exitcode is None:
                with contextlib.suppress(Error):
                    ProcHelpers.kill_pids([self._sc.pid, ], kill_children=True, must_die=False,
                                          pman=self._pman)

            msg = f"failed to extract socket file path from 'stc-agent' log\n" \
                  f"The command was: {self._cmd}\n" \
                  f"The log is in '{self._logpath}'{self._pman.hostmsg}"

        if logerr:
            msg += f"\nFailed to read the log file: {logerr}"
        elif logdata:
            msg += f"\nLog file contents was:\n{logdata}"

        raise Error(msg)

    def _setup_stc_agent_ssh_forwarding(self):
        """
        This is a helper function for '_start_stc_agent()' which sets up an SSH forwarding between
        local host and the SUT.

        'stc-agent' always listens on a Unix socket, which means that we cannot directly connect to
        it when 'stc-agent' runs on a remote host. Therefore, we create an SSH tunnel which will
        forward TCP stream between a local TCP port the remote Unix socket.
        """

        pman = self._pman
        self._ssht_port = RemoteHelpers.get_free_port()
        self._sc_id = f"{self._ssht_port}:{pman.hostname}:{self._uspath}"


        ssh_opts = pman.get_ssh_opts()
        cmd = f"ssh -L {self._ssht_port}:{self._uspath} -N {ssh_opts} {pman.hostname}"
        with LocalProcessManager.LocalProcessManager() as lpman:
            self._ssht = lpman.run_async(cmd)

        # Wait the tunnel to get established.
        start_time = time.time()
        timeout = max(pman.connection_timeout, 5)
        msg = f"failed to establish SSH tunnel between localhost and {pman.hostname} " \
              f"with this command:\n{cmd}"

        while time.time() - start_time <= timeout:
            _LOG.debug("trying to connect to localhost:%s", self._ssht_port)
            # pylint: disable=no-member
            stdout, stderr, exitcode = self._ssht.wait(timeout=1, capture_output=True)

            if exitcode is not None:
                raise Error(pman.get_cmd_failure_msg(cmd, stdout, stderr, exitcode, startmsg=msg))

            try:
                self._connect()
            except Error:
                pass
            else:
                self._disconnect()
                return

        raise Error(f"{msg}\nTried for {timeout} seconds, but could not connect to "
                    f"localhost:{self._ssht_port}\nCheck '{self._logpath}'{pman.hostmsg} for "
                    f"details")

    def _get_unshare_version(self):
        """
        Returns version number of the 'unshare' program installed on the system where 'stc-agent' is
        going to be executed.
        """

        stdout, _ = self._pman.run_verify(f"{self._unshare_path} --version")
        # The expected output example: unshare from util-linux 2.35.2.
        return stdout.split(" ")[-1].strip()

    def _start_stc_agent(self):
        """Helper function for 'configure()' that starts 'stc-agent'."""

        self._init_paths()

        # Kill a possibly running stale 'stc-agent' process.
        msg = f"stale {self.scpath} process{self._pman.hostmsg}"
        ProcHelpers.kill_processes(self._sc_search, kill_children=True, log=True, name=msg,
                                   pman=self._pman)
        if self._pman.is_remote:
            # Kill a possibly running stale SSH tunnel process.
            msg = f"stale stc-agent SSH tunnel process{self._pman.hostmsg}"
            ProcHelpers.kill_processes(self._ssht_search, kill_children=True, log=True, name=msg,
                                       pman=self._pman)

        # Format the command for executing 'stc-agent'.
        self._cmd = f"{self.scpath} --sut-name {self._sutname}"
        if _LOG.getEffectiveLevel() == logging.DEBUG:
            self._cmd = f"{self._cmd} -d"

        self._logpath = self._logsdir / f"stc-agent-{self._pman.hostname}.log.txt"
        self._cmd = f"{self._cmd} > '{self._logpath}' 2>&1"

        # And format the 'stc-agent' command prefix.
        cmd_prefix = ""
        if self._unshare_path:
            # Older version of 'unshare' did not support the '--kill-child' option. Note, unshare
            # version structure is similar to kernel version, so we use 'KernelVersion' module.
            ver = self._get_unshare_version()
            if KernelVersion.kver_ge(ver, "2.32"):
                opt_kc = " --kill-child"
            else:
                opt_kc = ""
            cmd_prefix += f"{self._unshare_path} --pid --fork --mount-proc{opt_kc} -- "

        if self._nice_path:
            cmd_prefix += f"{self._nice_path} -n -20 -- "

        if cmd_prefix:
            self._cmd = f"{cmd_prefix} {self._cmd}"

        self._sc = self._pman.run_async(self._cmd, shell=True)
        self._fetch_stat_collect_socket_path()

        if self._pman.is_remote:
            # 'stc-agent' runs on the SUT and we cannot connect to the Unix socket file directly.
            # Setup SSH forwarding.
            self._setup_stc_agent_ssh_forwarding()

    def _init_outdir(self, discovery=False):
        """
        Helper function for 'configure()' that creates the output directory and various of its
        sub-direcories.
        """

        if not self.outdir:
            self.outdir = self._pman.mkdtemp(prefix="stc-agent-")
            self._outdir_created = True
            _LOG.debug("created output directory '%s'%s", self.outdir, self._pman.hostmsg)
        else:
            try:
                self._pman.mkdir(self.outdir, parents=True)
            except ErrorExists:
                pass
            else:
                self._outdir_created = True

        self._logsdir = self.outdir / "logs"
        self._pman.mkdir(self._logsdir, exist_ok=True)

        if discovery:
            # The statistics collected during discovery belong to the logs.
            self._statsdir = self._logsdir / "discovery-stats"
        else:
            self._statsdir = self.outdir / "stats"
        self._pman.mkdir(self._statsdir, exist_ok=True)

    def configure(self, discovery=False):
        """Configure statistic collectors."""

        stnames = self.get_enabled_stats()
        sysinfo = False
        if "sysinfo" in stnames:
            stnames.remove("sysinfo")
            sysinfo = True

        if not stnames:
            _LOG.debug("skip starting stc-agent%s - no statistics collectors",
                       self._pman.hostmsg)
            if sysinfo:
                self._init_outdir(discovery=False)
            return

        self._init_outdir(discovery=discovery)
        if not self._sc:
            self._start_stc_agent()
        if not self._sock:
            self._connect()

        self._send_command("set-stats", arg=",".join(stnames))

        for stname in stnames:
            self._set_collector_property(stname, "outdir", self._statsdir)
            self._set_collector_property(stname, "logdir", self._logsdir)
            self._set_collector_property(stname, "toolpath", self.stinfo[stname]["toolpath"])
            self._set_collector_property(stname, "interval", self.stinfo[stname]["interval"])
            self._set_collector_property(stname, "fallible", self.stinfo[stname]["fallible"])

        # Configure all the statistics-specific properties.
        for stname in stnames:
            for name, value in self.stinfo[stname]["props"].items():
                if value:
                    self._set_collector_property(stname, name, value)

        self._send_command("configure")

    def discover(self):
        """Discover and return list of statistics that can be collected."""

        stnames = self.get_enabled_stats()
        _LOG.debug("discovery: trying the following statistics: %s", ", ".join(stnames))

        if stnames:
            with contextlib.suppress(SCReplyError):
                self.configure(discovery=True)
                self.start(sysinfo=False)
                self.stop(sysinfo=False)

            stnames -= self._get_failed_collectors()

        _LOG.debug("discovered the following statistics: %s", ", ".join(stnames))
        return stnames

    def get_enabled_stats(self):
        """Return the list of enabled statistics."""

        return {stname for stname, stinfo in self.stinfo.items() if stinfo["enabled"]}

    def __init__(self, pman, sutname, outdir=None, scpath=None):
        """
        Initialize a class instance. The input arguments are as follows.
          * pman - a process manager associated with the host to run 'stc-agent' on.
          * outdir - path to the directory to store the logs and the collected statistics. Stored in
                     a temporary directory if not provided.
          * sutname - name of the System Under Test. Will be used for messages and searching for
                      stale 'stc-agent' process instances for the same SUT.
          * scpath - path to 'stc-agent' on the host defined by 'pman'. Searched for in '$PATH'
                     if not provided.
        """

        self._pman = pman
        self._sutname = sutname
        self.outdir = outdir
        self.scpath = scpath

        self.stinfo = DEFAULT_STINFO.copy()

        # Whether the 'self._pman' object should be closed.
        self._close_pman = False
        # The commant to start 'stc-agent'.
        self._cmd = None

        # Paths to the 'unshare' and 'nice' tools on the same host where 'stc-agent' runs.
        self._unshare_path = None
        self._nice_path = None

        self._outdir_created = False
        self._statsdir = None
        self._logsdir = None
        self._logpath = None

        # The 'stc-agent' process search pattern.
        self._sc_search = f"{self.scpath} --sut-name {self._sutname}"
        # The SSH tunnel process search pattern.
        self._ssht_search = f"ssh -L .*:.*stc-agent-{self._sutname}-.* -N"

        self._sc = None
        self._sc_id = None
        self._uspath = None
        self._ssht = None
        self._ssht_port = None
        self._sock = None
        self._timeout = 60
        self._start_time = None

        # Initialize the statistics dictionary.
        _set_stinfo_defaults(self.stinfo)

    def close(self):
        """Close the statistics collector."""

        if getattr(self, "_sock", None):
            if self._start_time:
                with contextlib.suppress(Exception):
                    self._send_command("stop")
            with contextlib.suppress(Exception):
                self._send_command("exit")
            with contextlib.suppress(Exception):
                self._disconnect()
            self._sock = None

        if getattr(self, "_pman", None):
            if self._ssht:
                with contextlib.suppress(Exception):
                    ProcHelpers.kill_processes(self._ssht_search, pman=self._pman)
                self._ssht = None

            if self._sc:
                with contextlib.suppress(Exception):
                    ProcHelpers.kill_processes(self._sc_search, pman=self._pman)
                self._sc = None

            # Remove the output directory if we created it.
            if getattr(self, "_outdir_created", None):
                with contextlib.suppress(Exception):
                    self._pman.rmtree(self.outdir)
                self._outdir_created = None

            if getattr(self, "_close_pman", None):
                self._pman.close()
            self._pman = None

class _InBandCollector(_Collector):
    """
    This class handles the "in-band" statistics collection. In this case, 'stc-agent' runs on the
    SUT and statistics collectors also run on the SUT.
    """

    def __init__(self, pman, outdir=None, scpath=None):
        """Initialize a class instance. The arguments are the same as in 'STCAgent.__init__()'."""

        # Call the base class constructor.
        super().__init__(pman, pman.hostname, outdir=outdir, scpath=scpath)

        # Cleanup 'self.stinfo' by removing out-of-band statistics.
        for stname in list(self.stinfo):
            if not self.stinfo[stname]["inband"]:
                del self.stinfo[stname]

class _OutOfBandCollector(_Collector):
    """
    This class handles the "out-of-band" statistics collection. In this case, 'stc-agent' runs on
    the local host, but it collects information about the SUT via an "out-of-band" channel.

    One example of an "out-of-band" collector is "acpower": it reads power meter data on the local
    host via something like USB or serial. The power meter, however, measures SUT power consumption.

    Another example is the "ipmi" collector. It runs the 'ipmitool' on the local host, but the tool
    collects information about the SUT by talking to SUT's BMC module via the network.
    """

    def __init__(self, sutname, outdir=None, scpath=None):
        """
        Initialize a class instance. The 'sutname' argument is name of the SUT to collect the
        statistics for. This string will be passed over to 'stc-agent' and will affect its messages.
        It will also be used fo distinguishing between multiple 'stc-agent' processes. This name
        will not be used for connecting to the SUT.

        The other arguments are the same as in 'STCAgent.__init__()'.
        """

        # Call the base class constructor.
        pman = LocalProcessManager.LocalProcessManager()
        super().__init__(pman, sutname, outdir=outdir, scpath=scpath)

        # Make sure we close the process manager.
        self._close_pman = True

        # Cleanup 'self.stinfo' by removing in-band statistics.
        for stname in list(self.stinfo):
            if self.stinfo[stname]["inband"]:
                del self.stinfo[stname]
