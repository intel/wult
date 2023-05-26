# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module provides API for collecting SUT statistics.
"""

import copy
import logging
from pepclibs.helperlibs import Trivial
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.collector import _STCAgent, _SpecStatsCollect

_LOG = logging.getLogger()

# An "aggregate statistic" is a statistic which can be used when a system-specific configuration is
# unknown. For example, the aggregate statistic name "ipmi" will try to resolve to "ipmi-oob" and
# fall back on "ipmi-inband" if out-of-band IPMI collection is not possible on the SUT.
#
# The following constant maps aggregate statistic names to specific statistic names. It partially
# mimics the '_STINFO' dictionary structure.
_AGGR_STINFO = {
    "ipmi": {
        "stnames": {"ipmi-inband", "ipmi-oob"},
        "interval": None,
        "toolpath": None,
        "description": "an \"aggregate statistics name\" that will be resolved to \"ipmi-inband\" "
                       "or \"ipmi-oob\".",
   },
}

# The statistics description dictionary.
_STINFO = { **_AGGR_STINFO, **_STCAgent.STINFO}

def get_stnames(include_aggregate=True):
    """
    Returns all statistic names. The arguments are as follows:
     * include_aggregate - if 'True', include the aggregate statistic names, otherwise include only
                           specific statistic names.
    """

    if include_aggregate:
        return list(_STINFO)
    return list(_STCAgent.STINFO)

def get_stinfo(stname):
    """Return information about statistic 'stname'."""

    if stname in _STINFO:
        return _STINFO[stname]

    stnames = ", ".join(get_stnames())
    raise Error(f"unknown statistic name '{stname}', the known names are:\n  {stnames}")

def check_stname(stname):
    """Verify that 'stname' is a known statistic name."""
    get_stinfo(stname)

def check_stnames(stnames):
    """Verify that statistics in the 'stnames' list are legit."""

    for stname in stnames:
        get_stinfo(stname)

class StatsCollect(_SpecStatsCollect.SpecStatsCollect):
    """
    This class provides API for collecting SUT statistics, such as 'turbostat' data and AC power.
    This class supports both specific and aggregate statistics.

    The usage model of this class is as follows.
      1. Create an object. This will run 'stc-agent' on the SUT (in-band statistics collection) and
         the local host (out-of-band collection). 'stc-agent' is just an agent that listens for
         commands on a Unix socket. The commands are like "start collecting", "stop collecting",
         "set properties", etc. 'stc-agent' runs various collectors.

         Example of "in-band" collectors: acpower, ipmi-inband. These tools run on the local system,
         but collect information about the remote system.

      2. Call 'set_info_logging()' to enable high-level log messages about big steps, such as
          discovery results.
      3. Optionally set the list of statistics collectors that are going to be used by running the
         'set_disabled_stats()', 'set_enabled_stats()'.
      4. Optionally set tool path and properties for certain statistics using 'set_prop()' and
         'set_toolpath()'.
      5. Optionally set the 'stc-agent' paths on the local and remote systems. By default the
         'stc-agent' program is looked for in the paths from the 'PATH' environment variable.

         Note: up to this point, the 'stc-agent' processes have not been started. The configuration
         passed via the 'set_*()' methods was not yet communicated to 'stc-agent'. But it will be
         sent to 'stc-agent' as soon as it starts. And it starts when 'discover()' or 'configure()'
         methods are called.

      6. Optionally discover the available statistics by running the 'discover()' method. Once the
         discovery is finished, re-run 'set_enabled_stats()' to enable the discovered statistics.
      7. Run the 'configure()' method to configure the statistics collectors.
      8. Optionally add a label using 'add_label()'.
      9. Run 'start()' to start collecting the statistics. Supposedly after the 'start()' method is
         finished, you run a workload on the SUT.
      10. Optionally add more labels using 'add_label()'.
      11. Run 'stop()' to stop collecting the statistics. You can repeat the start/stop cycles and
          re-configure the collectors between the cycles.
      10. Run 'finalize()' to finalize statistics collection (copy the data from remote host to the
          local host, etc).
    """

    def _separate_aggr_vs_specific(self, stnames):
        """
        Splits statistics names in 'stnames' on two sets - the aggregate statistics names and the
        specific statistics names. Returns those two sets.
        """

        aggr_stnames = stnames & set(self._aggr_stinfo)
        spec_stnames = stnames & set(self._spec_stinfo)

        unknown_stnames = stnames - aggr_stnames - spec_stnames
        if unknown_stnames:
            unknown_stname = unknown_stnames.pop()
            known_stnames = list(self._aggr_stinfo) + list(self._inbagent.stinfo) + \
                            list(self._oobagent.stinfo)
            known_stnames = ", ".join(known_stnames)
            raise Error(f"unknown statistic name '{unknown_stname}', the known names are:\n"
                        f"  {known_stnames}")

        return aggr_stnames, spec_stnames

    def _normalize_stnames(self, stnames):
        """
        Turn statistics names list in 'stnames' into a python 'set', handle the special cases of
        'None' and "all", which means "all statistics".
        """

        if stnames in (None, "all"):
            stnames = set(self._inbagent.stinfo)
            if self._oobagent is not None:
                stnames.update(set(self._oobagent.stinfo))
        elif Trivial.is_iterable(stnames):
            stnames = set(stnames)
        else:
            raise Error(f"BUG: bad statistic names '{stnames}': provide an iterable collection")

        return stnames

    def set_enabled_stats(self, stnames):
        """
        Enable statistics in 'stnames'. If 'stname' is "all" or 'None', enable all statistics.
        Note, all statistics are enabled by default when an instance of this class is created.
        """

        stnames = self._normalize_stnames(stnames)

        aggr_stnames, spec_stnames = self._separate_aggr_vs_specific(stnames)

        if aggr_stnames:
            _LOG.debug("enabling the following aggregate statistics: %s", ", ".join(aggr_stnames))
        if spec_stnames:
            _LOG.debug("enabling the following specific statistics: %s", ", ".join(spec_stnames))

        for astname in aggr_stnames:
            enabled = False
            for stname in self._aggr_stinfo[astname]["stnames"]:
                try:
                    super().set_enabled_stats(set([stname]))
                    enabled = True
                except Error as err:
                    _LOG.debug("failed to enable specific statistic '%s' as part of aggregate "
                               "statistic '%s':\n%s", stname, astname, err.indent(2))
                spec_stnames.discard(stname)

            if not enabled:
                raise Error(f"could not enable any of the specific statistics for aggregate "
                            f"statistic '{astname}'")

        super().set_enabled_stats(spec_stnames)

    def set_disabled_stats(self, stnames):
        """Same as 'set_enabled_stats()', but for disabling."""

        stnames = self._normalize_stnames(stnames)
        aggr_stnames, spec_stnames = self._separate_aggr_vs_specific(stnames)

        if aggr_stnames:
            _LOG.debug("disabling the following aggregate statistics: %s", ", ".join(aggr_stnames))
        if spec_stnames:
            _LOG.debug("disabling the following specific statistics: %s", ", ".join(spec_stnames))

        for astname in aggr_stnames:
            super().set_disabled_stats(self._aggr_stinfo[astname]["stnames"])
            spec_stnames -= self._aggr_stinfo[astname]["stnames"]

        super().set_disabled_stats(spec_stnames)

    def get_enabled_stats(self):
        """Return a set containing all the the enabled statistic names."""

        enabled_stnames = super().get_enabled_stats()
        for astname, astinfo in self._aggr_stinfo.items():
            if enabled_stnames & astinfo["stnames"]:
                enabled_stnames.add(astname)
        return enabled_stnames

    def get_disabled_stats(self):
        """Return a set containing all the the disabled statistic names."""

        disabled_stnames = super().get_disabled_stats()
        for astname, astinfo in self._aggr_stinfo.items():
            if all(stname in disabled_stnames for stname in astinfo["stnames"]):
                disabled_stnames.add(astname)
        return disabled_stnames

    def _reject_aggr_stnames(self, stnames, operation):
        """If 'stnames' includes an aggregate statistics, raise an error."""

        aggr_stnames, _ = self._separate_aggr_vs_specific(stnames)
        if aggr_stnames:
            astname = aggr_stnames.pop()
            spec_stnames = ", ".join(self._aggr_stinfo[astname]["stnames"])
            raise Error(f"cannot {operation} for an aggregate statistic '{astname}'. Please, use "
                        f"one of the following specific statistics instead:\n  {spec_stnames}")

    def _reject_aggr_stname(self, stname, operation):
        """Raise an error if 'stname' is an aggregate statistic."""
        self._reject_aggr_stnames(set([stname]), operation)

    def set_intervals(self, intervals):
        """
        Set intervals for statistics collectors. The 'intervals' argument should be a dictionary
        with statistics collector names as keys and the collection interval as the value. This
        method should be called prior to the 'configure()' method. By default the statistics
        collectors use intervals from the '_STINFO' statistics description dictionary.

        Returns a dictionary similar to 'intervals', but only including enabled statistics and
        possibly rounded interval values as 'float' type.
        """

        self._reject_aggr_stnames(set(intervals), "set interval")
        super().set_intervals(intervals)

    def get_toolpath(self, stname):
        """
        Get currently configured path to the tool collecting the 'stname' statistics. The path is on
        the same host where 'stc-agent' runs (local host for out-of-band statistics, the SUT for
        in-band statistics.
        """

        self._reject_aggr_stname(stname, "get tool path")
        return super().get_toolpath(stname)

    def set_toolpath(self, stname, path):
        """
        Set path to the tool collecting the 'stname' statistics to 'path'. The path is supposed to
        be on the same host where 'stc-agent' runs (local host for out-of-band statistics, the SUT
        for in-band statistics.
        """

        self._reject_aggr_stname(stname, "set tool path")
        super().set_toolpath(stname, path)

    def set_prop(self, stname, name, value):
        """Set 'stname' statistic collector's property 'name' to value 'value'."""

        self._reject_aggr_stname(stname, f"set property '{name}'")
        super().set_prop(stname, name, value)

    def _expand_aggr_stnames(self, stnames):
        """
        Expand aggregate statistic names in 'stnames'. Return a new set of statistic names which
        does not contain any aggregate statistic names.
        """

        exp_stnames = set()
        for stname in stnames:
            if stname in self._aggr_stinfo:
                exp_stnames.update(self._aggr_stinfo[stname]["stnames"])
            elif stname in self._inbagent.stinfo or stname in self._oobagent.stinfo:
                exp_stnames.add(stname)
            else:
                stnames = ", ".join(get_stnames())
                raise Error(f"unknown statistic name '{stname}', the known names are:\n  {stnames}")

        return exp_stnames

    def discover(self):
        """
        Discover and return set of statistics that can be collected for SUT. This method probes all
        non-disabled statistics collectors and returns the names of the successfully probed ones (in
        form of a 'set()').

        Note, prior to calling this method, you can (but do not have to) use the following methods.
         * 'set_disabled_stats()' and 'set_enabled_stats()' prior to to enable/disable certain
            statistics.
         * 'set_intervals()' - to configure the statistics collectors' intervals.
         * 'set_prop()' - to configure statistics collectors' properties.
         * 'set_toolpath()' - to configure statistics collectors' tools paths.

        The above methods will not communicate to the 'stc-agent' process(es), which may not even
        have been started yet. They just save the configuration in an internal dictionary. The
        'discover()' method will start the 'stc-agent' process(es) and pass all the saved
        configuration to them.
        """

        enabled_stnames = self.get_enabled_stats()
        aggr_stnames, _ = self._separate_aggr_vs_specific(enabled_stnames)

        discover_stnames = super().get_enabled_stats()
        if discover_stnames:
            _LOG.log(self._infolvl, "Discovering the following statistics: %s",
                     ", ".join(discover_stnames))
        else:
            return set()

        discovered_stnames = self._discover(discover_stnames)

        for astname in aggr_stnames:
            astinfo = self._aggr_stinfo[astname]
            # Cache the specific statistics available for the aggregate statistics.
            astinfo["resolved"] = astinfo["stnames"] & discovered_stnames

            if astname in discover_stnames:
                # Also include the aggregate statistic name to the returned set of discovered
                # statistics.
                discovered_stnames.add(astname)

        if discovered_stnames:
            _LOG.log(self._infolvl, "Discovered the following statistics: %s",
                     ", ".join(discovered_stnames))
        else:
            _LOG.log(self._infolvl, "Discovered no statistics%s", self._pman.hostmsg)

        return discovered_stnames

    def configure(self):
        """
        Configure the enabled statistics collectors.

        Please, also refer to the 'Notes' in the 'discover()' method - they are relevant to
        'configure()' as well.
        """

        aggr_stnames, _ = self._separate_aggr_vs_specific(self.get_enabled_stats())

        for astname in aggr_stnames:
            astinfo = self._aggr_stinfo[astname]
            if astinfo["resolved"]:
                super().set_enabled_stats(astinfo["resolved"])
                continue

            _LOG.log(self._infolvl, "Resolving the '%s' statistic", astname)
            discovered_stnames = self._discover(self.get_enabled_stats() & astinfo["stnames"])
            if discovered_stnames:
                _LOG.log(self._infolvl, "Resolved the '%s' statistic to '%s'",
                         astname, ", ".join(discovered_stnames))
                super().set_enabled_stats(discovered_stnames)

                # Make sure only the resolved 'stname' is enabled out of all of the
                # 'astinfo["stnames"]'.
                unused = {stat for stat in astinfo["stnames"] if stat not in discovered_stnames}
                super().set_disabled_stats(unused)
            else:
                stnames = ", ".join(astinfo["stnames"])
                raise Error(f"cannot configure aggregate statistic '{astname}' - none of the "
                            f"following specific statistics are supported:\n  {stnames}")

        _LOG.log(self._infolvl, "Configuring the following statistics: %s",
                 ", ".join(self._get_enabled_stats()))

        super().configure()

    def _set_aggr_stinfo_defaults(self):
        """Add default keys to the aggregate statistics description dictionary."""

        for info in self._aggr_stinfo.values():
            if "resolved" not in info:
                info["resolved"] = set()

    def __init__(self, pman, reportid, cpunum=None, cmd=None, local_outdir=None,
                 remote_outdir=None):
        """
        Initialize a class instance. The arguments are the same as
        'WORawResult.__init__()' except for:
          * pman - the process manager object associated with the SUT (the host to collect the
                   statistics for). Note, a reference to the 'pman' object will be saved and it will
                   be used in various methods, so it has to be kept connected. The reference will be
                   dropped once the 'close()' method is invoked.
          * local_outdir - output directory path on the local host for storing the local
                           'stc-agent' logs and results (the collected statistics). A temporary
                           directory is created and used if 'local_outdir' is not provided.
          * remote_outdir - output directory path on the remote host (the SUT) for storing the
                            remote 'stc-agent' logs and results (the collected statistics). A
                            temporary directory is created and used if 'remote_outdir' is not
                            provided.

        The collected statistics will be stored in the 'stats' sub-directory of the output
        directory, the 'stc-agent' logs will be stored in the 'logs' sub-directory.

        If the an output directory was not provided and instead, was created by 'StatsCollect', the
        directory gets removed in the 'close()' method.
        """

        super().__init__(pman, reportid, cpunum, cmd, local_outdir, remote_outdir)

        # Initialize the aggregate statistics dictionary.
        self._aggr_stinfo = copy.deepcopy(_AGGR_STINFO)
        self._spec_stinfo = copy.deepcopy(_SpecStatsCollect.STINFO)
        self._set_aggr_stinfo_defaults()
