# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2020 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module provides API for dealing with Linux function trace buffer.
"""

import logging
from collections import namedtuple
from wultlibs.helperlibs import ProcHelpers, FSHelpers
from wultlibs.helperlibs.Exceptions import Error, ErrorNotSupported, ErrorTimeOut

# A function trace buffer line.
FtraceLine = namedtuple("FTraceLine", ["procname", "pid", "cpunum", "flags", "timestamp", "func",
                                       "msg"])
FtraceLine.__doc__ = """
A kernel function trace buffer line.
  o procname - process name.
  o pid - process PID.
  o cpunum - logical CPU number.
  o flags - trace flags.
  o timestamp - the trace timestamp.
  o func - name of the kernel function where the trace happened.
  o msg - the trace buffer message.
"""

_LOG = logging.getLogger()

class FTrace:
    """This class represents the Linux function trace buffer."""

    def _clear(self):
        """Clear the function trace buffer."""

        _LOG.debug("clearing the trace buffer")
        with self._proc.open(self.ftpath, "w+") as fobj:
            fobj.write("0")

    def getlines(self):
        """
        Yield trace buffer lines one-by-one. Wait for a trace line for maximum 'timeout' seconds.
        """

        while True:
            stdout, stderr, exitcode = self._reader.wait_for_cmd(timeout=self.timeout, by_line=True,
                                                                 wait_for_exit=False, join=False)

            if not stdout and not stderr and exitcode is None:
                raise ErrorTimeOut(f"no data in trace buffer for {self._reader.timeout} seconds"
                                   f"{self._proc.hostmsg}")


            # The process has terminated or printed something to standard error.
            if exitcode is not None or stderr:
                msg = self._reader.cmd_failed_msg(stdout, stderr, exitcode)
                raise Error(f"the function trace reader process has exited unexpectedly:\n{msg}")

            for line in stdout:
                if line.startswith("#"):
                    continue
                split = line.split(maxsplit=5)
                if len(split) != 6:
                    stdout = "".join(stdout)
                    raise Error(f"processing the following data from the trace buffer:\n{stdout}\n"
                                f"Failure: unexpected trace buffer line{self._proc.hostmsg} - less "
                                f"than 6 comma-separated elements:\n{line}")
                procinfo, cpunum, flags, timestamp, func, msg = split
                procname, pid = procinfo.split("-")
                self.raw_line = line
                yield FtraceLine(procname, pid, cpunum, flags, timestamp, func, msg.strip())

    def __init__(self, proc, timeout=30):
        """
        Class constructor. The arguments are as follows.
          * proc - the 'Proc' or 'SSH' object that defines the host to operate on. This object will
                   keep a 'proc' reference and use it in various methods.
          * timeout - longest time in seconts to wait for data in the trace buffer.
        """

        self._reader = None
        self._proc = proc
        self.timeout = timeout
        self.raw_line = None

        mntpoint = FSHelpers.mount_debugfs(proc=proc)
        self.ftpath = mntpoint.joinpath("tracing/trace")
        self.ftpipe_path = mntpoint.joinpath("tracing/trace_pipe")

        for path in (self.ftpath, self.ftpipe_path):
            if not FSHelpers.isfile(path, proc=proc):
                raise ErrorNotSupported(f"linux kernel function trace file was not found at "
                                        f"'{path}'{proc.hostmsg}")

        cmd = f"cat {self.ftpipe_path}"
        name = "stale wult function trace reader process"
        ProcHelpers.kill_processes(cmd, log=True, name=name, proc=self._proc)
        self._clear()
        self._reader = self._proc.run_async(cmd, shell=True)

    def close(self):
        """Stop following the function trace buffer."""

        if getattr(self, "_proc", None):
            proc = self._proc
            self._proc = None
        else:
            return

        if getattr(self, "_reader", None) and getattr(self._reader, "pid", None):
            _LOG.debug("killing the function trace reader process PID %d%s",
                       self._reader.pid, proc.hostmsg)
            ProcHelpers.kill_pids(self._reader.pid, kill_children=True, must_die=False, proc=proc)
            self._reader = None

    def __enter__(self):
        """Enter the run-time context."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the runtime context."""
        self.close()
