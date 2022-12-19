#!/usr/bin/env python3
#
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
import logging
import itertools
from pathlib import Path
from pepclibs import CStates, PStates, CPUInfo
from pepclibs.helperlibs import ClassHelpers, Human, LocalProcessManager, Trivial
from pepclibs.helperlibs.Exceptions import Error
from wultlibs import _ToolsCommon
from statscollectlibs.helperlibs import ReportID

_LOG = logging.getLogger()

PROP_INFOS = {
    "cstates" : {
        "name" : "requestable C-state",
        "sname" : "CPU",
        "cmd" : "pepc cstates config --disable all --enable {} --cpus {scope}"},
    "pcstates" : {
        "name" : "package C-state",
        "sname" : "package",
        "cmd" : "pepc cstates config --pkg-cstate-limit {} --cpus {scope}"},
    "freqs" : {
        "name" : "CPU frequency",
        "sname" : "CPU",
        "cmd" : "pepc pstates config --min-freq {} --max-freq {} --cpus {scope}"},
    "uncore_freqs" : {
        "name" : "uncore frequency",
        "moniker" : "uf",
        "sname" : "die",
        "cmd" : "pepc pstates config --min-uncore-freq {} --max-uncore-freq {} --cpus " \
                "{scope}"},
    "governor" : {
        "moniker" : "gov",
        "cmd" : "pepc pstates config --governor {} --cpus {scope}"},
    "aspm" : {
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

def _create_reportid(props, prefix=None, suffix=None):
    """Create report id from used properties 'props'."""

    reportid = ""

    if prefix:
        reportid += str(prefix)

    # In report id, the package C-state limit, is value for measured C-state (e.g. 'c6_pc6'). If
    # package C-state limit does not make sense for the measured C-state (e.g. PC6 with C1), the
    # package C-state value is not added, and moniker will be just 'c1'.
    cstate = props.get("cstates")
    if "pcstates" in props:
        if cstate not in PC0_ONLY_STATES:
            cstate += f"_{props['pcstates']}"
    if reportid:
        reportid += "-"
    reportid += cstate


    for pname, val in props.items():
        if pname in ("cstates", "pcstates"):
            continue

        if pname in ("freqs", "uncore_freqs") and val == "unl":
            continue

        reportid += "-"

        moniker = PROP_INFOS[pname].get("moniker", "")
        if moniker:
            reportid += f"{moniker}_"
        reportid += f"{val}"

    if suffix:
        reportid += f"-{suffix}"

    return reportid.lower()

def _get_workload_cmd_formatter(args):
    """Create and return object for creating workload commands."""

    toolname = args.toolpath.name

    if toolname in ("wult", "ndl"):
        return _WultCmdFormatter(args)

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
                raise Error("requestable C-state name '{csname}' not available{self._pman.hostmsg}")

        return [csname.upper() for csname in csnames]

    def _init_props_dict(self):
        """Initialize 'props' dictionary."""

        for pname, pinfo in PROP_INFOS.items():
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
        The properties 'props' might include properties which are not needed for the configuration.
        E.g. configuring package C-state to 'PC0' is not needed when we are testing 'C1'. Return
        property dictionary with needed properties. If the configuration doesn't make sense at all,
        returns 'None'.
        """

        if props.get("cstates") in PC0_ONLY_STATES:
            if "pcstates" in props:
                if props.get("pcstates") != "PC0":
                    _LOG.debug("the C-state '%s' doesn't make sense with package C-state '%s', " \
                               "skip configuration\n", props["cstates"], props["pcstates"])
                    return None

                del props["pcstates"]

            for pname in ("cstate_prewake", "c1_demotion", "c1_undemotion"):
                if props.get(pname) == "on":
                    _LOG.debug("enabling %s with '%s' doesn't make sense, skip " \
                               "configuration", self.props[pname]["name"], props["cstates"])
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

        for pname, values in inprops.items():
            if not isinstance(values, list):
                values = Trivial.split_csv_line(values)

            if pname == "cstates":
                values = self._normalize_csnames(values)
                self._requested_cstates = values
            if pname == "pcstates":
                values = [val.upper() for val in values]

            inprops[pname] = values

        for values in itertools.product(*inprops.values()):
            props = dict(zip(inprops.keys(), values))

            props = self._strip_props(props)
            if props:
                yield props

    def __init__(self, pman):
        """The class constructor."""

        self._pman = pman

        self._cpuinfo = None
        self._rcsobj = None
        self._csobj = None
        self._psobj = None

        self._requested_cstates = None
        self.props = {}

        self._init_props_dict()

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

        if sname is None and pname in PROP_INFOS:
            sname = PROP_INFOS[pname].get("sname")

        return sname

    def _get_prop_scope(self, pname):
        """Get scope as CPUs for property 'pname'."""

        if not self._only_measured_cpu:
            return "all"

        sname = self._get_prop_sname(pname)
        if sname is None:
            return None

        cpuinfo = self._get_cpuinfo()
        levels = cpuinfo.get_cpu_levels(self._cpunum)

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

        if csname == "all" or self._only_one_cstate:
            return csname

        all_csnames = self._normalize_csnames("all")

        if "POLL" not in self._requested_cstates and "POLL" in all_csnames:
            all_csnames.remove("POLL")

        idx = all_csnames.index(csname)
        return ",".join(all_csnames[:idx+1])

    def get_commands(self, props):
        """Yield list of 'pepc' commands to configure system according to properties 'props'."""

        for pname, value in props.items():
            if pname not in PROP_INFOS:
                raise Error(f"unkown property '{pname}'")

            if pname == "cstates":
                value = self._csnames_to_enable(value)

            if pname == "aspm":
                if value == "on":
                    value = "powersave"
                elif value == "off":
                    value = "performance"

            scope = self._get_prop_scope(pname)

            # We use 'unl' keyword to express unlocked frequency value, and the frequency options
            # have two values.
            if value == "unl":
                values = ["min", "max"]
            else:
                values = [value] * PROP_INFOS[pname]["cmd"].count("{}")

            cmd = PROP_INFOS[pname]["cmd"].format(*values, scope=scope)

            if self._pman.hostname != "localhost":
                cmd += f" -H {self._pman.hostname}"

            yield cmd

    def __init__(self, pman, only_measured_cpu, only_one_cstate, cpunum):
        """The class constructor."""

        super().__init__(pman)

        self._only_measured_cpu = only_measured_cpu
        self._only_one_cstate = only_one_cstate
        self._cpunum = cpunum

class _ToolCmdFormatterBase(ClassHelpers.SimpleCloseContext):
    """A base class to help creating commands."""

    def get_commands(self, props):  # pylint: disable=unused-argument
        """Create and yield command to run the tool."""

        cmd = str(self.toolpath)
        if self._toolopts:
            cmd += f" {self._toolopts}"

        yield cmd

    def __init__(self, args):
        """The class constructor."""

        self.toolpath = Path(args.toolpath)
        self._toolopts = args.toolopts
        self._outdir = args.outdir
        self._reportid_prefix = args.reportid_prefix
        self._reportid_suffix = args.reportid_suffix

        if not self._outdir:
            self._outdir = ReportID.format_reportid(prefix=self.toolpath.name)

class _BenchmarkCmdFormatter(_ToolCmdFormatterBase):
    """A Helper class for creating 'benchmark' commands."""

    def get_commands(self, props):
        """Create and yield command to run the 'benchmark' tool."""

        for cmd in super().get_commands(props):
            reportid = _create_reportid(props, prefix=self._reportid_prefix,
                                        suffix=self._reportid_suffix)
            cmd += f" -o {self._outdir}/{reportid}"

            yield cmd

class _WultCmdFormatter(_ToolCmdFormatterBase):
    """A Helper class for creating 'wult' or 'ndl' commands."""

    def _create_command(self, devid, reportid=None):
        """Create and return 'wult' or 'ndl' command."""

        cmd = f"{self.toolpath} start -c {self._datapoints}"

        if self.toolpath.name == "wult":
            cmd += f" --cpunum {self._cpunum}"

        cmd += f" {devid}"

        if reportid:
            cmd += f" --reportid {reportid} -o {self._outdir}/{reportid}"
        else:
            cmd = f" -o {self._outdir}"

        if self._toolopts:
            cmd += f" {self._toolopts}"

        if self._hostname != "localhost":
            cmd += f" -H {self._hostname}"

        return cmd

    def get_commands(self, props):
        """Create and yield 'wult' or 'ndl' commands."""

        for devid in self._devids:
            prefix = devid
            if self._reportid_prefix:
                prefix = f"{self._reportid_prefix}-{prefix}"

            reportid = _create_reportid(props, prefix=prefix, suffix=self._reportid_suffix)
            yield self._create_command(devid, reportid=reportid)

    def __init__(self, args):
        """The class constructor."""

        super().__init__(args)

        self._devids = Trivial.split_csv_line(args.devids)
        self._cpunum = args.cpunum
        self._datapoints = args.datapoints
        self._hostname = args.hostname

class _CmdlineRunner(ClassHelpers.SimpleCloseContext):
    """Helper class for running commandline commands."""

    def _get_lpman(self):
        """Return 'LocalProcessManager' object."""

        if not self._lpman:
            self._lpman = LocalProcessManager.LocalProcessManager()

        return self._lpman

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
        res = self._get_lpman().run(cmd, output_fobjs=(sys.stdout, sys.stderr))
        if res.exitcode != 0:
            msg = f"failed to run command:\n'{cmd}'"
            if self._stop_on_failure:
                msg += "\nstop processing more commands and exit"
                _LOG.error_out(msg)

            _LOG.error(msg)

    def __init__(self, dry_run=False, stop_on_failure=False):
        """The class constructor."""

        self._dry_run = dry_run
        self._stop_on_failure = stop_on_failure
        self._lpman = None

    def close(self):
        """Uninitialize the class objetc."""
        ClassHelpers.close(self, close_attrs=("_lpman"))

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

        props_strs = []
        for pname, value in props.items():
            name = self._pepc_formatter.props[pname].get("name")
            props_strs.append(f"{name}: {value}")

        return ", ".join(props_strs)

    def get_props_batch(self, inprops):
        """
        Yield dictionary with system properties, with property name as key and property value as
        value.
        """
        yield from self._pepc_formatter.iter_props(inprops)

    def configure(self, props):
        """Set properties 'props'."""

        for cmd in self._pepc_formatter.get_commands(props):
            self._run_command(cmd)

    def run(self, props):
        """Run workload command with system properties 'props'."""

        for cmd in self._wl_formatter.get_commands(props=props):
            self._run_command(cmd)

    def __init__(self, args):
        """The class constructor."""

        super().__init__(dry_run=args.dry_run, stop_on_failure=args.stop_on_failure)

        self._pman = None
        self._wl_formatter = None
        self._pepc_formatter = None

        self._pman = _ToolsCommon.get_pman(args)
        self._pepc_formatter = _PepcCmdFormatter(self._pman, args.only_measured_cpu,
                                                 args.only_one_cstate, args.cpunum)
        self._wl_formatter = _get_workload_cmd_formatter(args)

    def close(self):
        """Uninitialize the class objetc."""
        ClassHelpers.close(self, close_attrs=("_pepc_formatter", "_pman"))

class BatchReport(_CmdlineRunner):
    """Helper class for 'exercise-sut' tool to create reports for series of results."""

    def _get_result_paths(self, searchpaths): # pylint: disable=no-self-use
        """Find all result paths in list of paths 'searchpaths'. Returns single list of paths."""

        for searchpath in searchpaths:
            for respath in os.scandir(searchpath):
                if respath.is_dir():
                    yield Path(respath.path)

    def _get_grouped_paths(self, searchpaths, diff_monikers, include_monikers, exclude_monikers):
        """
        Find results from paths 'searchpaths'. Group results according to arguments:
          * diff_monikers - List of monikers to group results with.
          * include - List of monikers that must be found from the result path name.
          * exclude - List of monikers that must not be found from the result path name.

        Returns dictionary with common directory name as key and list matching paths as values.
        """

        groups = {}
        for respath in self._get_result_paths(searchpaths):
            path_monikers = respath.name.split("-")

            if include_monikers and not include_monikers.issubset(set(path_monikers)):
                continue

            if exclude_monikers and exclude_monikers.intersection(set(path_monikers)):
                continue

            for moniker in path_monikers:
                if moniker in diff_monikers:
                    path_monikers.remove(moniker)

            outpath = Path("-vs-".join(diff_monikers))

            outpath = outpath / "-".join(path_monikers)
            if outpath not in groups:
                groups[outpath] = []

            groups[outpath].append(respath)

        return groups

    def group_results(self, searchpaths, diff=None, include=None, exclude=None):
        """
        Find results from paths 'searchpaths'. Group results according to arguments:
          * diff - Comma-separated list of monikers to group results with.
          * include - Comma-separated list of monikers that must be found from the result path name.
          * exclude - Comma-separated list of monikers that must not be found from the result path
                      name.

        Yields tuple with common directory name as key and list of paths matching to the rules as
        value.
        """

        diff_monikers = []
        include_monikers = None
        exclude_monikers = None

        if diff:
            diff_monikers = Trivial.split_csv_line(diff)

        if include:
            include_monikers = set(Trivial.split_csv_line(include))

        if exclude:
            exclude_monikers = set(Trivial.split_csv_line(exclude))

        grouped_paths = self._get_grouped_paths(searchpaths, diff_monikers, include_monikers,
                                                exclude_monikers)

        def _get_path_sortkey(path):
            """Method for sorting paths according to diff monikers."""

            path_monikers = path.name.split("-")
            for moniker in diff_monikers:
                if moniker in path_monikers:
                    return diff_monikers.index(moniker)

            return len(diff_monikers)

        for outpath, paths in grouped_paths.items():
            paths.sort(key=_get_path_sortkey)

            yield outpath, paths

    def generate_report(self, respaths, outpath):
        """Generate the report for list of results in 'respaths', store the report to 'outpath'."""

        if outpath.exists():
            _LOG.warning("path '%s' exists, skip generating report", outpath)
            return

        cmd = f"nice -n19 ionice -c3 {self._toolpath} report "

        if self._toolopts:
            cmd += f"{self._toolopts} "

        res_str = " ".join([str(path) for path in respaths])
        cmd += f"{res_str} -o {outpath}"

        self._run_command(cmd)

    def __init__(self, toolpath, outpath, toolopts=None, dry_run=False, stop_on_failure=False):
        """The class constructor."""

        self._toolpath = toolpath
        self._outpath = outpath
        self._toolopts = toolopts

        super().__init__(dry_run=dry_run, stop_on_failure=stop_on_failure)
