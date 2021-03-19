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

import logging
from pathlib import Path
from wultlibs.helperlibs import Procs
from wultlibs.helperlibs.Exceptions import Error
from wultlibs.sysconfiglibs import CPUInfo

_CPU_BYTEORDER = "little"

# Platform info MSR.
MSR_PLATFORM_INFO = 0xCE

# Scalable bus speed MSR.
MSR_FSB_FREQ = 0xCD

# C-state configuration control MSR.
MSR_PKG_CST_CONFIG_CONTROL = 0xE2
CFG_LOCK = 15
C1_AUTO_DEMOTION_ENABLE = 26
MAX_PKG_C_STATE_MASK = 0xF

# Feature control MSR.
MSR_MISC_FEATURE_CONTROL = 0x1A4
MLC_STREAMER = 0
MLC_SPACIAL = 1
DCU_STREAMER = 2
DCU_IP = 3

# Turbo ratio limit MSR, informs about turbo frequencies for core croups.
MSR_TURBO_RATIO_LIMIT = 0x1AD

# Energy performance bias MSR.
MSR_ENERGY_PERF_BIAS = 0x1B0

# Power control MSR.
MSR_POWER_CTL = 0x1FC
C1E_ENABLE = 1
CSTATE_PREWAKE_DISABLE = 30

# PM enable MSR.
MSR_PM_ENABLE = 0x770
HWP_ENABLE = 0

# HWP Request MSR. Includes hardware power management control bits.
MSR_HWP_REQUEST = 0x774
PKG_CONTROL = 42
EPP_VALID = 60

_LOG = logging.getLogger()

def bit_mask(bitnr):
    """Return bitmask for a bit by its number."""
    return 1 << bitnr

def is_bit_set(bitnr, bitval):
    """
    Return 'True' if bit number 'bitnr' is set in MSR value 'bitval', otherwise returns
    'False'.
    """
    return bit_mask(bitnr) & bitval

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

        for cpu in cpus:
            path = Path(f"/dev/cpu/{cpu}/msr")
            try:
                with self._proc.open(path, "rb") as fobj:
                    fobj.seek(address)
                    val = fobj.read(regsize)
            except Error as err:
                raise Error(f"failed to read MSR '{hex(address)}' from file '{path}'"
                            f"{self._proc.hostmsg}:\n{err}") from err

            val = int.from_bytes(val, byteorder=_CPU_BYTEORDER)
            yield (cpu, val)

    def read(self, address, regsize=8, cpu=0):
        """
        Read an MSR on single CPU and return read result. Arguments are same as in read_iter().
        """

        _, msr = next(self.read_iter(address, regsize, cpu))
        return msr

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

        val_bytes = val.to_bytes(regsize, byteorder=_CPU_BYTEORDER)
        for cpu in cpus:
            path = Path(f"/dev/cpu/{cpu}/msr")
            try:
                with self._proc.open(path, "wb") as fobj:
                    fobj.seek(address)
                    fobj.write(val_bytes)
                    _LOG.debug("CPU%d: MSR 0x%x: wrote 0x%x", cpu, address, val)
            except Error as err:
                raise Error(f"failed to write MSR '{hex(address)}' to file '{path}'"
                            f"{self._proc.hostmsg}:\n{err}") from err

    def set(self, address, mask, regsize=8, cpus="all"):
        """Set 'mask' bits in MSR. Arguments are the same as in 'write()'."""

        regsize, cpus = self._handle_arguments(regsize, cpus)

        for cpunum, msr in self.read_iter(address, regsize, cpus):
            new = msr | mask
            if msr != new:
                self.write(address, new, regsize, cpunum)

    def clear(self, address, mask, regsize=8, cpus="all"):
        """Clear 'mask' bits in MSR. Arguments are the same as in 'write()'."""

        regsize, cpus = self._handle_arguments(regsize, cpus)

        for cpunum, msr in self.read_iter(address, regsize, cpus):
            new = msr & ~mask
            if msr != new:
                self.write(address, new, regsize, cpunum)

    def __init__(self, proc=None):
        """The class constructor."""

        if not proc:
            proc = Procs.Proc()
        self._proc = proc
        self._cpuinfo = None

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
