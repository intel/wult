# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2020-2020 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Antti Laakso <antti.laakso@linux.intel.com>

"""
This module contains helper functions to read and write CPU Model Specific Registers. This module
has been designed and implemented for Intel CPUs.
"""

import sys
import logging
import contextlib
from pathlib import Path
from hashlib import sha256
from wultlibs.helperlibs import ArgParse, Procs, Logging, Trivial
from wultlibs.helperlibs.Exceptions import Error
from wultlibs.sysconfiglibs import CPUInfo

_CPU_BYTEORDER = "little"

MSR_PLATFORM_INFO = 0xCE

# Scaleable bus speed.
MSR_FSB_FREQ = 0xCD

# C-state configuration control.
MSR_PKG_CST_CONFIG_CONTROL = 0xE2
CFG_LOCK = 15
C1_AUTO_DEMOTION_ENABLE = 26
MAX_PKG_C_STATE_MASK = 0xF

MSR_MISC_FEATURE_CONTROL = 0x1A4
MLC_STREAMER = 0
MLC_SPACIAL = 1
DCU_STREAMER = 2
DCU_IP = 3

# Maximum ratio limit of turbo mode by core groups.
MSR_TURBO_RATIO_LIMIT = 0x1AD

# Group size of active cores for turbo mode operation.
MSR_TURBO_GROUP_CORECNT = 0x1AE

# Energy performance bias hint.
MSR_ENERGY_PERF_BIAS = 0x1B0

MSR_POWER_CTL = 0x1FC
C1E_ENABLE = 1
CSTATE_PREWAKE_DISABLE = 30

MSR_PM_ENABLE = 0x770
HWP_ENABLE = 0

# Hardware-managed P-states control hints per CPU.
MSR_HWP_REQUEST = 0x774
PKG_CONTROL = 42
EPP_VALID = 60

_LOG = logging.getLogger()
Logging.setup_logger(prefix="MSR.py")

def bit_mask(nr):
    """Return bitmask for a bit by its number."""
    return 1 << nr

