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
from pepclibs.helperlibs import ClassHelpers, Trivial
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.collector import _STCAgent

_LOG = logging.getLogger()

# An "aggregate statistic name" is a statistic name which can be used when a system-specific
# configuration is unknown. For example, the aggregate statistic name "ipmi" will try to resolve to
# "ipmi-oob" and fall back on "ipmi-inband" if out-of-band IPMI collection is not possible on the
# SUT.
#
# The following constant maps aggregate statistic names to specific statistic names. It partially
# mimics the '_STCAgent.STATS_INFO' dictionary structure.
_AGGR_STINFO = {
    "ipmi": {
        "stnames": {"ipmi-inband", "ipmi-oob"},
        "interval": None,
        "toolpath": None,
        "description": "an \"aggregate statistics name\" that will be resolved to \"ipmi-inband\" "
                       "or \"ipmi-oob\".",
   },
}

def get_stnames(include_aggregate=True):
    """
    Returns all statistic names. The arguments are as follows:
     * include_aggregate - if 'True', include the aggregate statistic names, otherwise include only
                           specific statistic names.
    """

    stnames = list(_STCAgent.STATS_INFO)
    if include_aggregate:
        stnames += list(_AGGR_STINFO)

    return stnames

def get_stinfo(stname, allow_aggregate=True):
    """
    Return information about statistic 'stname'. The arguments are as follows:
     * stname - name of the statistic to return the information about.
     * allow_aggregate - if 'False', errors if 'stname' is an aggregate statistic name or an invalid
                         statistic name. Otherwise, only errors if 'stname' if not a valid statistic
                         name.
    """

    if stname in _AGGR_STINFO:
        if not allow_aggregate:
            stnames = ", ".join(get_stnames(include_aggregate=allow_aggregate))
            raise Error(f"'{stname}' is an aggregate statistic name, please specify one of the "
                        f"following specific statistic names:\n  {stnames}")
        return _AGGR_STINFO[stname]

    if stname in _STCAgent.STATS_INFO:
        return _STCAgent.STATS_INFO[stname]

    stnames = ", ".join(get_stnames(include_aggregate=allow_aggregate))
    raise Error(f"unknown statistic name '{stname}', the known names are:\n  {stnames}")

def check_stname(stname, allow_aggregate=True):
    """
    Verify that 'stname' is a known statistic name. The arguments are as follows:
     * stname - the statistic name to verify.
     * allow_aggregate - if 'False', errors if 'stname' is an aggregate statistic name or an invalid
                         statistic name. Otherwise, only errors if 'stname' if not a valid statistic
                         name.
    """

    get_stinfo(stname, allow_aggregate=allow_aggregate)

def check_stnames(stnames):
    """Verify that statistics in the 'stnames' list are legit."""

    for stname in stnames:
        get_stinfo(stname)

