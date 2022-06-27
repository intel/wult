# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2016-2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module implements parsing for the output of the "turbostat" Linux tool. The input file should
consist of one or multiple turbostat data tables.
"""

import re
from itertools import zip_longest
from pepclibs.helperlibs import Trivial
from pepclibs.helperlibs.Exceptions import Error
from wultlibs.parsers import _ParserBase

# The default regular expression for turbostat columns to parse.
_COLS_REGEX = r".*\s*Avg_MHz\s+(Busy%|%Busy)\s+Bzy_MHz\s+.*"

# Aggregation methods used by turbostat to summarise columns.
SUM = "sum"
AVG = "average"

def get_aggregation_method(key):
    """
    Turbostat summaries are aggregations of values for all CPUs in the system. Different columns
    are aggregated with different methods. Given a 'key', this function returns one of the
    aggregation method constants.
    """

    # For IRQ, SMI, and C-state requests count - just return the sum.
    if key in ("IRQ", "SMI") or re.match("^C[0-9][A-Z]?$", key):
        return SUM
    return AVG

def _parse_turbostat_line(heading, line):
    """Parse a single turbostat line."""

    line_data = {}
    for key, value in zip_longest(heading.keys(), line):
        if value is not None and value != "-":
            if not heading[key]:
                if Trivial.is_int(value):
                    heading[key] = int
                elif Trivial.is_float(value):
                    heading[key] = float
                else:
                    heading[key] = str
            line_data[key] = heading[key](value)

    return line_data

def _construct_totals(packages):
    """
    Turbostat provide package and core totals in some lines of the table. This function moves them
    to the "totals" key of the package hierarchy.
    """

    def calc_total(vals, key):
        """
        Calculate the "total" value for a piece of turbostat statistics defined by 'key'. The
        resulting "total" value is usually the average, but some statistics require just the sum,
        for example the IRQ count. This function returns the proper "total" value depending on the
        'key' contents. Arguments are as follows:
         * vals - an interable containing all of the different values of 'key'.
         * key - the name of the turbostat metric which the values in 'vals' represent.
        """

        agg_method = get_aggregation_method(key)
        if agg_method == SUM:
            return sum(vals)
        if agg_method == AVG:
            return sum(vals)/len(vals)
        raise Error(f"BUG: unable to summarise turbostat column '{key}' with method '{agg_method}'")

    for pkginfo in packages.values():
        for coreinfo in pkginfo["cores"].values():
            sums = {}
            for cpuinfo in coreinfo["cpus"].values():
                for key, val in cpuinfo.items():
                    if key not in sums:
                        sums[key] = []
                    sums[key].append(val)

            if "totals" not in coreinfo:
                coreinfo["totals"] = {}
            for key, vals in sums.items():
                coreinfo["totals"][key] = calc_total(vals, key)

        sums = {}
        for coreinfo in pkginfo["cores"].values():
            for key, val in coreinfo["totals"].items():
                if key not in sums:
                    sums[key] = []
                sums[key].append(val)

        if "totals" not in pkginfo:
            pkginfo["totals"] = {}
        for key, vals in sums.items():
            pkginfo["totals"][key] = calc_total(vals, key)

    # Remove the CPU information keys that are actually not CPU-level but rather core or package
    # level. We already have these keys in core or package totals.
    common_keys = None
    for pkginfo in packages.values():
        for coreinfo in pkginfo["cores"].values():
            for cpuinfo in coreinfo["cpus"].values():
                if common_keys is None:
                    common_keys = set(cpuinfo)
                else:
                    common_keys &= set(cpuinfo)

    for pkginfo in packages.values():
        for coreinfo in pkginfo["cores"].values():
            for cpuinfo in coreinfo["cpus"].values():
                for key in list(cpuinfo):
                    if key not in common_keys:
                        del cpuinfo[key]

    # The the *_MHz totals provided by turbostat are weighted averages of the per-CPU values. The
    # weights are the amoung of cycles the CPU spent executing instructions instead of being in a
    # C-state.
    ignore_keys = ("Avg_MHz", "Bzy_MHz")
    for pkginfo in packages.values():
        for key in ignore_keys:
            del pkginfo["totals"][key]
        for coreinfo in pkginfo["cores"].values():
            for key in ignore_keys:
                del coreinfo["totals"][key]

def _construct_the_result(totals, cpus, nontable):
    """
    Construct and return the final dictionary corresponding to a parsed turbostat table.
    """

    result = {}
    result["nontable"] = nontable
    result["totals"] = totals

    # Additionally provide the "packages" info sorted in the (Package,Core,CPU) order.
    result["packages"] = packages = {}
    cpu_count = core_count = pkg_count = 0

    for cpuinfo in cpus.values():
        if "Package" not in cpuinfo:
            # The turbostat table does not include the "Package" column in case if there is only one
            # CPU package. Emulate it.
            cpuinfo["Package"] = "0"
        if cpuinfo["Package"] not in packages:
            packages[cpuinfo["Package"]] = pkgdata = {}
            pkg_count += 1
        if "cores" not in pkgdata:
            pkgdata["cores"] = {}

        cores = pkgdata["cores"]
        if cpuinfo["Core"] not in cores:
            cores[cpuinfo["Core"]] = coredata = {}
            core_count += 1

        if "cpus" not in coredata:
            coredata["cpus"] = {}
        cpus = coredata["cpus"]
        cpus[cpuinfo["CPU"]] = cpuinfo
        cpu_count += 1

        # The package/core/CPU number keys in 'cpuinfo' are not needed anymore.
        for key in ("Package", "Core", "CPU"):
            del cpuinfo[key]

    result["cpu_count"] = cpu_count
    result["core_count"] = core_count
    result["pkg_count"] = pkg_count

    _construct_totals(packages)

    return result

def _parse_cpu_flags(nontable, line):
    """Parse turbostat CPU flags."""

    prefix = "CPUID(6):"
    if line.startswith(prefix):
        tsflags = line[len(prefix):].split(",")
        nontable["flags"] = [tsflag.strip() for tsflag in tsflags]

def _add_nontable_data(nontable, line):
    """
    Turbostat prints lots of useful information when used with the '-d' option. Try to identify the
    useful bits and add them to the "nontable" dictionary.
    """

    # Example:
    # 10 * 100 = 1000 MHz max efficiency frequency
    match = re.match(r'\d+ \* [.\d]+ = ([.\d]+) MHz max efficiency frequency', line)
    if match:
        nontable["MaxEfcFreq"] = float(match.group(1))
        return

    # Example:
    # 18 * 100 = 1800 MHz base frequency
    match = re.match(r'\d+ \* [.\d]+ = ([.\d]+) MHz base frequency', line)
    if match:
        nontable["BaseFreq"] = float(match.group(1))
        return

    # Example:
    # 22 * 100 = 2200 MHz max turbo 8 active cores
    match = re.match(r'\d+ \* [.\d]+ = ([.\d]+) MHz max turbo (\d+) active cores', line)
    if match:
        if not "MaxTurbo" in nontable:
            nontable["MaxTurbo"] = {}
        nontable["MaxTurbo"][match.group(2)] = float(match.group(1))
        return

    # Example:
    # cpu0: MSR_PKG_POWER_INFO: 0xf0ce803980528 (165 W TDP, RAPL 115 - 413 W, 0.014648 sec.)
    match = re.match(r'cpu\d+: MSR_PKG_POWER_INFO: .+ \(([.\d]+) W TDP, .+\)', line)
    if match:
        nontable["TDP"] = int(match.group(1))
        return

    _parse_cpu_flags(nontable, line)

class TurbostatParser(_ParserBase.ParserBase):
    """This class represents the turbostat output parser."""

    def _next(self):
        """
        Generator which yields a dictionary corresponding to one snapshot of turbostat output at a
        time.
        """

        cpus = {}
        table_started = False
        nontable = {}
        heading = totals = None

        tbl_regex = re.compile(self._cols_regex)

        for line in self._lines:
            # Ignore empty and 'jitter' lines like "turbostat: cpu65 jitter 2574 5881".
            if not line or line.startswith("turbostat: "):
                continue

            # Match the beginning of the turbostat table.
            if not table_started and not re.match(tbl_regex, line):
                _add_nontable_data(nontable, line)
                continue

            line = line.split()
            if Trivial.is_float(line[0]):
                # This is the continuation of the table we are currently parsing. It starts either
                # with a floating-point 'Time_Of_Day_Seconds' an integer 'Core' value. Each line
                # describes a single CPU.
                cpu_data = _parse_turbostat_line(heading, line)
                cpus[cpu_data["CPU"]] = cpu_data
            else:
                # This is the start of the new table.
                if cpus or table_started:
                    if not cpus:
                        # This is the the special case for single-CPU systems. Turbostat does not
                        # print the totals because there is only one CPU and totals is the the same
                        # as the CPU information.
                        cpus[0] = totals
                    yield _construct_the_result(totals, cpus, nontable)
                    nontable = {}
                    cpus = {}

                heading = {}
                for key in line:
                    if "%" in key or "Watt" in key or key in {"Time_Of_Day_Seconds", "IPC"}:
                        heading[key] = float
                    elif key in ("Package", "Core", "CPU"):
                        heading[key] = str
                    else:
                        heading[key] = None

                # The next line is total statistics across all CPUs, exept if there is only one
                # single CPU in the system.

                # False pylint warning, see issue: https://github.com/PyCQA/pylint/issues/1830
                line = next(self._lines).split() # pylint: disable=stop-iteration-return

                # On systems with a single core turbostat does not include the "Core" colum. Similar
                # to single CPU systems - the CPU column is excluded. Make sure we always have them.
                for key in ("Core", "CPU"):
                    if key not in heading:
                        heading[key] = str
                        line.append("0")

                totals = _parse_turbostat_line(heading, line)

            table_started = True

        yield _construct_the_result(totals, cpus, nontable)

    def __init__(self, path=None, lines=None, cols_regex=None):
        """
        TurbostatParser constructor. Arguments:
        * path: same as in ParserBase.__init__()
        * lines: same as in ParserBase.__init__()
        * cols_regex: the regular expression to match against the 'turbostat' heading line (first
                      line printed with 'turbostat -q -S'). Has to be uses in case 'turbostat' was
                      run with custom colums selection (see 'turbostat --show').
        """

        super().__init__(path, lines)

        if not cols_regex:
            cols_regex = _COLS_REGEX

        self._cols_regex = cols_regex