class MSR:
    """This class provides helpers to read and write CPU Model Specific Registers."""

    def _handle_arguments(self, regsize, cpus):
        """Validate arguments, and convert 'cpus' to valid list of CPU numbers if needed."""

        regsizes = (4, 8)
        if regsize not in regsizes:
            regsizes_str = ",".join([str(val) for val in regsizes])
            raise Error(f"invalid register size value '{regsize}', use one of: {regsizes_str}")

        if not self._cpuinfo:
            self._cpuinfo = CPUInfo.CPUInfo(proc=self._proc)
        cpus = self._cpuinfo.get_cpu_list(cpus)

        return (regsize, cpus)

    @staticmethod
    def _get_sha256(path, proc):
        """Calculate sha256 checksum of the file 'path' on the host defined by 'proc'."""

        checksum = None
        with contextlib.suppress(Error):
            with proc.open(path, "rb") as fobj:
                data = fobj.read()
                checksum = sha256(data).hexdigest()

        return checksum

    def _run_on_remote_host(self, method, *args):
        """"Run MSR method 'method' on remote host."""

        cmd = f"python -- {self._rpath} {method}"
        for arg in args:
            if Trivial.is_iterable(arg):
                arg = ",".join([str(val) for val in arg])
            cmd += f" {arg}"

        stdout, _ = self._proc.run_verify(cmd, join=False)
        return stdout, cmd

    def _read_iter(self, address, regsize, cpus):
        """
        Implements the 'read_iter()' function. This implementation runs fast locally ('self._proc'
        is the local host), but runs slowly remotely ('self._proc' is a remote host).
        """

        for cpu in cpus:
            path = Path(f"/dev/cpu/{cpu}/msr")
            try:
                with self._proc.open(path, "rb") as fobj:
                    fobj.seek(address)
                    val = fobj.read(regsize)
            except Error as err:
                raise Error(f"failed to read MSR '{hex(address)}' via '{path}'{self._proc.hostmsg}:"
                            f"\n{err}") from err

            val = int.from_bytes(val, byteorder=_CPU_BYTEORDER)
            yield (cpu, val)

    def _read_iter_remote(self, address, regsize, cpus):
        """
        Optimized version of '_read_iter()' for the remote case. Instead of reading MSR registers
        individually over the network, we run 'MSR.py' (ourselves!) on the remote host and parse its
        output. This ends up being a lot faster.
        """

        result, cmd = self._run_on_remote_host("read_iter", address, regsize, cpus)

        errmsg = f"ran the following command{self._proc.hostmsg}:\n{cmd}\n"
        if len(result) != len(cpus):
            raise Error(f"{errmsg}Expected to receive {len(cpus)} lines, but instead {len(result)} "
                        f"lines were received")

        for line in result:
            args = ArgParse.parse_int_list(line.strip(), dedup=False)
            if len(args) != 2:
                raise Error(f"{errmsg}Expected lines with two integers in form of 'cpu,value', got "
                            f"this line:\n\t{line}")
            yield (int(args[0]), int(args[1]))

    def read_iter(self, address, regsize=8, cpus="all"):
        """
        Read an MSR register on one or multiple CPUs and yield tuple with CPU number and the read
        result.
          * address - address of MSR register.
          * regsize - size of MSR register in bytes.
          * cpus - list of CPU numbers value should be read from. It is the same as the 'cpus'
                   argument of the 'CPUIdle.get_cstates_info()' function - please, refer to the
                   'CPUIdle' module for the exact format description.
        """

        regsize, cpus = self._handle_arguments(regsize, cpus)

        if self._remote_run_ok:
            reader = self._read_iter_remote(address, regsize, cpus)
        else:
            reader = self._read_iter(address, regsize, cpus)

        yield from reader

    def read(self, address, regsize=8, cpu=0):
        """
        Read an MSR on single CPU and return read result. Arguments are same as in read_iter().
        """

        _, msr = next(self.read_iter(address, regsize, cpu))
        return msr

    def _write(self, address, val, regsize, cpus):
        """Implements the 'write()' function (local case and unoptimized remote case)."""

        val_bytes = val.to_bytes(regsize, byteorder=_CPU_BYTEORDER)
        for cpu in cpus:
            path = Path(f"/dev/cpu/{cpu}/msr")
            try:
                with self._proc.open(path, "wb") as fobj:
                    fobj.seek(address)
                    fobj.write(val_bytes)
                    _LOG.debug("CPU%d: MSR 0x%x: wrote 0x%x", cpu, address, val)
            except Error as err:
                raise Error(f"failed to write MSR '{hex(address)}' via '{path}'"
                            f"{self._proc.hostmsg}:\n{err}") from err

    def write(self, address, val, regsize=8, cpus="all"):
        """
        Write MSR register. The arguments are as follows.
          * address - address of MSR register.
          * val - integer value to write to MSR.
          * regsize - size of MSR register in bytes.
          * cpus - list of CPU numbers write should be done at. It is the same as the 'cpus'
                   argument of the 'CPUIdle.get_cstates_info()' function - please, refer to the
                   'CPUIdle' module for the exact format description.
        """

        regsize, cpus = self._handle_arguments(regsize, cpus)

        if self._remote_run_ok:
            self._run_on_remote_host("write", address, val, regsize, cpus)
        else:
            self._write(address, val, regsize, cpus)

    def _set(self, address, mask, regsize, cpus):
        """Implements the 'set()' function (local case and unoptimized remote case)."""

        for cpunum, msr in self.read_iter(address, regsize, cpus):
            new = msr | mask
            if msr != new:
                self.write(address, new, regsize, cpunum)

    def set(self, address, mask, regsize=8, cpus="all"):
        """Set 'mask' bits in MSR. Arguments are the same as in 'write()'."""

        regsize, cpus = self._handle_arguments(regsize, cpus)

        if self._remote_run_ok:
            self._run_on_remote_host("set", address, mask, regsize, cpus)
        else:
            self._set(address, mask, regsize, cpus)

    def _clear(self, address, mask, regsize=8, cpus="all"):
        """Implements the 'clear()' function (local case and unoptimized remote case)."""

        regsize, cpus = self._handle_arguments(regsize, cpus)

        for cpunum, msr in self.read_iter(address, regsize, cpus):
            new = msr & ~mask
            if msr != new:
                self.write(address, new, regsize, cpunum)

    def clear(self, address, mask, regsize=8, cpus="all"):
        """Clear 'mask' bits in MSR. Arguments are the same as in 'write()'."""

        regsize, cpus = self._handle_arguments(regsize, cpus)

        if self._remote_run_ok:
            self._run_on_remote_host("clear", address, mask, regsize, cpus)
        else:
            self._clear(address, mask, regsize, cpus)

    def _can_run_on_remote_host(self):
        """Returns 'True' if commands can be executed on remote host, returns 'False' otherwise."""

        if not self._proc.is_remote:
            return False

        cmd = "python -c 'from wultlibs.sysconfiglibs import MSR;print(MSR.__file__)'"
        try:
            self._rpath = self._proc.run_verify(cmd)[0].strip()
        except Error:
            return False

        rchksum = self._get_sha256(self._rpath, self._proc)
        lchksum = self._get_sha256(__file__, Procs.Proc())

        if lchksum != rchksum or not lchksum:
            return False

        return True

    def __init__(self, proc=None):
        """The class constructor."""

        if not proc:
            proc = Procs.Proc()
        self._proc = proc
        self._cpuinfo = None
        # Path to MSR.py (ourselves) on the remote host.
        self._rpath = None
        # Whether it is OK to run 'MSR.py' on the remote host as an optimization.
        self._remote_run_ok = self._can_run_on_remote_host()

    def close(self):
        """Uninitialize the class object."""

        if getattr(self, "_proc", None):
            self._proc = None
        if getattr(self, "_cpuinfo", None):
            self._cpuinfo.close()
            self._cpuinfo = None

    def __enter__(self):
        """Enter the runtime context."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the runtime context."""
        self.close()

