# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module implements collecting the "system information" type of statistics.
"""

import logging
from pepclibs.helperlibs.Exceptions import Error

_LOG = logging.getLogger()

def _run_commands(cmdinfos, pman):
    """Execute the commands specified in the 'cmdinfos' dictionary."""

    if pman.is_remote:
        # In case of a remote host, it is much more efficient to run all commands in one go, because
        # in this case only one SSH session needs to be established.
        cmd = ""
        for cmdinfo in cmdinfos.values():
            cmd += cmdinfo["cmd"] + " &"

        cmd += " wait"
        try:
            pman.run_verify(cmd, shell=True)
        except Error as err:
            _LOG.warning("Some system statistics were not collected")
            _LOG.debug(str(err))
    else:
        procs = []
        errors = []
        for cmdinfo in cmdinfos.values():
            try:
                procs.append(pman.run_async(cmdinfo["cmd"], shell=True))
            except Error as err:
                errors.append(str(err))

        for cmd_proc in procs:
            try:
                cmd_proc.wait(capture_output=False, timeout=5*60)
            except Error as err:
                errors.append(str(err))

        if errors:
            _LOG.warning("Not all the system statistics were collected, here are the failures\n%s",
                         "\nNext error:\n".join(errors))

def _collect_totals(outdir, when, pman):
    """
    This is a helper for collecting the global statistics which may change after a workload has been
    run on the SUT. For example, 'dmesg' may have additional lines, come 'cpufreq' sysfs files may
    change, etc. We collect this sort of information twice - before and after the workload.

    The 'outdir' is path on the SUT defined by the 'pman' object and the 'when' argument should be a
    "before" or "after" string.
    """

    cmdinfos = {}

    pattern = r"""find /sys/devices/system/cpu/ -type f -regex '.*/%s/.*' """ \
              r"""-exec sh -c "echo '{}:'; cat '{}'; echo" \; > '%s' 2>&1"""

    cmdinfos["cpuidle"] = cmdinfo = {}
    outfile = outdir / f"sys-cpuidle.{when}.raw.txt"
    cmdinfo["outfile"] = outfile
    cmdinfo["cmd"] = pattern % ("cpuidle", outfile)

    cmdinfos["cpufreq"] = cmdinfo = {}
    outfile = outdir / f"sys-cpufreq.{when}.raw.txt"
    cmdinfo["outfile"] = outfile
    cmdinfo["cmd"] = pattern % ("cpufreq", outfile)

    cmdinfos["turbostat"] = cmdinfo = {}
    outfile = outdir / f"turbostat-d.{when}.raw.txt"
    cmdinfo["outfile"] = outfile
    cmdinfo["cmd"] = f"turbostat -- sleep 1 > '{outfile}' 2>&1"

    cmdinfos["dmesg"] = cmdinfo = {}
    outfile = outdir / f"dmesg.{when}.raw.txt"
    cmdinfo["outfile"] = outfile
    cmdinfo["cmd"] = f"dmesg > '{outfile}' 2>&1"

    cmdinfos["journalctl"] = cmdinfo = {}
    outfile = outdir / f"journalctl-b.{when}.raw.txt"
    cmdinfo["outfile"] = outfile
    cmdinfo["cmd"] = f"journalctl -b > '{outfile}' 2>&1"

    cmdinfos["x86_energy_perf_policy"] = cmdinfo = {}
    outfile = outdir / f"x86_energy_perf_policy.{when}.raw.txt"
    cmdinfo["outfile"] = outfile
    cmdinfo["cmd"] = f"x86_energy_perf_policy > '{outfile}' 2>&1"

    cmdinfos["proc_interrupts"] = cmdinfo = {}
    outfile = outdir / f"interrupts.{when}.raw.txt"
    cmdinfo["outfile"] = outfile
    cmdinfo["cmd"] = f"cat /proc/interrupts > '{outfile}' 2>&1"

    return _run_commands(cmdinfos, pman)

def collect_before(outdir, pman):
    """
    Collect information about a host defined by th 'pman' process manager object.

    This function is supposed to be called before running a workload on the SUT. It will collect
    various global data like the contents of the '/proc/cmdline' file, the 'lspci' output, and store
    the data in the 'outdir' directory on the SUT.
    """

    pman.mkdir(outdir, parents=True, exist_ok=True)

    cmdinfos = {}

    cmdinfos["proc_cmdline"] = cmdinfo = {}
    outfile = outdir / "proc_cmdline.raw.txt"
    cmdinfo["outfile"] = outfile
    cmdinfo["cmd"] = f"cat /proc/cmdline > '{outfile}' 2>&1"

    cmdinfos["uname_a"] = cmdinfo = {}
    outfile = outdir / "uname-a.raw.txt"
    cmdinfo["outfile"] = outfile
    cmdinfo["cmd"] = f"uname -a > '{outfile}' 2>&1"

    cmdinfos["dmidecode"] = cmdinfo = {}
    outfile = outdir / "dmidecode.raw.txt"
    cmdinfo["outfile"] = outfile
    cmdinfo["cmd"] = f"dmidecode > '{outfile}' 2>&1"

    cmdinfos["dmidecode_u"] = cmdinfo = {}
    outfile = outdir / "dmidecode-u.raw.txt"
    cmdinfo["outfile"] = outfile
    cmdinfo["cmd"] = f"dmidecode -u > '{outfile}' 2>&1"

    cmdinfos["lspci"] = cmdinfo = {}
    outfile = outdir / "lspci.raw.txt"
    cmdinfo["outfile"] = outfile
    cmdinfo["cmd"] = f"lspci > '{outfile}' 2>&1"

    cmdinfos["lspci_vvv"] = cmdinfo = {}
    outfile = outdir / "lspci-vvv.raw.txt"
    cmdinfo["outfile"] = outfile
    cmdinfo["cmd"] = f"lspci -vvv > '{outfile}' 2>&1"

    cmdinfos["proc_cpuinfo"] = cmdinfo = {}
    outfile = outdir / "proc_cpuinfo.raw.txt"
    cmdinfo["outfile"] = outfile
    cmdinfo["cmd"] = f"cat /proc/cpuinfo > '{outfile}' 2>&1"

    cmdinfos["lsmod"] = cmdinfo = {}
    outfile = outdir / "lsmod.raw.txt"
    cmdinfo["outfile"] = outfile
    cmdinfo["cmd"] = f"lsmod > '{outfile}' 2>&1"

    cmdinfos["lsusb"] = cmdinfo = {}
    outfile = outdir / "lsusb.raw.txt"
    cmdinfo["outfile"] = outfile
    cmdinfo["cmd"] = f"lsusb > '{outfile}' 2>&1"

    cmdinfos["lsusb_v"] = cmdinfo = {}
    outfile = outdir / "lsusb-v.raw.txt"
    cmdinfo["outfile"] = outfile
    cmdinfo["cmd"] = f"lsusb -v > '{outfile}' 2>&1"

    cmdinfos["lsblk"] = cmdinfo = {}
    outfile = outdir / "lsblk.raw.txt"
    cmdinfo["outfile"] = outfile
    cmdinfo["cmd"] = f"lsblk > '{outfile}' 2>&1"

    cmdinfos["sysctl_all"] = cmdinfo = {}
    outfile = outdir / "sysctl-all.raw.txt"
    cmdinfo["outfile"] = outfile
    cmdinfo["cmd"] = f"sysctl --all > '{outfile}' 2>&1"

    cmdinfos["pepc_cstates"] = cmdinfo = {}
    outfile = outdir / "pepc_cstates.raw.txt"
    cmdinfo["outfile"] = outfile
    cmdinfo["cmd"] = f"pepc cstates info > '{outfile}' 2>&1"

    cmdinfos["pepc_pstates"] = cmdinfo = {}
    outfile = outdir / "pepc_pstates.raw.txt"
    cmdinfo["outfile"] = outfile
    cmdinfo["cmd"] = f"pepc pstates info > '{outfile}' 2>&1"

    _run_commands(cmdinfos, pman)
    _collect_totals(outdir, "before", pman)

def collect_after(outdir, pman):
    """
    Collect information about a host defined by th 'pman' process manager object.

    This function is supposed to be called after running a workload on the SUT. It will collect the
    information that may change after the workload. For example, the 'dmesg' output may contain new
    lines, so it is beneficial to have a 'dmesg' snapshot before and after the workload. The data
    will be stored in the 'outdir' directory on the SUT.
    """

    _collect_totals(outdir, "after", pman)
