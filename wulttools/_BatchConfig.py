# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Antti Laakso <antti.laakso@linux.intel.com>
#         Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
A helper module for the 'exercise-sut' tool to configure target system with various system property
permutations.
"""

import os
import sys
import time
import logging
import itertools
from pathlib import Path
from pepclibs import CStates, PStates, CPUInfo
from pepclibs.helperlibs import ClassHelpers, Human, LocalProcessManager, Trivial
from pepclibs.helperlibs.Exceptions import Error
from wulttools import _Common
from statscollectlibs.helperlibs import ReportID

_LOG = logging.getLogger()

PROP_INFOS = {
    "cstates" : {
        "name" : "Requestable C-state",
        "sname" : "CPU",
        "cmd" : "pepc cstates config --disable all --enable {} --cpus {scope}"},
    "pcstates" : {
        "name" : "Package C-state",
        "sname" : "package",
        "cmd" : "pepc cstates config --pkg-cstate-limit {} --cpus {scope}"},
    "freqs" : {
        "name" : "CPU frequency",
        "sname" : "CPU",
        "cmd" : "pepc pstates config --min-freq {} --max-freq {} --cpus {scope}"},
    "uncore_freqs" : {
        "name" : "Uncore frequency",
        "moniker" : "uf",
        "sname" : "die",
        "cmd" : "pepc pstates config --min-uncore-freq {} --max-uncore-freq {} --cpus " \
                "{scope}"},
    "governor" : {
        "moniker" : "gov",
        "cmd" : "pepc pstates config --governor {} --cpus {scope}"},
    "aspm" : {
        "name" : "ASPM",
        "moniker" : "aspm",
        "cmd" : "pepc aspm config --policy {}"},
    "c1_demotion" : {
        "moniker" : "c1d",
        "cmd" : "pepc cstates config --c1-demotion {} --cpus {scope}"},
    "c1_undemotion" : {
        "moniker" : "c1und",
        "cmd" : "pepc cstates config --c1-undemotion {} --cpus {scope}"},
    "c1e_autopromote" : {
        "moniker" : "autoc1e",
        "cmd" : "pepc cstates config --c1e-autopromote {} --cpus {scope}"},
    "cstate_prewake" : {
        "moniker" : "cpw",
        "cmd" : "pepc cstates config --cstate-prewake {} --cpus {scope}"},
    "epp" : {
        "moniker" : "epp",
        "cmd" : "pepc pstates config --epp {} --cpus {scope}"},
    "epb" : {
        "moniker" : "epb",
        "cmd" : "pepc pstates config --epb {} --cpus {scope}"},
    "turbo" : {
        "moniker" : "turbo",
        "cmd" : "pepc pstates config --turbo {}"},
    "online" : {
        "cmd" : "pepc cpu-hotplug online --cpus {}"},
}

PC0_ONLY_STATES = ("POLL", "C1", "C1E")

def list_monikers():
    """Helper to print moniker for each property, if any."""

    min_len = 0
    monikers = {}

    for pname, pinfo in PROP_INFOS.items():
        if "moniker" not in pinfo:
            continue

        name = None
        if pname in PStates.PROPS:
            name = PStates.PROPS[pname].get("name")
        elif pname in CStates.PROPS:
            name = CStates.PROPS[pname].get("name")
        else:
            name = pinfo.get("name")

        if len(name) > min_len:
            min_len = len(name)

        monikers[pinfo["moniker"]] = name

    for moniker, name in monikers.items():
        msg = f"{name:<{min_len}}: {moniker}"
        _LOG.info(msg)

def _get_workload_cmd_formatter(pman, args):
    """Create and return object for creating workload commands."""

    toolname = args.toolpath.name

    if toolname in ("wult", "ndl"):
        return _WultCmdFormatter(pman, args)

    if toolname == "benchmark":
        return _BenchmarkCmdFormatter(args)

    return _ToolCmdFormatterBase(args)

class _PropIteratorBase(ClassHelpers.SimpleCloseContext):
    """Class to help iterating system property permutations."""

    def _get_cpuinfo(self):
        """Return 'CPUInfo.CPUInfo()' object."""

        if not self._cpuinfo:
            self._cpuinfo = CPUInfo.CPUInfo(pman=self._pman)
        return self._cpuinfo

    def _get_reqcstates(self):
        """Return 'CStates.ReqCStates()' object."""

        if not self._rcsobj:
            self._rcsobj = CStates.ReqCStates(pman=self._pman, cpuinfo=self._get_cpuinfo())
        return self._rcsobj

    def _get_cstates(self):
        """Return 'CStates.CStates()' object."""

        if not self._csobj:
            self._csobj = CStates.CStates(pman=self._pman, cpuinfo=self._get_cpuinfo())
        return self._csobj

    def _get_pstates(self):
        """Return 'CStates.CStates()' object."""

        if not self._psobj:
            self._psobj = PStates.PStates(pman=self._pman, cpuinfo=self._get_cpuinfo())
        return self._psobj

    def props_to_str(self, props):
        """Convert property dictionary 'props' to human readable string."""

        props_strs = []
        for pname, value in props.items():
            name = self.props[pname].get("name")
            props_strs.append(f"{name}: {value}")

        return ", ".join(props_strs)

    def _normalize_pcsnames(self, pcsnames):
        """Normalize and validate list of package C-state names 'pcsnames'."""

        allpcsnames = []
        for _, pinfo in self._get_cstates().get_props(("pkg_cstate_limit",), "all"):
            _pcsnames = pinfo["pkg_cstate_limit"].get("pkg_cstate_limits", None)
            if not _pcsnames:
                continue

            for pcsname in _pcsnames:
                if pcsname not in allpcsnames:
                    allpcsnames.append(pcsname)

        if "all" in pcsnames:
            return allpcsnames

        for pcsname in pcsnames:
            if pcsname.upper() not in allpcsnames:
                raise Error(f"package C-state '{pcsname}' not available{self._pman.hostmsg}")

        return [pcsname.upper() for pcsname in pcsnames]

    def _normalize_csnames(self, csnames):
        """Normalize and validate list of requestable C-state names 'csnames'."""

        allcsnames = []
        for _, csinfo in self._get_reqcstates().get_cstates_info(csnames="all", cpus="all"):
            for csname in csinfo:
                if csname not in allcsnames:
                    allcsnames.append(csname)

        if "all" in csnames:
            return allcsnames

        for csname in csnames:
            if csname.upper() not in allcsnames:
                raise Error(f"requestable C-state '{csname}' not available{self._pman.hostmsg}")

        csnames = [csname.upper() for csname in csnames]
        return [csname for csname in allcsnames if csname in csnames]

    def _is_prop_supported(self, pname, warn=False):
        """
        Return 'True' if property 'pname' is supported, returns 'False' otherwise. Prints warning if
        'warn' is 'True'.
        """

        if warn:
            log_method = _LOG.warning
        else:
            log_method = _LOG.debug

        if pname in ("cstates", "freqs", "online", "aspm"):
            return True

        if pname == "uncore_freqs":
            cmd = "pepc pstates info --min-uncore-freq --max-uncore-freq"
            stdout, _ = self._pman.run_verify(cmd)

            uncore_supported = True
            for line in stdout.split("\n"):
                if "not supported" in line:
                    log_method(line)
                    uncore_supported = False

            return uncore_supported

        if pname == "pcstates":
            cmd = "pepc cstates info --pkg-cstate-limit"
            stdout, _ = self._pman.run_verify(cmd)

            if "not supported" in stdout:
                log_method(stdout.strip())
                return False

            for line in stdout.split("\n"):
                if "Package C-state limit lock: 'on'" in line:
                    log_method(line)
                    return False

            return True

        pcsobj = None
        if pname in self._get_pstates().props:
            pcsobj = self._get_pstates()
        elif pname in self._get_cstates().props:
            pcsobj = self._get_cstates()

        if pcsobj is None:
            log_method("property '%s' is not supported, skip configuring it", pname)
            return False

        for _, pinfo in pcsobj.get_props((pname,), cpus="all"):
            if not pinfo[pname].get(pname, None):
                log_method("property '%s' is not supported, skip configuring it", pname)
                return False

        return True

    def _init_props_dict(self):
        """Initialize 'props' dictionary."""

        for pname, pinfo in PROP_INFOS.items():
            if not self._is_prop_supported(pname):
                continue

            self.props[pname] = {}
            self.props[pname]["moniker"] = pinfo.get("moniker")
            self.props[pname]["cmd"] = pinfo.get("cmd")

            sname = None
            name = None
            if pname in self._get_pstates().props:
                sname = self._get_pstates().props[pname].get("sname")
                name = self._get_pstates().props[pname].get("name")
            elif pname in self._get_cstates().props:
                sname = self._get_cstates().props[pname].get("sname")
                name = self._get_cstates().props[pname].get("name")
            else:
                sname = pinfo.get("sname")
                name = pinfo.get("name")

            self.props[pname]["sname"] = sname
            self.props[pname]["name"] = name

    def _strip_props(self, props):
        """
        The properties 'props' might include properties which are not supported or needed for the
        configuration. E.g. configuring package C-state to 'PC0' is not needed when we are testing
        'C1'. Return property dictionary with supported and needed properties. If the configuration
        doesn't make sense at all, returns 'None'.
        """

        if props.get("cstates") in PC0_ONLY_STATES:
            notice = None

            if "pcstates" in props:
                if props.get("pcstates") != "PC0":
                    notice = f"enabling '{props['cstates']}' doesn't make sense with package " \
                             f"C-state '{props['pcstates']}', skip configuration:\n" \
                             f"{self.props_to_str(props)}"

                del props["pcstates"]

            for pname in ("cstate_prewake", "c1_demotion", "c1_undemotion"):
                if props.get(pname) == "on":
                    name = self.props[pname]["name"]
                    notice = f"enabling '{name}' with '{props['cstates']}' doesn't make sense, " \
                             f"skip configuration:\n{self.props_to_str(props)}"

            if notice:
                _LOG.notice(notice)
                return None

        return props

    def iter_props(self, inprops):
        """
        Options, like C-states, may hold multiple different values we want to run workload
        with. Create all possible permutations of the settings and yield each permutation
        as a dictionary.

        E.g. if 'inprops' would have following option values:
        {"cstates" : ["C1", "C6"], "cstate_prewake" : ["on", "off"]}

        this method would yield following permutations:
        {'cstates': 'C1', 'cstate_prewake': 'on'}
        {'cstates': 'C1', 'cstate_prewake': 'off'}
        {'cstates': 'C6', 'cstate_prewake': 'on'}
        {'cstates': 'C6', 'cstate_prewake': 'off'}

        """

        props = {}
        for pname, values in inprops.items():
            if not self._is_prop_supported(pname, warn=True):
                continue

            if not isinstance(values, list):
                values = Trivial.split_csv_line(values)

            if pname == "cstates":
                values = self._normalize_csnames(values)
            if pname == "pcstates":
                values = self._normalize_pcsnames(values)

            props[pname] = values

        for values in itertools.product(*props.values()):
            prop_combination = dict(zip(props.keys(), values))

            prop_combination = self._strip_props(prop_combination)
            if prop_combination:
                yield prop_combination

    def __init__(self, pman):
        """The class constructor."""

        self._pman = pman

        self._cpuinfo = None
        self._rcsobj = None
        self._csobj = None
        self._psobj = None

        self.props = {}

        try:
            self._init_props_dict()
        except Error as err:
            _LOG.error_out("initializing property information failed%s:\n%s",
                           self._pman.hostmsg, err)

    def close(self):
        """Uninitialize the class object."""

        ClassHelpers.close(self, close_attrs={"_cpuinfo", "_rcsobj", "_csobj", "_psobj"})

class _PepcCmdFormatter(_PropIteratorBase):
    """A Helper class for creating 'pepc' commands."""

    def _get_prop_sname(self, pname):
        """Get name of the scope for property 'pname'."""

        sname = None
        for obj in (self._get_cstates(), self._get_pstates()):
            if pname in obj.props:
                sname = obj.props[pname].get("sname")

        if sname is None and pname in self.props:
            sname = self.props[pname].get("sname")

        return sname

    def _get_prop_scope(self, pname, cpu=0):
        """Get scope as CPUs for property 'pname', for CPU 'cpu'."""

        if cpu is None:
            cpu = 0

        if not self._only_measured_cpu:
            return "all"

        sname = self._get_prop_sname(pname)
        if sname is None:
            return None

        cpuinfo = self._get_cpuinfo()
        levels = cpuinfo.get_cpu_levels(cpu)

        cpus = None
        if sname == "CPU":
            cpus = levels["CPU"]
        if sname in ("core", "node", "die"):
            method = getattr(cpuinfo, f"{sname}s_to_cpus")
            cpus = method(levels[sname], packages=levels["package"])
        if sname == "package":
            cpus = cpuinfo.packages_to_cpus(packages=levels["package"])

        if cpus is None:
            raise Error(f"unknown scope for property '{pname}'")

        if isinstance(cpus, list):
            cpus = Human.rangify(cpus)

        return cpus

    def _csnames_to_enable(self, csname):
        """
        Returns C-state names to enable as a string. The string can be single C-state name or
        comma-separated list of C-state names.
        """

        csnames = set()

        if csname == "all":
            return csname

        if self._cstates_always_enable:
            csnames.update(self._cstates_always_enable)

        if self._only_one_cstate:
            csnames.add(csname)
        else:
            all_csnames = self._normalize_csnames("all")
            idx = all_csnames.index(csname)
            csnames.update(all_csnames[:idx+1])

        csnames = self._normalize_csnames(csnames)
        return ",".join(csnames)

    def get_commands(self, props, cpu=0):
        """Yield list of 'pepc' commands to configure system according to properties 'props'."""

        for pname, value in props.items():
            if pname not in self.props:
                continue

            if pname == "cstates":
                value = self._csnames_to_enable(value)

            if pname == "aspm":
                if value == "on":
                    value = "powersupersave"
                elif value == "off":
                    value = "performance"

            scope = self._get_prop_scope(pname, cpu=cpu)

            # We use 'unl' keyword to express unlocked frequency value, and the frequency options
            # have two values.
            if value == "unl":
                values = ["min", "max"]
            else:
                values = [value] * self.props[pname]["cmd"].count("{}")

            cmd = self.props[pname]["cmd"].format(*values, scope=scope)

            if self._pman.hostname != "localhost":
                cmd += f" -H {self._pman.hostname}"

            yield cmd

    def __init__(self, pman, only_measured_cpu, only_one_cstate, cstates_always_enable):
        """The class constructor."""

        super().__init__(pman)

        self._only_measured_cpu = only_measured_cpu
        self._only_one_cstate = only_one_cstate
        self._cstates_always_enable = cstates_always_enable

        csnames = Trivial.split_csv_line(cstates_always_enable)
        self._cstates_always_enable = self._normalize_csnames(csnames)

class _ToolCmdFormatterBase(ClassHelpers.SimpleCloseContext):
    """A base class to help creating commands."""

    def _create_reportid(self, props, devid=None, cpu=None):
        """Create report ID from used properties 'props'."""

        monikers = []

        if self._hostname != "localhost":
            monikers.append(self._hostname)

        if devid:
            monikers.append(devid)

        # There are core C-states that are not affected by package C-states, for example C1. Avoid
        # appending the package C-state suffix to the moniker (e.g., avoid "c1_pc6', use 'c1'
        # instead).
        cstate = props.get("cstates")
        if "pcstates" in props:
            if cstate is None:
                cstate = props['pcstates']
            elif cstate not in PC0_ONLY_STATES:
                cstate += f"_{props['pcstates']}"

        if cstate:
            monikers.append(cstate)

        for pname, val in props.items():
            if pname in ("cstates", "pcstates"):
                continue

            if pname in ("freqs", "uncore_freqs") and val == "unl":
                continue

            moniker = PROP_INFOS[pname].get("moniker", "")
            if moniker:
                moniker = f"{moniker}_"
            moniker += f"{val}"

            monikers.append(moniker)

        if cpu is not None:
            monikers.append(f"cpu{cpu}")

        reportid = "-".join(monikers)
        reportid = ReportID.format_reportid(prefix=self._reportid_prefix, reportid=reportid,
                                            append=self._reportid_suffix)

        return reportid.lower()

    def _get_toolopts(self, reportid):
        """Get tool options, if any."""

        toolopts = self._toolopts
        if "__reportid__" in toolopts:
            toolopts = toolopts.replace("__reportid__", reportid)

        return toolopts

    def get_command(self, props, devid, cpu): # pylint: disable=unused-argument
        """Create and return command to run the tool."""

        cmd = str(self.toolpath)

        reportid = self._create_reportid(props)
        toolopts = self._get_toolopts(reportid)
        if toolopts:
            cmd += f" {toolopts}"

        return cmd

    def __init__(self, args):
        """The class constructor."""

        with LocalProcessManager.LocalProcessManager() as lpman:
            self.toolpath = lpman.which(args.toolpath)

        self._toolopts = args.toolopts
        self._outdir = args.outdir
        self._reportid_prefix = args.reportid_prefix
        self._reportid_suffix = args.reportid_suffix
        self._hostname = args.hostname
        self._stats = args.stats

        if not self._outdir:
            self._outdir = ReportID.format_reportid(prefix=self.toolpath.name)

class _BenchmarkCmdFormatter(_ToolCmdFormatterBase):
    """A Helper class for creating 'benchmark' commands."""

    def get_command(self, props, devid, cpu):
        """Create and return command to run the 'benchmark' tool."""

        cmd = super().get_command(props, devid, cpu)
        reportid = self._create_reportid(props)
        cmd = f"{cmd} --reportid {reportid} -o {self._outdir}/{reportid}"

        if self._stats:
            cmd += f" --stats {self._stats}"

        return cmd

class _WultCmdFormatter(_ToolCmdFormatterBase):
    """A Helper class for creating 'wult' or 'ndl' commands."""

    def _create_command(self, devid, cpu, reportid=None):
        """Create and return 'wult' or 'ndl' command."""

        cmd = f"{self.toolpath} "
        if _LOG.colored:
            cmd += " --force-color"
        cmd += f" start -c {self._datapoints}"

        if cpu is not None and self.toolpath.name in ("wult", "ndl"):
            cmd += f" --cpunum {cpu}"

        cmd += f" {devid}"

        if reportid:
            cmd += f" --reportid {reportid} -o {self._outdir}/{reportid}"
        else:
            cmd = f" -o {self._outdir}"

        if self._stats:
            cmd += f" --stats {self._stats}"

        toolopts = self._get_toolopts(reportid)
        if toolopts:
            cmd += f" {toolopts}"

        if self._hostname != "localhost":
            cmd += f" -H {self._hostname}"

        return cmd

    def get_command(self, props, devid, cpu):
        """Create and return 'wult' or 'ndl' command."""

        reportid = self._create_reportid(props, devid=devid, cpu=cpu)
        return self._create_command(devid, cpu, reportid=reportid)

    def __init__(self, pman, args):
        """The class constructor."""

        super().__init__(args)

        self._pman = pman
        self._datapoints = args.datapoints

    def close(self):
        """Uninitialize the class objetc."""
        ClassHelpers.close(self, unref_attrs=("_pman",))

class _CmdlineRunner(ClassHelpers.SimpleCloseContext):
    """Helper class for running commandline commands."""

    def _handle_error(self, cmd):
        """Handle error for running command 'cmd'."""

        msg = f"failed to run command:\n'{cmd}'"
        if self._stop_on_failure:
            msg += "\nstop processing more commands and exit"
            _LOG.error_out(msg)

        _LOG.error(msg)

    def _get_completed_procs(self):
        """Yield completed command process objects."""

        for proc in self._procs:
            if proc.poll() is None:
                continue

            yield proc

    def _handle_proc(self, proc):
        """Wait for command process 'proc' and handle the output."""

        stdout, stderr, exitcode = proc.wait()

        if stdout:
            _LOG.info(stdout)
        if stderr:
            _LOG.info(stderr)

        if exitcode != 0:
            self._handle_error(proc.cmd)

    def _active_proc_count(self):
        """
        Go through list of started processes, handle completed ones, and return number of active
        processes.
        """

        procs_done = set()
        for proc in self._get_completed_procs():
            self._handle_proc(proc)
            procs_done.add(proc)

        self._procs -= procs_done

        for proc in procs_done:
            proc.close()

        return len(self._procs)

    def _run_async(self, cmd):
        """
        Run command 'cmd' asynchronously. If more than 'self._proc_count' processes are already
        running, wait until one of the running processes completes before running the command.
        """

        while self._active_proc_count() >= self._proc_count:
            # Wait until one of the commands are done.
            time.sleep(1)

        _LOG.debug("running command: '%s'", cmd)
        proc = self._lpman.run_async(cmd)
        self._procs.add(proc)

    def _run_command(self, cmd):
        """
        Run command 'cmd' with process manager object 'pman'. If 'dry_run' is 'True', print the
        command instad of running it. If any of the commands failed and 'stop_on_failure' is 'True',
        print error and exit.
        """

        if self._dry_run:
            _LOG.info(cmd)
            return

        _LOG.debug("running command: '%s'", cmd)
        if self._proc_count:
            self._run_async(cmd)
        else:
            res = self._lpman.run(cmd, output_fobjs=(sys.stdout, sys.stderr))
            if res.exitcode != 0:
                self._handle_error(cmd)

    def wait(self):
        """Wait until all commands have completed."""

        while self._active_proc_count() != 0:
            time.sleep(1)
            continue

    def __init__(self, dry_run=False, stop_on_failure=False, proc_count=None):
        """
        The class constructor, arguments are as follows.
          * dry_run - if 'True', print the command instead of running it.
          * stop_on_failure - if 'True', print error and terminate program execution.
          * proc_count - number of processes to run in parallel.
        """

        self._dry_run = dry_run
        self._stop_on_failure = stop_on_failure
        self._proc_count = proc_count

        self._lpman = LocalProcessManager.LocalProcessManager()
        self._procs = set()

        if self._proc_count and not dry_run:
            _LOG.notice("running up to %s commands in parallel.", self._proc_count)

    def close(self):
        """Uninitialize the class objetc."""

        for proc in self._procs:
            proc.close()

        ClassHelpers.close(self, close_attrs=("_lpman",))

class BatchConfig(_CmdlineRunner):
    """
    Helper class for 'exercise-sut' tool to configure and exercise SUT with different system
    configuration permutations.
    """

    def deploy(self):
        """Deploy 'wult' to the SUT."""

        if self._wl_formatter.toolpath.name not in ("wult", "ndl"):
            raise Error("deploy supported only by tools 'wult' and 'ndl'")

        deploy_cmd = f"{self._wl_formatter.toolpath} deploy"

        if self._pman.hostname != "localhost":
            deploy_cmd += f" -H {self._pman.hostname}"

        self._run_command(deploy_cmd)

    def props_to_str(self, props):
        """Convert property dictionary 'props' to human readable string."""

        return self._pepc_formatter.props_to_str(props)

    def get_props_batch(self, inprops):
        """
        Yield dictionary with system properties, with property name as key and property value as
        value.
        """

        yield from self._pepc_formatter.iter_props(inprops)

    def configure(self, props, cpu):
        """Set properties 'props'."""

        for cmd in self._pepc_formatter.get_commands(props, cpu):
            self._run_command(cmd)

    def run(self, props, devid, cpu):
        """Run workload command with system properties 'props' and device ID 'devid'."""

        cmd = self._wl_formatter.get_command(props, devid, cpu)
        self._run_command(cmd)

    def __init__(self, args):
        """The class constructor."""

        super().__init__(dry_run=args.dry_run, stop_on_failure=args.stop_on_failure)

        self._pman = _Common.get_pman(args)
        self._pepc_formatter = _PepcCmdFormatter(self._pman, args.only_measured_cpu,
                                                 args.only_one_cstate, args.cstates_always_enable)
        self._wl_formatter = _get_workload_cmd_formatter(self._pman, args)

    def close(self):
        """Uninitialize the class objetc."""
        ClassHelpers.close(self, close_attrs=("_pepc_formatter", "_pman"))

class BatchReport(_CmdlineRunner):
    """Helper class for 'exercise-sut' tool to create reports for series of results."""

    def _get_result_paths(self, searchpaths):
        """Find all result paths in list of paths 'searchpaths'. Returns single list of paths."""

        for searchpath in searchpaths:
            if not searchpath.exists():
                raise Error(f"input path '{searchpath}' does not exist")

            if not searchpath.is_dir():
                raise Error(f"input path '{searchpath}' is not a directory")

            for respath in os.scandir(searchpath):
                if respath.is_dir():
                    yield Path(respath.path)

    def _resolve_path_monikers(self, diff_monikers, path_monikers):
        """
        Resolve common monikers between 'diff_monikers' and 'path_monikers' lists. Returns 'None'
        if common monikers not found.
        """

        if not diff_monikers:
            return path_monikers

        common_monikers = []
        for diff_moniker in diff_monikers:
            # Diff moniker might include dash ('-'), in which case we need to look for each
            # sub-string.
            sub_strings = diff_moniker.split("-")
            if set(sub_strings).issubset(path_monikers):
                common_monikers.append(diff_moniker)
                for sub_string in sub_strings:
                    path_monikers.remove(sub_string)

        # Include only results which have common monikers, or empty diff moniker ("") included.
        if common_monikers or "" in diff_monikers:
            return path_monikers

        return None

    def _get_grouped_paths(self, searchpaths, diff_monikers, include_monikers, exclude_monikers):
        """
        Find results from paths 'searchpaths'. Group results according to arguments:
          * diff_monikers - List of monikers to group results with.
          * include - List of monikers that must be found from the result path name.
          * exclude - List of monikers that must not be found from the result path name.

        Returns dictionary with common directory name as key and list matching paths as values.
        """

        basepath = Path("-vs-".join([moniker for moniker in diff_monikers if moniker]))

        groups = {}
        for respath in self._get_result_paths(searchpaths):
            path_monikers = respath.name.split("-")

            if include_monikers and not include_monikers.issubset(set(path_monikers)):
                continue

            if exclude_monikers and exclude_monikers.intersection(set(path_monikers)):
                continue

            path_monikers = self._resolve_path_monikers(diff_monikers, path_monikers)
            if not path_monikers:
                continue

            outpath = basepath / "-".join(path_monikers)
            if outpath not in groups:
                groups[outpath] = []

            groups[outpath].append(respath)

        return groups

    def group_results(self, searchpaths, diffs=None, include=None, exclude=None):
        """
        Find results from paths 'searchpaths'. Group results according to arguments:
          * diffs - Comma-separated list of monikers to group results with.
          * include - Comma-separated list of monikers that must be found from the result path name.
          * exclude - Comma-separated list of monikers that must not be found from the result path
                      name.

        Yields tuple with common directory name as key and list of paths matching to the rules as
        value.
        """

        diff_monikers = []
        include_monikers = None
        exclude_monikers = None

        if diffs:
            diff_monikers = Trivial.split_csv_line(diffs, dedup=True, keep_empty=True)

        if include:
            include_monikers = set(Trivial.split_csv_line(include))

        if exclude:
            exclude_monikers = set(Trivial.split_csv_line(exclude))

        grouped_paths = self._get_grouped_paths(searchpaths, diff_monikers, include_monikers,
                                                exclude_monikers)

        def _get_path_sortkey(path):
            """
            Method for sorting paths according to order of given diff monikers, or order of input
            paths.
            """

            path_monikers = path.name.split("-")
            for moniker in diff_monikers:
                if moniker in path_monikers:
                    return diff_monikers.index(moniker)

            for searchpath in searchpaths:
                if path.parent == searchpath:
                    return searchpaths.index(searchpath)

            return len(diff_monikers)

        for outpath, paths in grouped_paths.items():
            paths.sort(key=_get_path_sortkey)

            # Yield paths only for diffs where all requested results are found.
            if diff_monikers and len(paths) < len(diff_monikers):
                continue

            yield outpath, paths

    def generate_report(self, respaths, outpath):
        """Generate the report for list of results in 'respaths', store the report to 'outpath'."""

        if outpath.exists():
            _LOG.warning("path '%s' exists", outpath)

        cmd = f"nice -n19 ionice -c3 {self._toolpath} "

        if self._toolpath.name in ("wult", "ndl", "stats-collect"):
            cmd += "report "

        if self._toolopts:
            cmd += f"{self._toolopts} "

        res_str = " ".join([str(path) for path in respaths])
        cmd += f"{res_str} -o {outpath}"

        self._run_command(cmd)

    def __init__(self, toolpath, outpath, toolopts=None, dry_run=False, stop_on_failure=False,
                 proc_count=None):
        """The class constructor."""

        super().__init__(dry_run=dry_run, stop_on_failure=stop_on_failure, proc_count=proc_count)

        self._toolpath = self._lpman.which(toolpath)
        self._outpath = outpath
        self._toolopts = toolopts
