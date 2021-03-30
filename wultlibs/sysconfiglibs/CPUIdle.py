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
from wultlibs.helperlibs import FSHelpers, Procs, Trivial
from wultlibs.helperlibs.Exceptions import Error
from wultlibs.sysconfiglibs import CPUInfo

_LOG = logging.getLogger()

class CPUIdle:
    """This class provides API to the "cpuidle" Linux sybsystem."""

    def _get_cpuinfo(self):
        """Return an instance of 'CPUInfo' class."""

        if not self._cpuinfo:
            self._cpuinfo = CPUInfo.CPUInfo(proc=self._proc)
        return self._cpuinfo

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

        # 'None' will be translated to all C-states in '_get_cstates_info()'.
        if cstates == "all":
            cstates = None

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

    def _normalize_cpus(self, cpus):
        """
        Some methods accept CPUs as list or range of CPUs as described in 'get_cstates_info()'.
        Turn this userinput in 'cpus' as list of integers and return it.
        """

        cpuinfo = self._get_cpuinfo()
        return cpuinfo.get_cpu_list(cpus)

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

        cpus = self._normalize_cpus(cpus)
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

        cpus = self._normalize_cpus(cpus)
        cstates = self._normalize_cstates(cstates)

        for info in self._get_cstates_info(cpus, cstates, ordered):
            yield info

    def get_cstates_info_dict(self, cpu, cstates=None, ordered=True):
        """
        Returns a dictionary describing all C-states of CPU 'cpu'. C-state index is used as
        dictionary key. The 'cstates' and 'ordered' arguments are the same as in
        'get_cstates_info()'.
        """

        if not Trivial.is_int(cpu):
            raise Error(f"bad CPU number '{cpu}', should be an integer")

        info_dict = {}
        for info in self.get_cstates_info(cpus=cpu, cstates=cstates, ordered=ordered):
            info_dict[info["index"]] = info
        return info_dict

    def get_cstate_info(self, cpu, cstate):
        """
        Returns information about C-state 'cstate' on CPU number 'cpu'. The C-state can be specified
        both by its index and name.
        """

        return next(self.get_cstates_info(cpu, cstate))

    def __init__(self, proc=None, cpuinfo=None):
        """
        The class constructor. The arguments are as follows.
          * proc - the 'Proc' or 'SSH' object that defines the host to run the measurements on.
          * cpuinfo - CPU information object generated by 'CPUInfo.CPUInfo()'.
        """

        if not proc:
            proc = Procs.Proc()

        self._lscpu_info = None
        self._cpuinfo = cpuinfo
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
