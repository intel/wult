# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module provides API for dealing with Linux function trace buffer.
"""

import logging
import contextlib
import re
from pepclibs.helperlibs import ClassHelpers, KernelVersion
from pepclibs.helperlibs.Exceptions import Error, ErrorNotSupported, ErrorTimeOut
from statscollectlibs.helperlibs import ProcHelpers
from wultlibs.helperlibs import FSHelpers

_LOG = logging.getLogger()

class FTraceLine():
    """
    This class represents an ftrace buffer line. When an instance is created, the trace buffer line
    is split and the following attributes become available.
      * procname - process name.
      * pid - process PID.
      * cpunum - logical CPU number.
      * flags - trace flags.
      * timestamp - the trace timestamp.
      * func - name of the kernel function where the trace happened.
      * msg - the trace buffer message (comes after all the standard prefixes including process
      *       name, PID, etc)
      * line - full trace buffer line (includes all the standard prefixes)
    """

    def __init__(self, line):
        """Create a class instance for trace buffer line 'line'."""

        self.line = line.strip()
        self.procname = None
        self.pid = None
        self.cpunum = None
        self.flags = None
        self.timestamp = None
        self.func = None
        self.msg = None

        split = self.line.split(maxsplit=5)
        if len(split) == 6:
            procinfo, self.cpunum, self.flags, self.timestamp, self.func, self.msg = split
            self.procname, self.pid = procinfo.split("-")

class FTrace(ClassHelpers.SimpleCloseContext):
    """This class represents the Linux function trace buffer."""

    def _reset_state(self):
        """Reset the function tracer to a known state."""

        # Enable tracing if necessary.
        with self._pman.open(self._paths["tracing_on"], "w+") as fobj:
            val = fobj.read()
            if val.strip() != "1":
                _LOG.debug("enabling tracing")
                fobj.write("1")
                self._disable_tracing = True

        # Set current tracer to 'nop'. There are multiple ftrace output formats, and not all are
        # supported by this module. Reset ftrace to the default format.
        with self._pman.open(self._paths["current_tracer"], "w+") as fobj:
            val = fobj.read()
            if val.strip() != "nop":
                _LOG.debug("setting tracer to 'nop'")
                fobj.write("nop")

        # Disable all trace events.
        with self._pman.open(self._paths["set_event"], "w") as fobj:
            _LOG.debug("clearing trace events")
            fobj.write("")

        # Clear the function trace buffer.
        _LOG.debug("clearing the trace buffer")
        with self._pman.open(self._paths["trace"], "w+") as fobj:
            fobj.write("0")

    def getlines(self):
        """
        Yield trace buffer lines one-by-one. Wait for a trace line for maximum 'timeout' seconds.
        """

        if self._reader is None:
            self._reader = self._pman.run_async(self._reader_cmd)

        while True:
            stdout, stderr, exitcode = self._reader.wait(timeout=self.timeout, lines=[32, None],
                                                         join=False)

            if not stdout and not stderr and exitcode is None:
                raise ErrorTimeOut(f"no data in trace buffer for {self._reader.timeout} seconds"
                                   f"{self._pman.hostmsg}")


            # The process has terminated or printed something to standard error.
            if exitcode is not None or stderr:
                msg = self._reader.get_cmd_failure_msg(stdout, stderr, exitcode)

                # Check for 6.5 kernel bug. Attempting to open trace_pipe will return -EBUSY. Detect
                # this situation and print a useful error to the user.
                if re.search("trace_pipe: Device or resource busy", msg, re.MULTILINE):
                    kver = KernelVersion.get_kver(pman=self._pman)
                    if KernelVersion.kver_ge(kver, "6.5") and KernelVersion.kver_lt(kver, "6.6"):
                        raise Error(f"kernel bug detected with kernel {kver}. Trace subsystem with "
                                    f"6.5-6.6 kernels is known to be bugged, please upgrade your "
                                    f"kernel to latest 6.5-stable or 6.6-rc2.")
                raise Error(f"the function trace reader process has exited unexpectedly:\n{msg}")

            for line in stdout:
                if line.startswith("#"):
                    continue
                self.raw_line = line.strip()
                yield FTraceLine(line)

    def __init__(self, pman, cpunum, timeout=30):
        """
        Class constructor. The arguments are as follows.
          * pman - the process manager object that defines the host to operate on.
          * cpunum - the CPU to read trace buffer for.
          * timeout - longest time in seconds to wait for data in the trace buffer.
        """

        self._reader = None
        self._reader_cmd = None
        self._pman = pman
        self.timeout = timeout

        self._paths = {}
        self._debugfs_mntpoint = None
        self._unmount_debugfs = None
        self._disable_tracing = None
        self.raw_line = None

        self._debugfs_mntpoint, self._unmount_debugfs = FSHelpers.mount_debugfs(pman=self._pman)
        self._paths["trace"] = self._debugfs_mntpoint.joinpath("tracing/trace")
        self._paths["trace_pipe"] = \
            self._debugfs_mntpoint.joinpath(f"tracing/per_cpu/cpu{cpunum}/trace_pipe")
        self._paths["tracing_on"] = self._debugfs_mntpoint.joinpath("tracing/tracing_on")
        self._paths["current_tracer"] = self._debugfs_mntpoint.joinpath("tracing/current_tracer")
        self._paths["set_event"] = self._debugfs_mntpoint.joinpath("tracing/set_event")

        for path in self._paths.values():
            if not self._pman.is_file(path):
                raise ErrorNotSupported(f"linux ftrace file '{path}' not found{self._pman.hostmsg}")

        self._reader_cmd = f"cat {self._paths['trace_pipe']}"
        name = "stale wult function trace reader process"
        ProcHelpers.kill_processes(self._reader_cmd, kill_children=True, log=True, name=name,
                                   pman=self._pman)

        self._reset_state()

    def enable_event(self, event):
        """Enable trace event 'event'."""

        path = self._debugfs_mntpoint.joinpath(f"tracing/events/{event}/enable")
        _LOG.debug("enabling trace event '%s'", event)

        with self._pman.open(path, "w") as fobj:
            fobj.write("1")

    def close(self):
        """Stop following the function trace buffer."""

        if getattr(self, "_pman", None) and getattr(self, "_reader", None):
            if getattr(self._reader, "pid", None):
                _LOG.debug("killing the function trace reader process PID %d%s",
                           self._reader.pid, self._pman.hostmsg)
                ProcHelpers.kill_pids(self._reader.pid, kill_children=True, must_die=False,
                                      pman=self._pman)
            self._reader.close()

        if getattr(self, "_disable_tracing", None):
            with contextlib.suppress(Error):
                with self._pman.open(self._paths["tracing_on"], "w+") as fobj:
                    fobj.write("0")
                self._disable_tracing = False

        if getattr(self, "_unmount_debugfs", None):
            with contextlib.suppress(Error):
                self._pman.run(f"unmount {self._debugfs_mntpoint}")

        ClassHelpers.close(self, unref_attrs=("_reader", "_pman"))