class _StatsCollectNoAggr(ClassHelpers.SimpleCloseContext):
    """
    This class provides API for collecting SUT statistics, such as 'turbostat' data and AC power.
    This class supports specific statistics (such as 'turbostat', 'ipmi-oob', 'ipmi-in'), but it
    does not support aggregate statistics (such as 'ipmi').
    """

    def _separate_inb_vs_oob(self, stnames):
        """
        Split statistic names 'stnames' on two sets - the in-band and the out-of-band statistics.
        Return a tuple of those two sets.
        """

        inb_stnames = stnames & set(self._inbagent.stinfo)
        oob_stnames = stnames & set(self._oobagent.stinfo)

        unknown_stnames = stnames - inb_stnames - oob_stnames
        if unknown_stnames:
            unknown_stname = unknown_stnames.pop()
            known_stnames = list(self._inbagent.stinfo) + list(self._oobagent.stinfo)
            known_stnames = ", ".join(known_stnames)
            raise Error(f"unknown statistic name '{unknown_stname}', the known names are:\n"
                        f"  {known_stnames}")

        return inb_stnames, oob_stnames

    def _separate_local_vs_remote(self, stnames):
        """
        Split statistic names 'stnames' on two sets - the statistics collected by a local
        'stc-agent' instance, and the statistics collected by the remote 'stc-agent' instance.
        Return a tuple of those two sets.
        """

        inb_stnames, oob_stnames = self._separate_inb_vs_oob(stnames)

        # Please, refer to the commentaries in '__init__()' for the mapping between in-/out-of-band
        # and local/remote.

        if self._pman.is_remote:
            local_stnames = oob_stnames
            remote_stnames = inb_stnames
        else:
            local_stnames = inb_stnames
            remote_stnames = ()

        return local_stnames, remote_stnames

    def get_max_interval(self):
        """
        Returns the longest currently configured interval value. If all statistics are disabled,
        returns 0.
        """

        inb_max_interval = self._inbagent.get_max_interval()
        if self._oobagent:
            oob_max_interval = self._oobagent.get_max_interval()
        else:
            oob_max_interval = 0

        return max(inb_max_interval, oob_max_interval)

    def set_info_logging(self, enable):
        """Enable or disable infomrational logging messages printed with the "INFO" log level."""

        if enable:
            self._infolvl = logging.INFO
        else:
            self._infolvl = logging.DEBUG

        self._inbagent.infolvl = self._infolvl
        if self._oobagent:
            self._oobagent.infolvl = self._infolvl

    @staticmethod
    def _normalize_stnames(stnames):
        """
        Turn statistics names list in 'stnames' into python 'set', andle the special cases of
        'None' and "all", which means "all statistics".
        """

        if stnames in (None, "all"):
            stnames = set(_STCAgent.STATS_INFO) | set(_AGGR_STINFO)
        elif Trivial.is_iterable(stnames):
            stnames = set(stnames)
        else:
            raise Error(f"BUG: bad statistic names '{stnames}': provide an iterable collection")

        return stnames

    def _toggle_enabled(self, stnames, value):
        """Enabled/disable 'stnames' statistics."""

        stnames = self._normalize_stnames(stnames)
        inb_stnames, oob_stnames = self._separate_inb_vs_oob(stnames)

        for stname in inb_stnames:
            self._inbagent.stinfo[stname]["enabled"] = value
        for stname in oob_stnames:
            self._oobagent.stinfo[stname]["enabled"] = value

    def set_enabled_stats(self, stnames):
        """
        Enable statistics in 'stnames'. If 'stname' is "all" or 'None', enable all statistics.
        Note, all statistics are enabled by default when an instance of this class is created.
        """

        _LOG.debug("enabling the following statistics: %s", ", ".join(stnames))
        self._toggle_enabled(stnames, True)

    def set_disabled_stats(self, stnames):
        """Same as 'set_enabled_stats()', but for disabling."""

        _LOG.debug("disabling the following statistics: %s", ", ".join(stnames))
        self._toggle_enabled(stnames, False)

    def _get_enabled_stats_noaggr(self):
        """Implements 'get_enabled_stats()'."""

        stnames = self._inbagent.get_enabled_stats()
        if self._oobagent:
            stnames |= self._oobagent.get_enabled_stats()

        return stnames

    def get_enabled_stats(self):
        """Return a set containing all the the enabled statistic names."""
        return self._get_enabled_stats_noaggr()

    def _get_disabled_stats_noaggr(self):
        """Implements 'get_disabled_stats()'."""

        stnames = self._inbagent.get_disabled_stats()
        if self._oobagent:
            stnames |= self._oobagent.get_disabled_stats()

        return stnames

    def get_disabled_stats(self):
        """Return a set containing all the the disabled statistic names."""
        return self._get_disabled_stats_noaggr()

    def set_intervals(self, intervals):
        """
        Set intervals for statistics collectors. The 'intervals' argument should be a dictionary
        with statistics collector names as keys and the collection interval as the value. This
        method should be called prior to the 'configure()' method. By default the statistics
        collectors use intervals from the '_STCAgent.STATS_INFO' statistics description dictionary.

        Returns a dictionary similar to 'intervals', but only including enabled statistics and
        possibly rounded interval values as 'float' type.
        """

        inb_stnames, oob_stnames = self._separate_inb_vs_oob(set(intervals))

        inb_intervals = {stname: intervals[stname] for stname in inb_stnames}
        oob_intervals = {stname: intervals[stname] for stname in oob_stnames}

        intervals = self._inbagent.set_intervals(inb_intervals)
        if self._oobagent:
            intervals.update(self._oobagent.set_intervals(oob_intervals))
        return intervals

    def _get_stinfo(self, stname):
        """Get statistics description dictionary for the 'stname' statistics."""

        if stname in self._inbagent.stinfo:
            return self._inbagent.stinfo[stname]

        if self._oobagent:
            return self._oobagent.stinfo[stname]

        stnames = ", ".join(get_stnames(include_aggregate=False))
        raise Error(f"unknown statistic name '{stname}', the known names are: {stnames}")

    def get_toolpath(self, stname):
        """
        Get currently configured path to the tool collecting the 'stname' statistics. The path is on
        the same host where 'stc-agent' runs (local host for out-of-band statistics, the SUT for
        in-band statistics.
        """

        stinfo = self._get_stinfo(stname)
        return stinfo["toolpath"]

    def set_toolpath(self, stname, path):
        """
        Set path to the tool collecting the 'stname' statistics to 'path'. The path is supposed to
        be on the same host where 'stc-agent' runs (local host for out-of-band statistics, the SUT
        for in-band statistics.
        """

        stinfo = self._get_stinfo(stname)
        stinfo["toolpath"] = path

    def set_prop(self, stname, name, value):
        """Set 'stname' statistic collector's property 'name' to value 'value'."""

        stinfo = self._get_stinfo(stname)

        if name not in stinfo["props"]:
            msg = f"unknown property '{name}' for the '{stname}' statistics"
            if stinfo["props"]:
                msg += f", known properties are: {', '.join(stinfo['props'])}"
            raise Error(msg)

        stinfo["props"][name] = str(value)

    def set_stcagent_path(self, local_path=None, remote_path=None):
        """
        Configure the 'stc-agent' program path. The arguments are as follows.
          * local_path - path to the 'stc-agent' program on the local system.
          * remote_path - path to the 'stc-agent' program on the remote system.
        """

        # Please, refer to the commentaries in '__init__()' for the mapping between in-/out-of-band
        # and local/remote.
        if self._pman.is_remote:
            local_coll = self._oobagent
            remote_coll = self._inbagent
        else:
            local_coll = self._inbagent
            remote_coll = None

        if local_path:
            local_coll.set_stcagent_path(local_path)
        if remote_path and remote_coll:
            remote_coll.set_stcagent_path(remote_path)

    def _is_stcagent_needed(self, stnames):
        """Implements 'is_stcagent_needed()'."""

        # Please, refer to the commentaries in '_init_()' for the mapping between in-/out-of-band
        # and local/remote.

        local_needed, remote_needed = (False, False)
        local_stnames, remote_stnames = self._separate_local_vs_remote(stnames)

        # Note, the 'sysinfo' collector does not require the 'stc-agent' program.
        if local_stnames and list(local_stnames) != ["sysinfo"]:
            local_needed = True
        if remote_stnames:
            remote_needed = True

        return local_needed, remote_needed

    def is_stcagent_needed(self):
        """
        Check if the local and remote 'stc-agent' programs are needed to collect the currently
        enabled statistics. Returns a '(local_needed, remote_needed) tuple, where 'local_needed' is
        a boolean indicating if a local 'stc-agent' program is needed, and 'remote_needed' is a
        boolean indicating if a remote 'stc-agent' program is needed.
        """

        stnames = self._get_enabled_stats_noaggr()
        return self._is_stcagent_needed(stnames)

    def _discover(self, stnames):
        """
        Helper function for 'discover()'. Provide 'stnames' to discover a specific set of
        statistics.
        """

        inband_stnames, oob_stnames = self._separate_inb_vs_oob(stnames)
        available = self._inbagent.discover(inband_stnames)
        if self._oobagent:
            available |= self._oobagent.discover(oob_stnames)

        return available

    def _handle_conflicting_stats(self):
        """
        Some statistic collectors are mutually exclusive, for example "ipmi" and "ipmi-inband". This
        function handles situations when both collectors are requested.
        """

        if not self._oobagent:
            return

        if self._inbagent.stinfo["ipmi-inband"]["enabled"] and \
           self._oobagent.stinfo["ipmi-oob"]["enabled"]:
            # IPMI in-band and out-of-band collect the same information, but 'ipmi-oob' is
            # supposedly less intrusive.
            _LOG.log(self._infolvl, "Disabling 'ipmi-inband' statistics in favor of 'ipmi-oob'")
            self._inbagent.stinfo["ipmi-inband"]["enabled"] = False

    def configure(self):
        """
        Configure the enabled statistics collectors.

        Please, also refer to the 'Notes' in the 'discover()' method - they are relevant to
        'configure()' as well.
        """

        self._inbagent.configure()
        if self._oobagent:
            self._oobagent.configure()

        self._handle_conflicting_stats()

    def start(self):
        """Start collecting the statistics."""

        _LOG.log(self._infolvl, "Starting statistics collectors")
        self._inbagent.start()
        if self._oobagent:
            self._oobagent.start()

    def stop(self, sysinfo=True):
        """Stop collecting the statistics."""

        _LOG.log(self._infolvl, "Stopping statistics collectors")
        self._inbagent.stop(sysinfo=sysinfo)
        if self._oobagent:
            self._oobagent.stop(sysinfo=sysinfo)

    def copy_remote_data(self, include_logs=True, include_data=True):
        """
        Copy all statistics data from the 'self.remote_outdir' directory on the remote host to the
        'self.local_outdir' directory on the local host. The arguments are as follows.
          * include_logs - if 'True', include the remote 'stc-agent' logs as well.
          * include_data - if 'True', include the statistics data files as well.
        """

        if not self.remote_outdir:
            return

        exclude = None
        # We add trailing slash to the remote directory path in order to make rsync copy the
        # contents of the remote directory, but not the directory itself.
        srcpath = f"{self.remote_outdir}/"
        what = "statistics data files and logs"

        if include_logs and not include_data:
            exclude = "stats"
            what = "statistics logs"
        elif not include_logs and include_data:
            srcpath = f"{self.remote_outdir}/stats"
            what = "statistics data files"
        elif not include_logs and not include_data:
            raise Error("either statistics logs or data have to be included")

        _LOG.log(self._infolvl, "Copy %s from '%s' to '%s'",
                 what, self._pman.hostname, self.local_outdir)

        rsync_opts = "-rltD"
        if exclude:
            rsync_opts = f"{rsync_opts} --exclude '{exclude}'"

        self._pman.rsync(f"{srcpath}/", self.local_outdir, opts=rsync_opts, remotesrc=True,
                         remotedst=False)

    def __init__(self, pman, local_outdir=None, remote_outdir=None):
        """
        Initialize a class instance. The arguments are as follows.
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

        self._pman = pman
        self.local_outdir = None
        self.remote_outdir = None

        # The in-band and out-of-band statistics collector objects.
        self._inbagent = None
        self._oobagent = None

        # Log level for some of the high-level messages.
        self._infolvl = logging.DEBUG

        # Mapping between in-/out-of-band and local/remote.
        #
        # -------------------------------------------------
        # |             |     Local SUT     Remote SUT    |
        # -------------------------------------------------
        # | In-band     |     local_outdir  remote_outdir |
        # -------------------------------------------------
        # | Out-of-band |     'None'        local_outdir  |
        # -------------------------------------------------
        # * The out-of-band statistics are always collected by the local 'stc-agent' instance, so
        #   its output directory is always 'local_outdir'.
        # * However, if the SUT is the local host, the in-band 'stc-agent' output directory is in
        #   'local_outdir', and the out-of-band 'stc-agent' is not used at all, so there is no
        #   "remote output directory.

        if pman.is_remote:
            inb_outdir = remote_outdir
            oob_outdir = local_outdir
        else:
            inb_outdir = local_outdir
            oob_outdir = -1 # Just a bogus value, should not be used.

        self._inbagent = _STCAgent.InBandCollector(pman, outdir=inb_outdir)
        if pman.is_remote:
            # Do not create the out-of-band collector if 'pman' represents the local host.
            # Out-of-band collectors by definition run on a host different to the SUT.
            self._oobagent = _STCAgent.OutOfBandCollector(pman.hostname, outdir=oob_outdir)
            self.local_outdir = self._oobagent.outdir
            self.remote_outdir = self._inbagent.outdir
        else:
            self.local_outdir = self._inbagent.outdir

    def close(self):
        """Close the statistics collector."""
        ClassHelpers.close(self, close_attrs=("_oobagent", "_inbagent"), unref_attrs=("_pman",))

class StatsCollect(_StatsCollectNoAggr):
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
      8. Run 'start()' to start collecting the statistics. Supposedly after the 'start()' method is
         finished, you run a workload on the SUT.
      9. Run 'stop()' to stop collecting the statistics. You can repeat the start/stop cycles and
         re-configure the collectors between the cycles.
      10. Copy statistics and logs from the remote host to the local output directory using
          'copy_remote_data()'.
    """

    def _separate_aggr_vs_specific(self, stnames):
        """
        Splits statistics names in 'stnames' on two sets - the aggregate statistics names and the
        specific statistics names. Returns those two sets.
        """

        aggr_stnames = stnames & set(self._aggr_stinfo)
        spec_stnames = stnames & (set(self._inbagent.stinfo) | set(self._oobagent.stinfo))

        unknown_stnames = stnames - aggr_stnames - spec_stnames
        if unknown_stnames:
            unknown_stname = unknown_stnames.pop()
            known_stnames = list(self._aggr_stinfo) + list(self._inbagent.stinfo) + \
                            list(self._oobagent.stinfo)
            known_stnames = ", ".join(known_stnames)
            raise Error(f"unknown statistic name '{unknown_stname}', the known names are:\n"
                        f"  {known_stnames}")

        return aggr_stnames, spec_stnames

    def set_enabled_stats(self, stnames):
        """Same as '_StatsCollectNoAggr.set_enabled_stats()'."""

        stnames = self._normalize_stnames(stnames)
        aggr_stnames, spec_stnames = self._separate_aggr_vs_specific(stnames)

        for astname in aggr_stnames:
            self._aggr_stinfo[astname]["enabled"] = True
            super().set_enabled_stats(self._aggr_stinfo[astname]["stnames"])

        super().set_enabled_stats(spec_stnames)

        _LOG.debug("enabling the following aggregate statistics: %s", ", ".join(aggr_stnames))

    def set_disabled_stats(self, stnames):
        """Same as '_StatsCollectNoAggr.set_disabled_stats()'."""

        stnames = self._normalize_stnames(stnames)
        aggr_stnames, spec_stnames = self._separate_aggr_vs_specific(stnames)

        for astname in aggr_stnames:
            self._aggr_stinfo[astname]["enabled"] = False
            super().set_disabled_stats(self._aggr_stinfo[astname]["stnames"])

        super().set_disabled_stats(spec_stnames)

        _LOG.debug("disabling the following aggregate statistics: %s", ", ".join(aggr_stnames))

    def get_enabled_stats(self):
        """Same as '_StatsCollectNoAggr.get_enabled_stats()'."""

        stnames = super().get_enabled_stats()
        for astname, astinfo in self._aggr_stinfo.items():
            if astinfo["enabled"]:
                stnames.add(astname)
        return stnames

    def get_disabled_stats(self):
        """Same as '_StatsCollectNoAggr.get_disabled_stats()'."""

        stnames = super().get_enabled_stats()
        for astname, astinfo in self._aggr_stinfo.items():
            if not astinfo["enabled"]:
                stnames.add(astname)
        return stnames

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
        """Same as '_StatsCollectNoAggr.set_intervals()'."""

        self._reject_aggr_stnames(set(intervals), "set interval")
        super().set_intervals(intervals)

    def get_toolpath(self, stname):
        """Same as '_StatsCollectNoAggr.get_toolpath()'."""

        self._reject_aggr_stname(stname, "get tool path")
        return super().get_toolpath(stname)

    def set_toolpath(self, stname, path):
        """Same as '_StatsCollectNoAggr.set_toolpath()'."""

        self._reject_aggr_stname(stname, "set tool path")
        super().set_toolpath(stname, path)

    def set_prop(self, stname, name, value):
        """Same as '_StatsCollectNoAggr.set_prop()'."""

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
                stnames = ", ".join(get_stnames(include_aggregate=True))
                raise Error(f"unknown statistic name '{stname}', the known names are:\n  {stnames}")

        return exp_stnames

    def is_stcagent_needed(self):
        """Same as '_StatsCollectNoAggr.is_stcagent_needed()'."""

        stnames = self._expand_aggr_stnames(self.get_enabled_stats())
        return super()._is_stcagent_needed(stnames)

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

        discover_stnames = self._expand_aggr_stnames(self.get_enabled_stats())
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
        """Same as '_StatsCollectNoAggr.configure()'."""

        aggr_stnames, _ = self._separate_aggr_vs_specific(self.get_enabled_stats())

        for astname in aggr_stnames:
            astinfo = self._aggr_stinfo[astname]
            if astinfo["resolved"]:
                super().set_enabled_stats(astinfo["resolved"])
                continue

            _LOG.log(self._infolvl, "Resolving the '%s' statistic", astname)
            discovered_stnames = self._discover(astinfo["stnames"])
            if discovered_stnames:
                _LOG.log(self._infolvl, "Resolved the '%s' statistic to '%s'",
                         astname, ", ".join(discovered_stnames))
                super().set_enabled_stats(discovered_stnames)
            else:
                stnames = ", ".join(astinfo["stnames"])
                raise Error(f"cannot configure aggregate statistic '{astname}' - none of the "
                            f"following specific statistics are supported:\n  {stnames}")

        _LOG.log(self._infolvl, "Configuring the following statistics: %s",
                 ", ".join(self._get_enabled_stats_noaggr()))

        super().configure()

    def _set_aggr_stinfo_defaults(self):
        """Add default keys to the aggregate statistics description dictionary."""

        for info in self._aggr_stinfo.values():
            if "enabled" not in info:
                info["enabled"] = False
            if "resolved" not in info:
                info["resolved"] = set()

    def __init__(self, pman, local_outdir=None, remote_outdir=None):
        """Same as '_StatsCollectNoAggr.__init__()'."""

        super().__init__(pman, local_outdir=local_outdir, remote_outdir=remote_outdir)

        # Initialize the aggregate statistics dictionary.
        self._aggr_stinfo = copy.deepcopy(_AGGR_STINFO)
        self._set_aggr_stinfo_defaults()
