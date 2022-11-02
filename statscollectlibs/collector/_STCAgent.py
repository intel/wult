# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module provides two statistic collector classes: 'InBandCollector' and 'OutOfBandCollector'.
"""

import copy
import time
import socket
import logging
import contextlib
from pathlib import Path
from pepclibs.helperlibs import LocalProcessManager, Trivial, ClassHelpers
from pepclibs.helperlibs.Exceptions import Error, ErrorExists
from statscollectlibs.collector import SysInfo
from statscollectlibs.helperlibs import KernelVersion, ProcHelpers, RemoteHelpers

_LOG = logging.getLogger()

# The message delimiter used by 'stc-agent'.
_DELIMITER = "--\n".encode("utf-8")

# The default statistics information. This dictionary is used by the '_STCAgent' class by default,
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
# ipmi-oob:
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
STINFO = {
    "sysinfo" : {
        "interval" : None,
        "inband" : True,
        "toolpath" : None,
        "description" : "Not really a statistics collector, but just a script that saves all sorts "
                        "of information about the SUT (e.g., 'dmesg', 'lspci -vvv' and 'dmidecode' "
                        "output, and more). One snapshot of the SUT information is taken before "
                        "the workload, and the other snapshot is taken after the workload. The "
                        "second snapshot, however, includes only the information that could "
                        "potentially change while the workload was running (e.g., 'dmesg' may "
                        "include new messages).",
    },
    "turbostat" : {
        "interval" : 5,
        "inband" : True,
        "toolpath" : "turbostat",
        "description" : "Periodically run the 'turbostat' tool and collect C-state residency, "
                        "average CPU frequency, RAPL data, and more.",
    },
    "ipmi-oob" : {
        "interval" : 5,
        "inband" : False,
        "fallible" : True,
        "toolpath" : "ipmi-helper",
        "description" : "Periodically run 'ipmitool' to collect platform IPMI data, such as fans "
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
    "ipmi-inband" : {
        "interval" : 5,
        "inband" : True,
        "fallible" : True,
        "toolpath" : "ipmi-helper",
        "description" : "Same as the 'ipmi-oob' statistics, but the data are collected by running "
                        "'ipmitool' on the SUT (in-band).",
    },
    "acpower" : {
        "interval" : 1,
        "inband" : False,
        "toolpath" : "yokotool",
        "description" : "Collect SUT wall socket power consumption from an external Yokogawa power "
                       "meter using 'yokotool'.",
        "props" : {
            "devnode" : None,
            "pmtype" : None,
        }
    },
}

class SCReplyError(Error):
    """This exception is raised when 'stc-agent' replies that a command has failed."""

class _STCAgent(ClassHelpers.SimpleCloseContext):
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
                # Connect to 'stc-agent' directly via the Unix socket file.
                self._sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                self._sock.connect(self._uspath)
        except socket.error as err:
            raise Error(f"cannot connect to 'stc-agent' at {self._stca_id}:\n{err}") from err

        _LOG.debug("connected to 'stc-agent' at %s", self._stca_id)

    def _disconnect(self):
        """Disconnect from 'stc-agent'."""

        assert self._sock

        try:
            self._sock.shutdown(socket.SHUT_RDWR)
            self._sock.close()
            self._sock = None
        except socket.error as err:
            raise Error(f"cannot disconnect from 'stc-agent' at {self._stca_id}: {err}") from err

        _LOG.debug("disconnected from 'stc-agent' at %s", self._stca_id)

    def _send_msg(self, msg):
        """Send a message to 'stc-agent'."""

        buf = msg.encode("utf-8") + _DELIMITER
        total = 0

        while total < len(buf):
            sent = self._sock.send(buf[total:])
            if sent == 0:
                raise Error(f"'stc-agent' at {self._stca_id} closed the connection")
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
                raise Error(f"'stc-agent' at {self._stca_id} closed the connection")

            # This inefficient, but good enough for our small messages.
            msg += buf
            if msg[-len(_DELIMITER):] == _DELIMITER:
                return msg[:-len(_DELIMITER)].decode("utf-8")

        raise Error(f"time out waiting for the 'stc-agent' response at {self._stca_id}")

    def _send_command(self, cmd, arg=None):
        """Send a command to 'stc-agent', verify and return the response."""

        if arg:
            cmd += " " + arg

        stca_str = f"'stc-agent' at {self._stca_id}"
        check_log_msg = f"Check 'stc-agent' log file{self._pman.hostmsg}':\n{self._logpath}"

        _LOG.debug("sending the following command to %s:\n%s", stca_str, cmd)

        try:
            self._send_msg(cmd)
        except (Error, socket.error) as err:
            raise Error(f"failed to send the following message to "
                        f"{stca_str}:\n{cmd}\n{err}\n{check_log_msg}") from err

        try:
            msg = self._recv_msg()
        except (Error, socket.error) as err:
            raise Error(f"failed receiving the reply to the following command from {stca_str}: "
                        f"{cmd}\n{err}\n{check_log_msg}") from err

        if msg == "OK":
            return None

        if msg.startswith("OK "):
            return msg[3:]

        raise SCReplyError(f"{stca_str} did not respond with 'OK' to the following command:\n{cmd}"
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
        collectors use intervals from the 'STINFO' statistics description dictionary. Returns a
        dictionary of the same structure as 'interval', but with interval values that will actually
        be used for all the statistics collectors.
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

    def set_stcagent_path(self, path):
        """
        Configure the 'stc-agent' program path. The arguments are as follows.
          * path - path to the 'stc-agent' program. If 'None', the program will be searched for in
                   the paths defined by the 'PATH' environment variable.
        """

        if self._stca:
            raise Error(f"cannot set 'stc-agent' path to '{path}'{self._pman.hostmsg}: the program "
                        f"has already been started")
        self._stca_path = path

    def _stname_enabled(self, stname):
        """
        Helper function for '_ensure_min_collect_time()'. Returns 'True' if the statistic 'stname'
        is in 'stinfo' and enabled. Otherwise, returns 'False'.
        """

        if stname not in self.stinfo:
            return False
        return self.stinfo[stname]["enabled"]

    def get_max_interval(self):
        """
        Returns the maximum statistics collection interval value for all enabled statistics in
        'stinfo'.
        """

        intervals = []
        for info in self.stinfo.values():
            if info["enabled"] and info["interval"] is not None:
                intervals.append(info["interval"])

        if intervals:
            return max(intervals)

        return 0

    def _ensure_min_collect_time(self):
        """
        This method makes sure all statistics collector made progress and collected at least one
        piece of statistics.
        """

        if not self._start_time:
            raise Error("statistics collection did not start yet")

        max_interval = self.get_max_interval()
        if max_interval == 0:
            return

        # Add some margin of safety.
        max_interval += 1

        if self._stname_enabled("ipmi-inband") or self._stname_enabled("ipmi-oob"):
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
                _LOG.log(self.infolvl, "Collecting %s system information", self._sutname)
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
                _LOG.log(self.infolvl, "Collecting more %s system information", self._sutname)
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

        if not self._stca:
            return set()

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
        if not self._stca_path:
            self._stca_path = self._pman.which("stc-agent")

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

    def _fetch_stcagent_socket_path(self):
        """
        This is a helper for '_start_stc_agent()'. When 'stc-agent' starts, it prints unix socket
        path it is listening for connections on. This functions parses 'stc-agent' output and
        fetches the socket path.
        """

        # Spend max. 5 secs waiting for 'stc-agent' to startup and print the socket file path.
        attempts = 0
        while not self._uspath and attempts < 5:
            _, _, exitcode = self._stca.wait(timeout=1, capture_output=False)
            attempts += 1

            logdata = logerr = None
            try:
                with self._pman.open(self._logpath, "r") as fobj:
                    logdata = fobj.read()
            except Error:
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
            _LOG.debug("stc-agent PID: %d, socket file path: %s", self._stca.pid, self._uspath)

            self._stca_id = f"{self._pman.hostname}:{self._uspath}"
            msg = f"stc-agent (PID {self._stca.pid}) that reported it is listening on Unix " \
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
                    ProcHelpers.kill_pids([self._stca.pid, ], kill_children=True, must_die=False,
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
        self._stca_id = f"{self._ssht_port}:{pman.hostname}:{self._uspath}"


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
        msg = f"stale {self._stca_path} process"
        self._stca_search = f"{self._stca_path} --sut-name {self._sutname}"
        ProcHelpers.kill_processes(self._stca_search, kill_children=True, log=True, name=msg,
                                   pman=self._pman)
        if self._pman.is_remote:
            # Kill a possibly running stale SSH tunnel process.
            msg = "stale stc-agent SSH tunnel process"
            self._ssht_search = f"ssh -L .*:.*stc-agent-{self._sutname}-.* -N"
            ProcHelpers.kill_processes(self._ssht_search, kill_children=True, log=True, name=msg,
                                       pman=self._pman)

        # Format the command for executing 'stc-agent'.
        self._cmd = f"{self._stca_path} --sut-name {self._sutname}"
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

        self._stca = self._pman.run_async(self._cmd, shell=True)
        self._fetch_stcagent_socket_path()

        if self._pman.is_remote:
            # 'stc-agent' runs on the SUT and we cannot connect to the Unix socket file directly.
            # Setup SSH forwarding.
            self._setup_stc_agent_ssh_forwarding()

    def _init_outdir(self, for_discovery=False):
        """
        Helper function for 'configure()' that creates the output directory and various of its
        sub-directories.
        """

        self._logsdir = self.outdir / "logs"
        self._pman.mkdir(self._logsdir, exist_ok=True)

        if for_discovery:
            # The statistics collected during discovery belong to the logs.
            self._statsdir = self._logsdir / "discovery-stats"
        else:
            self._statsdir = self.outdir / "stats"
        self._pman.mkdir(self._statsdir, exist_ok=True)

    def _configure(self, stnames, for_discovery=False):
        """
        Configure statistic collectors. If 'for_discovery' is 'True', configure the collectors for
        running the discovery process. Otherwise configure the collectors for collecting the
        statistics.
        """

        sysinfo = False
        if "sysinfo" in stnames:
            stnames = stnames.copy()
            stnames.remove("sysinfo")
            sysinfo = True

        if not stnames:
            _LOG.debug("skip starting stc-agent%s - no statistics collectors",
                       self._pman.hostmsg)
            if sysinfo:
                self._init_outdir(for_discovery=False)
            return

        self._init_outdir(for_discovery=for_discovery)
        if not self._stca:
            self._start_stc_agent()
        if not self._sock:
            self._connect()

        self._send_command("set-stats", arg=",".join(stnames))

        for stname in stnames:
            self._set_collector_property(stname, "outdir", self._statsdir)
            self._set_collector_property(stname, "logdir", self._logsdir)
            self._set_collector_property(stname, "toolpath", self.stinfo[stname]["toolpath"])
            self._set_collector_property(stname, "interval", self.stinfo[stname]["interval"])

            # During discovery, all collectors should be fallible so that if one fails, it doesn't
            # block the discovery of other collectors.
            fallible = True if for_discovery else self.stinfo[stname]["fallible"]
            self._set_collector_property(stname, "fallible", fallible)

        # Configure all the statistics-specific properties.
        for stname in stnames:
            for name, value in self.stinfo[stname]["props"].items():
                if value:
                    self._set_collector_property(stname, name, value)

        self._send_command("configure")

    def configure(self, stnames=None):
        """Configure statistic collectors."""

        if not stnames:
            stnames = self.get_enabled_stats()

        if not stnames:
            _LOG.debug("no enabled statistics, skip configuring statistics%s", self._pman.hostmsg)
            return

        self._configure(stnames, for_discovery=False)

    def discover(self, stnames=None):
        """
        Discover and return list of statistics that can be collected. Optionally, use the 'stnames'
        parameter to specify a set containing the names of statistics to be checked. If 'stnames' is
        not provided, checks all enabled statistics.
        """

        if not stnames:
            stnames = self.get_enabled_stats()

        if not stnames:
            _LOG.debug("no enabled statistics, skip discovery%s", self._pman.hostmsg)
            return stnames

        _LOG.debug("discovery: trying the following statistics%s: %s",
                   self._pman.hostmsg, ", ".join(stnames))

        with contextlib.suppress(SCReplyError):
            self._configure(stnames, for_discovery=True)
            self.start(sysinfo=False)
            self.stop(sysinfo=False)

        stnames -= self._get_failed_collectors()
        _LOG.debug("discovered the following statistics%s: %s",
                   self._pman.hostmsg, ", ".join(stnames))

        return stnames

    def get_enabled_stats(self):
        """Return the list of enabled statistics."""

        return {stname for stname, stinfo in self.stinfo.items() if stinfo["enabled"]}

    def get_disabled_stats(self):
        """Return the list of disabled statistics."""

        return {stname for stname, stinfo in self.stinfo.items() if not stinfo["enabled"]}

    def _set_stinfo_defaults(self):
        """Add default keys to the statistics description dictionary."""

        for info in self.stinfo.values():
            if "enabled" not in info:
                info["enabled"] = False
            if "fallible" not in info:
                info["fallible"] = False
            if "props" not in info:
                info["props"] = {}

    def __init__(self, pman, sutname, outdir=None, stca_path=None):
        """
        Initialize a class instance. The input arguments are as follows.
          * pman - a process manager associated with the host to run 'stc-agent' on.
          * outdir - path to the directory to store the logs and the collected statistics. Stored in
                     a temporary directory if not provided.
          * sutname - name of the System Under Test. Will be used for messages and searching for
                      stale 'stc-agent' process instances for the same SUT.
          * stca_path - path to 'stc-agent' program on the host defined by 'pman'. Searched for in
                      '$PATH' if not provided.
        """

        self._pman = pman
        self._sutname = sutname
        self.outdir = outdir
        self._stca_path = stca_path

        # The statistics information dictionary.
        self.stinfo = None

        # Log level for some of the high-level messages.
        self.infolvl = logging.DEBUG

        # Whether the 'self._pman' object should be closed.
        self._close_pman = False
        # The command to start 'stc-agent'.
        self._cmd = None

        # Paths to the 'unshare' and 'nice' tools on the same host where 'stc-agent' runs.
        self._unshare_path = None
        self._nice_path = None

        self._outdir_created = False
        self._statsdir = None
        self._logsdir = None
        self._logpath = None

        # The 'stc-agent' process search pattern.
        self._stca_search = None
        # The SSH tunnel process search pattern.
        self._ssht_search = None

        self._stca = None
        self._stca_id = None
        self._uspath = None
        self._ssht = None
        self._ssht_port = None
        self._sock = None
        self._timeout = 60
        self._start_time = None

        # Initialize the statistics dictionary.
        self.stinfo = copy.deepcopy(STINFO)
        self._set_stinfo_defaults()

        if not self.outdir:
            self.outdir = self._pman.mkdtemp(prefix="stc-agent-")
            self._outdir_created = True
            _LOG.debug("created output directory '%s'%s", self.outdir, self._pman.hostmsg)
        else:
            self.outdir = self._pman.abspath(self.outdir)
            try:
                self._pman.mkdir(self.outdir, parents=True)
            except ErrorExists:
                pass
            else:
                self._outdir_created = True

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

            if self._stca:
                with contextlib.suppress(Exception):
                    ProcHelpers.kill_processes(self._stca_search, pman=self._pman)
                self._stca = None

            # Remove the output directory if we created it.
            if getattr(self, "_outdir_created", None):
                with contextlib.suppress(Exception):
                    self._pman.rmtree(self.outdir)
                self._outdir_created = None

            if getattr(self, "_close_pman", None):
                self._pman.close()
            self._pman = None

class InBandCollector(_STCAgent):
    """
    This class handles the "in-band" statistics collection. In this case, 'stc-agent' runs on the
    SUT and statistics collectors also run on the SUT.
    """

    def __init__(self, pman, outdir=None, stca_path=None):
        """
        Initialize a class instance. The arguments are the same as in '_STCAgent.__init__()'.
        """

        # Call the base class constructor.
        super().__init__(pman, pman.hostname, outdir=outdir, stca_path=stca_path)

        # Cleanup 'self.stinfo' by removing out-of-band statistics.
        for stname in list(self.stinfo):
            if not self.stinfo[stname]["inband"]:
                del self.stinfo[stname]

class OutOfBandCollector(_STCAgent):
    """
    This class handles the "out-of-band" statistics collection. In this case, 'stc-agent' runs on
    the local host, but it collects information about the SUT via an "out-of-band" channel.

    One example of an "out-of-band" collector is "acpower": it reads power meter data on the local
    host via something like USB or serial. The power meter, however, measures SUT power consumption.

    Another example is the "ipmi-oob" collector. It runs the 'ipmitool' on the local host, but the
    tool collects information about the SUT by talking to SUT's BMC module via the network.
    """

    def __init__(self, sutname, outdir=None, stca_path=None):
        """
        Initialize a class instance. The 'sutname' argument is name of the SUT to collect the
        statistics for. This string will be passed over to 'stc-agent' and will affect its messages.
        It will also be used for distinguishing between multiple 'stc-agent' processes. This name
        will not be used for connecting to the SUT.

        The other arguments are the same as in '_STCAgent.__init__()'.
        """

        # Call the base class constructor.
        pman = LocalProcessManager.LocalProcessManager()
        super().__init__(pman, sutname, outdir=outdir, stca_path=stca_path)

        # Make sure we close the process manager.
        self._close_pman = True

        # Cleanup 'self.stinfo' by removing in-band statistics.
        for stname in list(self.stinfo):
            if self.stinfo[stname]["inband"]:
                del self.stinfo[stname]
