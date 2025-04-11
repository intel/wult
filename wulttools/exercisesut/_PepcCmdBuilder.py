# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023-2024 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Antti Laakso <antti.laakso@linux.intel.com>
#         Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
A helper module for the 'exercise-sut' -tool to create 'pepc' tool commands.
"""

import itertools
from pepclibs.helperlibs import Logging, ClassHelpers, Trivial
from pepclibs.helperlibs.Exceptions import Error
from pepclibs import CStates, PStates
from wulttools.exercisesut import _Common

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.wult.{__name__}")

PC0_ONLY_STATES = ("POLL", "C1", "C1E")

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

        for pname, pinfo in _Common.PROP_INFOS.items():

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

    def normalize_inprops(self, inprops):
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

class PepcCmdBuilder(_PropIteratorBase):
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

    def __init__(self, pman, cpuinfo, cpuidle, only_measured_cpu, skip_io_dies, only_one_cstate,
                 cstates_always_enable):
        """
        The class constructor.

        Args:
            pman: The process manager object defining the system to measure.
            cpuinfo: The 'CPUInfo' object for the measured system.
            cpuidle: The 'CPUIdle.CPUIdle()' object for the measured system.
            only_measured_cpu: If 'True', only the measured CPU is configured.
            skip_io_dies: If 'True', skip configuration of I/O dies.
            only_one_cstate: If 'True', only measured C-state is enabled.
            cstates_always_enable: Comma-separated list of C-states to always enable.
        """

        super().__init__(pman, cpuinfo, cpuidle)

        self._only_measured_cpu = only_measured_cpu
        self._skip_io_dies = skip_io_dies
        self._only_one_cstate = only_one_cstate
        self._cstates_always_enable = cstates_always_enable

        if self._cstates_always_enable:
            csnames = Trivial.split_csv_line(self._cstates_always_enable)
            self._cstates_always_enable = self._normalize_csnames(csnames)
