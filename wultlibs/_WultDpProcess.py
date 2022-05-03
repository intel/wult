# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module implements the main wult functionality - runs wake latency measurement experiments and
saves the results.
"""

import time
import logging
from pepclibs import CStates
from pepclibs.helperlibs import ClassHelpers
from pepclibs.helperlibs.Exceptions import Error
from wultlibs import WultDefs
from wultlibs.helperlibs import Human

_LOG = logging.getLogger()

class DatapointProcessor:
    """
    The datapoint processor class implements raw datapoint processing. Takes raw datapoints on
    input and provides processed datapoints on output. Processing includes filtering unwanted
    datapoints, calculating C-state residency percentages, and so on.
    """

    def _warn(self, key, msg, *args):
        """Rate-limited warnings printing."""

        _LOG.debug(msg, *args)

        if key not in self._warnings:
            self._warnings[key] = {"cnt" : 0, "tprint" : time.time(), "suppressed" : 0}
            _LOG.warning(msg, *args)
            return

        winfo = self._warnings[key]
        winfo["cnt"] += 1
        ts = time.time()
        if ts - winfo["tprint"] < 1:
            winfo["suppressed"] += 1
            # Do not print the warning more often than every second.
            return

        _LOG.warning(msg, *args)
        if winfo["suppressed"]:
            _LOG.notice("suppressed %d messages like this (total %d)",
                        winfo["suppressed"], winfo["cnt"])

        winfo["tprint"] = ts
        winfo["suppressed"] = 0

    @staticmethod
    def _is_poll_idle(dp):
        """Returns 'True' if the 'dp' datapoint contains the POLL idle state data."""
        return dp["ReqCState"] == 0

    def _get_req_cstate_name(self, dp):
        """Returns requestable C-state name for datapoint 'dp'."""

        try:
            return self._csmap[dp["ReqCState"]]
        except KeyError:
            # Supposedly an bad C-state index.
            indexes_str = ", ".join(f"{idx} ({csname})" for idx, csname in  self._csmap.items())
            raise Error(f"bad C-state index '{dp['ReqCState']}' in the following datapoint:\n"
                        f"{Human.dict2str(dp)}\nAllowed indexes are:\n{indexes_str}") from None

    def _process_cstates(self, dp):
        """
        Validate various datapoint 'dp' fields related to C-states. Populate the processed
        datapoint 'dp' with fields related to C-states.
        """

        dp["ReqCState"] = self._get_req_cstate_name(dp)

        if dp["TotCyc"] == 0:
            raise Error(f"Zero total cycles ('TotCyc'), this should never happen, unless there is "
                        f"a bug. The raw datapoint is:\n{Human.dict2str(dp)}") from None

        # The driver takes TSC and MPERF counters so that the MPERF interval is inside the
        # TSC interval, so delta TSC (total cycles) is expected to be always greater than
        # delta MPERF (C0 cycles).
        if dp["TotCyc"] < dp["CC0Cyc"]:
            raise Error(f"total cycles is smaller than CC0 cycles, the raw datapoint is:\n"
                        f"{Human.dict2str(dp)}")

        # Add the C-state percentages.
        for field in self._cs_fields:
            cyc_filed = WultDefs.get_cscyc_metric(WultDefs.get_csname(field))

            # In case of POLL state, calculate only CC0%.
            if self._is_poll_idle(dp) and cyc_filed != "CC0Cyc":
                dp[field] = 0
                continue

            dp[field] = dp[cyc_filed] / dp["TotCyc"] * 100.0

            if dp[field] > 100:
                loglevel = logging.DEBUG
                # Sometimes C-state residency counters are not precise, especially during short
                # sleep times. Warn only about too large percentage.
                if dp[field] > 300:
                    loglevel = logging.WARNING

                csname = WultDefs.get_csname(field)
                _LOG.log(loglevel, "too high %s residency of %.1f%%, using 100%% instead. The "
                                   "datapoint is:\n%s", csname, dp[field], Human.dict2str(dp))
                dp[field] = 100.0

        if self._has_cstates and not self._is_poll_idle(dp):
            # Populate 'CC1Derived%' - the software-calculated CC1 residency, which is useful to
            # have because not every Intel platform has a hardware CC1 counter. Calculated as total
            # cycles minus cycles in C-states other than CC1.

            non_cc1_cyc = 0
            for field in dp.keys():
                if WultDefs.is_cscyc_metric(field) and WultDefs.get_csname(field) != "CC1":
                    non_cc1_cyc += dp[field]

            dp["CC1Derived%"] = (dp["TotCyc"] - non_cc1_cyc) / dp["TotCyc"] * 100.0
            if dp["CC1Derived%"] < 0:
                # The C-state counters are not always precise, and we may end up with a negative
                # number.
                dp["CC1Derived%"] = 0
        else:
            dp["CC1Derived%"] = 0

    def _cyc_to_ns(self, cyc):
        """Convert TSC cycles to nanoseconds."""
        return int((cyc * 1000) / self.tsc_mhz)

    def _calc_wult_igb_delays(self, dp):
        """Calculate warmup and latch delays in case of 'wult_igb' driver."""

        dp["WarmupDelay"] = self._cyc_to_ns(dp["WarmupDelayCyc"])
        dp["LatchDelay"] = self._cyc_to_ns(dp["LatchDelayCyc"])

    def _apply_time_adjustments(self, dp):
        """
        Some drivers provide adjustments for 'TAI', 'TBI', and 'TInr', for example 'wult_igb'. The
        adjustments are there for improving measurement accuracy, and they are in CPU cycles. This
        function adjusts 'SilentTime', 'WakeLatency', and 'IntrLatency' accordingly.

        This function also validates the adjusted values. Returns the datapoint in case of success
        and 'None' if the datapoint has to be dropped.
        """

        # Apply the adjustments if the driver provides them.
        if "TBIAdjCyc" in dp:
            tbi_adj = self._cyc_to_ns(dp["TBIAdjCyc"])
            dp["SilentTimeRaw"] = dp["SilentTime"]
            dp["SilentTime"] -= tbi_adj

            if dp["TBI"] + tbi_adj >= dp["LTime"]:
                _LOG.debug("adjusted 'TBI' is greater than 'LTime', the scheduled event must have "
                           "happened before the CPU entered the idle state. The datapoint is:\n%s\n"
                           "Adjusted 'TBI' is %d + %d = %d ns\nDropping this datapoint\n",
                           Human.dict2str(dp),  dp["TBI"], tbi_adj, dp["TBI"] + tbi_adj)
                return None

        if "TAIAdjCyc" in dp:
            tai_adj = self._cyc_to_ns(dp["TAIAdjCyc"])
            tintr_adj = self._cyc_to_ns(dp["TIntrAdjCyc"])

            dp["WakeLatencyRaw"] = dp["WakeLatency"]
            dp["IntrLatencyRaw"] = dp["IntrLatency"]
            dp["WakeLatency"] -= tai_adj
            dp["IntrLatency"] -= tintr_adj

            if dp["TAI"] - tai_adj <= dp["LTime"]:
                _LOG.debug("adjusted 'TAI' is smaller than 'LTime', the CPU must have woken up "
                           "before 'LTime'. The datapoint is:\n%s\n"
                           "Adjusted 'TAI' is %d - %d = %d ns\nDropping this datapoint\n",
                           Human.dict2str(dp),  dp["TAI"], tai_adj, dp["TAI"] - tai_adj)
                return None
            if dp["TIntr"] - tintr_adj <= dp["LTime"]:
                _LOG.debug("adjusted 'TIntr' is smaller than 'LTime', the CPU must have woken up "
                           "before 'LTime'. The datapoint is:\n%s\n"
                           "Adjusted 'TIntr' is %d - %d = %d ns\nDropping this datapoint\n",
                           Human.dict2str(dp),  dp["TIntr"], tintr_adj, dp["TIntr"] - tintr_adj)
                return None

        return dp

    def _check_cstate_intrs(self, dp):
        """
        Check that interrupt status, enabled or disabled, remains the same for the each C-state
        during the measurement. E.g. if the first datapoint has interrupts enabled and the requested
        C-state is C1, the following datapoints with C1 should have the interrupts enabled too.

        Raises an exception if interrupt status is different than in previous datapoints.
        """

        cstate = dp["ReqCState"]
        if cstate not in self._cstate_intrs:
            self._cstate_intrs[cstate] = dp["IntrOff"]

        if self._cstate_intrs[cstate] != dp["IntrOff"]:
            status = "disabled" if dp["IntrOff"] else "enabled"
            raise Error(f"interrupts are {status} for the datapoint, which is different from other "
                        f"observed datapoints with requested C-state '{cstate}'. The datapoint is:"
                        f"\n{Human.dict2str(dp)}\nDropping this datapoint\n") from None

    def _process_time(self, dp):
        """
        Calculate, validate, and initialize fields related to time, for example 'WakeLatency' and
        'IntrLatency'.
        """

        if self._drvname == "wult_igb":
            self._calc_wult_igb_delays(dp)

        dp["SilentTime"] = dp["LTime"] - dp["TBI"]
        if self._intr_focus:
            # We do not measure 'WakeLatency' in this case, but it is handy to have it in the
            # dictionary as '0'. We'll remove it at the end of this function.
            dp["WakeLatency"] = 0
        else:
            dp["WakeLatency"] = dp["TAI"] - dp["LTime"]
        dp["IntrLatency"] = dp["TIntr"] - dp["LTime"]

        if self._drvname == "wult_tdt":
            # In case of 'wult_tdt' driver the time is in TSC cycles, convert to nanoseconds.
            for key in ("SilentTime", "WakeLatency", "IntrLatency"):
                dp[key] = self._cyc_to_ns(dp[key])

        if not self._apply_time_adjustments(dp):
            return None

        self._check_cstate_intrs(dp)

        # Try to compensate for the overhead introduced by wult drivers.
        #
        # Some C-states are entered with interrupts enabled (e.g., POLL), and some C-states are
        # entered with interrupts disabled. This is indicated by the 'IntrOff' flag ('IntrOff ==
        # True' are the datapoints for C-states entered with interrupts disabled).
        if dp["IntrOff"]:
            # 1. When the CPU exits the C-state, it runs 'after_idle()' before the interrupt
            #    handler.
            #    1.1. If 'self._intr_focus == False', 'WakeLatency' is measured in 'after_idle()'.
            #         This introduces additional overhead, and delays the interrupt handler. This
            #         overhead can be estimated using 'AICyc1' and 'AICyc2' TSC counter snapshots.
            #    1.2. If 'self._intr_focus == True', 'WakeLatency' is not measured at all.
            # 2. The interrupt handler is executed shortly after 'after_idle()' finishes and the
            #    "cpuidle" Linux kernel subsystem re-enables CPU interrupts.

            if dp["WakeLatency"] >= dp["IntrLatency"]:
                self._warn("IntrOff_WakeLatency_GT_IntrLatency",
                           "'WakeLatency' is greater than 'IntrLatency', even though interrupts "
                           "were disabled. The datapoint is:\n%s\nDropping this datapoint\n",
                           Human.dict2str(dp))
                return None

            if self._early_intr:
                self._warn("IntrOff_early_intr",
                           "hit a datapoint with interrupts disabled even though the early "
                           "interrupts feature was enabled. The datapoint is:\n%s\n"
                           "Dropping this datapoint\n", Human.dict2str(dp))
                return None

            if self._intr_focus:
                overhead = 0
            else:
                overhead = dp["AICyc2"] - dp["AICyc1"]
            overhead = self._cyc_to_ns(overhead)

            if overhead >= dp["IntrLatency"]:
                # This sometimes happens, most probably because the overhead is measured by reading
                # TSC at the beginning and the end of the 'after_idle()' function, which runs as
                # soon as the CPU wakes up. The 'IntrLatency' is measured using a delayed event
                # device (e.g., a NIC). So we are comparing two time intervals from different time
                # sources.
                _LOG.debug("The overhead is greater than interrupt latency ('IntrLatency'). The "
                           "datapoint is:\n%s\nThe overhead is: %f\nDropping this datapoint\n",
                           Human.dict2str(dp), overhead)
                return None

            if dp["WakeLatency"] >= dp["IntrLatency"] - overhead:
                # This condition may happen for similar reasons.
                _LOG.debug("'WakeLatency' is greater than 'IntrLatency' - overhead, even though "
                           "interrupts were disabled. The datapoint is:\n%s\nThe overhead is: %f\n"
                           "Dropping this datapoint\n", Human.dict2str(dp), overhead)
                return None

            if "IntrLatencyRaw" not in dp:
                dp["IntrLatencyRaw"] = dp["IntrLatency"]
            dp["IntrLatency"] -= overhead

        if not dp["IntrOff"] and not self._intr_focus:
            # 1. When the CPU exits the C-state, it runs the interrupt handler before
            #    'after_idle()'.
            # 2. The interrupt latency is measured in the interrupt handler. This introduces
            #    additional overhead, and delays 'after_idle()'. This overhead can be estimated
            #    using 'IntrCyc1' and 'IntrCyc2' TSC counter snapshots. But if 'self._intr_focus ==
            #    True', 'WakeLatency' is not going to be measured anyway.
            # 3. 'after_idle()' is executed after the interrupt handler and measures 'WakeLatency',
            #    which is greater than 'IntrLatency' in this case.
            #
            # Bear in mind, that wult interrupt handler may be executed after interrupt handlers, in
            # case there are multiple pending interrupts. Also keep in mind that in case of
            # timer-based measurements, the generic Linux interrupt handler is executed first, and
            # wult's handler may be called after other registered handlers. In other words, there
            # may be many CPU instructions between the moment the CPU wakes up from the C-state and
            # the moment it executes wult's interrupt handler.

            if self._drvname == "wult_tdt":
                csname = self._get_req_cstate_name(dp)
                self._warn(f"tdt_{csname}_IntrOn",
                           "The %s C-state has interrupts enabled and therefore, can't be "
                           "collected with the 'tdt' driver. Use another driver for %s.",
                           csname, csname)
                _LOG.debug("dropping datapoint with interrupts enabled - the 'tdt' driver does not "
                           "handle them correctly. The datapoint is:\n%s", Human.dict2str(dp))
                return None

            if dp["IntrLatency"] >= dp["WakeLatency"]:
                self._warn("IntrON_IntrLatency_GT_WakeLatency",
                           "'IntrLatency' is greater than 'WakeLatency', even though interrupts "
                           "were enabled. The datapoint is:\n%s\nDropping this datapoint\n",
                           Human.dict2str(dp))
                return None

            if self._intr_focus:
                overhead = 0
            else:
                overhead = dp["IntrCyc2"] - dp["IntrCyc1"]
            overhead = self._cyc_to_ns(overhead)

            if overhead >= dp["WakeLatency"]:
                _LOG.debug("overhead is greater than wake latency ('WakeLatency'). The "
                           "datapoint is:\n%s\nThe overhead is: %f\nDropping this datapoint\n",
                           overhead, Human.dict2str(dp))
                return None

            if dp["IntrLatency"] >= dp["WakeLatency"] - overhead:
                _LOG.debug("'IntrLatency' is greater than 'WakeLatency' - overhead, even though "
                           "interrupts were enabled. The datapoint is:\n%s\nThe overhead is: %f\n"
                           "Dropping this datapoint\n", Human.dict2str(dp), overhead)
                return None

            if "WakeLatencyRaw" not in dp:
                dp["WakeLatencyRaw"] = dp["WakeLatency"]
            dp["WakeLatency"] -= overhead

        if self._intr_focus:
            # In case of interrupt-focused measurements we do not really measure 'WakeLatency', but
            # we add it to 'dp' in order to have less 'if' statements in the code. But now it is
            # time to delete it from 'dp'.
            if "WakeLatencyRaw" in dp:
                del dp["WakeLatencyRaw"]
            del dp["WakeLatency"]

        return dp

    def _finalize_dp(self, dp):
        """Remove extra fields from the processed data point."""

        for field in list(dp):
            if not field.endswith("Raw") and field not in self._fields:
                del dp[field]

        return dp

    def _process_datapoint(self, rawdp):
        """Process a raw datapoint 'rawdp'. Returns the processed datapoint."""

        # Avoid extra copying for efficiency.
        dp = rawdp

        # Calculate latency and other metrics providing time intervals.
        if not self._process_time(dp):
            return None

        # Add and validated C-state related fields.
        self._process_cstates(dp)

        # Some raw datapoint values are in nanoseconds, but we need them to be in microseconds.
        # Save time in microseconds.
        for field in dp:
            if field in self._us_fields_set:
                dp[field] /= 1000.0

        return self._finalize_dp(dp)

    def _calculate_tsc_rate(self, rawdp):
        """
        TSC rate is calculated using 'BICyc' and 'BIMonotinic' raw datapoint fields. These fields
        are read one after another with interrupts disabled. The former is "TSC cycles Before Idle",
        the latter stands for "Monotonic time Before Idle". The "Before Idle" part is not relevant
        here at all, it just tells that these counters were read just before the system enters an
        idle state.

        We need a couple of datapoints far enough apart in order to calculate TSC rate. This method
        is called for every datapoint, and once there are a couple of datapoints
        'self.tsc_cal_time' seconds apart, this function calculates TSC rate and stores it in
        'self.tsc_mhz'.
        """

        if self.tsc_mhz:
            # TSC rate is already known, skip the calculations.
            return

        if rawdp["SMICnt"] != 0 or rawdp["NMICnt"] != 0:
            # Do not use this datapoint, there was an SMI or NMI, and there is a chance that it
            # happened between the 'BICyc' and 'BIMonotinic' reads, which may skew our TSC rate
            # calculations.
            _LOG.debug("NMI/SMI detected, won't use the datapoint for TSC rate calculations:\n%s",
                       Human.dict2str(rawdp))
            return

        if not self._tsc1:
            # We are called for the first time.
            self._tsc1 = rawdp["BICyc"]
            self._ts1 = rawdp["BIMonotinic"]
            return

        tsc2 = rawdp["BICyc"]
        ts2 = rawdp["BIMonotinic"]

        # Bear in mind that 'ts' is in nanoseconds.
        if ts2 - self._ts1 < self.tsc_cal_time * 1000000000:
            return

        # Should not really happen, but let's be paranoid.
        if ts2 == self._ts1:
            _LOG.debug("TSC did not change, won't use the datapoint for TSC rate calculations:\n%s",
                       Human.dict2str(rawdp))
            return

        self.tsc_mhz = ((tsc2 - self._tsc1) * 1000.0) / (ts2 - self._ts1)

    def add_raw_datapoint(self, rawdp):
        """
        Process a raw datapoint 'rawdp'. The "raw" part in this context means that 'rawdp' contains
        the datapoint as the kernel driver provided it. This function processes it and returns the
        processed datapoint.

        Notice: for efficiency purposes this function does not make a copy of 'rawdp' and instead,
        uses and even modifies 'rawdp'. In other words, the caller should not use 'rawdp' after
        calling this function.
        """

        self._calculate_tsc_rate(rawdp)
        if not self.tsc_mhz:
            self._rawdps.append(rawdp)
        else:
            dp = self._process_datapoint(rawdp)
            if dp:
                self._dps.append(dp)

    def get_processed_datapoints(self):
        """
        This generator yields the processed datapoints.
        """

        if not self.tsc_mhz:
            return

        for rawdp in self._rawdps:
            dp = self._process_datapoint(rawdp)
            if dp:
                yield dp

        self._rawdps = []

        for dp in self._dps:
            yield dp

        self._dps = []

    def prepare(self, rawdp, keep_rawdp):
        """
        This helper should be called as soon as the first raw datapoint 'raw' is acquired. It
        prepared for processing datapoints by building various data structures. For example, we
        learn about the C-state names from the first datapoint.
        """

        raw_fields = list(rawdp.keys())

        defs = WultDefs.WultDefs(raw_fields)

        self._cs_fields = []
        self._has_cstates = False

        for field in raw_fields:
            csname = WultDefs.get_csname(field, must_get=False)
            if not csname:
                # Not a C-state field.
                continue
            self._has_cstates = True
            self._cs_fields.append(WultDefs.get_csres_metric(csname))

        self._us_fields_set = {field for field, vals in defs.info.items() \
                               if vals.get("unit") == "microsecond"}

        # Form the preliminary list of fields in processed datapoints. Fields from the "defs" file
        # go first. The list (but we use dictionary in this case) will be amended later.
        self._fields = {}
        for field in defs.info:
            self._fields[field] = None

        if keep_rawdp:
            for field in raw_fields:
                self._fields[field] = None

    def _build_csmap(self, rcsobj):
        """
        Wult driver supplies the requested C-state index. Build a dictionary mapping the index to
        C-state name.
        """

        close = False
        try:
            if rcsobj is None:
                rcsobj = CStates.ReqCStates(pman=self._pman)
                close = True
            csinfo = rcsobj.get_cpu_cstates_info(self._cpunum)
        finally:
            if close:
                rcsobj.close()

        # Check that there are idle states that we can measure.
        for info in csinfo.values():
            if not info["disable"]:
                break
        else:
            raise Error(f"no idle states are enabled on CPU {self._cpunum}{self._pman.hostmsg}")

        self._csmap = {}
        for csname, cstate in csinfo.items():
            self._csmap[cstate["index"]] = csname

    def __init__(self, cpunum, pman, drvname, intr_focus=None, early_intr=None, tsc_cal_time=10,
                 rcsobj=None):
        """
        The class constructor. The arguments are as follows.
          * cpunum - the measured CPU number.
          * pman - the process manager object that defines the host to run the measurements on.
          * drvname - name of the driver providing the datapoints
          * intr_focus - enable interrupt latency focused measurements ('WakeLatency' is not
          *              measured in this case, only 'IntrLatency').
          * early_intr - enable interrupts before entering the C-state.
          * tsc_cal_time - amount of seconds to use for calculating TSC rate.
          * rcsobj - the 'CStates' object initialized for the measured system.
        """

        self._cpunum = cpunum
        self._pman = pman
        self._drvname = drvname
        self._intr_focus = intr_focus
        self._early_intr = early_intr
        self.tsc_cal_time = tsc_cal_time

        # Processed datapoint field names.
        self._fields = None
        # Interrupt status of observed C-states.
        self._cstate_intrs = {}
        # C-state index -> name mapping.
        self._csmap = None
        # TSC rate in MHz (cycles / microsecond).
        self.tsc_mhz = None

        # The driver provides TSC cycles and monotonic time (nanoseconds) which are read one after
        # the other with interrupts disabled. We use them for calculating the TSC rate. The 'tsc1'
        # and 'ts1' are the TSC cycles / monotonic time values from the very first datapoint.
        self._tsc1 = None
        self._ts1 = None

        self._dps = []
        self._rawdps = []
        self._has_cstates = None
        self._cs_fields = None
        self._us_fields_set = None

        # Information about printed warnings.
        self._warnings = {}

        self._build_csmap(rcsobj)

    def close(self):
        """Close the datapoint processor."""
        ClassHelpers.close(self, unref_attrs=("_pman",))

    def __enter__(self):
        """Enter the run-time context."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the runtime context."""
        self.close()
