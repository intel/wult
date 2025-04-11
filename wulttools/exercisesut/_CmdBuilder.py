# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023-2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Antti Laakso <antti.laakso@linux.intel.com>
#         Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
A helper module for the 'exercise-sut' tool to configure target system with various system property
permutations.
"""

from pepclibs.helperlibs import Logging, ClassHelpers, LocalProcessManager
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.helperlibs import ReportID
from statscollecttools import ToolInfo as StcToolInfo
from wulttools.ndl import ToolInfo as NdlToolInfo
from wulttools.pbe import ToolInfo as PbeToolInfo
from wulttools.wult import ToolInfo as WultToolInfo
from wulttools.exercisesut import _Common

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.wult.{__name__}")

NDL_TOOLNAME = NdlToolInfo.TOOLNAME
PBE_TOOLNAME = PbeToolInfo.TOOLNAME
STC_TOOLNAME = StcToolInfo.TOOLNAME
WULT_TOOLNAME = WultToolInfo.TOOLNAME

_DEPLOYABLE_TOOLS = (WULT_TOOLNAME, NDL_TOOLNAME, PBE_TOOLNAME, STC_TOOLNAME)

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

def get_workload_cmd_builder(cpuidle, **kwargs):
    """Create and return object for creating workload commands."""

    toolname = kwargs["toolpath"].name

    if toolname == WULT_TOOLNAME:
        return _WultCmdBuilder(cpuidle, **kwargs)

    if toolname == NDL_TOOLNAME:
        return _NdlCmdBuilder(cpuidle, **kwargs)

    if toolname == STC_TOOLNAME:
        return _StatsCollectCmdBuilder(**kwargs)

    if toolname == PBE_TOOLNAME:
        return _PbeCmdBuilder(**kwargs)

    return _CmdBuilderBase(**kwargs)

class _CmdBuilderBase(ClassHelpers.SimpleCloseContext):
    """A base class to help creating commands."""

    def create_reportid(self, props, **kwargs):
        """Create report ID from used properties 'props'."""

        monikers = []

        if self._hostname != "localhost":
            monikers.append(self._hostname)

        if "devid" in kwargs:
            monikers.append(kwargs["devid"])

        for pname, val in props.items():
            moniker = _Common.PROP_INFOS[pname].get("moniker", "")
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

    def get_deploy_command(self):
        """Return command to deploy the tool."""

        if self.toolpath.name not in _DEPLOYABLE_TOOLS:
            raise Error(f"deploy supported only by tools {', '.join(_DEPLOYABLE_TOOLS)}")

        cmd = f"{self.toolpath} deploy"

        if self._hostname != "localhost":
            cmd += f" -H {self._hostname}"

        return cmd

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

    def __init__(self, **kwargs):
        """
        The class constructor.
            Args:
                **kwargs: Input arguments passed down to workload tool.
        """

        with LocalProcessManager.LocalProcessManager() as lpman:
            self.toolpath = lpman.which(kwargs["toolpath"])

        self._toolopts = kwargs["toolopts"]
        self._outdir = kwargs["outdir"]
        self._reportid_prefix = kwargs["reportid_prefix"]
        self._reportid_suffix = kwargs["reportid_suffix"]
        self._hostname = kwargs["hostname"]
        self._debug = kwargs["debug"]
        self._stats = kwargs["stats"]
        self._stats_intervals = kwargs["stats_intervals"]

        if not self._outdir:
            self._outdir = ReportID.format_reportid(prefix=self.toolpath.name)

    def close(self):
        """Uninitialize the class objetc."""

class _WultCmdBuilder(_CmdBuilderBase):
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

    def __init__(self, cpuidle, **kwargs):
        """
        The class constructor. The arguments are as follows.
          * cpuidle - the 'CPUIdle.CPUIdle()' object for the measured system.
          * args - input arguments. Should be instead a bunch of args or kwargs (TODO).
        """

        super().__init__(**kwargs)

        self._cpuidle = cpuidle
        self._datapoints = kwargs["datapoints"]
        self._stats = kwargs["stats"]
        self._use_cstate_filters = not kwargs["no_cstate_filters"]

        self._c6_enters_pc6 = not self._c6p_exists()

    def close(self):
        """Uninitialize the class objetc."""
        ClassHelpers.close(self, unref_attrs=("_cpuidle",))

class _NdlCmdBuilder(_WultCmdBuilder):
    """A Helper class for creating 'ndl' commands."""

    def __init__(self, cpuidle, **kwargs):
        """The class constructor. The arguments are same as for _WultCmdBuilder class."""

        super().__init__(cpuidle, **kwargs)

        # The ndl doesn't support C-state filters.
        self._use_cstate_filters = False

class _StatsCollectCmdBuilder(_CmdBuilderBase):
    """A Helper class for creating 'stats-collect' commands."""

    def _create_command(self, command, reportid=None):
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

        return self._create_command(kwargs["command"], reportid=reportid)

class _PbeCmdBuilder(_CmdBuilderBase):
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
