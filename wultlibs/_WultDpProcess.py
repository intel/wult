# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module provides the 'DatapointProcessor' class which implements raw datapoint processing.

Terminology:
  * Raw datapoint - a datapoint as provided by the driver, before the user-space processing.
  * Processed datapoint - a datapoint after the user-space processing: the final metrics are
                          calculated, and unneeded raw fields are removed (unless 'keep_rawdp').
  * Discarded datapoint - a datapoint that fails the user-space processing checks, for example
                          because the timing is inconsistent. It is never yielded.
  * Dropped datapoint - a datapoint the driver considers invalid and would drop, but sends for
                        debugging purposes. The datapoint has one of the 'Drop*' metrics set to
                        'True'.
  * Accepted datapoint - the opposite of the dropped datapoint: all the 'Drop*' metrics are 'False'.
"""

import collections
from pepclibs import CPUIdle
from pepclibs.helperlibs import Logging, ClassHelpers
from pepclibs.helperlibs.Exceptions import Error
from wultlibs import WultMDC
from wultlibs.helperlibs import Human

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.wult.{__name__}")

# Consecutive datapoints contradicting the decided interrupt order of a C-state, after which the
# C-state is considered inconsistent.
_INTR_NOISE_MAX = 100

# Consecutive "off" datapoints (the interrupt handler did not run before 'after_idle()'), without
# any "on" datapoint, after which a C-state is decided to be requested with interrupts disabled.
_INTR_OFF_CONFIRM = 10

# Datapoint fields that the driver sets to 'True' for dropped datapoints.
_DROP_FIELDS = ("DropNoIdle", "DropEarlyWake", "DropLateIdle", "DropEarlyIntr")
# Debug metrics, saved only with 'keep_rawdp'.
_DEBUG_FIELDS = ("IdleCnt", "PrevTAI") + _DROP_FIELDS

def _is_dropped(dp):
    """Return 'True' if 'dp' is a dropped datapoint."""

    return any(dp.get(key) for key in _DROP_FIELDS)

class _CStates(ClassHelpers.SimpleCloseContext):
    """
    This is an internal class used only by the 'DatapointProcessor'. This class encapsulates all the
    complexity related to C-states.
    """

    def _init_idx2name(self):
        """
        Raw datapoints include C-state indexes, but no C-state names. Build a dictionary mapping
        indices to names.
        """

        # Check that there are idle states that we can measure.
        for info in self._rcsinfo.values():
            if not info["disable"]:
                break
        else:
            raise Error(f"no idle states are enabled on CPU {self._cpu}{self._pman.hostmsg}")

        for csname, cstate in self._rcsinfo.items():
            self._idx2name[cstate["index"]] = csname

    def get_req_cstate_name(self, rawdp):
        """Returns requestable C-state name for raw datapoint 'rawdp'."""

        try:
            return self._idx2name[rawdp["ReqCState"]]
        except KeyError:
            # Supposedly an bad C-state index.
            idx2name_str = ", ".join(f"{idx} ({name})" for idx, name in self._idx2name.items())
            raise Error(f"bad C-state index '{rawdp['ReqCState']}' in the following datapoint:\n"
                        f"{Human.dict2str(rawdp)}\nAllowed indexes are:\n{idx2name_str}") from None

    @staticmethod
    def _check_rawdp_timing(rawdp):
        """
        Checks if raw datapoint timing is consistent with C-state IRQ order. Returns 'rawdp' if the
        timing is all right, returns 'None' otherwise.
        """

        if rawdp["IntrOff"]:
            if rawdp["AITS2"] > rawdp["IntrTS1"]:
                _LOG.debug("'AITS2' > 'IntrTS1', even though interrupts were disabled.\n"
                           "Dropping the following datapoint\n%s", Human.dict2str(rawdp))
                return None
        else:
            if rawdp["IntrTS2"] > rawdp["AITS1"]:
                _LOG.debug("'IntrTS2' > 'AITS1', even though interrupts were enabled.\n"
                           "Dropping the following datapoint\n%s", Human.dict2str(rawdp))
                return None

        return rawdp

    def add_raw_datapoint(self, rawdp):
        """
        Add a raw datapoint 'rawdp' and use it for detecting interrupt order. The datapoint is
        yielded by 'get_raw_datapoint()' if the interrupt order of its C-state is decided by then,
        and discarded otherwise.

        About requestable C-states interrupt order. Most C-states are requested with local CPU
        interrupts disabled. This means that when the event armed by 'wult' happens, the CPU exits
        the C-state, and continues executing instructions after 'mwait'. The CPU will run some
        housekeeping code in the "cpuidle" Linux subsystem, and then interrupts are re-enabled, and
        CPU jumps to the interrupt handler. In wult terms, we say that 'after_idle()' happens before
        the interrupt handler.

        Some C-states, however, are requested with interrupts enabled. For example, 'POLL' and C1 on
        some platforms. In this case, when CPU exits the C-state, it jumps to the interrupt handler
        right away, runs it first, and then returns to after 'mwait' to continue executing the
        'cpuidle' code. In wult terms, we say that interrupt handler runs before 'after_idle()'.

        For every possible requestable C-state, wult must know whether it is requested with
        interrupts enabled or disabled. This information is crucial for correct latency
        calculations. However, there is no easy way to figure this out. We just have to analyze
        datapoints and check what happened first: the interrupt handler or 'after_idle()'.

        The complication here is that when interrupts are enabled, the interrupt handler is not
        guaranteed to happen earlier than 'after_idle()'. In some cases, when the CPU was woken up
        by a non-interrupt event (e.g., because the Linux scheduler woke us up by writing to the
        memory address monitored by the 'mwait' instruction), 'after_idle()' happens first. And if
        this non-interrupt event happened just before wult interrupt, the interrupt handler may run
        right after 'after_idle()'. So it may look like the CPU woke up because of a wult event, and
        'after_idle()' ran before the interrupt handler.

        To overcome this complication, use the asymmetry: the interrupt handler can run before
        'after_idle()' only if the C-state is requested with interrupts enabled. Call a datapoint
        "on" if the interrupt handler ran before 'after_idle()', and "off" otherwise. A single
        "on" datapoint proves that interrupts are enabled. "Off" datapoints prove nothing, but
        noise is rare, so '_INTR_OFF_CONFIRM' "off" datapoints in a row, without any "on" datapoint,
        are taken as evidence that interrupts are disabled.

        Until the interrupt order of a C-state is decided, its datapoints are discarded. This
        loses fewer than '_INTR_OFF_CONFIRM' datapoints per C-state, but keeps the datapoint order
        and does not hold back datapoints of other C-states. The decision is final, so the output
        never has datapoints with different interrupt orders for the same C-state. Datapoints
        contradicting the decision are discarded as noise. If '_INTR_NOISE_MAX' of them come in a
        row, the decision was wrong, and an error is raised. Dropped datapoints are not used for
        detecting the interrupt order.

        The actions depending on the decision and on the added datapoint:

          Decided  Observed  Action
          -------  --------  ----------------------------------------------------------
          none     on        Decide "on", accept.
          none     off       Discard, decide "off" and accept after '_INTR_OFF_CONFIRM' in a row.
          on       on        Accept.
          on       off       Discard as noise, fail after '_INTR_NOISE_MAX' in a row.
          off      off       Accept.
          off      on        Discard as noise, fail after '_INTR_NOISE_MAX' in a row.
        """

        csname = rawdp["ReqCState"] = self.get_req_cstate_name(rawdp)

        # The 'POLL' state is always requested with interrupts enabled.
        if csname != "POLL" and not _is_dropped(rawdp):
            self._update_intr_order(csname, rawdp["TIntr"] < rawdp["TAI"])

        self._queue.append(rawdp)

    def get_raw_datapoint(self):
        """
        This generator yields the raw datapoints saved by 'add_raw_datapoint()', in the order they
        were added. The 'IntrOff' field is set, and the datapoints of C-states with undecided
        interrupt order and the datapoints failing the timing check are discarded. Dropped
        datapoints skip the timing check.
        """

        while self._queue:
            rawdp = self._queue.popleft()
            csname = rawdp["ReqCState"]

            if csname == "POLL":
                rawdp["IntrOff"] = False
                yield rawdp
                continue

            if csname not in self._introff:
                continue

            rawdp["IntrOff"] = self._introff[csname]
            if _is_dropped(rawdp) or self._check_rawdp_timing(rawdp):
                yield rawdp

    def _decide(self, csname, intr_off):
        """Decide that C-state 'csname' is requested with interrupts disabled if 'intr_off'."""

        self._introff[csname] = intr_off
        self._noise_cnt[csname] = 0
        _LOG.debug("interrupt order for %s: requested with interrupts %s",
                   csname, "disabled" if intr_off else "enabled")

    def _update_intr_order(self, csname, intr_on):
        """
        Update and verify the interrupt order of C-state 'csname' using a datapoint where the
        interrupt handler ran first if 'intr_on' is 'True'.
        """

        introff = self._introff.get(csname)

        if introff is None:
            if intr_on:
                self._decide(csname, False)
                return

            self._off_cnt[csname] = self._off_cnt.get(csname, 0) + 1
            if self._off_cnt[csname] >= _INTR_OFF_CONFIRM:
                self._decide(csname, True)
            return

        if intr_on != introff:
            # The datapoint is consistent with the decided interrupt order.
            self._noise_cnt[csname] = 0
            return

        self._noise_cnt[csname] += 1
        if self._noise_cnt[csname] >= _INTR_NOISE_MAX:
            state = "disabled" if introff else "enabled"
            raise Error(f"inconsistent interrupt order for the {csname} requestable C-state: it "
                        f"was decided to be requested with interrupts {state}, but the last "
                        f"{_INTR_NOISE_MAX} datapoints show the opposite order of the interrupt "
                        f"handler and 'after_idle()'")

    def __init__(self, cpu, pman, cpuidle=None):
        """
        The class constructor. The arguments are as follows.
          * cpu - the measured CPU number.
          * pman - the process manager object that defines the host to run the measurements on.
          * cpuidle - the 'CPUIdle.CPUIdle()' object initialized for the measured system.
        """

        self._cpu = cpu
        self._pman = pman
        self._cpuidle = cpuidle

        self._close_cpuidle = cpuidle is None

        # C-states information provided by 'CPUIdle.CPUIdle()'
        self._rcsinfo = None
        # C-state index -> C-state name dictionary..
        self._idx2name = {}

        # Count of consecutive "off" datapoints for C-states with undecided interrupt order.
        # Dictionary keys are C-state names.
        self._off_cnt = {}
        # Count of consecutive datapoints contradicting the decided interrupt order. Dictionary
        # keys are C-state names.
        self._noise_cnt = {}
        # Interrupt status of requestable C-states with decided interrupt order. Dictionary keys are
        # C-state names, the values are:
        #   * 'True' if the C-state is requested with interrupts disabled.
        #   * 'False' if the C-state is requested with interrupts enabled.
        self._introff = {}
        # Raw datapoints waiting for the interrupt order decision, in the order they were added.
        self._queue = collections.deque()

        if not self._cpuidle:
            self._cpuidle = CPUIdle.CPUIdle(pman=self._pman)

        self._rcsinfo = self._cpuidle.get_cpu_cstates_info(self._cpu)

        self._init_idx2name()

    def close(self):
        """Uninitialize and close the object."""
        ClassHelpers.close(self, close_attrs=("_cpuidle",), unref_attrs=("_pman", "_rcsinfo"))

class _TSCRate:
    """
    This is an internal class used only by the 'DatapointProcessor'. This class encapsulates
    all the complexity related to TSC rate calculation.
    """

    def _calculate_tsc_rate(self, rawdp):
        """
        TSC rate is calculated using 'BICyc' and 'BIMonotonic' raw datapoint fields. These fields
        are read one after another with interrupts disabled. The former is "TSC cycles Before Idle",
        the latter stands for "Monotonic time Before Idle". The "Before Idle" part is not relevant
        here at all, it just tells that these counters were read just before the system enters an
        idle state.

        We need a couple of datapoints far enough apart in order to calculate TSC rate. This method
        is called for every datapoint, and once there are a couple of datapoints
        'self._tsc_cal_time' seconds apart, this function calculates TSC rate and stores it in
        'self.tsc_mhz'.
        """

        if rawdp["SMICnt"] != 0 or rawdp["NMICnt"] != 0:
            # Do not use this datapoint, there was an SMI or NMI, and there is a chance that it
            # happened between the 'BICyc' and 'BIMonotonic' reads, which may skew our TSC rate
            # calculations.
            _LOG.debug("NMI/SMI detected, won't use the datapoint for TSC rate calculations:\n%s",
                       Human.dict2str(rawdp))
            return

        if not self._tsc1:
            # We are called for the first time.
            self._tsc1 = rawdp["BICyc"]
            self._ts1 = rawdp["BIMonotonic"]
            _LOG.info("Calculating TSC rate for %s", Human.duration(self._tsc_cal_time))
            return

        tsc2 = rawdp["BICyc"]
        ts2 = rawdp["BIMonotonic"]

        # Bear in mind that 'ts' is in nanoseconds.
        if ts2 - self._ts1 < self._tsc_cal_time * 1000000000:
            return

        # Should not really happen, but let's be paranoid.
        if ts2 == self._ts1:
            _LOG.debug("TSC did not change, won't use the datapoint for TSC rate calculations:\n%s",
                       Human.dict2str(rawdp))
            return

        self.tsc_mhz = ((tsc2 - self._tsc1) * 1000.0) / (ts2 - self._ts1)
        _LOG.info("TSC rate is %.6f MHz", self.tsc_mhz)

    def add_raw_datapoint(self, rawdp):
        """
        Add a raw datapoint 'rawdp' and use it for calculating TSC rate. The datapoint is held back
        in a queue, and 'get_raw_datapoint()' yields it, in the order the datapoints were added, as
        soon as the TSC rate is known.

        The idea here is that we need to collect raw datapoints for 'self._tsc_cal_time' seconds,
        and hold them on. After 'self._tsc_cal_time' seconds worth of datapoints are available, we
        can calculate TSC rate. Then the TSC rate can be used for processing the datapoints that we
        held and for new datapoints.
        """

        # Dropped datapoints may have zero 'BICyc' and 'BIMonotonic'.
        if not self.tsc_mhz and not _is_dropped(rawdp):
            self._calculate_tsc_rate(rawdp)

        self._rawdps.append(rawdp)

    def get_raw_datapoint(self):
        """
        This generator yields the raw datapoints saved by 'add_raw_datapoint()', in the order they
        were added, when TSC rate has been calculated.
        """

        if self.tsc_mhz:
            for rawdp in self._rawdps:
                yield rawdp
            self._rawdps = []

    def cyc_to_ns(self, cyc):
        """Convert TSC cycles to nanoseconds."""

        return int((cyc * 1000) / self.tsc_mhz)

    def __init__(self, tsc_cal_time):
        """
        The class constructor. The arguments are as follows.
          * tsc_cal_time - amount of seconds to use for calculating TSC rate.
        """

        self._tsc_cal_time = tsc_cal_time

        # TSC rate in MHz (cycles / microsecond).
        self.tsc_mhz = None

        # The driver provides TSC cycles and monotonic time (nanoseconds) which are read one after
        # the other with interrupts disabled. We use them for calculating the TSC rate. The 'tsc1'
        # and 'ts1' are the TSC cycles / monotonic time values from the very first datapoint.
        self._tsc1 = None
        self._ts1 = None

        self._rawdps = []

class DatapointProcessor(ClassHelpers.SimpleCloseContext):
    """
    The datapoint processor class implements raw datapoint processing. Takes raw datapoints on
    input and provides processed datapoints on output. Processing includes filtering unwanted
    datapoints, calculating C-state residency percentages, and so on.
    """

    @staticmethod
    def _is_poll_idle(dp):
        """Returns 'True' if the 'dp' datapoint contains the POLL idle state data."""
        return dp["ReqCState"] == "POLL"

    @staticmethod
    def _filter_out_noise(dp):
        """
        The unrelated interrupts before the expected delayed event are considered to be "noise".
        Filter the datapoint with noise.

        Returns the datapopint if there was no "noise", returns 'None' otherwise.

        The method does not filter out datapoints with SMIs and let's upper layers decide whether to
        keep them or not.
        """

        if dp.get("NMICnt", 0) > 0:
            return None
        if dp.get("SWIRQCnt", 0) > 0:
            return None

        return dp

    def _process_cstates(self, dp):
        """
        Validate various datapoint 'dp' fields related to C-states. Populate the processed
        datapoint 'dp' with fields related to C-states.
        """

        if dp["TotCyc"] == 0:
            raise Error(f"Zero total cycles ('TotCyc'), this should never happen, unless there is "
                        f"a bug. The raw datapoint is:\n{Human.dict2str(dp)}") from None

        # The driver takes TSC and MPERF counters so that the MPERF interval is inside the
        # TSC interval, so delta TSC (total cycles) is expected to be always greater than
        # delta MPERF (C0 cycles).
        #
        # However, we observed that on some platforms we still get smaller total cycles, and we do
        # not know why. May be this is related to instructions re-ordering. This is why we only
        # warn, instead of raising an error.
        if dp["TotCyc"] < dp["CC0Cyc"]:
            msg = f"total cycles is smaller than CC0 cycles for the following datapoint:\n" \
                  f"{Human.dict2str(dp)}\nWe are not sure why this happens, but we observed " \
                  f"this on non-server platforms.\nThis and all the other datapoints like this " \
                  f"will be dropped"
            _LOG.debug(msg)
            _LOG.warn_once(msg)

        # Add the C-state percentages.
        for field in self._cs_fields:
            cyc_field = WultMDC.get_cscyc_metric(WultMDC.get_csname(field))

            # In case of POLL state, calculate only CC0%.
            if self._is_poll_idle(dp) and cyc_field != "CC0Cyc":
                dp[field] = 0
                continue

            dp[field] = dp[cyc_field] / dp["TotCyc"] * 100.0

            if dp[field] > 100:
                csname = WultMDC.get_csname(field)
                msg = f"too high '{csname}' C-state residency of {dp[field]:.1f}% for the " \
                      f"following datapoint:\n{Human.dict2str(dp)}"

                # Sometimes C-state residency counters are not precise, especially during short
                # sleep times. Warn only about too large percentage.
                if dp[field] < 300:
                    msg = f"{msg}\nAdjusting the residency to 100% for this and all other " \
                          f"datapoints with {csname} residency greater than 100%, but smaller " \
                          f"than 300%."
                    _LOG.debug(msg)
                    _LOG.warn_once(msg)
                    dp[field] = 100.0
                else:
                    msg = f"{msg}\nDropping this and all other datapoints with {csname} " \
                          f"residency greater than 300%"
                    _LOG.debug(msg)
                    _LOG.warn_once(msg)
                    return None

        if self._has_cstates and not self._is_poll_idle(dp):
            # Populate 'CC1Derived%' - the software-calculated CC1 residency, which is useful to
            # have because not every Intel platform has a hardware CC1 counter. Calculated as total
            # cycles minus cycles in C-states other than CC1.

            non_cc1_cyc = 0
            for field in dp.keys():
                if WultMDC.is_cscyc_metric(field) and WultMDC.get_csname(field) != "CC1":
                    non_cc1_cyc += dp[field]

            dp["CC1Derived%"] = (dp["TotCyc"] - non_cc1_cyc) / dp["TotCyc"] * 100.0
            if dp["CC1Derived%"] < 0:
                # The C-state counters are not always precise, and we may end up with a negative
                # number.
                dp["CC1Derived%"] = 0
        else:
            dp["CC1Derived%"] = 0

        return dp

    @staticmethod
    def _apply_time_adjustments(dp):
        """
        Some drivers provide adjustments for 'TAI', 'TBI', and 'TInr', for example 'wult_igb'. The
        adjustments are there for improving measurement accuracy, and they are in nanoseconds. This
        function adjusts 'SilentTime', 'WakeLatency', and 'IntrLatency' accordingly.

        This function also validates the adjusted values. Returns the datapoint in case of success
        and 'None' if the datapoint has to be dropped.
        """

        # Apply the adjustments if the driver provides them.
        if "TBIAdj" in dp:
            tbi_adj = dp["TBIAdj"]
            dp["SilentTimeRaw"] = dp["SilentTime"]
            dp["SilentTime"] -= tbi_adj

            if dp["TBI"] + tbi_adj >= dp["LTime"]:
                _LOG.debug("adjusted 'TBI' is greater than 'LTime', the scheduled event must have "
                           "happened before the CPU entered the idle state. The datapoint is:\n%s\n"
                           "Adjusted 'TBI' is %d + %d = %d ns\nDropping this datapoint\n",
                           Human.dict2str(dp),  dp["TBI"], tbi_adj, dp["TBI"] + tbi_adj)
                return None

        if "TAIAdj" in dp:
            tai_adj = dp["TAIAdj"]
            tintr_adj = dp["TIntrAdj"]

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

    def _process_time(self, dp):
        """
        Calculate, validate, and initialize fields related to time, for example 'WakeLatency' and
        'IntrLatency'.
        """

        dp["SilentTime"] = dp["LTime"] - dp["TBI"]
        dp["WakeLatency"] = dp["TAI"] - dp["LTime"]
        dp["IntrLatency"] = dp["TIntr"] - dp["LTime"]

        for metric in ("LDist", "SilentTime", "IntrLatency", "WakeLatency"):
            if dp.get(metric, 0) < 0:
                raise Error(f"negative or missing '{metric}' value. The datapoint is:\n"
                            f"{Human.dict2str(dp)}") from None

        if self._drvname == "wult_tdt":
            # In case of 'wult_tdt' driver the time is in TSC cycles, convert to nanoseconds.
            for key in ("SilentTime", "WakeLatency", "IntrLatency"):
                dp[key] = self._tscrate.cyc_to_ns(dp[key])

        dp["WakeLatencyRaw"] = dp["WakeLatency"]
        dp["IntrLatencyRaw"] = dp["IntrLatency"]

        if not self._apply_time_adjustments(dp):
            return None

        # Try to compensate for the overhead introduced by wult drivers.
        #
        # Some C-states are entered with interrupts enabled (e.g., POLL), and some C-states are
        # entered with interrupts disabled. This is indicated by the 'IntrOff' flag ('IntrOff ==
        # True' are the datapoints for C-states entered with interrupts disabled).
        if dp["IntrOff"]:
            # 1. When the CPU exits the C-state, it runs 'after_idle()' before the interrupt
            #    handler. 'WakeLatency' is measured in 'after_idle()'. This introduces additional
            #    overhead, and delays the interrupt handler. This overhead can be estimated using
            #    using 'AITS1'/'AITS2' time-stamps.
            # 2. The interrupt handler is executed shortly after 'after_idle()' finishes and the
            #    "cpuidle" Linux kernel subsystem re-enables CPU interrupts.

            overhead = dp["AITS2"] - dp["AITS1"]

            if overhead >= dp["IntrLatency"]:
                # This sometimes happens, most probably because the overhead is measured using
                # monotonic time, while 'IntrLatency' is measured using the delayed event device
                # (e.g., a NIC). So we are possibly mixing time intervals from two different time
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

            dp["IntrLatency"] -= overhead
        else:
            # 1. When the CPU exits the C-state, it runs the interrupt handler before
            #    'after_idle()'.
            # 2. The interrupt latency is measured in the interrupt handler. This introduces
            #    additional overhead, and delays 'after_idle()'. This overhead can be estimated
            #    using 'IntrTS1' and 'IntrTS2' time-stamps.
            # 3. 'after_idle()' is executed after the interrupt handler and measures 'WakeLatency',
            #    which is greater than 'IntrLatency' in this case.
            #
            # Bear in mind, that wult interrupt handler may be executed after interrupt handlers, in
            # case there are multiple pending interrupts. Also keep in mind that in case of
            # timer-based measurements, the generic Linux interrupt handler is executed first, and
            # wult's handler may be called after other registered handlers. In other words, there
            # may be many CPU instructions between the moment the CPU wakes up from the C-state and
            # the moment it executes wult's interrupt handler.

            overhead = dp["IntrTS2"] - dp["IntrTS1"]

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

            dp["WakeLatency"] -= overhead

        return dp

    def _process_aperf_mperf(self, dp):
        """Calculate CPU frequency based on APERF and MPERF data."""

        for metric in ("AIAperf", "IntrAperf", "AIMperf", "IntrMperf"):
            if dp.get(metric, 0) == 0:
                msg = f"negative or missing '{metric}' value. The datapoint is:\n%s\n" \
                      "Dropping this and all the other datapoints like this."
                _LOG.debug(msg, Human.dict2str(dp))
                _LOG.warn_once(msg, Human.dict2str(dp))
                return None

        err_fmt = "hit a datapoint with '%s' >= '%s', even though interrupts were %s. " \
                  "The datapoint is :\n%s\nDropping this and all the other datapoints like this."
        if dp["IntrOff"]:
            # 'IntrOff == True' indicates that 'after_idle' happened prior to the interrupt, so
            # "IntrAperf" must be greater than "AIAperf" and "IntrMperf" must be greater than
            # "AIMperf".
            if dp["AIAperf"] >= dp["IntrAperf"]:
                msg = err_fmt % ("AIAperf", "IntrAperf", "disabled", Human.dict2str(dp))
                _LOG.debug(msg)
                _LOG.warn_once(msg)
                return None

            if dp["AIMperf"] >= dp["IntrMperf"]:
                msg = err_fmt %("AIMperf", "IntrMperf", "disabled", Human.dict2str(dp))
                _LOG.debug(msg)
                _LOG.warn_once(msg)
                return None

            delta_aperf = dp["IntrAperf"] - dp["AIAperf"]
            delta_mperf = dp["IntrMperf"] - dp["AIMperf"]
        else:
            # 'IntrOff == False' indicates that the interrupt happened prior to 'after_idle', so
            # "AIAperf" must be greater than "IntrAperf" and "AIMperf" greater be larger than
            # "IntrMperf".
            if dp["IntrAperf"] >= dp["AIAperf"]:
                msg = err_fmt % ("IntrAperf", "AIAperf", "enabled", Human.dict2str(dp))
                _LOG.debug(msg)
                _LOG.warn_once(msg)
                return None

            if dp["IntrMperf"] >= dp["AIMperf"]:
                msg = err_fmt %("IntrMperf", "AIMperf", "enabled", Human.dict2str(dp))
                _LOG.debug(msg, Human.dict2str(dp))
                _LOG.warn_once(msg, Human.dict2str(dp))
                return None

            delta_aperf = dp["AIAperf"] - dp["IntrAperf"]
            delta_mperf = dp["AIMperf"] - dp["IntrMperf"]

        dp["CPUFreq"] = self._tscrate.tsc_mhz * delta_aperf / delta_mperf

        return dp

    def _finalize_dp(self, dp):
        """Remove extra fields from the processed data point."""

        for field in list(dp):
            if field not in self._allowed_fields:
                del dp[field]

        return dp

    def _process_datapoint(self, rawdp):
        """Process a raw datapoint 'rawdp'. Returns the processed datapoint."""
        if rawdp["SMICnt"] != 0:
            _LOG.debug("SMI detected, the datapoint is\n%s",Human.dict2str(rawdp))
            _LOG.warn_once("SMI detected")
        if rawdp["NMICnt"] !=0:
            _LOG.debug("NMI detected, the datapoint is\n%s",Human.dict2str(rawdp))
            _LOG.warn_once("NMI detected")

        # Avoid extra copying for efficiency.
        dp = rawdp

        # Calculate latency and other metrics providing time intervals.
        dp = self._process_time(dp)
        if not dp:
            return None

        # Calculate CPU frequency.
        dp = self._process_aperf_mperf(dp)
        if not dp:
            return None

        # Add and validated C-state related fields.
        dp = self._process_cstates(dp)
        if not dp:
            return None

        # Some raw datapoint values are in nanoseconds, but we need them to be in microseconds.
        # Save time in microseconds.
        for field in dp:
            if field in self._us_fields_set:
                dp[field] /= 1000.0

        dp = self._finalize_dp(dp)
        if self._processed_fields is None:
            self._processed_fields = list(dp)

        return dp

    @staticmethod
    def is_dropped(dp):
        """Return 'True' if 'dp' is a dropped datapoint."""

        return _is_dropped(dp)

    def _get_dropped_dp(self, rawdp):
        """
        Turn a dropped raw datapoint into a datapoint to save. The fields are the same as in the
        processed datapoints. The values are not validated, and the metrics calculated by
        user-space are set to zero.
        """

        dp = {field: rawdp.get(field, 0) for field in self._processed_fields}

        for field in self._us_fields_set:
            if field in dp:
                dp[field] /= 1000.0

        for field in self._bool_fields:
            if field in dp and field not in rawdp:
                dp[field] = False

        return dp

    def add_raw_datapoint(self, rawdp):
        """
        Add a raw datapoint. The arguments are as follows.
          * rawdp - the raw datapoint to add.

        Notice: for efficiency purposes this function does not make a copy of the 'rawdp'
        dictionary. Instead, 'get_datapoints()' extends and modifies the dictionary in-place when
        processing it. Therefore, the caller should not use 'rawdp' after calling this method.
        """

        # The driver sends the drop flags as 0 or 1. Use booleans, same as for 'IntrOff'.
        for field in _DROP_FIELDS:
            if field in rawdp:
                rawdp[field] = bool(rawdp[field])

        if self.is_dropped(rawdp):
            # Without 'keep_rawdp' the 'Drop*' metrics are not saved, so dropped datapoints would
            # look like accepted ones. Do not keep them in this case.
            if not self._keep_rawdp:
                return
        else:
            rawdp = self._filter_out_noise(rawdp)
            if not rawdp:
                return

        self._tscrate.add_raw_datapoint(rawdp)

    def get_datapoints(self):
        """Yield processed and dropped datapoints."""

        for rawdp in self._tscrate.get_raw_datapoint():
            self._csobj.add_raw_datapoint(rawdp)

        for rawdp in self._csobj.get_raw_datapoint():
            if self.is_dropped(rawdp):
                # The fields of dropped datapoints are defined by the first processed datapoint.
                if self._processed_fields is not None:
                    yield self._get_dropped_dp(rawdp)
                continue

            dp = self._process_datapoint(rawdp)
            if dp:
                yield dp

    def prepare(self, rawdp, keep_rawdp):
        """
        Prepare for datapoints processing. The arguments are as follows.
          * rawdp - the first acquired raw datapoint.
          * keep_rawdp - by default, many raw datapoint fields are dropped and do not make it to the
                         'datapoints.csv' file. But if 'keep_rawdp' is 'True', all the datapoint raw
                         fields will also be saved in the CSV file.

        This method should be called as soon as the first raw datapoint is acquired. It build
        various internal data structures, for example list of available C-states.
        """

        raw_fields = list(rawdp.keys())

        self._keep_rawdp = keep_rawdp
        mdo = WultMDC.WultMDC(raw_fields)

        self._cs_fields = []
        self._has_cstates = False

        for field in raw_fields:
            csname = WultMDC.get_csname(field, must_get=False)
            if not csname:
                # Not a C-state field.
                continue
            self._has_cstates = True
            self._cs_fields.append(WultMDC.get_csres_metric(csname))

        self._us_fields_set = {field for field, vals in mdo.mdd.items() \
                               if vals.get("unit") == "microsecond"}
        self._bool_fields = {field for field, vals in mdo.mdd.items() if vals.get("type") == "bool"}

        # Form the preliminary list of fields in processed datapoints. Fields from the metrics
        # definition YAML file file go first. The list (but we use dictionary in this case) will be
        # amended later.
        self._allowed_fields = {}
        for field in mdo.mdd:
            self._allowed_fields[field] = None

        if keep_rawdp:
            for field in raw_fields:
                self._allowed_fields[field] = None
        else:
            for field in _DEBUG_FIELDS:
                self._allowed_fields.pop(field, None)

    def __init__(self, cpu, pman, drvname, tsc_cal_time=10, cpuidle=None):
        """
        The class constructor. The arguments are as follows.
          * cpu - the measured CPU number.
          * pman - the process manager object that defines the host to run the measurements on.
          * drvname - name of the driver providing the datapoints.
          * tsc_cal_time - amount of seconds to use for calculating TSC rate.
          * cpuidle - the 'CPUIdle.CPUIdle()' object initialized for the measured system.
        """

        self._cpu = cpu
        self._pman = pman
        self._drvname = drvname

        # A '_CStates' class object.
        self._csobj = None
        # A '_TSCRate' class object.
        self._tscrate = None

        # Fields allowed in processed datapoints, may include fields that are never produced.
        self._allowed_fields = None

        # Field names of processed datapoints, all of which have the same fields.
        self._processed_fields = None
        self._keep_rawdp = False
        self._has_cstates = None
        self._cs_fields = None
        self._us_fields_set = None
        self._bool_fields = None

        self._csobj = _CStates(self._cpu, self._pman, cpuidle=cpuidle)
        self._tscrate = _TSCRate(tsc_cal_time)

    def close(self):
        """Close the datapoint processor."""
        ClassHelpers.close(self, close_attrs=("_csobj",), unref_attrs=("_pman",))
