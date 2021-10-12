# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2020 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module implements the main wult functionality - runs wake latency measurement experiments and
saves the results.
"""

import logging
from helperlibs.Exceptions import Error
from helperlibs import Human
from pepclibs import CPUIdle
from wultlibs import Defs

_LOG = logging.getLogger()

class DatapointProcessor:
    """
    The datapoint processor class implements raw datapoint processing. Takes raw datapoints on
    input and provides processed datapoints on output. Processing includes filtering unwanted
    datapoints, calculating C-state residency percentages, and so on.
    """

    @staticmethod
    def _is_poll_idle(dp):
        """Returns 'True' if the 'dp' datapoint contains the POLL idle state data."""
        return dp["ReqCState"] == 0

    def _process_cstates(self, rawdp, dp):
        """
        Validate various raw datapoint 'rawdp' fields related to C-states. Populate the processed
        datapoint 'dp' with fields related to C-states.
        """

        # Turn the C-state index into the C-state name.
        try:
            dp["ReqCState"] = self._csinfo[rawdp["ReqCState"]]["name"]
        except KeyError:
            # Supposedly an bad C-state index.
            indexes_str = ", ".join(f"{idx} ({val['name']})" for idx, val in  self._csinfo.items())
            raise Error(f"bad C-state index '{rawdp['ReqCState']}' in the following datapoint:\n"
                        f"{Human.dict2str(rawdp)}\nAllowed indexes are:\n{indexes_str}") from None

        if rawdp["TotCyc"] == 0:
            raise Error(f"Zero total cycles ('TotCyc'), this should never happen, unless there is "
                        f"a bug. The raw datapoint is:\n{Human.dict2str(rawdp)}") from None

        # The driver takes TSC and MPERF counters so that the MPERF interval is inside the
        # TSC interval, so delta TSC (total cycles) is expected to be always greater than
        # delta MPERF (C0 cycles).
        if rawdp["TotCyc"] < rawdp["CC0Cyc"]:
            raise Error(f"total cycles is smaller than CC0 cycles, the raw datapoint is:\n"
                        f"{Human.dict2str(rawdp)}")

        # Add the C-state percentages.
        for field in self._cs_fields:
            cyc_filed = Defs.get_cscyc_colname(Defs.get_csname(field))

            # In case of POLL state, calculate only CC0%.
            if self._is_poll_idle(rawdp) and cyc_filed != "CC0Cyc":
                dp[field] = 0
                continue

            dp[field] = rawdp[cyc_filed] / rawdp["TotCyc"] * 100.0

            if dp[field] > 100:
                loglevel = logging.DEBUG
                # Sometimes C-state residency counters are not precise, especially during short
                # sleep times. Warn only about too large percentage.
                if dp[field] > 300:
                    loglevel = logging.WARNING

                csname = Defs.get_csname(field)
                _LOG.log(loglevel, "too high %s residency of %.1f%%, using 100%% instead. The "
                                   "datapoint is:\n%s", csname, dp[field], Human.dict2str(rawdp))
                dp[field] = 100.0

        if self._has_cstates and not self._is_poll_idle(rawdp):
            # Populate 'CC1Derived%' - the software-calculated CC1 residency, which is useful to
            # have because not every Intel platform has a hardware CC1 counter. Calculated as total
            # cycles minus cycles in C-states other than CC1.

            non_cc1_cyc = 0
            for field in rawdp.keys():
                if Defs.is_cscyc_colname(field) and Defs.get_csname(field) != "CC1":
                    non_cc1_cyc += rawdp[field]

            dp["CC1Derived%"] = (rawdp["TotCyc"] - non_cc1_cyc) / rawdp["TotCyc"] * 100.0
            if dp["CC1Derived%"] < 0:
                # The C-state counters are not always precise, and we may end up with a negative
                # number.
                dp["CC1Derived%"] = 0
        else:
            dp["CC1Derived%"] = 0

    def _cyc_to_ns(self, cyc):
        """Convert TSC cycles to nanoseconds."""
        return (cyc * 1000) / self.tsc_mhz

    def _cyc_to_us(self, cyc):
        """Convert TSC cycles to microseconds."""
        return cyc / self.tsc_mhz

    def _adjust_wult_igb_time(self, rawdp):
        """
        The 'wult_igb' driver needs to access the NIC over PCIe, which may add a significan overhead
        and increas inaccuracy. In order to improve this, the driver provides TSC snapshots taken at
        various points in 'get_time_before_idle()' ('DrvBICyc1', 'DrvBICyc2', 'DrvBICyc3') and in
        'get_time_after_idle()' ('DrvAICyc2', 'DrvAICyc3').
        """

        keys = ("DrvBICyc1", "DrvBICyc2", "DrvBICyc3", "DrvAICyc1", "DrvAICyc2", "DrvAICyc3")
        for key in keys:
            if key not in rawdp:
                raise Error(f"the '{key}' field was not found, make sure you have up-to-date wult "
                            f"drivers installed{self._proc.hostmsg}\nThe raw datapoint is:\n"
                            f"{Human.dict2str(rawdp)}")

        # In 'time_before_idle()', we first flush posted writes, then latch the NIC time by reading
        # a NIC register over PCIe. We have 2 TSC timestamp around the latch register read:
        # 'DrvBICyc1' and 'DrvBICyc2'. We assume that the read operation reached the NIC roughly
        # ('DrvBICyc2' - 'DrvBICyc1') / 2 TSC cycles after it was initiated on the CPU.
        tbi_adj = (rawdp["DrvBICyc2"] - rawdp["DrvBICyc1"]) / 2

        # After the time was latched, and 'DrvBICyc2' timestampe taken, we read the latched NIC time
        # from the NIC. And this read operation takes 'DrvBICyc3' - 'DrvBICyc2' cycles, which can be
        # considered as an added 'time_before_idle()' delay. Let's "compensate" for this delay.
        tbi_adj += rawdp["DrvBICyc3"] - rawdp["DrvBICyc2"]

        # Convert cycles to nanoseconds.
        tbi_adj = self._cyc_to_ns(tbi_adj)

        # Keep in mind: 'rawdp["TBI"]' is time in nanoseconds from the NIC. But 'tbi_adj' was
        # measured using CPU's TSC. We adjust the NIC-based time using TSC-based time here. This is
        # not ideal.
        rawdp["TBI"] += tbi_adj

        # In 'time_after_idle()' we start with "warming up" the link between the CPU and the link
        # (e.g., flush posted writes, wake it up from an L-state). The warm up is just a read
        # operation. But we have TSC values taken around the warm up read: 'DrvAICyc1' and
        # 'DrvAICyc2'. The warm up time is 'WarmupDelay'.
        rawdp["WarmupDelay"]= self._cyc_to_ns(rawdp["DrvAICyc2"] - rawdp["DrvAICyc1"])

        # After this we latch the NIC time. This time is referred to as 'LatchDelay'.
        rawdp["LatchDelay"] = self._cyc_to_ns(rawdp["DrvAICyc3"] - rawdp["DrvAICyc2"])

        # We need to "compensate" for the warm up delay and adjust for NIC time latch delay,
        # similarly to how we did it for 'TBI'.
        tai_adj = rawdp["DrvAICyc2"] - rawdp["DrvAICyc1"]
        tai_adj += (rawdp["DrvAICyc3"] - rawdp["DrvAICyc2"]) / 2
        tai_adj = self._cyc_to_ns(tai_adj)
        rawdp["TAI"] -= tbi_adj

    def _process_time(self, rawdp, dp):
        """
        Calculate, validate, and initialize fields related to time, for example 'WakeLatency' and
        'IntrLatency'.
        """

        if self._drvname == "wult_igb":
            self._adjust_wult_igb_time(rawdp)

        dp["SilentTime"] = rawdp["LTime"] - rawdp["TBI"]
        if self._intr_focus:
            # We do not measure 'WakeLatency' in this case, but it is handy to have it in the
            # dictionary as '0'. We'll remove it at the end of this function.
            dp["WakeLatency"] = 0
        else:
            dp["WakeLatency"] = rawdp["TAI"] - rawdp["LTime"]
        dp["IntrLatency"] = rawdp["TIntr"] - rawdp["LTime"]

        for key in ("SilentTime", "WakeLatency", "IntrLatency"):
            if self._drvname == "wult_tdt":
                # The time is in TSC cycles.
                dp[key] = self._cyc_to_us(dp[key])
            else:
                # The time is in nanoseconds.
                dp[key] /= 1000.0

        # Try to compensate for the overhead introduced by wult drivers.
        #
        # Some C-states are entered with interrupts enabled (e.g., POLL), and some C-states are
        # entered with interrupts disabled. This is indicated by the 'IntrOff' flag ('IntrOff ==
        # True' are the datapoints for C-states entered with interrupts disabled).
        if rawdp["IntrOff"]:
            # 1. When the CPU exits the C-state, it runs 'after_idle()' before the interrupt
            #    handler.
            #    1.1. If 'self._intr_focus == False', 'WakeLatency' is measured in 'after_idle()'.
            #         This introduces additional overhead, and delays the interrupt handler. This
            #         overhead can be estimated using 'AICyc1' and 'AICyc2' TSC counter snapshots.
            #    1.2. If 'self._intr_focus == True', 'WakeLatency' is not measured at all.
            # 2. The interrupt handler is executed shortly after 'after_idle()' finishes and the
            #    CPUIdle Linux kernel subsystem re-enables CPU interrupts.

            if dp["WakeLatency"] >= dp["IntrLatency"]:
                _LOG.warning("'WakeLatency' is greater than 'IntrLatency', even though interrupts "
                             "were disabled. The datapoint is:\n%s\nDropping this datapoint\n",
                             Human.dict2str(rawdp))
                return None

            if self._early_intr:
                _LOG.warning("hit a datapoint with interrupts disabled even though the early "
                             "interrupts feature was enabled. The datapoint is:\n%s\n"
                             "Dropping this datapoint\n", Human.dict2str(rawdp))
                return None

            if self._intr_focus:
                overhead = 0
            else:
                overhead = rawdp["AICyc2"] - rawdp["AICyc1"]
            overhead = self._cyc_to_us(overhead)

            if overhead >= dp["IntrLatency"]:
                # This sometimes happens, most probably because the overhead is measured by reading
                # TSC at the beginning and the end of the 'after_idle()' function, which runs as
                # soon as the CPU wakes up. The 'IntrLatency' is measured using a delayed event
                # device (e.g., a NIC). So we are comparing two time intervals from different time
                # sources.
                _LOG.debug("The overhead is greater than interrupt latency ('IntrLatency'). The "
                           "datapoint is:\n%s\nThe overhead is: %f\nDropping this datapoint\n",
                           Human.dict2str(rawdp), overhead)
                return None

            if dp["WakeLatency"] >= dp["IntrLatency"] - overhead:
                # This condition may happen for similar reasons.
                _LOG.debug("'WakeLatency' is greater than 'IntrLatency' - overhead, even though "
                           "interrupts were disabled. The datapoint is:\n%s\nThe overhead is: %f\n"
                           "Dropping this datapoint\n", Human.dict2str(rawdp), overhead)
                return None

            dp["IntrLatency"] -= overhead

        if not rawdp["IntrOff"] and not self._intr_focus:
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
                _LOG.debug("dropping datapoint with interrupts enabled - the 'tdt' driver does not "
                           "handle them correctly. The datapoint is:\n%s", Human.dict2str(rawdp))
                return None

            if dp["IntrLatency"] >= dp["WakeLatency"]:
                _LOG.warning("'IntrLatency' is greater than 'WakeLatency', even though interrupts "
                             "were enabled. The datapoint is:\n%s\nDropping this datapoint\n",
                             Human.dict2str(rawdp))
                return None

            if self._intr_focus:
                overhead = 0
            else:
                overhead = rawdp["IntrCyc1"] - rawdp["IntrCyc2"]
            overhead = self._cyc_to_us(overhead)

            if overhead >= dp["WakeLatency"]:
                _LOG.debug("Overhead is greater than wake latency ('WakeLatency'). The "
                           "datapoint is:\n%s\nThe overhead is: %f\nDropping this datapoint\n",
                           overhead, Human.dict2str(rawdp))
                return None

            if dp["IntrLatency"] >= dp["WakeLatency"] - overhead:
                _LOG.debug("'IntrLatency' is greater than 'WakeLatency' - overhead, even though "
                           "interrupts were enabled. The datapoint is:\n%sThe overhead is: %f\n"
                           "Dropping this datapoint\n", overhead, Human.dict2str(rawdp))
                return None

            dp["WakeLatency"] -= overhead

        if self._intr_focus:
            del dp["WakeLatency"]

        return dp

    def _init_dp(self, rawdp):
        """Create and initialize a processed datapoint from raw datapoint 'rawdp'."""

        dp = {}
        for field in self.fields:
            dp[field] = rawdp.get(field, None)

        return dp

    def _process_datapoint(self, rawdp):
        """Process a raw datapoint 'rawdp'. Retuns the processed datapoint."""

        dp = self._init_dp(rawdp)

        # Calculate latencies and other metrics providing time intervals.
        if not self._process_time(rawdp, dp):
            return None

        # Add and validated C-state related fields.
        self._process_cstates(rawdp, dp)

        # Some raw datapoint values are in nanoseconds, but we need them to be in microseconds.
        # Save time in microseconds.
        for field in dp:
            if field in rawdp and field in self._us_fields_set:
                dp[field] = rawdp[field] / 1000.0

        return dp

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
        the datapoint as the kernel driver provided it. This function processes it and retuns the
        processed datapoint.

        Notice: for effeciency purposes this function does not make a copy of 'rawdp' and instead,
        uses and even modifies 'rawd'. In other words, the caller should not use 'rawdp' after
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

        defs = Defs.Defs("wult")
        defs.populate_cstates(raw_fields)

        self._cs_fields = []
        self._has_cstates = False

        for field in raw_fields:
            csname = Defs.get_csname(field, default=None)
            if not csname:
                # Not a C-state field.
                continue
            self._has_cstates = True
            self._cs_fields.append(Defs.get_csres_colname(csname))

        self._us_fields_set = {field for field, vals in defs.info.items() \
                               if vals.get("unit") == "microsecond"}

        # Form the list of fileds in processed datapoints. Fields from the "defs" file go first.
        fields = []
        for field in defs.info:
            if Defs.is_csres_colname(field) or field in rawdp:
                fields.append(field)
                continue

            if not defs.info[field].get("optional"):
                if self._intr_focus and field == "WakeLatency":
                    # In case of interrupt-focused measurements 'WakeLatency' is not measured.
                    continue
                fields.append(field)

        if keep_rawdp:
            # Append raw fields. In case of a duplicate name:
            # * if the values are the same too, drop the raw field.
            # * if the values are different, keep both, just prepend the raw field name with "Raw".
            fields_set = set(fields)

            for field in raw_fields:
                if field not in fields_set:
                    fields.append(field)

        self.fields = fields

    def __init__(self, cpunum, proc, drvname, intr_focus=None, early_intr=None, tsc_cal_time=10,
                 csinfo=None):
        """
        The class constructor. The arguments are as follows.
          * cpunum - the measured CPU numer.
          * proc - the 'Proc' or 'SSH' object that defines the host to run the measurements on.
          * drvname - name of the driver providing the datapoints
          * intr_focus - enable inerrupt latency focused measurements ('WakeLatency' is not measured
                         in this case, only 'IntrLatency').
          * early_intr - enable intrrupts before entering the C-state.
          * tsc_cal_time - amount of seconds to use for calculating TSC rate.
          * csinfo - C-state information for the CPU to measure ('res.cpunum'), generated by
                    'CPUIdle.get_cstates_info_dict()'.
        """

        self._proc = proc
        self._drvname = drvname
        self._intr_focus = intr_focus
        self._early_intr = early_intr
        self.tsc_cal_time = tsc_cal_time
        self._csinfo = csinfo

        # Processed datapoint field names.
        self.fields = None
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

        if self._csinfo is None:
            with CPUIdle.CPUIdle(proc=proc) as cpuidle:
                self._csinfo = cpuidle.get_cstates_info_dict(cpunum)

        # Check that there are idle states that we can measure.
        for info in csinfo.values():
            if not info["disable"]:
                break
        else:
            raise Error(f"no idle states are enabled on CPU {cpunum}{proc.hostmsg}")

    def close(self):
        """Close the datapoint processor."""

        if getattr(self, "_proc", None):
            self._proc = None
        else:
            return

        if getattr(self, "_csinfo", None):
            self._csinfo = None


    def __enter__(self):
        """Enter the run-time context."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the runtime context."""
        self.close()
