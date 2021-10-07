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

    def _apply_dp_overhead(self, rawdp, dp):
        """
        This is a helper function for '_process_datapoint()' which handles the 'AIOverhead' and
        'IntrOverhead' values and modifies the 'dp' datapoint accordingly.

        'AIOverhead' stands for 'After Idle Overhead', and this is the time it takes to get all the
        data ('WakeLatency', C-state counters, etc) after idle, but before the interrupt handler.
        This value will be non-zero value for C-states that are entered with interrupts disabled
        (all C-states except for 'POLL' today, as of Aug 2021). In this case 'IntrOverhead' will be
        0.

        'IntrOverhead' stands for 'Interrupt Overhead', and this is the time it takes to get all the
        data ('IntrLatency', C-state counters, etc) in the interrupt handler, before 'WakeLatency'
        is taken after idle. This value will be non-zero only for C-states that are entered with
        interrupts enabled (only the 'POLL' state today, as of Aug 2021).

        The overhead values are in nanoseconds. And they should be subtracted from wake/interrupt
        latency, because they do not contribute to the latency, they are the extra time added by
        wult driver between the wake event and "after idle" or interrupt.
        """

        if rawdp["AIOverhead"] and rawdp["IntrOverhead"]:
            raise Error(f"Both 'AIOverhead' and 'IntrOverhead' are not 0 at the same time. The "
                        f"datapoint is:\n{Human.dict2str(rawdp)}") from None

        if rawdp["IntrOff"]:
            # Interrupts were disabled.
            if rawdp["WakeLatency"] >= rawdp["IntrLatency"]:
                _LOG.warning("'WakeLatency' is greater than 'IntrLatency', even though interrupts "
                             "were disabled. The datapoint is:\n%s\nDropping this datapoint\n",
                             Human.dict2str(rawdp))
                return None

            if self._early_intr:
                _LOG.warning("hit a datapoint with interrupts disabled even though the early "
                             "interrupts feature was enabled. The datapoint is:\n%s\n"
                             "Dropping this datapoint\n", Human.dict2str(rawdp))
                return None

            if rawdp["AIOverhead"] >= rawdp["IntrLatency"]:
                # This sometimes happens, and here are 2 contributing factors that may lead to this
                # condition.
                # 1. The overhead is measured by reading TSC at the beginning and the end of the
                #    'after_idle()' function, which runs as soon as the CPU wakes up. The
                #    'IntrLatency' is measured using a delayed event device (e.g., a NIC). So we are
                #    comparing two time intervals from different time sources.
                # 2. 'AIOverhead' is the overhead of 'after_idle()', where we don't exactly know why
                #    we woke up, and we cannot tell with 100% certainty that we woke because of the
                #    interrupt that we armed. We could wake up or a different event, before launch
                #    time, close enough to the armed event. In this situation, we may measure large
                #    enough 'AIOverhead', then the armed event happens when the CPU is in C0, and we
                #    measure very small 'IntrLatency'.
                _LOG.debug("'AIOverhead' is greater than interrupt latency ('IntrLatency'). The "
                           "datapoint is:\n%s\nDropping this datapoint\n", Human.dict2str(rawdp))
                return None

            if rawdp["WakeLatency"] >= rawdp["IntrLatency"] - rawdp["AIOverhead"]:
                # This condition may happen for similar reasons.
                _LOG.debug("'WakeLatency' is greater than 'IntrLatency' - 'AIOverhead', even "
                           "though interrupts were disabled. The datapoint is:\n%s\nDropping this "
                           "datapoint\n", Human.dict2str(rawdp))
                return None

            dp["IntrLatency"] -= rawdp["AIOverhead"]
        elif not self._intr_focus:
            # Interrupts were enabled.

            if self._drvname == "wult_tdt":
                _LOG.debug("dropping datapoint with interrupts enabled - the 'tdt' driver does not "
                           "handle them correctly. The datapoint is:\n%s", Human.dict2str(rawdp))
                return None

            if rawdp["IntrLatency"] >= rawdp["WakeLatency"]:
                _LOG.warning("'IntrLatency' is greater than 'WakeLatency', even though interrupts "
                             "were enabled. The datapoint is:\n%s\nDropping this datapoint\n",
                             Human.dict2str(rawdp))
                return None

            if rawdp["IntrOverhead"] >= rawdp["WakeLatency"]:
                _LOG.debug("'IntrOverhead' is greater than wake latency ('WakeLatency'). The "
                           "datapoint is:\n%s\nDropping this datapoint\n", Human.dict2str(rawdp))
                return None

            if rawdp["IntrLatency"] >= rawdp["WakeLatency"] - rawdp["IntrOverhead"]:
                _LOG.debug("'IntrLatency' is greater than 'WakeLatency' - 'IntrOverhead', even "
                           "though interrupts were enabled. The datapoint is:\n%s\nDropping this "
                           "datapoint\n", Human.dict2str(rawdp))
                return None

            dp["WakeLatency"] -= rawdp["IntrOverhead"]
        return dp

    def _process_datapoint_cstates(self, rawdp, dp):
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

    def _init_dp(self, rawdp):
        """Create and intialized a processed datapoint from raw datapoint 'rawdp'."""

        dp = {}
        for field in self.fields:
            dp[field] = rawdp.get(field, None)

        return dp

    def _process_datapoint(self, rawdp):
        """Process a raw datapoint 'rawdp'. Retuns the processed datapoint."""

        dp = self._init_dp(rawdp)

        # Add and validated C-state related fields.
        self._process_datapoint_cstates(rawdp, dp)

        if not self._apply_dp_overhead(rawdp, dp):
            return None

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
        here at all, it jsut tells that these counters were read just before the system enters an
        idle state.

        We need a couple of datapoints fare enough apart in order to calculate TSC rate. This method
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
        Process a raw datapoint 'rawdp'. The "raw" part in this contenxs means that 'rawdp' contains
        the datapoint as the kernel driver provided it. This function processes it and retuns the
        processed datapoint.
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
                self._dps.append(dp)

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
                raise Error(f"the mandatory '{field}' filed was not found. The datapoint is:\n"
                            f"{Human.dict2str(rawdp)}")

        if keep_rawdp:
            # Append raw fields. In case of a duplicate name:
            # * if the values are the same too, drop the raw field.
            # * if the values are different, keep both, just prepend the raw field name with "Raw".
            fields_set = set(fields)

            for field in raw_fields:
                if field not in fields_set:
                    fields.append(field)

        self.fields = fields

        # Sanity check: no values should be 'None'.
        dp = self._process_datapoint(rawdp)
        if any(val is None for val in dp.values()):
            raise Error("bug: 'None' values found in the following datapoint:\nHuman.dict2str(dp)")

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
          * tsc_cal_time - amount of senconds to use for calculating TSC rate.
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
