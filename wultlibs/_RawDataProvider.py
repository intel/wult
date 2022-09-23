# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module implements the base class for raw data provider classes.
"""

import logging
from pepclibs.helperlibs.Exceptions import Error, ErrorTimeOut
from pepclibs.helperlibs import Trivial, ClassHelpers, KernelModule
from statscollectlibs.helperlibs import ProcHelpers
from wultlibs import Devices
from wultlibs.helperlibs import FSHelpers, Human

_LOG = logging.getLogger()

class RawDataProviderBase(ClassHelpers.SimpleCloseContext):
    """
    The base class for raw data provider classes.
    """

    def _adjust_and_validate_ldist(self):
        """
        Adjust the values launch distance values (if they are set to 0). Validate that the launch
        distance range ('self.ldist') is withing the allowed limits ('self.ldist_limits').
        """

        ldist_min, ldist_max  = self.ldist_limits

        if self.ldist[0] == 0:
            _LOG.info("Setting min. launch distance to %d ns", ldist_min)
            self.ldist = (ldist_min, self.ldist[1])

        if self.ldist[1] == 0:
            _LOG.info("Setting max. launch distance to %d ns", ldist_max)
            self.ldist = (self.ldist[0], ldist_max)

        try:
            Trivial.validate_range(self.ldist[0], self.ldist[1], min_limit=ldist_min,
                                   max_limit=ldist_max, what="launch distance range in nanoseconds")
        except Error as err:
            ldist0 = Human.duration_ns(self.ldist[0])
            ldist1 = Human.duration_ns(self.ldist[1])
            ldist_min = Human.duration_ns(ldist_min)
            ldist_max = Human.duration_ns(ldist_max)

            msg = str(err)
            if self.ldist[0] == self.ldist[1]:
                msg += "\nProvided launch disatnce: {ldist0}"
            else:
                msg += f"\nProvided launch disatnce range: [{ldist0}, {ldist1}]"

            msg += f"\nSupported min. and max. launch distance values: {ldist_min}, {ldist_max}"
            raise Error(msg) from err

    def __init__(self, dev, pman, ldist, timeout=None):
        """
        Initialize a class instance for device 'dev'. The arguments are as follows.
          * dev - the device object created with 'Devices.GetDevice()'.
          * pman - the process manager object defining host to operate on.
          * ldist - a pair of numbers specifying the launch distance range in nanoseconds.
          * timeout - the maximum amount of seconds to wait for a raw datapoint. Default is 10
                      seconds.
        """

        self.dev = dev
        self._pman = pman
        self.ldist = ldist
        self._timeout = timeout

        # The allowed 'ldsit' range, should be initialized by a subclass.
        self.ldist_limits = None

        if timeout is None:
            self._timeout = 10

        msg = f"Using device '{self.dev.info['devid']}'{pman.hostmsg}:\n" \
              f" * {self.dev.info['descr']}"
        _LOG.info(msg)

    def close(self):
        """Uninitialize everything."""
        ClassHelpers.close(self, unref_attrs=("dev", "_pman"))

class DrvRawDataProviderBase(RawDataProviderBase):
    """
    The base class for raw data providers in case Linux kernel drivers are used. In other words,
    this class is 'RawDataProviderBase' + drivers loading/unloading support.
    """

    def _load(self):
        """Load all the necessary kernel drivers."""

        loaded = []
        for drvobj in self.drvobjs:
            try:
                drvobj.load(opts=self._drvinfo[drvobj.name]["params"])
                loaded.append(drvobj)
            except Error:
                # Unload the loaded drivers.
                for udrvobj in reversed(loaded):
                    try:
                        udrvobj.unload()
                    except Error as err:
                        _LOG.warning("failed to unload module '%s'%s:\n%s", udrvobj.name,
                                     self._pman.hostmsg, err)
                raise

    def _unload(self, everything=False):
        """
        Unload kernel drivers. The arguments are as follows.
          * everything - if 'False', unload only the previously loaded drivers, otherwise unload all
                         possible drivers.
        """

        if everything:
            for drvname in Devices.ALL_DRVNAMES:
                with KernelModule.KernelModule(drvname, pman=self._pman,
                                               dmesg=self.dev.dmesg_obj) as drvobj:
                    drvobj.unload()
        else:
            for drvobj in reversed(self.drvobjs):
                drvobj.unload()

    def prepare(self):
        """Prepare to start the measurements."""

        # Unload all the drivers.
        self._unload(everything=True)

    def __init__(self, dev, pman, ldist, drvinfo=None, timeout=None, **kwargs):
        """
        Initialize a class instance. The arguments are as follows.
          * drvinfo - a dictionary describing the kernel drivers to load/unload.
          * All other arguments are the same as in 'RawDataProviderBase.__init__()'.

        The 'drvinfo' dictionary schema is as follows.
          { drvname1: { "params" : <module parameters> },
            drvname2: { "params" : <module parameters> },
           ... etc ... }

          * drvname - driver name.
          * params - driver module parameters.

        Note, the reason for 'kwargs' argument and for 'drvinfo' being a keyword argument (even
        though it is not optional) is to support multiple inheritance cases: a subclass may inherit
        this class and another class, which has a different constructor signature. In this case the
        unknown arguments are simply ignored.
        """

        super().__init__(dev, pman, ldist, timeout=timeout, **kwargs)

        self._drvinfo = drvinfo
        self.drvobjs = []

        self.debugfs_mntpoint = None
        self._unmount_debugfs = None

        for drvname in self._drvinfo.keys():
            drvobj = KernelModule.KernelModule(drvname, pman=pman, dmesg=dev.dmesg_obj)
            self.drvobjs.append(drvobj)

        self.debugfs_mntpoint, self._unmount_debugfs = FSHelpers.mount_debugfs(pman=pman)

    def close(self):
        """Uninitialize everything."""

        if getattr(self, "drvobjs", None):
            try:
                self._unload()
            except Error as err:
                _LOG.warning(err)

            for drvobj in self.drvobjs:
                try:
                    drvobj.close()
                except Error as err:
                    _LOG.warning(err)

            self.drvobjs = []

        if getattr(self, "_unmount_debugfs", None):
            try:
                self._pman.run("unmount {self.debugfs_mntpoint}")
            except Error as err:
                _LOG.warning(err)

        super().close()

class HelperRawDataProviderBase(RawDataProviderBase):
    """
    The base class for raw data providers which are based on a helper program printing datapoints
    data to 'stdout'.
    """

    def _error_pfx(self):
        """
        Forms and returns the starting part of an error message related to a general helper process
        failure.
        """

        return f"the '{self._helpername}' process{self._pman.hostmsg}"

    def _get_lines(self):
        """Reads helper program 'stdout' output and yield it line by line."""

        while True:
            stdout, stderr, exitcode = self._proc.wait(timeout=self._timeout, lines=[1, None],
                                                       join=False)
            if exitcode is not None:
                msg = self._proc.get_cmd_failure_msg(stdout, stderr, exitcode,
                                                     timeout=self._timeout)
                raise Error(f"{self._error_pfx()} has exited unexpectedly\n{msg}")
            if stderr:
                raise Error(f"{self._error_pfx()} printed an error message:\n{''.join(stderr)}")
            if not stdout:
                raise ErrorTimeOut(f"{self._error_pfx()} did not provide any output for "
                                   f"{self._timeout} seconds")

            for line in stdout:
                yield line.strip()

    def _get_stderr(self):
        """Read and return standard error output of the helper program, if any."""

        _, stderr, exitcode = self._proc.wait(timeout=1, lines=[None, None], join=True)
        if exitcode is not None:
            return ""
        return stderr.strip()

    def _start_helper(self):
        """Start the helper program."""

        cmd = f"{self._helper_path} {self._helper_opts}"
        self._proc = self._pman.run_async(cmd)

    def _exit_helper(self):
        """Make the helper program exit."""

        _LOG.debug("stopping '%s'", self._helpername)
        self._proc.stdin.write("q\n".encode("utf8"))
        # self._proc.stdin.flush()
        # Note: the above line causes a stacktrace if 'self._proc' is an 'SSHProcessManager'. I
        # think it is a paramiko bug. As a work around, we do not flush and rely that
        # 'self._proc.stdin' is either unbuffered or line-buffered, which is the case for both
        # 'LocalProcessManager' and 'SSHProcessManager'.
        #
        # Traceback (most recent call last):
        #  File "/usr/lib/python3.10/site-packages/paramiko/file.py", line 66, in __del__
        #    self.close()
        #  File "/usr/lib/python3.10/site-packages/paramiko/file.py", line 84, in close
        #    self.flush()
        #  File "/usr/lib/python3.10/site-packages/paramiko/file.py", line 92, in flush
        #    self._write_all(self._wbuffer.getvalue())
        # ValueError: I/O operation on closed file.

        _, _, exitcode = self._proc.wait(timeout=5)
        if exitcode is None:
            _LOG.warning("the '%s' program PID %d%s failed to exit, killing it",
                         self._helpername, self._proc.pid, self._pman.hostmsg)
            ProcHelpers.kill_pids(self._proc.pid, kill_children=True, must_die=False,
                                  pman=self._pman)

        self._proc = None

    def prepare(self):
        """Prepare to start the measurements."""

        # Kill stale helper process, if any.
        regex = f"^.*{self._helper_path} .*$"
        ProcHelpers.kill_processes(regex, log=True, name=f"stale '{self._helpername}' process",
                                   pman=self._pman)

    def _get_ldist_limits(self):
        """Returns the min. and max. launch distance supported by the driver."""

        cmd = f"{self._helper_path} --print-max-ldist"
        stdout, _ = self._pman.run_verify(cmd)

        errmsg = f"ran the following command{self._pman.hostmsg}:\n{cmd}"

        lines = len(stdout.splitlines())
        if lines != 1:
            raise Error(f"{errmsg}\nbut got {lines} lines of output instead of one:\n{stdout}")

        pfx = f"{self._helpername}: max. ldist: "
        if not stdout.startswith(pfx):
            raise Error(f"{errmsg}\nbut got unexpected output:\n{stdout}")

        ldist_max = Trivial.str_to_int(stdout[len(pfx):], what="max. launch distance value")
        if ldist_max <= 0:
            raise Error(f"BUG: {errmsg}\ngot non-positive max. launch distance value: {ldist_max}")

        # Min. launch distance is set to 1us.
        return (1000, ldist_max)

    def __init__(self, dev, pman, ldist, helper_path=None, timeout=None, **kwargs):
        """
        Initialize a class instance. The arguments are as follows.
          * helper_path - path to the helper program which provides the datapoints.
          * All other arguments are the same as in 'RawDataProviderBase.__init__()'.

        Note, the reason for 'kwargs' is the same as described in
        'DrvRawDataProviderBase.__init__()'.
        """

        super().__init__(dev, pman, ldist, timeout=timeout, **kwargs)

        self._helper_path = helper_path

        self._helper_opts = None # The helper program command line options.
        self._proc = None        # The helper process.

        self._helpername = dev.helpername

        # Validate the helper path.
        if not self._pman.is_exe(self._helper_path):
            raise Error(f"bad 'self._helpername' helper path '{self._helper_path}' - does not "
                        f"exist{self._pman.hostmsg} or not an executable file")

        self.ldist_limits = self._get_ldist_limits()
        self._adjust_and_validate_ldist()

    def close(self):
        """Stop the measurements."""

        if getattr(self, "_proc", None):
            try:
                self._exit_helper()
            except Error as err:
                _LOG.warning(err)
            finally:
                self._proc = None
