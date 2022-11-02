# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module provides the 'SpecStatsCollect' class, which implements specific (non-aggreagete)
statistics collection.
"""

import logging
from pepclibs.helperlibs import ClassHelpers
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs import _StatsConfig
from statscollectlibs.collector import _STCAgent

_LOG = logging.getLogger()

# The statistics description dictionary.
STINFO = _STCAgent.STINFO

def get_stnames():
    """Return all specific statistic names."""
    return list(STINFO)

def get_stinfo(stname):
    """Return information about statistic 'stname'."""

    if stname in STINFO:
        return STINFO[stname]

    stnames = ", ".join(get_stnames())
    raise Error(f"unknown statistic name '{stname}', the known names are:\n  {stnames}")

def check_stname(stname):
    """Verify that 'stname' is a known statistic name."""
    get_stinfo(stname)

def check_stnames(stnames):
    """Verify that statistics in the 'stnames' list are legit."""

    for stname in stnames:
        get_stinfo(stname)

class SpecStatsCollect(ClassHelpers.SimpleCloseContext):
    """
    This class provides API for collecting specific SUT statistics, such as 'turbostat' data and AC
    power.
    """

    def _separate_inb_vs_oob(self, stnames):
        """
        Split statistic names 'stnames' on two sets - the in-band and the out-of-band statistics.
        Return a tuple of those two sets.
        """

        avail_inb_stnames = list(self._inbagent.stinfo)
        inb_stnames = stnames & set(avail_inb_stnames)

        # The out-of-band agent is not always initialised as it is not always needed.
        if self._oobagent is not None:
            avail_oob_stnames = list(self._oobagent.stinfo)
            oob_stnames = stnames & set(avail_oob_stnames)
        else:
            avail_oob_stnames = []
            oob_stnames = set()

        unavail_stnames = stnames - inb_stnames - oob_stnames
        if unavail_stnames:
            unavail_stname = unavail_stnames.pop()
            avail_stnames = avail_inb_stnames + avail_oob_stnames
            avail_stnames = ", ".join(avail_stnames)
            raise Error(f"unavailable statistic name '{unavail_stname}', the available names are:\n"
                        f"  {avail_stnames}")

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

    def _toggle_enabled(self, stnames, value):
        """Enabled/disable 'stnames' statistics."""

        inb_stnames, oob_stnames = self._separate_inb_vs_oob(stnames)

        for stname in inb_stnames:
            self._inbagent.stinfo[stname]["enabled"] = value
        for stname in oob_stnames:
            self._oobagent.stinfo[stname]["enabled"] = value

    def set_enabled_stats(self, stnames):
        """Same as 'StatsCollect.set_enabled_stats()'."""

        if not stnames:
            return

        _LOG.debug("enabling the following statistics: %s", ", ".join(stnames))
        self._toggle_enabled(stnames, True)

    def set_disabled_stats(self, stnames):
        """Same as 'StatsCollect.set_disabled_stats()'."""

        if not stnames:
            return

        _LOG.debug("disabling the following statistics: %s", ", ".join(stnames))
        self._toggle_enabled(stnames, False)

    def _get_enabled_stats(self):
        """Implements 'get_enabled_stats()'."""

        stnames = self._inbagent.get_enabled_stats()
        if self._oobagent:
            stnames |= self._oobagent.get_enabled_stats()

        return stnames

    def get_enabled_stats(self):
        """Same as 'StatsCollect.get_enabled_stats()'."""
        return self._get_enabled_stats()

    def _get_disabled_stats(self):
        """Implements 'get_disabled_stats()'."""

        stnames = self._inbagent.get_disabled_stats()
        if self._oobagent:
            stnames |= self._oobagent.get_disabled_stats()

        return stnames

    def get_disabled_stats(self):
        """Same as 'StatsCollect.get_disabled_stats()'."""
        return self._get_disabled_stats()

    def set_intervals(self, intervals):
        """Same as 'StatsCollect.set_intervals()'."""

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

        stnames = ", ".join(get_stnames())
        raise Error(f"unknown statistic name '{stname}', the known names are: {stnames}")

    def get_toolpath(self, stname):
        """Same as 'StatsCollect.get_toolpath()'."""

        stinfo = self._get_stinfo(stname)
        return stinfo["toolpath"]

    def set_toolpath(self, stname, path):
        """Same as 'StatsCollect.set_toolpath()'."""

        stinfo = self._get_stinfo(stname)
        stinfo["toolpath"] = path

    def set_prop(self, stname, name, value):
        """Same as 'StatsCollect.set_prop()'."""

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

        stnames = self._get_enabled_stats()
        return self._is_stcagent_needed(stnames)

    def _discover(self, stnames):
        """
        Discover specific statistics in 'stnames'.
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
        """Same as 'StatsCollect.configure()'."""

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

    def _apply_cfg(self, stcagent):
        """
        Helper function for the class constructor. Applies the configuration in 'self._cfg' to
        'stcagent'.
        """

        cfg_stinfo = self._cfg.get_sut_cfg(stcagent.sutname)
        for stname, info in stcagent.stinfo.items():
            if stname not in cfg_stinfo:
                continue
            for key, val in info.items():
                if key == "props":
                    val.update(cfg_stinfo[stname].get("props", {}))
                else:
                    val = cfg_stinfo[stname].get(key, val)

    def __init__(self, pman, local_outdir=None, remote_outdir=None):
        """Same as 'StatsCollect.__init__()'."""

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

        self._cfg = _StatsConfig.StatsConfig()
        self._apply_cfg(self._inbagent)
        if self._oobagent is not None:
            self._apply_cfg(self._oobagent)

    def close(self):
        """Close the statistics collector."""
        ClassHelpers.close(self, close_attrs=("_oobagent", "_inbagent"), unref_attrs=("_pman",))
