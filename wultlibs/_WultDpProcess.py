# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module provides the 'DatapointProcessor' class which implements raw datapoint processing.
"""

import logging
from pepclibs import CStates
from pepclibs.helperlibs import ClassHelpers
from pepclibs.helperlibs.Exceptions import Error
from wultlibs import WultDefs
from wultlibs.helperlibs import Human

_LOG = logging.getLogger()

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
            raise Error(f"no idle states are enabled on CPU {self._cpunum}{self._pman.hostmsg}")

        for csname, cstate in self._rcsinfo.items():
            self._idx2name[cstate["index"]] = csname

    def _get_req_cstate_name(self, rawdp):
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
        Add a raw datapoint 'rawdp' and use it for detecting interrupt order. Returns 'rawdp' if
        interrupt order for the requested C-state in 'rawdp' is already known. Returns 'None'
        otherwise.

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
        guaranteed to happened earlier than 'after_idle()'. In some cases, when the CPU was woken up
        by a non-interrupt event (e.g., because the Linux scheduler woke us up by writing to the
        memory address monitored by the 'mwait' instruction), 'after_idle()' happens first. And if
        this non-interrupt event happened just before wult interrupt, the interrupt handler may run
        right after 'after_idle()'. So it may look the CPU woke up because of a wult event, and
        'after_idle()' ran before the interrupt handler.

        To overcome this complication, we collect many datapoints for requestable C-states, and
        look at the "interrupt handler vs 'after_idle()" order of the majority of datapoints. The
        datapoints are held back and stored in this class until we have enough of them. Then they
        are yielded by 'get_raw_datapoint()'.
        """

        csname = rawdp["ReqCState"] = self._get_req_cstate_name(rawdp)

        if self._early_intr:
            # When the "early interrupts" feature is used, wult enables interrupts before the
            # C-state is requrested.
            rawdp["IntrOff"] = False
            return rawdp

        if csname == "POLL":
            # This is an optimization. The 'POLL' state is always requested with interrupts enabled.
            rawdp["IntrOff"] = False
            return rawdp

        if csname != "C1":
            # This is another optimization. As of today, all C-states deeper than C1 are requested
            # with interrupts disabled. Only C1 is ambiguous.
            rawdp["IntrOff"] = True
            return rawdp

        if csname in self._introff:
            rawdp["IntrOff"] = self._introff[csname]
            return self._check_rawdp_timing(rawdp)

        if csname not in self._intr_order:
            self._intr_order[csname] = {"intr_on" : [], "intr_off" : [] }
            _LOG.debug("figuring out interrupt order for the %s requestable C-state", csname)

        _intr_order = self._intr_order[csname]

        if rawdp["TIntr"] < rawdp["TAI"]:
            _intr_order["intr_on"].append(rawdp)
        else:
            _intr_order["intr_off"].append(rawdp)

        # Check if we have enough "statistics" to judge whether interrupts were enabled or disabled.
        # Find the "interrupts on" vs "interrupts off" ratio (the "+ 1" part is to avoid division by
        # zero).
        ratio = float((len(_intr_order["intr_on"]) + 1)) / (len(_intr_order["intr_off"]) + 1)

        # Ratio 100:1 is good enough to make the final conclusion about the order.
        if ratio > 100:
            intr_off = False
        elif 1 / ratio > 100:
            intr_off = True
        else:
            intr_off = None

        if intr_off is not None:
            self._introff[csname] = intr_off
            _LOG.debug("figured out interrupt order for %s: requested with interrupts %s",
                       csname, "disabled" if intr_off else "enabled")

        return None

    def get_raw_datapoint(self):
        """
        This generator yields the raw datapoints saved by 'add_raw_datapoint()' when C-states
        interrupt order is figured out.
        """

        if not self._intr_order:
            return
        if not self._introff:
            return

        delete_csnames = []
        for csname, intr_order in self._intr_order.items():
            if csname in self._introff:
                if self._introff[csname]:
                    key = "intr_off"
                else:
                    key = "intr_on"
                for rawdp in intr_order[key]:
                    rawdp["IntrOff"] = self._introff[csname]
                    yield rawdp
                delete_csnames.append(csname)

        for csname in delete_csnames:
            del self._intr_order[csname]

    def __init__(self, cpunum, pman, rcsobj=None, early_intr=None):
        """
        The class constructor. The arguments are as follows.
          * cpunum - the measured CPU number.
          * pman - the process manager object that defines the host to run the measurements on.
          * rcsobj - the 'Cstates.ReqCStates()' object initialized for the measured system.
          * early_intr - enable interrupts before entering the C-state.
        """

        self._cpunum = cpunum
        self._pman = pman
        self._rcsobj = rcsobj
        self._early_intr = early_intr

        self._close_rcsobj = rcsobj is None

        # C-states information provided by ''Cstates.ReqCStates()'
        self._rcsinfo = None
        # C-state index -> C-state name dictionary..
        self._idx2name = {}

        # A dictionary indexed by C-state names, used for storing temporary data while figuring out
        # C-states interrupt order.
        self._intr_order = {}
        # Interrupt status of requestable C-states. Dictionary keys are C-state names, the values
        # are:
        #   * 'True' if the C-state is requested with interrupts disabled.
        #   * 'False' if the C-state is requested with interrupts enabled.
        self._introff = {}

        if not self._rcsobj:
            self._rcsobj = CStates.ReqCStates(pman=self._pman)

        self._rcsinfo = self._rcsobj.get_cpu_cstates_info(self._cpunum)

        self._init_idx2name()

    def close(self):
        """Uninitialize and close the object."""
        ClassHelpers.close(self, close_attrs=("_rcsobj",), unref_attrs=("_pman", "_rcsinfo"))

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
        'self._tsc_mhz'.
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

        self._tsc_mhz = ((tsc2 - self._tsc1) * 1000.0) / (ts2 - self._ts1)
        _LOG.info("TSC rate is %.6f MHz", self._tsc_mhz)

    def add_raw_datapoint(self, rawdp):
        """
        Add a raw datapoint 'rawdp' and use it for calculating TSC rate. Returns 'rawdp' if TSC
        rate has already been calculated and no more raw datapoints are required. Returns 'None'
        otherwise.

        The idea here is that we need to collect raw datapoints for 'self._tsc_cal_time' seconds,
        and hold them on. After 'self._tsc_cal_time' seconds worth of datapoints are available, we
        can calculate TSC rate. Then the TSC rate can be used for processing the datapoints that we
        held and for new datapoints. The held datapoints will be yielded by 'get_raw_datapoint()'.
        """

        if self._drvname != "wult_tdt":
            # Only the 'wult_tdt' driver requires TSC rate calculations.
            return rawdp

        if self._tsc_mhz:
            # TSC rate is already known, skip the calculations.
            return rawdp

        self._calculate_tsc_rate(rawdp)
        self._rawdps.append(rawdp)
        return None

    def get_raw_datapoint(self):
        """
        This generator yields the raw datapoints saved by 'add_raw_datapoint()' when TSC
        rate has been calculated.
        """

        if self._tsc_mhz:
            for rawdp in self._rawdps:
                yield rawdp
            self._rawdps = []

    def cyc_to_ns(self, cyc):
        """Convert TSC cycles to nanoseconds."""

        return int((cyc * 1000) / self._tsc_mhz)

    def __init__(self, drvname, tsc_cal_time):
        """
        The class constructor. The arguments are as follows.
          * drvname - name of the driver providing the datapoints.
          * tsc_cal_time - amount of seconds to use for calculating TSC rate.
        """

        self._drvname = drvname
        self._tsc_cal_time = tsc_cal_time

        # TSC rate in MHz (cycles / microsecond).
        self._tsc_mhz = None

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
        if dp["TotCyc"] < dp["CC0Cyc"]:
            raise Error(f"total cycles is smaller than CC0 cycles, the raw datapoint is:\n"
                        f"{Human.dict2str(dp)}")

        # Add the C-state percentages.
        for field in self._cs_fields:
            cyc_field = WultDefs.get_cscyc_metric(WultDefs.get_csname(field))

            # In case of POLL state, calculate only CC0%.
            if self._is_poll_idle(dp) and cyc_field != "CC0Cyc":
                dp[field] = 0
                continue

            dp[field] = dp[cyc_field] / dp["TotCyc"] * 100.0

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

        dp["WakeLatencyRaw"] = dp["WakeLatency"]
        dp["IntrLatencyRaw"] = dp["IntrLatency"]

        for metric in ("LDist", "SilentTime", "IntrLatency", "WakeLatency"):
            if dp.get(metric, 0) < 0:
                raise Error(f"negative '{metric}' value. The datapoint is:\n"
                            f"{Human.dict2str(dp)}") from None

        if self._drvname == "wult_tdt":
            # In case of 'wult_tdt' driver the time is in TSC cycles, convert to nanoseconds.
            for key in ("SilentTime", "WakeLatency", "IntrLatency"):
                dp[key] = self._tscrate.cyc_to_ns(dp[key])

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

            if self._early_intr:
                msg = "hit a datapoint with interrupts disabled even though the early interrupts "\
                      "feature was enabled. The datapoint is:\n%s\nDropping this datapoint\n"
                _LOG.debug(msg, Human.dict2str(dp))
                _LOG.warn_once(msg, Human.dict2str(dp))
                return None

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

            if self._drvname == "wult_tdt":
                csname = dp["ReqCState"]
                msg = f"The {csname} C-state has interrupts enabled and therefore, can't be "\
                      "collected with the 'wult_tdt' driver. Use another driver for %s."
                _LOG.debug(msg, csname)
                _LOG.warn_once(msg, csname)
                _LOG.debug("dropping datapoint with interrupts enabled - the 'wult_tdt' driver "
                           "does not handle them correctly. The datapoint is:\n%s",
                           Human.dict2str(dp))
                return None

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

        if self._drvname == "wult_tdt":
            # The 'wult_tdt' driver cannot really be used for measuring Interrupt latency, because
            # it measures 'WakeLatency' for the next TSC deadline timer, which is not necessarily
            # the one armed by wult. But 'IntrLatency' will be measured in wult timer handler, which
            # may be far away from the event 'WakeLatency' was measured for. Therefore, 'wult_tdt'
            # produces many datapoints with really large (and incorrect) 'IntrLatency'. Hence, we
            # remove it from the datapoint.
            if "IntrLatencyRaw" in dp:
                del dp["IntrLatencyRaw"]
            del dp["IntrLatency"]

        return dp

    def _finalize_dp(self, dp):
        """Remove extra fields from the processed data point."""

        for field in list(dp):
            if field not in self._fields:
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

    def add_raw_datapoint(self, rawdp):
        """
        Add and process a raw datapoint. The arguments are as follows.
          * rawdp - the raw datapoint to add and process.

        Notice: for efficiency purposes this function does not make a copy of the 'rawdp'
        dictionary. Instead, it extends and modifies it in-pace, and saves in an internal list. The
        dictionary will be yielded later by 'get_processed_datapoints()'. Therefore, the caller
        should not use 'rawdp' after calling this method.
        """

        rawdp = self._tscrate.add_raw_datapoint(rawdp)
        if rawdp:
            rawdp = self._csobj.add_raw_datapoint(rawdp)
            if rawdp:
                dp = self._process_datapoint(rawdp)
                if dp:
                    self._dps.append(dp)

    def get_processed_datapoints(self):
        """
        This generator yields the processed datapoints.
        """

        for rawdp in self._tscrate.get_raw_datapoint():
            rawdp = self._csobj.add_raw_datapoint(rawdp)
            if rawdp:
                dp = self._process_datapoint(rawdp)
                if dp:
                    yield dp

        for rawdp in self._csobj.get_raw_datapoint():
            dp = self._process_datapoint(rawdp)
            if dp:
                yield dp

        for dp in self._dps:
            yield dp

        self._dps = []

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

    def __init__(self, cpunum, pman, drvname, early_intr=None, tsc_cal_time=10, rcsobj=None):
        """
        The class constructor. The arguments are as follows.
          * cpunum - the measured CPU number.
          * pman - the process manager object that defines the host to run the measurements on.
          * drvname - name of the driver providing the datapoints.
          * early_intr - enable interrupts before entering the C-state.
          * tsc_cal_time - amount of seconds to use for calculating TSC rate.
          * rcsobj - the 'Cstates.ReqCStates()' object initialized for the measured system.
        """

        self._cpunum = cpunum
        self._pman = pman
        self._drvname = drvname
        self._early_intr = early_intr

        # A '_CStates' class object.
        self._csobj = None
        # A '_TSCRate' class object.
        self._tscrate = None

        # Processed datapoint field names.
        self._fields = None

        self._dps = []
        self._has_cstates = None
        self._cs_fields = None
        self._us_fields_set = None

        self._csobj = _CStates(self._cpunum, self._pman, rcsobj=rcsobj, early_intr=early_intr)
        self._tscrate = _TSCRate(self._drvname, tsc_cal_time)

    def close(self):
        """Close the datapoint processor."""
        ClassHelpers.close(self, close_attrs=("_csobj",), unref_attrs=("_pman",))
