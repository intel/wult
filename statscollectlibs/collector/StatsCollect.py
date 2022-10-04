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

import logging
from pepclibs.helperlibs import ClassHelpers
from pepclibs.helperlibs.Exceptions import Error, ErrorNotFound
from statscollectlibs.collector import _Collector
from statscollectlibs.collector._Collector import DEFAULT_STINFO

_LOG = logging.getLogger()

def _check_stname(stname):
    """Verify that 'stname' is a known statistic name."""

    if stname not in DEFAULT_STINFO:
        avail_stnames = ", ".join(DEFAULT_STINFO)
        raise Error(f"unknown statistic name '{stname}', the known names are: {avail_stnames}")

def _check_stnames(stnames):
    """Verify that statistics in the 'stnames' list are legit."""

    for stname in stnames:
        _check_stname(stname)

def _separate_inb_vs_oob(stnames):
    """
    Splits the list of statistics names 'stnames' on two sets - the in-band and the out-of-band
    statistics. Returns a tuple of those two sets.
    """

    inb_stnames = set()
    oob_stnames = set()
    for stname in stnames:
        _check_stname(stname)

        if DEFAULT_STINFO[stname]["inband"]:
            inb_stnames.add(stname)
        else:
            oob_stnames.add(stname)

    return (inb_stnames, oob_stnames)

