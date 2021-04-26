# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2016-2020 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module provides an API to get CPU information.
"""

import re
from itertools import groupby
from wultlibs.helperlibs.Exceptions import Error # pylint: disable=unused-import
from wultlibs.helperlibs import ArgParse, Procs, Trivial

# CPU model numbers.
INTEL_FAM6_SPR_X = 0x8F       # Sapphire Rapids Xeon.
INTEL_FAM6_ICELAKE_X = 0x6A   # Icelake Xeon.
INTEL_FAM6_ICELAKE_D = 0x6C   # Icelake Xeon D.
INTEL_FAM6_SKYLAKE_X = 0x55   # Skylake, Cascadelake, and Cooperlake Xeon.
INTEL_FAM6_BROADWELL_X = 0x4F # Broadwell Xeon.
INTEL_FAM6_BROADWELL_G = 0x47 # Broadwell Xeon with Graphics.
INTEL_FAM6_HASWELL_X = 0x3F   # Haswell Xeon.
INTEL_FAM6_IVYBRIDGE_X = 0x3E # Ivy Town Xeon.
INTEL_FAM6_GOLDMONT_D = 0x5F  # Goldmont Atom (Denverton).
INTEL_FAM6_TREMONT_D = 0x86   # Tremont Atom (Snow Ridge).

# CPU model description.
CPU_DESCR = {INTEL_FAM6_SPR_X: "Sapphire Rapids Xeon",
             INTEL_FAM6_ICELAKE_X: "Icelake Xeon",
             INTEL_FAM6_ICELAKE_D: "Icelake Xeon D",
             INTEL_FAM6_SKYLAKE_X: "Skylake/Cascadelake/Cooperlake Xeon",
             INTEL_FAM6_BROADWELL_X: "Broadwell Xeon",
             INTEL_FAM6_BROADWELL_G: "Broadwell Xeon with Graphics",
             INTEL_FAM6_HASWELL_X: "Haswell Xeon",
             INTEL_FAM6_IVYBRIDGE_X: "Ivy Town Xeon",
             INTEL_FAM6_GOLDMONT_D: "Goldmont Atom (Denverton)",
             INTEL_FAM6_TREMONT_D: "Tremont Atom (Snow Ridge)"}

LEVELS = ("pkg", "node", "core", "cpu")

def get_lscpu_info(proc=None):
    """
    Run the 'lscpu' command on the host defined by the 'proc' argument, and return the output in
    form of a dictionary. Thie dictionary will contain the general CPU information without the
    topology information. By default this function returns local CPU information. However, you can
    pass it an 'SSH' object via the 'proc' argument, in which case this function will return CPU
    information of the host the 'SSH' object is connected to.
    """

    if not proc:
        proc = Procs.Proc()

    cpuinfo = {}
    lscpu, _ = proc.run_verify("lscpu", join=False)

    # Parse misc. information about the CPU.
    patterns = ((r"^Architecture:\s*(.*)$", "arch"),
                (r"^Byte Order:\s*(.*)$", "byteorder"),
                (r"^Vendor ID:\s*(.*)$", "vendor"),
                (r"^Socket\(s\):\s*(.*)$", "packages"),
                (r"^CPU family:\s*(.*)$", "family"),
                (r"^Model:\s*(.*)$", "model"),
                (r"^Model name:\s*(.*)$", "modelname"),
                (r"^Model name:.*@\s*(.*)GHz$", "basefreq"),
                (r"^Stepping:\s*(.*)$", "stepping"),
                (r"^L1d cache:\s*(.*)$", "l1d"),
                (r"^L1i cache:\s*(.*)$", "l1i"),
                (r"^L2 cache:\s*(.*)$", "l2"),
                (r"^L3 cache:\s*(.*)$", "l3"),
                (r"^Flags:\s*(.*)$", "flags"))

    for line in lscpu:
        for pattern, key in patterns:
            match = re.match(pattern, line.strip())
            if not match:
                continue

            val = match.group(1)
            if Trivial.is_int(val):
                cpuinfo[key] = int(val)
            else:
                cpuinfo[key] = val

    if cpuinfo.get("flags"):
        cpuinfo["flags"] = cpuinfo["flags"].split()

    return cpuinfo

class CPUInfo:
    """
    Provide information about the CPU of a local or remote host.
    """

    def _get_lscpu(self):
        """Return the 'lscpu' output."""

        if self._lscpu_cache:
            return self._lscpu_cache

        # Note, we could just walk sysfs, but 'lscpu' seems a bit more convenient.
        cmd = "lscpu --all -p=socket,node,core,cpu,online"
        self._lscpu_cache, _ = self._proc.run_verify(cmd, join=False)
        return self._lscpu_cache

    def _get_level(self, start, end, nums=None):
        """
        Returns list of level 'end' values belonging to level 'start' for each ID in 'nums'. Returns
        all values if 'nums' is None or "all". Offline CPUs are ignored.
        """

        if start not in LEVELS or end not in LEVELS:
            levels = ", ".join(LEVELS)
            raise Error(f"bad levels '{start}','{end}', use: {levels}")

        start_idx = LEVELS.index(start)
        end_idx = LEVELS.index(end)
        if start_idx > end_idx:
            raise Error(f"bad level order, cannot get {end}s from level '{start}'")

        items = {}
        for line in self._get_lscpu():
            if line.startswith("#"):
                continue
            # Each line has comma-separated integers for socket, node, core and cpu. For example:
            # 1,1,9,61,Y. In case of offline CPU, the final element is going to be "N".
            line = line.strip().split(",")
            if line[-1] != "Y":
                # Skip non-online CPUs.
                continue
            line = [int(val) for val in line[0:-1]]
            if line[start_idx] in items.keys():
                items[line[start_idx]].append(line[end_idx])
            else:
                items[line[start_idx]] = [line[end_idx]]

        # So now 'items' is a dictionary with keys being the 'start' level elements and values being
        # lists of the 'end' level elements.
        # For example, suppose we are looking for CPUs in packages, and the system has 2 packages,
        # each containing 8 CPUs. The 'items' dictionary will look like this:
        # items[0] = {0, 2, 4, 6, 8, 10, 12, 14}
        # items[1] = {1, 3, 6, 7, 9, 11, 13, 15}
        # In this example, package 0 includes CPUs with even numbers, and package 1 includes CPUs
        # with odd numbers.

        if nums is None or nums == "all":
            nums = list(items.keys())
        else:
            nums = ArgParse.parse_int_list(nums, ints=True, dedup=True, sort=True)

        result = []
        for num in nums:
            if num not in items:
                items_str = ", ".join(str(key) for key in items)
                raise Error(f"{start} {num} does not exist{self._proc.hostmsg}, use: {items_str}")
            result += items[num]

        return Trivial.list_dedup(result)

    def get_cpus(self, lvl="cpu", nums=None):
        """
        Returns list of online CPU numbers belonging to level 'lvl' for each ID in 'nums'. The 'lvl'
        argument is one of the level names  defined in 'LEVELS'.

        For example, when 'lvl' is 'pkg' and 'nums' is '(1,3)', this function returns list of CPU
        numbers in packages number 1 and 3. If 'lvl' is 'core', and 'nums' is '(4,)', this function
        returns list of CPU numbers in core 4.

        Note, 'num' is allowed contain both integer and string type numbers. For example, both are
        OK: '(0, 2)' and '("0", "2")'. Returns all CPU numbers if 'nums' is None or "all".

        This function ignores offline CPUs and does not include them into the list.
        """

        return self._get_level(lvl, "cpu", nums)

    def get_cores(self, lvl="pkg", nums=None):
        """
        Returns list of core numbers, where at least one online CPU. 'nums' argument is same as
        in 'get_cpus()'.
        """

        return self._get_level(lvl, "core", nums)

    def get_packages(self, nums=None):
        """
        Returns list of package numbers, where at least one online CPU. 'nums' argument is same as
        in 'get_cpus()'.
        """

        return self._get_level("pkg", "pkg", nums)

    def get_cpu_list(self, cpus):
        """Validate CPUs in 'cpus'. Returns CPU numbers as list of integers."""

        allcpus = self.get_cpus()

        if cpus is None or cpus == "all":
            return allcpus

        allcpus = set(allcpus)
        cpus = ArgParse.parse_int_list(cpus, ints=True, dedup=True, sort=True)
        for cpu in cpus:
            if cpu not in allcpus:
                cpus_str = ", ".join([str(cpu) for cpu in sorted(allcpus)])
                raise Error(f"CPU{cpu} is not available{self._proc.hostmsg}, available CPUs are: "
                            f"{cpus_str}")

        return cpus

    def get_package_list(self, pkgs):
        """Validate packages in 'pkgs'. Returns packages as list of integers."""

        allpkgs = self.get_packages()

        if pkgs is None or pkgs == "all":
            return allpkgs

        allpkgs = set(allpkgs)
        pkgs = ArgParse.parse_int_list(pkgs, ints=True, dedup=True, sort=True)
        for pkg in pkgs:
            if pkg not in allpkgs:
                pkgs_str = ", ".join([str(pkg) for pkg in sorted(allpkgs)])
                raise Error(f"package '{pkg}' not available{self._proc.hostmsg}, available "
                            f"packages are: {pkgs_str}")

        return pkgs

    def cpu_to_package(self, cpu):
        """Returns integer package number for CPU number 'cpu'."""

        for pkg in self.get_packages():
            if cpu in self.get_cpus(lvl="pkg", nums=pkg):
                return pkg

        allcpus = self.get_cpus()
        cpus_str = ", ".join([str(cpu) for cpu in sorted(allcpus)])
        raise Error(f"CPU{cpu} is not available{self._proc.hostmsg}, available CPUs are:\n"
                    f"{cpus_str}")

    def cpu_to_core(self, cpu):
        """Returns integer core number for CPU number 'cpu'."""

        for core in self.get_cores():
            if cpu in self.get_cpus(lvl="core", nums=core):
                return core

        allcpus = self.get_cpus()
        cpus_str = ", ".join([str(cpu) for cpu in sorted(allcpus)])
        raise Error(f"CPU{cpu} is not available{self._proc.hostmsg}, available CPUs are:\n"
                    f"{cpus_str}")

    def _add_nums(self, nums):
        """Add numbers from 'lscpu' to the CPU geometry dictionary."""

        item = self.cpugeom[LEVELS[0] + "s"]
        for idx, lvl in enumerate(LEVELS[:-1]):
            last_level = False
            if idx == len(LEVELS) - 2:
                last_level = True

            num = int(nums[lvl])
            if num not in item:
                self.cpugeom[lvl + "cnt"] += 1
                if last_level:
                    item[num] = []
                else:
                    item[num] = {}

            if last_level:
                lvl = LEVELS[-1]
                item[num].append(int(nums[lvl]))
                self.cpugeom[lvl + "cnt"] += 1

            item = item[num]

    def _flatten_to_level(self, items, idx):
        """Flatten the multi-level 'items' dictionary down to level 'idx'."""

        if idx == 0:
            return items

        result = {}
        for item in items.values():
            add_items = self._flatten_to_level(item, idx - 1)
            if isinstance(add_items, list):
                if not result:
                    result = []
                result += add_items
            else:
                result.update(add_items)

        return result

    def get_cpu_geometry(self):
        """
        Get CPU geometry information. The resulting geometry dictionary is returnd and also saved in
        'self.cpugeom'. Note, if this method was already called before, it will return the cached
        geometry dircionary ('self.cpugeom').
        """

        if self.cpugeom:
            return self.cpugeom

        # All the level we are dealing with. The resulting dictionary will include a key for evey
        # level with a dictionary conatainging the partial hiararchy. The lowest level is always a
        # list though.
        self.cpugeom = cpugeom = {}
        for lvl in LEVELS:
            for pfx in ("", "off"):
                if pfx == "off" and lvl != LEVELS[-1]:
                    continue
                cpugeom[pfx + lvl + "s"] = {}
                cpugeom[pfx + lvl + "s_sorted"] = []
                cpugeom[pfx + lvl + "s_grouped"] = []
                cpugeom[pfx + lvl + "_ranges"] = []

        # Count of packages, NUMA nodes, cores, etc.
        for lvl in LEVELS:
            cpugeom[lvl + "cnt"] = 0

        # List of offline CPUs. Note, Linux does not provide topology information for offline CPUs,
        # so we only have the CPU numbers.
        cpugeom["offcpus"] = []
        # Offline CPUs count.
        cpugeom["offcpucnt"] = 0

        # Parse the 'lscpu' output.
        for line in self._get_lscpu():
            if line.startswith("#"):
                continue

            split_line = line.strip().split(",")
            nums = {key : split_line[idx] for idx, key in enumerate(LEVELS)}
            if split_line[-1] != "Y":
                cpugeom["offcpucnt"] += 1
                cpugeom["offcpus"].append(int(nums["cpu"]))
                continue

            self._add_nums(nums)

        # Now we have the full hierarcy (in 'cpugeom["pkgs"]'). Create partial hierarchies
        # ('cpugom["nodes"]', etc).
        for lvlidx, lvl in enumerate(LEVELS[1:]):
            cpugeom[lvl + "s"] = self._flatten_to_level(cpugeom[LEVELS[0] + "s"], lvlidx + 1)

        # Sort CPU lists by CPU number.
        for lvl in LEVELS:
            cpugeom[lvl + "s_sorted"] = sorted(cpugeom[lvl + "s"])
        cpugeom["offcpus_sorted"] = sorted(cpugeom["offcpus"])

        # Group consequative CPU numbers into ranges. The end result is list of lists of consequtive
        # CPU numbers. Do the same for packages, nodes and all the other levels.
        for lvl in LEVELS:
            # This is the grouping function that subtracts list index from CPU number.
            keyfunc = lambda elt: int(elt[1]) - elt[0]
            for pfx in ("", "off"):
                if pfx == "off" and lvl != LEVELS[-1]:
                    continue
                for _, grp in groupby(enumerate(cpugeom[pfx + lvl + "s_sorted"]), keyfunc):
                    cpugeom[pfx + lvl + "s_grouped"].append([elt[1] for elt in grp])
                for cpus in cpugeom[pfx + lvl + "s_grouped"]:
                    if len(cpus) == 1:
                        cpugeom[pfx + lvl + "_ranges"].append(str(cpus[0]))
                    else:
                        cpugeom[pfx + lvl + "_ranges"].append(f"{cpus[0]}-{cpus[-1]}")

        for lvl1 in LEVELS[1:]:
            for lvl2 in LEVELS[:-1]:
                if lvl1 == lvl2:
                    continue
                key = lvl1 + "s_per_" + lvl2
                lvl1_key = lvl1 + "cnt"
                lvl2_key = lvl2 + "cnt"
                try:
                    cpugeom[key] = int(cpugeom[lvl1_key] / cpugeom[lvl2_key])
                except ZeroDivisionError:
                    cpugeom[key] = 0

        return cpugeom

    def __init__(self, proc=None):
        """
        The class constructor. The 'proc' argument is a 'Proc' or 'SSH' object that defines the
        host to create a class instance for (default is the local host). This object will keep a
        'proc' reference and use it in various methods.
        """

        if not proc:
            proc = Procs.Proc()
        self._proc = proc

        self.cpugeom = None
        self._lscpu_cache = None

    def close(self):
        """Uninitialize the class object."""
        if getattr(self, "_proc", None):
            self._proc = None

    def __enter__(self):
        """Enter the runtime context."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the runtime context."""
        self.close()
