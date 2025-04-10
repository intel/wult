# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023-2024 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Antti Laakso <antti.laakso@linux.intel.com>
#         Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
A helper module for the 'exercise-sut' tool to configure target system with various system property
permutations.
"""

import itertools
from pepclibs import CStates, PStates, CPUIdle, CPUInfo
from pepclibs.helperlibs import Logging, ClassHelpers, LocalProcessManager, Trivial
from pepclibs.helperlibs import Systemctl
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.helperlibs import ReportID
from statscollecttools import ToolInfo as StcToolInfo
from wulttools._Common import get_pman
from wulttools.ndl import ToolInfo as NdlToolInfo
from wulttools.pbe import ToolInfo as PbeToolInfo
from wulttools.wult import ToolInfo as WultToolInfo
from wulttools.exercisesut import _Common

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.wult.{__name__}")

NDL_TOOLNAME = NdlToolInfo.TOOLNAME
PBE_TOOLNAME = PbeToolInfo.TOOLNAME
STC_TOOLNAME = StcToolInfo.TOOLNAME
WULT_TOOLNAME = WultToolInfo.TOOLNAME

PROP_INFOS = {
    "cstates": {
        "name": "Requestable C-state",
        "sname": "CPU",
        "cmd": "pepc cstates config --disable all --enable {} {scope_opts}"
    },
    "pcstates": {
        "name": "Package C-state",
        "sname": "package",
        "cmd": "pepc cstates config --pkg-cstate-limit {} {scope_opts}"
    },
    "freqs": {
        "name": "CPU frequency",
        "sname": "CPU",
        "cmd": "pepc pstates config --min-freq {} --max-freq {} {scope_opts}"
    },
    "uncore_freqs": {
        "name": "Uncore frequency",
        "moniker": "uf",
        "sname": "die",
        "cmd": "pepc pstates config --min-uncore-freq {} --max-uncore-freq {} {scope_opts}"
    },
    "aspm": {
        "name": "ASPM",
        "sname": "global",
        "moniker": "aspm",
        "cmd": "pepc aspm config --policy {}"
    },
    "cpufreq_governors": {
        "name": "CPU frequency governor",
        "moniker": "fgov",
        "pclass": "PStates",
        "pclass_pname": "governor",
        "cmd": "pepc pstates config --governor {} {scope_opts}"
    },
    "idle_governors": {
        "name": "Idle governor",
        "moniker": "igov",
        "pclass": "CStates",
        "pclass_pname": "governor",
        "cmd": "pepc cstates config --governor {} {scope_opts}"
    },
    "c1_demotion": {
        "moniker": "c1d",
        "pclass": "CStates",
        "cmd": "pepc cstates config --c1-demotion {} {scope_opts}"
    },
    "c1_undemotion": {
        "moniker": "c1und",
        "pclass": "CStates",
        "cmd": "pepc cstates config --c1-undemotion {} {scope_opts}"
    },
    "c1e_autopromote": {
        "moniker": "autoc1e",
        "pclass": "CStates",
        "cmd": "pepc cstates config --c1e-autopromote {} {scope_opts}"
    },
    "cstate_prewake": {
        "moniker": "cpw",
        "pclass": "CStates",
        "cmd": "pepc cstates config --cstate-prewake {} {scope_opts}"
    },
    "epp": {
        "moniker": "epp",
        "pclass": "PStates",
        "cmd": "pepc pstates config --epp {} {scope_opts}"
    },
    "epb": {
        "moniker": "epb",
        "pclass": "PStates",
        "cmd": "pepc pstates config --epb {} {scope_opts}"
    },
    "turbo": {
        "moniker": "turbo",
        "pclass": "PStates",
        "cmd": "pepc pstates config --turbo {}"
    },
    "online": {
        "name": "CPU online status",
        "sname": "CPU",
        "cmd": "pepc cpu-hotplug online {scope_opts}"
    },
}

PC0_ONLY_STATES = ("POLL", "C1", "C1E")

CSTATE_FILTERS = {
    "POLL": "ReqCState == 'POLL'",
    "C1": "(ReqCState == 'C1') & (CC1% > 0)",
    "C1E": "(ReqCState == 'C1E') & (CC1% > 0)",
    "C2": "(ReqCState == 'C2') & (CC6% > 0)",
    "C3": "(ReqCState == 'C3') & (CC7% > 0)",
    "C6": "(ReqCState == 'C6') & (CC6% > 0)",
    "C6P": "(ReqCState == 'C6P') & (PC6% > 0)",
    "C6S": "(ReqCState == 'C6S') & (MC6% > 0)",
    "C6SP": "(ReqCState == 'C6SP') & (PC6% > 0)",
    "C10": "(ReqCState == 'C10') & (CC7% > 0)",
    "C1_ACPI": "(ReqCState == 'C1_ACPI') & (CC1% > 0)",
    "C2_ACPI": "(ReqCState == 'C2_ACPI') & (CC6% > 0)",
    "C3_ACPI": "(ReqCState == 'C3_ACPI') & (CC7% > 0)",
    "PC6": "(PC6% > 0)"
}

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

        if not name:
            raise Error(f"BUG: no name for property '{pname}'")

        min_len = max(min_len, len(name))
        monikers[pinfo["moniker"]] = name

    for moniker, name in monikers.items():
        msg = f"{name:<{min_len}}: {moniker}"
        _LOG.info(msg)

def _get_workload_cmd_formatter(cpuidle, args):
    """Create and return object for creating workload commands."""

    toolname = args.toolpath.name

    if toolname in (WULT_TOOLNAME, NDL_TOOLNAME):
        return _WultCmdFormatter(cpuidle, args)

    if toolname == STC_TOOLNAME:
        return _StatsCollectCmdFormatter(args)

    if toolname == PBE_TOOLNAME:
        return _PbeCmdFormatter(args)

    return _ToolCmdFormatterBase(args)

class _PropIteratorBase(ClassHelpers.SimpleCloseContext):
    """Class to help iterating system property permutations."""

    def _get_csobj(self):
        """Return 'CStates.CStates()' object."""

        if not self._csobj:
            self._csobj = CStates.CStates(pman=self._pman, cpuinfo=self._cpuinfo,
                                          cpuidle=self._cpuidle)
        return self._csobj

    def _get_psobj(self):
        """Return 'CStates.CStates()' object."""

        if not self._psobj:
            self._psobj = PStates.PStates(pman=self._pman, cpuinfo=self._cpuinfo)
        return self._psobj

    def _get_pcsobj(self, pname, pinfo):
        """
        Return 'CStates.CStates()' or 'PStates.PStates()' for property 'pname', as well as name of
        the property in the returned object.
        """

        pcsobj = None
        if pinfo.get("pclass") == "PStates":
            pcsobj = self._get_psobj()
        elif pinfo.get("pclass") == "CStates":
            pcsobj = self._get_csobj()
        if not pcsobj:
            raise Error(f"BUG: no class defined for property '{pname}'")

        # Note, 'pname' is property name supported by this module. It may be the same as property
        # name in the 'PStates'/'CStates' modules, or may be different.
        if "pclass_pname" in pinfo:
            pcsobj_pname = pinfo["pclass_pname"]
        else:
            pcsobj_pname = pname

        return pcsobj, pcsobj_pname

    def props_to_str(self, props):
        """Convert property dictionary 'props' to human readable string."""

        props_strs = []
        for pname, value in props.items():
            name = self.props[pname].get("name")
            props_strs.append(f"{name}: {value}")

        return ", ".join(props_strs)

    def _get_pcsinfo(self):
        """Helper to read package C-state information, returns a dictionary."""

        cstates = self._get_csobj()
        pcsinfo = {}
        cpu_to_pkg = {}

        for package in self._cpuinfo.get_packages():
            cpu = self._cpuinfo.package_to_cpus(package)[0]
            cpu_to_pkg[cpu] = package
            pcsinfo[package] = {}

        for pinfo in cstates.get_prop_cpus("pkg_cstate_limit", cpus=cpu_to_pkg):
            pkg = cpu_to_pkg[pinfo["cpu"]]
            pcsinfo[pkg]["current_limit"] = pinfo["val"]

        for pinfo in cstates.get_prop_cpus("pkg_cstate_limits", cpus=cpu_to_pkg):
            pkg = cpu_to_pkg[pinfo["cpu"]]
            pcsinfo[pkg]["names"] = pinfo["val"]

        for pinfo in cstates.get_prop_cpus("pkg_cstate_limit_aliases", cpus=cpu_to_pkg):
            pkg = cpu_to_pkg[pinfo["cpu"]]
            pcsinfo[pkg]["aliases"] = pinfo["val"]

        for pinfo in cstates.get_prop_cpus("pkg_cstate_limit_lock", cpus=cpu_to_pkg):
            pkg = cpu_to_pkg[pinfo["cpu"]]
            pcsinfo[pkg]["limit_locked"] = pinfo["val"] == "on"

        return pcsinfo

    def _validate_pcsname(self, pcsinfo, pcsname):
        """Validate package C-state name 'pcsname'."""

        for _pcsinfo in pcsinfo.values():
            _pcsname = _pcsinfo["aliases"].get(pcsname, pcsname)

            if _pcsname not in _pcsinfo["names"]:
                raise Error(f"package C-state '{pcsname}' not available{self._pman.hostmsg}")
            if _pcsinfo["limit_locked"] and _pcsname != _pcsinfo["current_limit"]:
                raise Error(f"cannot set package C-state limit to '{pcsname}'{self._pman.hostmsg}, "
                            f"the MSR is locked and current limit is '{_pcsinfo['current_limit']}'")

    def _normalize_pcsnames(self, pcsnames):
        """Normalize and validate list of package C-state names 'pcsnames'."""

        pcsinfo = self._get_pcsinfo()

        if "all" in pcsnames:
            # Use values from first package.
            for _pcsinfo in pcsinfo.values():
                if _pcsinfo.get("limit_locked"):
                    return [_pcsinfo["current_limit"]]
                return _pcsinfo["names"]

        normalized_pcsnames = []
        for pcsname in pcsnames:
            _pcsname = pcsname.upper()
            # Special case for 'unlimited' value.
            if not _pcsname.startswith("PC"):
                _pcsname = pcsname.lower()

            self._validate_pcsname(pcsinfo, _pcsname)
            normalized_pcsnames.append(_pcsname)

        return normalized_pcsnames

    def _normalize_csnames(self, csnames):
        """Normalize and validate list of requestable C-state names 'csnames'."""

        allcsnames = []
        for _, csinfo in self._cpuidle.get_cstates_info(csnames="all", cpus="all"):
            for csname in csinfo:
                if csname not in allcsnames:
                    allcsnames.append(csname.upper())

        if "all" in csnames:
            return allcsnames

        csnames = [csname.upper() for csname in csnames]

        for csname in csnames:
            if csname not in allcsnames:
                raise Error(f"requestable C-state '{csname}' not available{self._pman.hostmsg}")

        return csnames

    def _is_prop_supported(self, pname, pinfo=None):
        """Return 'True' if property 'pname' is supported, returns 'False' otherwise."""

        if pname in {"cstates", "freqs", "online", "aspm"}:
            return True

        if not pinfo:
            pinfo = self.props.get(pname)
            if not pinfo:
                raise Error(f"BUG: unknown property '{pname}'")

        if pname == "uncore_freqs":
            cmd = "pepc pstates info --min-uncore-freq --max-uncore-freq"
            stdout, _ = self._pman.run_verify(cmd)

            uncore_supported = True
            for line in stdout.split("\n"):
                if "not supported" in line:
                    _LOG.debug(line)
                    uncore_supported = False

            return uncore_supported

        if pname == "pcstates":
            cmd = "pepc cstates info --pkg-cstate-limit"
            stdout, _ = self._pman.run_verify(cmd)

            if "not supported" in stdout:
                _LOG.debug(stdout.strip())
                return False

            return True

        pcsobj, pcsobj_pname = self._get_pcsobj(pname, pinfo)
        if pcsobj is None:
            raise Error(f"BUG: unknown property '{pname}'")

        for pvinfo in pcsobj.get_prop_cpus(pcsobj_pname, cpus="all"):
            if not pvinfo["val"]:
                _LOG.debug("property '%s' is not supported, skip configuring it", pname)
                return False

        return True

    def _init_props_dict(self):
        """Initialize 'props' dictionary."""

        for pname, pinfo in PROP_INFOS.items():

            if not self._is_prop_supported(pname, pinfo=pinfo):
                continue

            self.props[pname] = pinfo.copy()

            name = sname = None
            if "pclass" in pinfo:
                pcsobj, pcsobj_pname = self._get_pcsobj(pname, pinfo)
                name = pcsobj.props[pcsobj_pname]["name"]
                sname = pcsobj.props[pcsobj_pname]["sname"]
            else:
                name = pinfo["name"]
                sname = pinfo["sname"]

            self.props[pname]["sname"] = sname
            self.props[pname]["name"] = name

    def _normalize_inprops(self, inprops):
        """
        Normalize input properties 'inprops', and return it as a dictionary of property name as
        key and list of values as value.
        """

        props = {}
        for pname, values in inprops.items():
            if not self._is_prop_supported(pname):
                raise Error(f"the '{pname}' is not supported{self._pman.hostmsg}")

            if not isinstance(values, list):
                values = Trivial.split_csv_line(values)

            if pname == "cstates":
                values = self._normalize_csnames(values)
            if pname == "pcstates":
                values = self._normalize_pcsnames(values)

            props[pname] = values

        return props

    def _skip_alike(self, handled_props, props):
        """
        We might have properties which would result in duplicate configuration. E.g. requestable
        C-state 'C1' would be same with 'PC2' and with 'PC6'. Return 'True' if similar properties
        are found in list of already handled properties 'handled_props'.
        """

        if "cstates" not in props or props["cstates"] not in PC0_ONLY_STATES:
            return False

        for _props in handled_props:
            if "pcstates" not in _props or _props["pcstates"] == "PC0":
                continue

            # Skip if only difference is package C-states.
            diff = dict(set(_props.items()) ^ set(props.items()))
            if len(diff) == 1 and "pcstates" in diff:
                return True

        return False

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

        handled_props = []
        inprops = self._normalize_inprops(inprops)
        if not inprops:
            return

        for values in itertools.product(*inprops.values()):
            props = dict(zip(inprops.keys(), values))

            if self._skip_alike(handled_props, props):
                continue

            yield props

            handled_props.append(props)

    def __init__(self, pman, cpuinfo, cpuidle):
        """
        The class constructor. The arguments are as follows.
          * pman - the process manager object defining the system to measure.
          * cpuinfo - 'CPUInfo' object for the measured system.
          * cpuidle - the 'CPUIdle.CPUIdle()' object for the measured system.
        """

        self._pman = pman
        self._cpuinfo = cpuinfo
        self._cpuidle = cpuidle

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

        ClassHelpers.close(self, close_attrs={"_cpuidle", "_csobj", "_psobj"},
                           unref_attrs={"_cpuinfo", "_cpuidle", })

class _PepcCmdFormatter(_PropIteratorBase):
    """A Helper class for creating 'pepc' commands."""

    def _get_prop_sname(self, pname):
        """Get name of the scope for property 'pname'."""

        sname = None
        for obj in (self._get_csobj(), self._get_psobj()):
            if pname in obj.props:
                sname = obj.props[pname].get("sname")

        if sname is None and pname in self.props:
            sname = self.props[pname].get("sname")

        return sname

    def _get_scope_opts(self, pname, cpu=0):
        """
        Format and return a pepc "scope options" for the 'pepc' command, such as '--cpus',
        '--packages', etc. The arguments are as follows.
          * pname - measured property name.
          * cpu - measured CPU number.

        Figure out and return the necessary "scope options" that should be passed to the 'pepc'
        command when changing property 'pname'.
        """

        sname = self._get_prop_sname(pname)
        if sname in (None, "global"):
            return "--cpus all"

        if not self._only_measured_cpu:
            if sname == "die" and not self._skip_io_dies:
                return "--packages all --dies all --cpus all"
            return "--cpus all"

        levels = self._cpuinfo.get_cpu_levels(cpu)

        cpus = None
        if sname == "CPU":
            cpus = levels["CPU"]
        if sname in ("core", "node", "die"):
            method = getattr(self._cpuinfo, f"{sname}s_to_cpus")
            cpus = method(levels[sname], packages=levels["package"])
        if sname == "package":
            cpus = self._cpuinfo.packages_to_cpus(packages=levels["package"])

        opts = ""

        if sname == "die" and not self._skip_io_dies:
            package = levels["package"]
            io_dies = self._cpuinfo.get_dies(package=package, compute_dies=False, io_dies=True)
            if io_dies:
                # I/O dies have no CPUs, so '--cpus' does not cover them. Include them using
                # '--dies'.
                io_dies = Trivial.rangify(io_dies)
                opts = f"--packages {package} --dies {io_dies} "

        if cpus is None:
            raise Error(f"unknown scope for property '{pname}'")

        if isinstance(cpus, list):
            cpus = Trivial.rangify(cpus)

        return opts + f"--cpus {cpus}"

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
            csnames.update(all_csnames[:idx + 1])

        csnames = self._normalize_csnames(csnames)
        return ",".join(csnames)

    def get_commands(self, props, cpu=None):
        """
        Yield list of 'pepc' commands to configure the system for measuring properties 'props'. The
        arguments are as follows.
          * props - a dictionary describing the measured properties.
          * cpu - measured CPU number.
        """

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

            scope_opts = self._get_scope_opts(pname, cpu=cpu)

            # We use 'unl' keyword to express unlocked frequency value, and the frequency options
            # have two values.
            if value == "unl":
                values = ["min", "max"]
            else:
                values = [value] * self.props[pname]["cmd"].count("{}")

            cmd = self.props[pname]["cmd"].format(*values, scope_opts=scope_opts)

            if self._pman.hostname != "localhost":
                cmd += f" -H {self._pman.hostname}"

            yield cmd

    def __init__(self, pman, cpuinfo, cpuidle, args):
        """
        The class constructor. The arguments are as follows.
          * pman - the process manager object defining the system to measure.
          * cpuinfo - 'CPUInfo' object for the measured system.
          * cpuidle - the 'CPUIdle.CPUIdle()' object for the measured system.
          * args - input arguments, not clean, should be only_measured_cpu=False, etc kwargs (TODO).
        """

        super().__init__(pman, cpuinfo, cpuidle)

        self._only_measured_cpu = args.only_measured_cpu
        self._skip_io_dies = args.skip_io_dies
        self._only_one_cstate = args.only_one_cstate
        self._cstates_always_enable = args.cstates_always_enable

        if self._cstates_always_enable:
            csnames = Trivial.split_csv_line(self._cstates_always_enable)
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

        return self._toolopts.replace("{REPORTID}", reportid)

    def get_command(self, props, reportid, **kwargs): # pylint: disable=unused-argument
        """
        Format and return measurement command. The arguments are as follows.
          * props - a dictionary describing the measured properties.
          * reportid - report ID of the measurement result.
          * kwargs - additional arguments necessary to format the command.
        """

        cmd = str(self.toolpath)

        toolopts = self._get_toolopts(reportid)
        if toolopts:
            cmd += f" {toolopts}"

        return cmd

    def __init__(self, args):
        """
        The class constructor. The arguments are as follows.
          * args - input arguments. Should be instead a bunch of args or kwargs (TODO).
        """

        with LocalProcessManager.LocalProcessManager() as lpman:
            self.toolpath = lpman.which(args.toolpath)

        self._toolopts = args.toolopts
        self._outdir = args.outdir
        self._reportid_prefix = args.reportid_prefix
        self._reportid_suffix = args.reportid_suffix
        self._hostname = args.hostname
        self._debug = args.debug
        self._stats = args.stats
        self._stats_intervals = args.stats_intervals

        if not self._outdir:
            self._outdir = ReportID.format_reportid(prefix=self.toolpath.name)

class _WultCmdFormatter(_ToolCmdFormatterBase):
    """A Helper class for creating 'wult' or 'ndl' commands."""

    def _create_command(self, cpu, devid, reportid=None, cstate_filter=None):
        """Create and return 'wult' or 'ndl' command."""

        cmd = f"{self.toolpath} "
        if Logging.getLogger(Logging.MAIN_LOGGER_NAME).colored:
            cmd += " --force-color"
        cmd += f" start -c {self._datapoints}"

        if self._stats is not None:
            cmd += f" --stats=\"{self._stats}\""

        if self._stats_intervals is not None:
            cmd += f" --stats-intervals=\"{self._stats_intervals}\""

        if cpu is not None:
            cmd += f" --cpu {cpu}"

        if cstate_filter:
            cmd += f" --include=\"{cstate_filter}\""

        cmd += f" {devid}"

        if reportid:
            cmd += f" --reportid {reportid} -o {self._outdir}/{reportid}"
        else:
            cmd += f" -o {self._outdir}"

        if self._debug:
            cmd += " -d"

        toolopts = self._get_toolopts(reportid)
        if toolopts:
            cmd += f" {toolopts}"

        if self._hostname != "localhost":
            cmd += f" -H {self._hostname}"

        return cmd

    def _get_cstate_filter(self, props):
        """Get C-state filter string to include only datapoints with requested C-state residency."""

        if not self._use_cstate_filters:
            return None

        cstate_filter = None
        reqcstate = props.get("cstates")
        if reqcstate:
            cstate_filter = CSTATE_FILTERS.get(reqcstate)
            if reqcstate == "C6" and props.get("pcstates") == "PC6" and self._c6_enters_pc6:
                cstate_filter += f" & {CSTATE_FILTERS.get('PC6')}"

        return cstate_filter

    def get_command(self, props, reportid, **kwargs):
        """
        Format and return measurement command for 'wult' or 'ndl'. The arguments are as follows.
          * props - a dictionary describing the measured properties.
          * reportid - report ID of the measurement result.
          * kwargs - additional arguments necessary for formatting the command.
        """

        return self._create_command(kwargs["cpu"], kwargs["devid"], reportid=reportid,
                                    cstate_filter=self._get_cstate_filter(props))

    def _c6p_exists(self):
        """Check if requestable C-state C6P, C6S or C6SP is supported by the SUT."""

        for _, csinfo in self._cpuidle.get_cstates_info(csnames="all", cpus="all"):
            for csname in csinfo:
                if csname.startswith("C6") and csname != "C6":
                    return True

        return False

    def __init__(self, cpuidle, args):
        """
        The class constructor. The arguments are as follows.
          * cpuidle - the 'CPUIdle.CPUIdle()' object for the measured system.
          * args - input arguments. Should be instead a bunch of args or kwargs (TODO).
        """

        super().__init__(args)

        self._cpuidle = cpuidle
        self._datapoints = args.datapoints
        self._stats = args.stats
        self._use_cstate_filters = not args.no_cstate_filters

        self._c6_enters_pc6 = not self._c6p_exists()

    def close(self):
        """Uninitialize the class objetc."""
        ClassHelpers.close(self, unref_attrs=("_cpuidle",))

class _NdlCmdFormatter(_WultCmdFormatter):
    """A Helper class for creating 'ndl' commands."""

    def __init__(self, cpuidle, args):
        """The class constructor. The arguments are same as for _WultCmdFormatter class."""

        super().__init__(cpuidle, args)

        # The ndl doesn't support C-state filters.
        self._use_cstate_filters = False

class _StatsCollectCmdFormatter(_ToolCmdFormatterBase):
    """A Helper class for creating 'stats-collect' commands."""

    def _create_command(self, command, cpu, reportid=None):
        """Create and return 'stats-collect' command."""

        cmd = f"{self.toolpath} "
        if Logging.getLogger(Logging.MAIN_LOGGER_NAME).colored:
            cmd += " --force-color"
        cmd += " start"

        if self._stats is not None:
            cmd += f" --stats=\"{self._stats}\""

        if self._stats_intervals is not None:
            cmd += f" --stats-intervals=\"{self._stats_intervals}\""

        if reportid:
            cmd += f" --reportid {reportid} -o {self._outdir}/{reportid}"
            command = command.replace("{REPORTID}", reportid)
        else:
            cmd += f" -o {self._outdir}"

        if self._debug:
            cmd += " -d"

        toolopts = self._get_toolopts(reportid)
        if toolopts:
            cmd += f" {toolopts}"

        if cpu is not None:
            cmd += f" --cpu {cpu}"
            command = command.replace("{CPU}", cpu)

        if self._hostname != "localhost":
            cmd += f" -H {self._hostname}"

        cmd += f" '{command}'"

        return cmd

    def get_command(self, props, reportid, **kwargs):
        """
        Format and return the 'stats-collect' measurement command. The arguments are as follows.
          * props - a dictionary describing the measured properties. Unused. Should not be like
                    this, should be instead part of "kwargs" (TODO).
          * reportid - report ID of the measurement result.
          * kwargs - additional arguments necessary to format the command.
        """

        return self._create_command(kwargs["command"], kwargs["cpu"], reportid=reportid)

class _PbeCmdFormatter(_ToolCmdFormatterBase):
    """A Helper class for creating 'pbe' commands."""

    def _create_command(self, reportid=None):
        """Create and return 'pbe' command."""

        cmd = f"{self.toolpath} "
        if Logging.getLogger(Logging.MAIN_LOGGER_NAME).colored:
            cmd += " --force-color"
        cmd += " start"

        if self._stats is not None:
            cmd += f" --stats=\"{self._stats}\""

        if self._stats_intervals is not None:
            cmd += f" --stats-intervals=\"{self._stats_intervals}\""

        if reportid:
            cmd += f" --reportid {reportid} -o {self._outdir}/{reportid}"
        else:
            cmd += f" -o {self._outdir}"

        if self._debug:
            cmd += " -d"

        toolopts = self._get_toolopts(reportid)
        if toolopts:
            cmd += f" {toolopts}"

        if self._hostname != "localhost":
            cmd += f" -H {self._hostname}"

        return cmd

    def get_command(self, props, reportid, **kwargs):
        """
        Format and return the 'pbe' measurement command. The arguments are as follows.
          * props - a dictionary describing the measured properties. Unused. Should not be like
                    this, should be instead part of "kwargs" (TODO).
          * reportid - report ID of the measurement result.
          * kwargs - additional arguments necessary to format the command.
        """

        return self._create_command(reportid=reportid)

class BatchConfig(_Common.CmdlineRunner):
    """
    Helper class for 'exercise-sut' tool to configure and exercise SUT with different system
    configuration permutations (according to the input properties).
    """

    def deploy(self):
        """Deploy 'ndl', 'wult', 'pbe' or 'stats-collect' to the SUT."""

        if self._wfmt.toolpath.name not in (WULT_TOOLNAME, NDL_TOOLNAME, PBE_TOOLNAME,
                                            STC_TOOLNAME):
            raise Error(f"deploy supported only by tools '{WULT_TOOLNAME}', '{NDL_TOOLNAME}' and "
                        f"'{STC_TOOLNAME}'")

        deploy_cmd = f"{self._wfmt.toolpath} deploy"

        if self._pman.hostname != "localhost":
            deploy_cmd += f" -H {self._pman.hostname}"

        self._run_command(deploy_cmd)

    def props_to_str(self, props):
        """Convert property dictionary 'props' to human readable string."""

        return self._pfmt.props_to_str(props)

    def get_props_batch(self, inprops):
        """
        Yield dictionary with system properties, with property name as key and property value as
        value. The arguments are as follows.
          * inprops - the input properties dictionary, descripting the proprties and the values that
                      should be measured.
        """

        yield from self._pfmt.iter_props(inprops)

    def configure(self, props, cpu):
        """
        Configure the system for measurement. The arguments are as follows.
          * props - the measured properties and their values.
          * cpu - CPU number to configure.
        """

        for cmd in self._pfmt.get_commands(props, cpu):
            self._run_command(cmd)

    def create_reportid(self, props, **kwargs):
        """
        Create and return report ID. The arguments are as follows.
          * props - the measured properties and their values.
          * kwargs - additional parameters that may affect the report ID (TODO: why 'kwargs' should
                     be used?)
        """

        return self._wfmt.create_reportid(props, **kwargs)

    def run(self, props, reportid, **kwargs):
        """
        Run the measurements. The arguments are as follows.
          * props - the measured properties and their values.
          * reportid - report ID of the measurement result.
          * kwargs - additional parameters that may affect the report ID (TODO: why 'kwargs' should
                     be used?)
        """

        cmd = self._wfmt.get_command(props, reportid, **kwargs)
        self._run_command(cmd)

    def __init__(self, args):
        """
        The class constructor. The arguments are as follows.
          * args - the 'exercise-sut' input command line arguments.
        """

        self._pman = None
        self._cpuinfo = None
        self._cpuidle = None
        self._pfmt = None
        self._wfmt = None
        self._systemctl = None

        super().__init__(dry_run=args.dry_run, ignore_errors=args.ignore_errors)

        self._pman = get_pman(args)
        self._cpuinfo = CPUInfo.CPUInfo(pman=self._pman)
        self._cpuidle = CPUIdle.CPUIdle(pman=self._pman, cpuinfo=self._cpuinfo)
        self._pfmt = _PepcCmdFormatter(self._pman, self._cpuinfo, self._cpuidle, args)
        self._wfmt = _get_workload_cmd_formatter(self._cpuidle, args)

        self._systemctl = Systemctl.Systemctl(pman=self._pman)
        if self._systemctl.is_active("tuned"):
            self._systemctl.stop("tuned", save=True)

    def close(self):
        """Uninitialize the class objetc."""

        if self._systemctl:
            self._systemctl.restore()

        ClassHelpers.close(self, close_attrs=("_pfmt", "_wfmt", "_pman", "_systemctl"))