class StatsCollect(ClassHelpers.SimpleCloseContext):
    """
    This class provides API for collecting SUT statistics, such as 'turbostat' data and AC power.

    The usage model of this class is as follows.
      1. Create an object. This will run 'stc-agent' on the SUT (in-band statistics collection) and
         the local host (out-of-band collection). 'stc-agent' is just an agent that listens for
         commands on a Unix socket. The commands are like "start collecting", "stop collecting",
         "set properties", etc. 'stc-agent' runs various collectors.

         Example of "in-band" collectors: acpower, ipmi-inband. These tools run on the local system,
         but collect information about the remote system.
      2. Optionally set the list of statistics collectors that are going to be used by running the
         'set_disabled_stats()', 'set_enabled_stats()'.
      3. Optionally set tool path and properties for certain statistics using 'set_prop()' and
         'set_toolpath()'.
      4. Optionally set the 'stc-agent' paths on the local and remote systems. By default the
         'stc-agent' program is looked for in the paths from the 'PATH' environment variable.

         Note: up to this point, the 'stc-agent' processes have not been started. The configuration
         passed via the 'set_*()' methods was not yet communicated to 'stc-agent'. But it will be
         sent to 'stc-agent' as soon as it starts. And it starts when 'discover()' or 'configure()'
         methods are called.

      5. Optionally discover the available statistics by running the 'discover()' method. Once the
         discovery is finished, re-run 'set_enabled_stats()' to enable the discovered statistics.
      6. Run the 'configure()' method to configure the statistics collectors.
      7. Run 'start()' to start collecting the statistics. Supposedly after the 'start()' method is
         finished, you run a workload on the SUT.
      8. Run 'stop()' to stop collecting the statistics. You can repeat the start/stop cycles and
         re-configure the collectors between the cycles.
      9. Copy statistics and logs from the remote host to the local output directory using
         'copy_remote_data()'.
    """

    def get_max_interval(self):
        """
        Returns the longest currently configured interval value. If all statistics are disabled,
        returns 0.
        """

        inb_max_interval = _Collector.get_max_interval(self._inbcoll.stinfo)
        if self._oobcoll:
            oob_max_interval = _Collector.get_max_interval(self._oobcoll.stinfo)
        else:
            oob_max_interval = 0

        return max(inb_max_interval, oob_max_interval)

    def _toggle_enabled(self, stnames, value):
        """Enabled/disable 'stnames' statistics."""

        if stnames in (None, "all"):
            stnames = list(DEFAULT_STINFO)

        _check_stnames(stnames)
        inb_stnames, oob_stnames = _separate_inb_vs_oob(stnames)

        for stname in inb_stnames:
            self._inbcoll.stinfo[stname]["enabled"] = value
        for stname in oob_stnames:
            self._oobcoll.stinfo[stname]["enabled"] = value

    def set_enabled_stats(self, stnames):
        """
        Enable statistics in 'stnames'. If 'stname' is "all" or 'None', enable all statistics.

        Note, all statistics are enabled by default when an instance of this class is created.
        """

        self._toggle_enabled(stnames, True)

    def set_disabled_stats(self, stnames):
        """Same as 'set_enabled_stats()', but for disabling."""

        self._toggle_enabled(stnames, False)

    def get_enabled_stats(self):
        """Return the list of enabled statistic names."""

        stnames = self._inbcoll.get_enabled_stats()
        if self._oobcoll:
            stnames |= self._oobcoll.get_enabled_stats()

        return stnames

    def _handle_conflicting_stats(self):
        """
        Some statistic collectors are mutually exclusive, for example "ipmi" and "ipmi-inband". This
        function handles situations when both collectors are requested.
        """

        if not self._oobcoll:
            return

        if self._inbcoll.stinfo["ipmi-inband"]["enabled"] and \
           self._oobcoll.stinfo["ipmi-oob"]["enabled"]:
            # IPMI in-band and out-of-band collect the same information, but 'ipmi-oob' is
            # supposedly less intrusive.
            _LOG.info("Disabling 'ipmi-inband' statistics in favor of 'ipmi-oob'")
            self._inbcoll.stinfo["ipmi-inband"]["enabled"] = False

    def set_intervals(self, intervals):
        """
        Set intervals for statistics collectors. The 'intervals' argument should be a dictionary
        with statistics collector names as keys and the collection interval as the value. This
        method should be called prior to the 'configure()' method. By default the statistics
        collectors use intervals from the 'DEFAULT_STINFO' statistics description dictionary.

        Returns a dictionary similar to 'intervals', but only including enabled statistics and
        possibly rounded interval values as 'float' type.
        """

        _check_stnames(intervals.keys())
        inb_stnames, oob_stnames = _separate_inb_vs_oob(intervals.keys())

        inb_intervals = {stname: intervals[stname] for stname in inb_stnames}
        oob_intervals = {stname: intervals[stname] for stname in oob_stnames}

        intervals = self._inbcoll.set_intervals(inb_intervals)
        if self._oobcoll:
            intervals.update(self._oobcoll.set_intervals(oob_intervals))
        return intervals

    def _get_stinfo(self, stname):
        """Get statistics description dictionary for the 'stname' statistics."""

        if stname in self._inbcoll.stinfo:
            return self._inbcoll.stinfo[stname]

        if self._oobcoll:
            return self._oobcoll.stinfo[stname]

        raise ErrorNotFound(f"statistics '{stname}' is not available")

    def get_toolpath(self, stname):
        """
        Get currently configured path to the tool collecting the 'stname' statistics. The path is on
        the same host where 'stc-agent' runs (local host for out-of-band statistics, the SUT for
        in-band statistics.
        """

        _check_stname(stname)

        stinfo = self._get_stinfo(stname)
        return stinfo["toolpath"]

    def set_toolpath(self, stname, path):
        """
        Set path to the tool collecting the 'stname' statistics to 'path'. The path is supposed to
        be on the same host where 'stc-agent' runs (local host for out-of-band statistics, the SUT
        for in-band statistics.
        """

        _check_stname(stname)

        stinfo = self._get_stinfo(stname)
        stinfo["toolpath"] = path

    def set_prop(self, stname, name, value):
        """Set 'stname' statistic collector's property 'name' to value 'value'."""

        _check_stname(stname)

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
            local_coll = self._oobcoll
            remote_coll = self._inbcoll
        else:
            local_coll = self._inbcoll
            remote_coll = None

        if local_path:
            local_coll.set_stcagent_path(local_path)
        if remote_path and remote_coll:
            remote_coll.set_stcagent_path(remote_path)

    def discover(self):
        """
        Discover and return set of statistics that can be collected for SUT. This method probes all
        non-disabled statistics collectors.

        Notes.

        Prior to calling this method, you can (but do not have to) use the following methods.
         * 'set_disabled_stats()' and 'set_enabled_stats()' prior to to enable/disable certain
            statistics.
         * 'set_intervals()' - to configure the statistics collectors' intervals.
         * 'set_prop()' - to configure statistics collectors' properties.
         * 'set_toolpath()' - to configure statistics collectors' tools paths.

        These methods will not communicate to the 'stc-agent' process(es), which may not even have
        been started yet. They just save the configuration in an internal dictionary. The
        'discover()' method will start the 'stc-agent' process(es) and pass all the saved
        configuration to them.
        """

        stnames = self._inbcoll.discover()
        if self._oobcoll:
            stnames |= self._oobcoll.discover()
        return stnames

    def configure(self, discover=False, must_have=None):
        """
        Configure the statistics collectors. The arguments are as follows.
          * discover - if 'True', run the discovery process for all the enabled statistics, and
                       disable those that can't be collected. Otherwise, do not run discovery and
                       just configure all the enabled statistics.
          * must_have - list of statistics names that must be configured. If at the end of the
                        'configure()' method any of the 'must_have' statistics is disable, this
                        method raises and exception. By default, the 'must_have' list is empty.

        Note, if 'discover' is 'False', then this method will fail if any of the enabled statistics
        cannot be configured.

        Please, also refer to the 'Notes' in the 'discover()' method - they are relevant to
        'configure()' as well.
        """

        self._handle_conflicting_stats()

        inb_must_have = oob_must_have = None
        if must_have:
            inb_must_have, oob_must_have = _separate_inb_vs_oob(must_have)

        self._inbcoll.configure(discover=discover, must_have=inb_must_have)
        if self._oobcoll:
            self._oobcoll.configure(discover=discover, must_have=oob_must_have)

    def start(self):
        """Start collecting the statistics."""

        self._inbcoll.start()
        if self._oobcoll:
            self._oobcoll.start()

    def stop(self, sysinfo=True):
        """Stop collecting the statistics."""

        self._inbcoll.stop(sysinfo=sysinfo)
        if self._oobcoll:
            self._oobcoll.stop(sysinfo=sysinfo)

    def copy_remote_data(self):
        """
        If there are statistics collected on the remote host in 'self.remote_outdir', copy them over
        to 'self.local_outdir'. This will also include 'stc-agent' logs.
        """

        if not self.remote_outdir:
            return

        _LOG.debug("copy statistics from '%s:%s' to '%s'",
                   self._pman.hostname, self.remote_outdir, self.local_outdir)

        # We add trailing slash to the remote directory path in order to make rsync copy the
        # contents of the remote directory, but not the directory itself.
        self._pman.rsync(f"{self.remote_outdir}/", self.local_outdir, opts="rltD",
                         remotesrc=True, remotedst=False)

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
        self._inbcoll = None
        self._oobcoll = None

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

        self._inbcoll = _Collector.InBandCollector(pman, outdir=inb_outdir)
        if pman.is_remote:
            # Do not create the out-of-band collector if 'pman' represents the local host.
            # Out-of-band collectors by definition run on a host different to the SUT.
            self._oobcoll = _Collector.OutOfBandCollector(pman.hostname, outdir=oob_outdir)
            self.local_outdir = self._oobcoll.outdir
            self.remote_outdir = self._inbcoll.outdir
        else:
            self.local_outdir = self._inbcoll.outdir

    def close(self):
        """Close the statistics collector."""
        ClassHelpers.close(self, close_attrs=("_oobcoll", "_inbcoll"), unref_attrs=("_pman",))
