# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Antti Laakso <antti.laakso@linux.intel.com>
#         Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
A helper module for the 'exercise-sut' tool to configure target system with various system property
permutations.
"""

import logging
import itertools
from pepclibs import CStates, PStates, CPUIdle, CPUInfo
from pepclibs.helperlibs import ClassHelpers, Human, LocalProcessManager, Trivial, Systemctl
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.helperlibs import ReportID
from statscollecttools import ToolInfo as StcToolInfo
from wulttools._Common import get_pman
from wulttools.wult import ToolInfo as WultToolInfo
from wulttools.ndl import ToolInfo as NdlToolInfo
from wulttools.exercisesut import _Common

_LOG = logging.getLogger()

NDL_TOOLNAME = NdlToolInfo.TOOLNAME
STC_TOOLNAME = StcToolInfo.TOOLNAME
WULT_TOOLNAME = WultToolInfo.TOOLNAME

PROP_INFOS = {
    "cstates" : {
        "name" : "Requestable C-state",
        "sname" : "CPU",
        "cmd" : "pepc cstates config --disable all --enable {} --cpus {scope}"},
    "pcstates" : {
        "name" : "Package C-state",
        "moniker" : "pcs",
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
    "epp_hw" : {
        "moniker" : "epp",
        "cmd" : "pepc pstates config --epp-hw {} --cpus {scope}"},
    "epb" : {
        "moniker" : "epb",
        "cmd" : "pepc pstates config --epb {} --cpus {scope}"},
    "epb_hw" : {
        "moniker" : "epb",
        "cmd" : "pepc pstates config --epb-hw {} --cpus {scope}"},
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

    if toolname in (WULT_TOOLNAME, NDL_TOOLNAME):
        return _WultCmdFormatter(pman, args)

    if toolname == STC_TOOLNAME:
        return _StatsCollectCmdFormatter(pman, args)

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

    def _get_cpuidle(self):
        """Return 'CPUIdle.CPUIdle()' object."""

        if not self._cpuidle:
            self._cpuidle = CPUIdle.CPUIdle(pman=self._pman, cpuinfo=self._get_cpuinfo())
        return self._cpuidle

    def _get_cstates(self):
        """Return 'CStates.CStates()' object."""

        if not self._csobj:
            self._csobj = CStates.CStates(pman=self._pman, cpuinfo=self._get_cpuinfo(),
                                          cpuidle=self._get_cpuidle())
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
        pcsaliases = []
        cstates = self._get_cstates()
        for _, pinfo in cstates.get_props(("pkg_cstate_limits", "pkg_cstate_limit_aliases")):
            if pinfo["pkg_cstate_limits"]:
                for pcsname in pinfo["pkg_cstate_limits"]:
                    if pcsname not in allpcsnames:
                        allpcsnames.append(pcsname)

            if pinfo["pkg_cstate_limit_aliases"]:
                for pcsalias in pinfo["pkg_cstate_limit_aliases"]:
                    if pcsalias not in pcsaliases:
                        pcsaliases.append(pcsalias)

        if "all" in pcsnames:
            return allpcsnames

        pcsnames = [pcsname.upper() for pcsname in pcsnames]

        for pcsname in pcsnames:
            if pcsname not in allpcsnames and pcsname not in pcsaliases:
                raise Error(f"package C-state '{pcsname}' not available{self._pman.hostmsg}")

        return pcsnames

    def _normalize_csnames(self, csnames):
        """Normalize and validate list of requestable C-state names 'csnames'."""

        allcsnames = []
        for _, csinfo in self._get_cpuidle().get_cstates_info(csnames="all", cpus="all"):
            for csname in csinfo:
                if csname not in allcsnames:
                    allcsnames.append(csname)

        if "all" in csnames:
            return allcsnames

        csnames = [csname.upper() for csname in csnames]

        for csname in csnames:
            if csname not in allcsnames:
                raise Error(f"requestable C-state '{csname}' not available{self._pman.hostmsg}")

        return csnames

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
            if not pinfo[pname]:
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
            msg = None

            if "pcstates" in props:
                if props.get("pcstates") != "PC0":
                    msg = f"enabling '{props['cstates']}' doesn't make sense with package " \
                          f"C-state '{props['pcstates']}', skip configuration:\n" \
                          f"{self.props_to_str(props)}"

                del props["pcstates"]

            for pname in ("cstate_prewake", "c1_demotion", "c1_undemotion"):
                if props.get(pname) == "on":
                    name = self.props[pname]["name"]
                    msg = f"enabling '{name}' with '{props['cstates']}' doesn't make sense, " \
                          f"skip configuration:\n{self.props_to_str(props)}"

            if msg:
                _LOG.notice(msg)
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
        self._cpuidle = None
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

        ClassHelpers.close(self, close_attrs={"_cpuinfo", "_cpuidle", "_csobj", "_psobj"})

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

    def _get_cpus_by_prop_scope(self, pname, cpu=0):
        """
        Build and return a list of CPU number which includes 'cpu' plus all the other CPUs that
        would be affected if property 'pname' was changed on CPU 'cpu'. In other words, property
        'pname' has a scope (e.g., "package"), and the methods list of CPUs including 'cpu' and all
        other CPU numbers corresponding to the scope.
        """

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

    def get_commands(self, props, cpu=None):
        """Yield list of 'pepc' commands to configure system according to properties 'props'."""

        if cpu is None:
            cpu = 0

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

            scope = self._get_cpus_by_prop_scope(pname, cpu=cpu)

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

    def create_reportid(self, props, **kwargs):
        """Create report ID from used properties 'props'."""

        monikers = []

        if self._hostname != "localhost":
            monikers.append(self._hostname)

        if "devid" in kwargs:
            monikers.append(kwargs["devid"])

        for pname, val in props.items():
            if pname in ("freqs", "uncore_freqs") and val == "unl":
                continue

            moniker = PROP_INFOS[pname].get("moniker", "")
            if moniker:
                moniker = f"{moniker}_"
            moniker += f"{val}"

            monikers.append(moniker)

        cpu = kwargs.get("cpu", None)
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

    def get_command(self, props, reportid, **kwargs): # pylint: disable=unused-argument
        """Create and return command to run the tool."""

        cmd = str(self.toolpath)

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

        if not self._outdir:
            self._outdir = ReportID.format_reportid(prefix=self.toolpath.name)

class _BenchmarkCmdFormatter(_ToolCmdFormatterBase):
    """A Helper class for creating 'benchmark' commands."""

    def get_command(self, props, reportid, **kwargs):
        """Create and return command to run the 'benchmark' tool."""

        cmd = super().get_command(props, reportid, **kwargs)
        return f"{cmd} --reportid {reportid} -o {self._outdir}/{reportid}"

class _WultCmdFormatter(_ToolCmdFormatterBase):
    """A Helper class for creating 'wult' or 'ndl' commands."""

    def _create_command(self, cpu, devid, reportid=None):
        """Create and return 'wult' or 'ndl' command."""

        cmd = f"{self.toolpath} "
        if _LOG.colored:
            cmd += " --force-color"
        cmd += f" start -c {self._datapoints}"

        if cpu is not None:
            cmd += f" --cpunum {cpu}"

        cmd += f" {devid}"

        if reportid:
            cmd += f" --reportid {reportid} -o {self._outdir}/{reportid}"
        else:
            cmd += f" -o {self._outdir}"

        toolopts = self._get_toolopts(reportid)
        if toolopts:
            cmd += f" {toolopts}"

        if self._hostname != "localhost":
            cmd += f" -H {self._hostname}"

        return cmd

    def get_command(self, props, reportid, **kwargs):
        """Create and return 'wult' or 'ndl' command."""

        return self._create_command(kwargs["cpu"], kwargs["devid"], reportid=reportid)

    def __init__(self, pman, args):
        """The class constructor."""

        super().__init__(args)

        self._pman = pman
        self._datapoints = args.datapoints

    def close(self):
        """Uninitialize the class objetc."""
        ClassHelpers.close(self, unref_attrs=("_pman",))

class _StatsCollectCmdFormatter(_ToolCmdFormatterBase):
    """A Helper class for creating 'stats-collect' commands."""

    def _create_command(self, command, reportid=None):
        """Create and return 'stats-collect' command."""

        cmd = f"{self.toolpath} "
        if _LOG.colored:
            cmd += " --force-color"
        cmd += " start"

        if reportid:
            cmd += f" --reportid {reportid} -o {self._outdir}/{reportid}"
        else:
            cmd += f" -o {self._outdir}"

        toolopts = self._get_toolopts(reportid)
        if toolopts:
            cmd += f" {toolopts}"

        if self._hostname != "localhost":
            cmd += f" -H {self._hostname}"

        cmd += f" {command}"

        return cmd

    def get_command(self, props, reportid, **kwargs):
        """Create and return 'stats-collect' command."""

        return self._create_command(kwargs["command"], reportid=reportid)

    def __init__(self, pman, args):
        """The class constructor."""

        super().__init__(args)

        self._pman = pman
        self._datapoints = args.datapoints

    def close(self):
        """Uninitialize the class objetc."""
        ClassHelpers.close(self, unref_attrs=("_pman",))

class BatchConfig(_Common.CmdlineRunner):
    """
    Helper class for 'exercise-sut' tool to configure and exercise SUT with different system
    configuration permutations.
    """

    def deploy(self):
        """Deploy 'wult' to the SUT."""

        if self._wl_formatter.toolpath.name not in (WULT_TOOLNAME, NDL_TOOLNAME):
            raise Error(f"deploy supported only by tools '{WULT_TOOLNAME}' and '{NDL_TOOLNAME}'")

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

    def create_reportid(self, props, **kwargs):
        """Create and return report ID."""
        return self._wl_formatter.create_reportid(props, **kwargs)

    def run(self, props, cpu, reportid, **kwargs):
        """Run workload command with system properties 'props'."""

        cmd = self._wl_formatter.get_command(props, cpu=cpu, reportid=reportid, **kwargs)
        self._run_command(cmd)

    def __init__(self, args):
        """The class constructor."""

        super().__init__(dry_run=args.dry_run, stop_on_failure=args.stop_on_failure)

        self._pman = get_pman(args)
        self._pepc_formatter = _PepcCmdFormatter(self._pman, args.only_measured_cpu,
                                                 args.only_one_cstate, args.cstates_always_enable)
        self._wl_formatter = _get_workload_cmd_formatter(self._pman, args)

        self._systemctl = Systemctl.Systemctl(pman=self._pman)
        if self._systemctl.is_active("tuned"):
            self._systemctl.stop("tuned", save=True)

    def close(self):
        """Uninitialize the class objetc."""

        if self._systemctl:
            self._systemctl.restore()

        ClassHelpers.close(self, close_attrs=("_pepc_formatter", "_pman", "_systemctl"))
