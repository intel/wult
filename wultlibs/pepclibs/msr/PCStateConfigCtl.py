# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2020-2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Antti Laakso <antti.laakso@linux.intel.com>

"""
This module provides API for managing settings in MSR 0xE2 (MSR_PKG_CST_CONFIG_CONTROL). This is a
model-specific register found on many Intel platforms.
"""

from wultlibs.helperlibs import Procs
from wultlibs.pepclibs import CPUInfo
from wultlibs.pepclibs.msr import MSR
from wultlibs.pepclibs.CPUInfo import CPU_DESCR as _CPU_DESCR
from wultlibs.helperlibs.Exceptions import Error, ErrorNotSupported

# Package C-state configuration control Model Specific Register.
MSR_PKG_CST_CONFIG_CONTROL = 0xE2
CFG_LOCK = 15
C1_AUTO_DEMOTION_ENABLE = 26
MAX_PKG_C_STATE_MASK = 0xF

# Icelake Xeon Package C-state limits.
_ICX_PKG_CST_LIMITS = {"codes"   : {"pc0": 0, "pc2": 1, "pc6n":2, "unlimited" : 7},
                       "aliases" : {"pc6": "pc6n"}}
# Sky-/Cascade-/Cooper- lake Xeon Package C-state limits.
_SKX_PKG_CST_LIMITS = {"codes"   : {"pc0": 0, "pc2": 1, "pc6n":2, "pc6r": 3, "unlimited": 7},
                       "aliases" : {"pc6": "pc6r"}}

# Package C-state limits are platform specific.
_PKG_CST_LIMIT_MAP = {CPUInfo.INTEL_FAM6_ICELAKE_D: _ICX_PKG_CST_LIMITS,
                      CPUInfo.INTEL_FAM6_ICELAKE_X: _ICX_PKG_CST_LIMITS,
                      CPUInfo.INTEL_FAM6_SKYLAKE_X: _SKX_PKG_CST_LIMITS}