def get_cmdline_args(args):
    """Parse command line arguments."""

    res = []
    for arg in args:
        if Trivial.is_int(arg):
            arg = int(arg)
        else:
            arg = ArgParse.parse_int_list(arg, ints=True, sort=True)
        res.append(arg)

    return res

def main():
    """
    Script entry point. Some methods of this module can be used via command line by running 'python
    MSR.py <arguments>'. We use this to improve performance when dealing with a remote host.
    """

    # Allow calls to public methods only.
    mname = sys.argv[1]
    allowed_methods = ("read", "read_iter", "write", "set", "clear")
    if mname not in allowed_methods:
        msg = f"can't run method '{mname}', use one of: {','.join(allowed_methods)}"
        _LOG.error_out(msg)

    # Allow access only to predefined MSRs.
    args = get_cmdline_args(sys.argv[2:])
    allowed_msrs = set()
    for symbol in globals():
        if symbol.startswith("MSR_"):
            val = getattr(sys.modules[__name__], symbol)
            allowed_msrs.add(val)
    addr = args[0]
    if addr not in allowed_msrs:
        raise Error(f"access to MSR '{hex(addr)}' not allowed")

    with MSR() as msr:
        method = getattr(msr, mname)
        if mname == "read_iter":
            for cpu, val in method(*args):
                print(f"{cpu},{val}")
        elif mname == "read":
            print(method(*args))
        else:
            method(*args)

# The script entry point.
if __name__ == "__main__":

    try:
        sys.exit(main())
    except KeyboardInterrupt:
        _LOG.info("Interrupted, exiting")
    except Error as err:
        _LOG.error_out(err)
