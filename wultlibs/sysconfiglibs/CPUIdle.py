# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2016-2020 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module provides API for dealing with the Linux "cpuidle" subsystem.
"""

import re
import logging
from pathlib import Path
from wultlibs.helperlibs import ArgParse, FSHelpers, Procs, Trivial
from wultlibs.helperlibs.Exceptions import Error, ErrorNotSupported
from wultlibs.sysconfiglibs import CPUInfo, MSR

# CPU model numbers.
_INTEL_FAM6_ICELAKE_X = 0x6A
_INTEL_FAM6_SKYLAKE_X = 0x55

# Mapping CPU model number to description.
_CPU_DESCR = {_INTEL_FAM6_ICELAKE_X: "Icelake Xeon",
              _INTEL_FAM6_SKYLAKE_X: "Skylake/Cascadelake Xeon"}

# Skylake Xeon Package C-state limits. There are other platfrorms that have the same limits, so we
# use this dictionary for them too.
_SKX_PKG_CST_LIMITS = {"pc0": 0, "pc2": 1, "pc6n":2, "pc6r": 3, "unlimited": 7}

# Package C-state limits are platform specific.
_PKG_CST_LIMIT_MAP = {_INTEL_FAM6_ICELAKE_X: _SKX_PKG_CST_LIMITS,
                      _INTEL_FAM6_SKYLAKE_X: _SKX_PKG_CST_LIMITS}

_LOG = logging.getLogger()

class CPUIdle:
    """This class provides API to the "cpuidle" Linux sybsystem."""

    def _get_lscpu_info(self):
        """Return the result of 'CPUInfo.get_lscpu_info()'."""

        if not self._lscpu_cache:
            self._lscpu_cache = CPUInfo.get_lscpu_info(proc=self._proc)
        return self._lscpu_cache

    def _get_cpuinfo(self):
        """Return an instance of 'CPUInfo' class."""

        if not self._cpuinfo:
            self._cpuinfo = CPUInfo.CPUInfo(proc=self._proc)
        return self._cpuinfo

    def _check_cpu_pcs_limit_support(self):
        """Check if the package C-state limit functionality is supported for this CPU."""

        lscpuinfo = self._get_lscpu_info()
        model = lscpuinfo["model"]

        if model not in _PKG_CST_LIMIT_MAP:
            cpus_str = "\n* ".join([f"{_CPU_DESCR[model]} (CPU model {hex(model)})" for model in
                                    _PKG_CST_LIMIT_MAP])
            raise ErrorNotSupported(f"package C-state limit functionality is not supported"
                                    f"{self._proc.hostmsg} - CPU '{lscpuinfo['vendor']}, (CPU "
                                    f"model {hex(model)})' is not supported.\nThe supported CPUs "
                                    f"are:\n* {cpus_str}")

    def _get_pc_limit_value(self, pcs_limit):
        """
        Convert a package C-state name to integer package C-state limit value suitable for the
        'MSR_PKG_CST_CONFIG_CONTROL' register.
        """

        lscpuinfo = self._get_lscpu_info()
        model = lscpuinfo["model"]

        limit_val = None
        if pcs_limit:
            limit_val = _PKG_CST_LIMIT_MAP[model].get(pcs_limit.lower())
            if limit_val is None:
                limits_str = ", ".join(_PKG_CST_LIMIT_MAP[model])
                raise Error(f"cannot limit package C-state{self._proc.hostmsg}, '{pcs_limit}' is "
                            f"not supported for CPU {_CPU_DESCR[model]} (CPU model {hex(model)}).\n"
                            f"The supported package C-states are: {limits_str}")
        return int(limit_val)

    def _get_pcs_limit(self, msr, cpus, pcs_rmap):
        """
        Read 'PKG_CST_CONFIG_CONTROL' MSR for all CPUs 'cpus'. Returns a tuple of C-state limit
        value and locked bit boolean. The 'pcs_rmap' is reversed dictionary with package C-state
        code and name pairs.
        """

        pcs_code = max(pcs_rmap)
        locked = False
        for _, reg in msr.read_iter(MSR.MSR_PKG_CST_CONFIG_CONTROL, cpus=cpus):
            # The C-state limit value is smallest found among all CPUs and locked bit is 'True' if
            # any of the registers has locked bit set, otherwise it is 'False'.
            pcs_code = min(pcs_code, reg & MSR.MAX_PKG_C_STATE_MASK)
            locked = any((locked, reg & MSR.bit_mask(MSR.CFG_LOCK)))

            if pcs_code not in pcs_rmap:
                known_codes = ", ".join([str(code) for code in pcs_rmap])
                raise Error(f"unexpected package C-state limit code '{pcs_code}' read from "
                            f"'PKG_CST_CONFIG_CONTROL' MSR ({MSR.MSR_PKG_CST_CONFIG_CONTROL})"
                            f"{self._proc.hostmsg}, known codes are: {known_codes}")

        return (pcs_code, locked)

    def get_available_pcs_limits(self):
        """
        Return list of all available package C-state limits. Raises an Error if CPU model is not
        supported.
        """

        self._check_cpu_pcs_limit_support()

        lscpuinfo = self._get_lscpu_info()
        return _PKG_CST_LIMIT_MAP[lscpuinfo["model"]]

    def get_pcs_limit(self, pkgs="all"):
        """
        Get package C-state limit from 'MSR_PKG_CST_CONFIG_CONTROL' MSR for packages in 'pkgs'.
        Returns a dictionary with integer package numbers as keys, and values also being
        dictionaries with the following 2 elements.
          * limit - the package C-state limit name (small letters, e.g., pc0)
          * locked - a boolean, 'True' if the 'MSR_PKG_CST_CONFIG_CONTROL' register has the
            'CFG_LOCK' bit set, so it is impossible to change the package C-state limit, and 'False'
            otherwise.

        Note, even thought the 'MSR_PKG_CST_CONFIG_CONTROL' register is per-core, it anyway has
        package scope. This function checks the register on all cores and returns the resulting
        shallowest C-state limit. Returns dictionary with package C-state limit and MSR lock
        information.
        """

        self._check_cpu_pcs_limit_support()

        cpuinfo = self._get_cpuinfo()
        pkgs = cpuinfo.get_package_list(pkgs)

        lscpuinfo = self._get_lscpu_info()
        model = lscpuinfo["model"]
        # Get package C-state integer code -> name dictionary.
        pcs_rmap = {code:name for name, code in _PKG_CST_LIMIT_MAP[model].items()}

        limits = {}
        with MSR.MSR(proc=self._proc) as msr:
            for pkg in pkgs:
                limits[pkg] = {}
                cpus = cpuinfo.get_cpus(lvl="pkg", nums=[pkg])
                pcs_code, locked = self._get_pcs_limit(msr, cpus, pcs_rmap)
                limits[pkg] = {"limit" : pcs_rmap[pcs_code], "locked" : locked}

        return limits

    def set_pcs_limit(self, pcs_limit, pkgs="all"):
        """Set package C-state limit in 'MSR_PKG_CST_CONFIG_CONTROL' MSR for packages in 'pkgs'."""

        self._check_cpu_pcs_limit_support()
        limit_val = self._get_pc_limit_value(pcs_limit)

        cpuinfo = self._get_cpuinfo()
        pkgs = cpuinfo.get_package_list(pkgs)

        # Package C-state limit has packages scope, but the MSR is per-core.
        cpus = []
        cores = cpuinfo.get_cores(lvl="pkg", nums=pkgs)
        for core in cores:
            core_cpus = cpuinfo.get_cpus(lvl="core", nums=[core])
            if core_cpus:
                cpus.append(core_cpus[0])

        with MSR.MSR(proc=self._proc) as msr:
            for cpu, reg in msr.read_iter(MSR.MSR_PKG_CST_CONFIG_CONTROL, cpus=cpus):
                if reg & MSR.bit_mask(MSR.CFG_LOCK):
                    raise Error(f"cannot set package C-state limit{self._proc.hostmsg} for CPU "
                                f"'{cpu}', MSR ({MSR.MSR_PKG_CST_CONFIG_CONTROL}) is locked. "
                                f"Sometimes, depending on the vendor, there is a BIOS knob to "
                                f"unlock it.")

                reg = (reg & ~0x07) | limit_val
                msr.write(MSR.MSR_PKG_CST_CONFIG_CONTROL, reg, cpus=cpu)

    def _get_cstate_indexes(self, cpu):
        """Yield tuples of of C-state indexes and sysfs paths for cpu number 'cpu'."""

        basedir = self._sysfs_base / f"cpu{cpu}" / "cpuidle"
        name = None
        for name, path, typ in FSHelpers.lsdir(basedir, proc=self._proc):
            errmsg = f"unexpected entry '{name}' in '{basedir}'{self._proc.hostmsg}"
            if typ != "/" or not name.startswith("state"):
                raise Error(errmsg)
            index = name[len("state"):]
            if not Trivial.is_int(index):
                raise Error(errmsg)
            yield int(index), Path(path)

        if name is None:
            raise Error(f"C-states are not supported{self._proc.hostmsg}")

    def _name2idx(self, name):
        """Return C-state index for C-state name 'name'."""

        index = None
        names = []
        for index, path in self._get_cstate_indexes(0):
            with self._proc.open(path / "name", "r") as fobj:
                val = fobj.read().strip()
            if val.lower() == name.lower():
                break
            names.append(val)
        else:
            names = ", ".join(names)
            raise Error(f"unkown C-state '{name}', here are the C-states supported"
                        f"{self._proc.hostmsg}:\n{names}")
        return index

    def _normalize_cstates(self, cstates):
        """
        Some methods accept the C-states to operate on as a string or a list. There may be C-state
        names or indexes in the list. This method turns the user input into a list of C-state
        indexes and returns this list.
        """

        if isinstance(cstates, int):
            cstates = str(cstates)
        if cstates is not None:
            if isinstance(cstates, str):
                cstates = Trivial.split_csv_line(cstates, dedup=True)
            indexes = []
            for cstate in cstates:
                if not Trivial.is_int(cstate):
                    cstate = self._name2idx(cstate)
                indexes.append(int(cstate))
            cstates = indexes
        return cstates

    def _toggle_cstate(self, cpu, index, enable):
        """Enable or disable the 'index' C-state for CPU 'cpu'."""

        path = self._sysfs_base / f"cpu{cpu}" / "cpuidle" / f"state{index}" / "disable"
        if enable:
            val = "0"
            action = "enable"
        else:
            val = "1"
            action = "disable"

        msg = f"{action} C-state with index '{index}' for CPU {cpu}"
        _LOG.debug(msg)

        try:
            with self._proc.open(path, "r+") as fobj:
                fobj.write(val + "\n")
        except Error as err:
            raise Error(f"failed to {msg}:\n{err}") from err

        try:
            with self._proc.open(path, "r") as fobj:
                read_val = fobj.read().strip()
        except Error as err:
            raise Error(f"failed to {msg}:\n{err}") from err

        if val != read_val:
            raise Error(f"failed to {msg}:\nfile '{path}' contains '{read_val}', but should "
                        f"contain '{val}'")

    def _do_toggle_cstates(self, cpus, indexes, enable, dflt_enable):
        """Implements '_toggle_cstates()'."""

        if dflt_enable is not None:
            # Walk through all CPUs.
            go_cpus = go_indexes = None
        else:
            go_cpus = cpus
            go_indexes = indexes

        if cpus is not None:
            cpus = set(cpus)
        if indexes is not None:
            indexes = set(indexes)

        for info in self._get_cstates_info(go_cpus, go_indexes, False):
            cpu = info["cpu"]
            index = info["index"]
            if (cpus is None or cpu in cpus) and (indexes is None or index in indexes):
                self._toggle_cstate(cpu, index, enable)
            elif dflt_enable is not None:
                self._toggle_cstate(cpu, index, dflt_enable)

    def _toggle_cstates(self, cpus=None, cstates=None, enable=True, dflt_enable=None):
        """
        Enable or disable C-states 'cstates' on CPUs 'cpus'. The arguments are as follows.
          * cstates - same as in 'get_cstates_info()'.
          * cpus - same as in 'get_cstates_info()'.
          * enabled - if 'True', the specified C-states should be enabled on the specified CPUS,
                      otherwise disabled.
          * dflt_enable - if 'None', nothing is done for the CPUs and C-states that are not in the
                          'cstates'/'cpus' lists. If 'True', those C-states are enabled on those
                          CPUs, otherwise disabled.
        """

        if cpus == "all":
            cpus = None
        if cstates == "all":
            cstates = None
        cpus = ArgParse.parse_int_list(cpus, ints=True, dedup=True, sort=True)
        cstates = self._normalize_cstates(cstates)
        self._do_toggle_cstates(cpus, cstates, enable, dflt_enable)

    def enable_cstates(self, cpus=None, cstates=None):
        """
        Enable C-states 'cstates' on CPUs 'cpus'. The 'cstates' and 'cpus' arguments are the same as
        in 'get_cstates_info()'.
        """
        self._toggle_cstates(cpus, cstates, True)

    def disable_cstates(self, cpus=None, cstates=None):
        """
        Disable C-states 'cstates' on CPUs 'cpus'. The 'cstates' and 'cpus' arguments are the same
        as in 'get_cstates_info()'.
        """
        self._toggle_cstates(cpus, cstates, False)

    def _get_cstates_info(self, cpus, indexes, ordered):
        """Implements 'get_cstates_info()'."""

        indexes_regex = cpus_regex = "[[:digit:]]+"
        if cpus is not None:
            cpus_regex = "|".join([str(cpu) for cpu in cpus])
        if indexes is not None:
            indexes_regex = "|".join([str(index) for index in indexes])

        cmd = fr"find '{self._sysfs_base}' -type f -regextype posix-extended " \
              fr"-regex '.*cpu({cpus_regex})/cpuidle/state({indexes_regex})/[^/]+' " \
              fr"-exec printf '%s' {{}}: \; -exec grep . {{}} \;"

        stdout, _ = self._proc.run_verify(cmd, join=False)
        if not stdout:
            raise Error(f"failed to find C-states information in '{self._sysfs_base}'"
                        f"{self._proc.hostmsg}")

        if ordered:
            stdout = sorted(stdout)

        regex = re.compile(r".+/cpu([0-9]+)/cpuidle/state([0-9]+)/(.+):([^\n]+)")
        info = {}
        index = prev_index = cpu = prev_cpu = None

        for line in stdout:
            matchobj = re.match(regex, line)
            if not matchobj:
                raise Error(f"failed to parse the follwoing line from file in '{self._sysfs_base}'"
                            f"{self._proc.hostmsg}:\n{line.strip()}")

            cpu = int(matchobj.group(1))
            index = int(matchobj.group(2))
            key = matchobj.group(3)
            val = matchobj.group(4)
            if Trivial.is_int(val):
                val = int(val)

            if prev_cpu is None:
                prev_cpu = cpu
            if prev_index is None:
                prev_index = index

            if cpu != prev_cpu or index != prev_index:
                info["cpu"] = prev_cpu
                info["index"] = prev_index
                yield info
                prev_cpu = cpu
                prev_index = index
                info = {}

            info[key] = val

        info["cpu"] = prev_cpu
        info["index"] = prev_index
        yield info

    def get_cstates_info(self, cpus=None, cstates=None, ordered=True):
        """
        Yield information about C-states specified in 'cstate' for CPUs specified in 'cpus'.
          * cpus - list of CPUs and CPU ranges. This can be either a list or a string containing a
                   comma-separated list. For example, "0-4,7,8,10-12" would mean CPUs 0 to 4, CPUs
                   7, 8, and 10 to 12. 'None' and 'all' mean "all CPUs" (default).
          * cstates - the list of C-states to get information about. The list can contain both
                      C-state names and C-state indexes. It can be both a list or a string
                      containing a comma-separated list. 'None' and 'all' mean "all C-states"
                      (default).
          * ordered - if 'True', the yielded C-states will be ordered so that smaller CPU numbers
                      will go first, and for each CPU number shallower C-states will go first.
        """

        if cpus == "all":
            cpus = None
        if cstates == "all":
            cstates = None

        cpus = ArgParse.parse_int_list(cpus, ints=True, dedup=True, sort=True)
        cstates = self._normalize_cstates(cstates)
        for info in self._get_cstates_info(cpus, cstates, ordered):
            yield info

    def get_cstate_info(self, cpu, cstate):
        """
        Returns information about C-state 'cstate' on CPU number 'cpu'. The C-state can be specified
        both by its index and name.
        """

        return next(self.get_cstates_info(cpu, cstate))

    def __init__(self, proc=None):
        """
        The class constructor. The 'proc' argument is a 'Proc' or 'SSH' object that defines the
        host to create a class instance for (default is the local host). This object will keep a
        'proc' reference and use it in various methods.
        """

        if not proc:
            proc = Procs.Proc()

        self._lscpu_cache = None
        self._cpuinfo = None
        self._proc = proc
        self._sysfs_base = Path("/sys/devices/system/cpu")

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