class PCStateConfigCtl:
    """
    This class provides API for managing settings in MSR 0xE2 (MSR_PKG_CST_CONFIG_CONTROL). This is
    a model-specific register found on many Intel platforms.
    """

    def _get_cpuinfo(self):
        """Return an instance of 'CPUInfo' class."""

        if not self._cpuinfo:
            self._cpuinfo = CPUInfo.CPUInfo(proc=self._proc)
        return self._cpuinfo

    def _check_cpu_pcstate_limit_support(self):
        """Check if the package C-state limit functionality is supported for this CPU."""

        model = self._lscpu_info["model"]

        if model not in _PKG_CST_LIMIT_MAP:
            fmt = "%s (CPU model %#x)"
            cpulst = "\n* ".join([fmt % (_CPU_DESCR[model], model) for model in _PKG_CST_LIMIT_MAP])
            raise ErrorNotSupported(f"package C-state limit functionality is not supported"
                                    f"{self._proc.hostmsg} - CPU '{self._lscpu_info['vendor']}, "
                                    f"(CPU model {hex(model)})' is not supported.\nThe supported "
                                    f"CPUs are:\n* {cpulst}")

    def _get_pcstate_limit_value(self, pcs_limit):
        """
        Convert a package C-state name to integer package C-state limit value suitable for the
        'MSR_PKG_CST_CONFIG_CONTROL' register.
        """

        model = self._lscpu_info["model"]

        pcs_limit = str(pcs_limit)
        limit_val = _PKG_CST_LIMIT_MAP[model]["codes"].get(pcs_limit.lower())
        if limit_val is None:
            limits_str = ", ".join(_PKG_CST_LIMIT_MAP[model]["codes"])
            raise Error(f"cannot limit package C-state{self._proc.hostmsg}, '{pcs_limit}' is "
                        f"not supported for CPU {_CPU_DESCR[model]} (CPU model {hex(model)}).\n"
                        f"The supported package C-states are: {limits_str}")
        return limit_val

    def _get_pcstate_limit(self, cpus, pcs_rmap):
        """
        Read 'PKG_CST_CONFIG_CONTROL' MSR for all CPUs 'cpus'. The 'cpus' argument is the same as
        in 'set_c1_auto_demotion()' method. The 'pcs_rmap' is reversed dictionary with package
        C-state code and name pairs. Returns a tuple of C-state limit value and locked bit boolean.
        """

        pcs_code = max(pcs_rmap)
        locked = False
        for _, regval in self._msr.read_iter(MSR_PKG_CST_CONFIG_CONTROL, cpus=cpus):
            # The C-state limit value is smallest found among all CPUs and locked bit is 'True' if
            # any of the registers has locked bit set, otherwise it is 'False'.
            pcs_code = min(pcs_code, regval & MAX_PKG_C_STATE_MASK)
            locked = any((locked, regval & MSR.bit_mask(CFG_LOCK)))

            if pcs_code not in pcs_rmap:
                known_codes = ", ".join([str(code) for code in pcs_rmap])
                raise Error(f"unexpected package C-state limit code '{pcs_code}' read from "
                            f"'PKG_CST_CONFIG_CONTROL' MSR ({MSR_PKG_CST_CONFIG_CONTROL})"
                            f"{self._proc.hostmsg}, known codes are: {known_codes}")

        return (pcs_code, locked)

    def get_available_pcstate_limits(self):
        """
        Return list of all available package C-state limits. Raises an Error if CPU model is not
        supported.
        """

        self._check_cpu_pcstate_limit_support()
        return _PKG_CST_LIMIT_MAP[self._lscpu_info["model"]]

    def get_pcstate_limit(self, pkgs="all"):
        """
        Get package C-state limit for packages in 'pkgs'. Returns a dictionary with integer package
        numbers as keys, and values also being dictionaries with the following 2 elements.
          * limit - the package C-state limit name (small letters, e.g., pc0)
          * locked - a boolean, 'True' if the 'MSR_PKG_CST_CONFIG_CONTROL' register has the
            'CFG_LOCK' bit set, so it is impossible to change the package C-state limit, and 'False'
            otherwise.

        Note, even thought the 'MSR_PKG_CST_CONFIG_CONTROL' register is per-core, it anyway has
        package scope. This function checks the register on all cores and returns the resulting
        shallowest C-state limit. Returns dictionary with package C-state limit and MSR lock
        information.
        """

        self._check_cpu_pcstate_limit_support()

        cpuinfo = self._get_cpuinfo()
        pkgs = cpuinfo.get_package_list(pkgs)

        model = self._lscpu_info["model"]
        # Get package C-state integer code -> name dictionary.
        pcs_rmap = {code:name for name, code in _PKG_CST_LIMIT_MAP[model]["codes"].items()}

        limits = {}
        for pkg in pkgs:
            limits[pkg] = {}
            cpus = cpuinfo.get_cpus(lvl="pkg", nums=[pkg])
            pcs_code, locked = self._get_pcstate_limit(cpus, pcs_rmap)
            limits[pkg] = {"limit" : pcs_rmap[pcs_code], "locked" : locked}

        return limits

    def set_pcstate_limit(self, pcs_limit, pkgs="all"):
        """Set package C-state limit for packages in 'pkgs'."""

        self._check_cpu_pcstate_limit_support()
        limit_val = self._get_pcstate_limit_value(pcs_limit)

        cpuinfo = self._get_cpuinfo()
        pkgs = cpuinfo.get_package_list(pkgs)

        # Package C-state limit has package scope, but the MSR is per-core.
        cpus = []
        cores = cpuinfo.get_cores(lvl="pkg", nums=pkgs)
        for core in cores:
            core_cpus = cpuinfo.get_cpus(lvl="core", nums=[core])
            if core_cpus:
                cpus.append(core_cpus[0])

        for cpu, regval in self._msr.read_iter(MSR_PKG_CST_CONFIG_CONTROL, cpus=cpus):
            if MSR.is_bit_set(CFG_LOCK, regval):
                raise Error(f"cannot set package C-state limit{self._proc.hostmsg} for CPU "
                            f"'{cpu}', MSR ({MSR_PKG_CST_CONFIG_CONTROL}) is locked. Sometimes, "
                            f"depending on the vendor, there is a BIOS knob to unlock it.")

            regval = (regval & ~0x07) | limit_val
            self._msr.write(MSR_PKG_CST_CONFIG_CONTROL, regval, cpus=cpu)

    def c1_auto_demotion_enabled(self, cpu):
        """
        Returns 'True' if C1 auto demotion is enabled for CPU 'cpu', otherwise returns 'False'.
        """

        regval = self._msr.read(MSR_PKG_CST_CONFIG_CONTROL, cpu=cpu)
        return MSR.is_bit_set(C1_AUTO_DEMOTION_ENABLE, regval)

    def set_c1_auto_demotion(self, enable: bool, cpus="all"):
        """
        Enable or disable C1 autopromote for CPUs 'cpus'. The 'cpus' argument is the same as the
        'cpus' argument of the 'CPUIdle.get_cstates_info()' function - please, refer to the
        'CPUIdle' module for the exact format description.
        """
        self._msr.toggle_bit(MSR_PKG_CST_CONFIG_CONTROL, C1_AUTO_DEMOTION_ENABLE, enable, cpus=cpus)

    def __init__(self, proc=None, cpuinfo=None, lscpu_info=None):
        """
        The class constructor. The argument are as follows.
          * proc - the 'Proc' or 'SSH' object that defines the host to run the measurements on.
          * cpuinfo - CPU information object generated by 'CPUInfo.CPUInfo()'.
          * lscpu_info - CPU information generated by 'CPUInfo.get_lscpu_info()'.
        """

        if not proc:
            proc = Procs.Proc()

        self._proc = proc
        self._cpuinfo = cpuinfo
        self._lscpu_info = lscpu_info
        self._msr = MSR.MSR(proc=self._proc)

        if self._lscpu_info is None:
            self._lscpu_info = CPUInfo.get_lscpu_info(proc=self._proc)

        if self._lscpu_info["vendor"] != "GenuineIntel":
            raise ErrorNotSupported(f"unsupported CPU model '{self._lscpu_info['vendor']}', "
                                    f"model-specific register {hex(MSR_PKG_CST_CONFIG_CONTROL)} "
                                    f"(MSR_PKG_CST_CONFIG_CONTROL) is not available"
                                    f"{self._proc.hostmsg}. MSR_PKG_CST_CONFIG_CONTROL is "
                                    f"available only on Intel platforms")

    def close(self):
        """Uninitialize the class object."""

        if getattr(self, "_proc", None):
            self._proc = None
        if getattr(self, "_msr", None):
            self._msr.close()
            self._msr = None

    def __enter__(self):
        """Enter the runtime context."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the runtime context."""
        self.close()
