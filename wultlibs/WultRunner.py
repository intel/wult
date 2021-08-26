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

import time
import logging
import contextlib
from pathlib import Path
from wultlibs.helperlibs.Exceptions import Error, ErrorTimeOut
from wultlibs.helperlibs import FSHelpers, Human
from wultlibs.pepclibs import CPUIdle, Systemctl
from wultlibs import EventsProvider, Defs, _FTrace, _ProgressLine, WultStatsCollect

_LOG = logging.getLogger()

# Maximum count of unexpected lines in the trace buffer we tolerate.
_MAX_FTRACE_BAD_LINES = 10

def _dump_dp(dp):
    """Returns a string for datapoint 'dp' suitable for using in error messages."""

    import numpy                      # pylint: disable=import-outside-toplevel
    from itertools import zip_longest # pylint: disable=import-outside-toplevel

    # Printing one element per line takes too many lines and it is hard to read. So we attempt to
    # print 3 elements per line and align them for readability. So split items on 3 groups, each
    # group represents a column. The easy way of doing this is using 'numpy.array_split()'.
    split = [list(column) for column in numpy.array_split(numpy.array(list(dp)), 3)]

    columns = []
    for keys in split:
        # Create list of values for the keys in the column. Shorten the floating point numbers.
        vals = []
        for key in keys:
            val = dp[key]
            if isinstance(val, float):
                vals.append(f"{val:.2f}")
            else:
                vals.append(f"{val}")

        longest_key = max([len(key) for key in keys])
        longest_val = max([len(val) for val in vals])

        elts = []
        for key, val in zip(keys, vals):
            # Pad the keys/values to the longer key/value in the column.
            key = f"{(key + ':').ljust(longest_key + 1)}"
            val = f"{val.ljust(longest_val)}"
            elts.append(f"{key} {val}")

        columns.append(elts)

    return "\n".join(["    ".join(row).strip() for row in zip_longest(*columns, fillvalue="")])

def _apply_dp_overhead(dp):
    """
    This is a helper function for '_process_datapoint()' which handles the 'AIOverhead' and
    'IntrOverhead' values and modifies the 'dp' datapoint accordingly.

    'AIOverhead' stands for 'After Idle Overhead', and this is the time it takes to get all the data
    ('WakeLatency', C-state counters, etc) after idle, but before the interrupt handler. This value
    will be non-zero value for C-states that are entered with interrupts disabled (all C-states
    except for 'POLL' today, as of Aug 2021). In this case 'IntrOverhead' will be 0.

    'IntrOverhead' stands for 'Interrupt Overhead', and this is the time it takes to get all the
    data ('IntrLatency', C-state counters, etc) in the interrupt handler, before 'WakeLatency' is
    taken after idle. This value will be non-zero only for C-states that are entered with interrupts
    enabled (only the 'POLL' state today, as of Aug 2021).

    The overhead values are in nanoseconds. And they should be subtracted from wake/interrupt
    latency, because they do not contribute to the latency, they are the extra time added by wult
    driver between the wake event and "after idle" or interrupt.

    We do not save 'AIOverhead' and 'IntrOverhead' in the CSV file.
    """

    if dp["AIOverhead"] and dp["IntrOverhead"]:
        raise Error(f"Both 'AIOverhead' and 'IntrOverhead' are not 0 at the same time. The "
                    f"datapoint is:\n{_dump_dp(dp)}") from None

    if dp["IntrOff"]:
        # Interrupts were disabled.
        if dp["WakeLatency"] >= dp["IntrLatency"]:
            _LOG.warning("'WakeLatency' is greater than 'IntrLatency', even though interrupts "
                         "were disabled. The datapoint is:\n%s\nDropping this datapoint\n",
                         _dump_dp(dp))
            return None

        if dp["AIOverhead"] >= dp["IntrLatency"]:
            # This sometimes happens, and here are 2 contributing factors that may lead to this
            # condition.
            # 1. The overhead is measured by reading TSC at the beginning and the end of the
            #    'after_idle()' function, which runs as soon as the CPU wakes up. The 'IntrLatency'
            #    is measured using a delayed event device (e.g., a NIC). So we are comparing two
            #    time intervals from different time sources.
            # 2. 'AIOverhead' is the overhead of 'after_idle()', where we don't exactly know why we
            #    woke up, and we cannot tell with 100% certainty that we woke because of the
            #    interrupt that we armed. We could wake up or a different event, before launch time,
            #    close enough to the armed event. In this situation, we may measure large enough
            #    'AIOverhead', then the armed event happens when the CPU is in C0, and we measure
            #    very small 'IntrLatency'.
            _LOG.debug("'AIOverhead' is greater than interrupt latency ('IntrLatency'). The "
                       "datapoint is:\n%s\nDropping this datapoint\n", _dump_dp(dp))
            return None

        if dp["WakeLatency"] >= dp["IntrLatency"] - dp["AIOverhead"]:
            # This condition may happen for similar reasons.
            _LOG.debug("'WakeLatency' is greater than 'IntrLatency' - 'AIOverhead', even though "
                       "interrupts were disabled. The datapoint is:\n%s\nDropping this "
                       "datapoint\n", _dump_dp(dp))
            return None

        dp["IntrLatency"] -= dp["AIOverhead"]
    else:
        # Interrupts were enabled.
        if dp["IntrLatency"] >= dp["WakeLatency"]:
            _LOG.warning("'IntrLatency' is greater than 'WakeLatency', even though interrupts "
                         "were enabled. The datapoint is:\n%s\nDropping this datapoint\n",
                         _dump_dp(dp))
            return None

        if dp["IntrOverhead"] >= dp["WakeLatency"]:
            _LOG.debug("'IntrOverhead' is greater than wake latency ('WakeLatency'). The "
                       "datapoint is:\n%s\nDropping this datapoint\n", _dump_dp(dp))
            return None

        if dp["IntrLatency"] >= dp["WakeLatency"] - dp["IntrOverhead"]:
            _LOG.debug("'IntrLatency' is greater than 'WakeLatency' - 'IntrOverhead', even "
                       "though interrupts were enabled. The datapoint is:\n%s\nDropping this "
                       "datapoint\n", _dump_dp(dp))
            return None

        dp["WakeLatency"] -= dp["IntrOverhead"]
    return dp

class WultRunner:
    """Run wake latency measurement experiments."""

    def _run_post_trigger(self, latency):
        """Run the post-trigger program."""

        if self._post_trigger_range and \
           latency < self._post_trigger_range[0] or \
           latency > self._post_trigger_range[1]:
            return

        self._proc.run_verify(f"{self._post_trigger} --latency {latency}")

    def _validate_datapoint(self, fields, vals):
        """
        This is a helper function for '_get_datapoints()' which checks that every raw datapoint
        from the trace buffer has the same fields in the same order.
        """

        if len(fields) != len(self._fields) or len(vals) != len(self._fields) or \
           not all([f1 == f2 for f1, f2 in zip(fields, self._fields)]):
            old_fields = ", ".join(self._fields)
            new_fields = ", ".join(fields)
            raise Error(f"the very first raw datapoint has different fields comparing to a new "
                        f"datapointhad\n"
                        f"First datapoint fields count: {len(fields)}\n"
                        f"New datapoint fields count: {len(self._fields)}\n"
                        f"Fist datapoint fields:\n{old_fields}\n"
                        f"New datapoint fields:\n{new_fields}\n\n"
                        f"New datapoint full ftrace line:\n{self._ftrace.raw_line}")

    def _get_datapoints(self):
        """
        This generators reads the trace buffer and yields raw datapoints in form of a dictionary.
        The dictionary values are of integer type.
        """

        last_line = None
        yielded_lines = 0

        try:
            for line in self._ftrace.getlines():
                # Wult output format should be: field1=val1 field2=val2, and so on. Parse the line
                # and get the list of (field, val) pairs: [(field1, val1), (field2, val2), ... ].
                try:
                    if not line.msg:
                        raise ValueError
                    pairs = [pair.split("=") for pair in line.msg.split()]
                    fields, vals = zip(*pairs)
                    if len(fields) != len(vals):
                        raise ValueError
                except ValueError:
                    _LOG.debug("unexpected line in ftrace buffer%s:\n%s",
                               self._proc.hostmsg, line.msg)
                    continue

                yielded_lines += 1
                last_line = line.msg

                if self._fields:
                    self._validate_datapoint(fields, vals)
                else:
                    self._fields = fields

                yield dict(zip(fields, [int(val) for val in vals]))
        except ErrorTimeOut as err:
            msg = f"{err}\nCount of wult ftrace lines read so far: {yielded_lines}"
            if last_line:
                msg = f"{msg}\nLast seen wult ftrace line:\n{last_line}"
            raise ErrorTimeOut(msg) from err

    def _is_poll_idle(self, dp): # pylint: disable=no-self-use
        """Returns 'True' if the 'dp' datapoint contains the POLL idle state data."""
        return dp["ReqCState"] == 0

    def _process_datapoint_cstates(self, dp):
        """Add and validate various 'dp' datapoint fields related to C-states."""

        # Turn the C-state index into the C-state name.
        try:
            dp["ReqCState"] = self._csinfo[dp["ReqCState"]]["name"]
        except KeyError:
            # Supposedly an bad C-state index.
            indexes_str = ", ".join(f"{idx} ({val['name']})" for idx, val in  self._csinfo.items())
            raise Error(f"bad C-state index '{dp['ReqCState']}' in the following datapoint:\n"
                        f"{_dump_dp(dp)}\nAllowed indexes are:\n{indexes_str}") from None

        # The driver takes TSC and MPERF counters so that the MPERF interval is inside the
        # TSC interval, so delta TSC (total cycles) is expected to be always greater than
        # delta MPERF (C0 cycles).
        if dp["TotCyc"] < dp["CC0Cyc"]:
            raise Error(f"total cycles is smaller than CC0 cycles, the datapoint is:\n"
                        f"{_dump_dp(dp)}")

        if self._has_cstates and not self._is_poll_idle(dp):
            # Inject additional C-state information to the datapoint.
            # * CStatesCyc - combined count of CPU cycles in all non-CC0 C-states.
            # * DerivedCC1Cyc - software-calculated CC1 cycles, which is useful to have because not
            #                   every Intel platform has a HW CC1 counter. Calculated as "total
            #                   cycles" - "cycles in C-states other than CC1".
            cyc = sum([dp[name] for name in dp if name.startswith("CC") and name != "CC1Cyc"])
            dp["DerivedCC1Cyc"] = dp["TotCyc"] - cyc
            dp["CStatesCyc"] = dp["TotCyc"] - dp["CC0Cyc"]
            if dp["DerivedCC1Cyc"] < 0:
                # The C-state counters are not always precise, and we may end up with a negative
                # number.
                dp["DerivedCC1Cyc"] = 0
            if dp["CStatesCyc"] < 0:
                raise Error(f"negative 'CStatesCyc', the datapoint is:\n{_dump_dp(dp)}")
        else:
            dp["DerivedCC1Cyc"] = dp["CStatesCyc"] = 0

        # Add the C-state percentages.
        for colname in self._cs_colnames:
            field = Defs.get_cscyc_colname(Defs.get_csname(colname))

            # In case of POLL state, calculate only CC0%.
            if self._is_poll_idle(dp) and field != "CC0Cyc":
                dp[colname] = 0
                continue

            dp[colname] = dp[field] / dp["TotCyc"] * 100.0

            if dp[colname] > 100:
                loglevel = logging.DEBUG
                # Sometimes C-state residency counters are not precise, especially during short
                # sleep times. Warn only about too large percentage.
                if dp[colname] > 300:
                    loglevel = logging.WARNING

                csname = Defs.get_csname(colname)
                _LOG.log(loglevel, "too high %s residency of %.1f%%, using 100%% instead. The "
                                   "datapoint is:\n%s", csname, dp[colname], _dump_dp(dp))
                dp[colname] = 100.0

    def _process_datapoint(self, rawdp):
        """
        Process a raw datapoint 'rawdp'. The "raw" part in this contenxs means that 'rawdp' contains
        the datapoint as the kernel driver provided it. This function processes it and retuns the
        CSV datapoint. The CSV datapoint is derived from the raw datapoint, and it is later stored
        in the 'datapoints.csv' file. The CSV datapoint contains more fields comparing to the raw
        datapoint.
        """

        dp = rawdp

        if dp["TotCyc"] == 0:
            # This should not happen.
            raise Error(f"Zero total cycles ('TotCyc'), this should never happen, unless there is "
                        f"a bug. The datapoint is:\n{_dump_dp(dp)}") from None

        # Add and validated C-state related fields.
        self._process_datapoint_cstates(dp)

        if not _apply_dp_overhead(dp):
            return None

        # Save time in microseconds.
        times_us = {}
        for colname, val in dp.items():
            if colname in self._us_colnames:
                times_us[colname] = val / 1000
        dp.update(times_us)

        # Drop the not-so-useful columns.
        for colname in self._exclude_colnames:
            del dp[colname]
        return dp

    def _prepare_to_process_datapoints(self, rawdp):
        """
        This helper should be called as soon as the first raw datapoint 'raw' is acquired. It
        prepared for processing datapoints by building various data structures. For example, we
        learn about the C-state names from the first datapoint.
        """

        fields = list(rawdp.keys())
        fields = [col for col in list(fields) if col not in self._exclude_colnames]

        self._has_cstates = Defs.get_cscyc_colnames(fields)

        # Add the more metrics to the list of fields - we'll be injecting the values in
        # '_process_datapoint()'.
        if self._has_cstates:
            fields.insert(fields.index("CC0Cyc") + 1, "DerivedCC1Cyc")
        fields.append("CStatesCyc")

        # Get the C-states the measured platform provided by the driver for the measured platform.
        self._cs_colnames = list(Defs.get_cs_colnames(fields))

        # Driver sends time data in nanoseconds, build list of columns which we need to convert to
        # microseconds.
        defs = Defs.Defs(self._res.info["toolname"])
        self._us_colnames = [colname for colname, vals in defs.info.items() \
                             if vals.get("unit") == "microsecond"]

        # The raw datapoint does not include C-state residency data, it only has the C-state cycle
        # counters. We'll be calculating residencies later and include them too.
        for colname in self._cs_colnames:
            fields.append(colname)
        self._res.csv.add_header(fields)

    def _collect(self, dpcnt, tlimit):
        """
        Collect datapoints and stop when either the CSV file has 'dpcnt' datapoints in total or when
        collection time exceeds 'tlimit' (value '0' or 'None' means "no limit"). Returns count of
        collected datapoints. If the filters were configured, the returned value counts only those
        datapoints that passed the filters.
        """

        datapoints = self._get_datapoints()
        rawdp = next(datapoints)

        # We could actually process this datapoint, but we prefer to drop it and start with the
        # second one.
        self._prepare_to_process_datapoints(rawdp)

        # At least one datapoint should be collected within the 'timeout' seconds interval.
        timeout = self._timeout * 1.5
        start_time = last_collected_time = time.time()
        collected_cnt = 0
        for rawdp in datapoints:
            if tlimit and time.time() - start_time > tlimit:
                break

            if time.time() - last_collected_time > timeout:
                raise ErrorTimeOut(f"no datapoints accepted for {timeout} seconds. While the "
                                   f"driver does produce them, they are being rejected. One "
                                   f"possible reason is that they do not pass filters/selectors.")

            dp = self._process_datapoint(rawdp)
            if not dp:
                continue

            # Add the data to the CSV file.
            if not self._res.add_csv_row(dp):
                # the data point has not been added (e.g., because it did not pass row filters).
                continue

            collected_cnt += 1

            if self._post_trigger:
                self._run_post_trigger(dp["WakeLatency"])

            self._max_latency = max(dp["WakeLatency"], self._max_latency)
            self._progress.update(collected_cnt, self._max_latency)
            last_collected_time = time.time()

            if collected_cnt >= dpcnt:
                break

        return collected_cnt

    def run(self, dpcnt=1000000, tlimit=None):
        """
        Start the measurements. The arguments are as follows.
          * dpcnt - count of datapoints to collect.
          * tlimit - the measurements time limit in seconds.
        """

        self._res.write_info()

        if self._stcoll:
            # Start collecting statistics.
            self._stcoll.start()

        msg = f"Start measuring CPU {self._res.cpunum}{self._proc.hostmsg}, collecting {dpcnt} " \
              f"datapoints"
        if tlimit:
            msg += f", time limit is {Human.duration(tlimit)}"
        _LOG.info(msg)

        # Start printing the progress.
        self._progress.start()

        collected_cnt = 0
        try:
            self._ep.start()
            collected_cnt = self._collect(dpcnt, tlimit)
        except Error as err:
            dmesg = ""
            with contextlib.suppress(Error):
                dmesg = "\n" + self._dev.get_new_dmesg()
            if self._stcoll:
                with contextlib.suppress(Error):
                    self._stcoll.stop()
                with contextlib.suppress(Error):
                    self._stcoll.copy_stats()
            raise Error(f"{err}{dmesg}") from err
        finally:
            self._progress.update(collected_cnt, self._max_latency, final=True)

        _LOG.info("Finished measuring CPU %d%s", self._res.cpunum, self._proc.hostmsg)

        # Check if there were any bug/warning messages in 'dmesg'.
        dmesg = ""
        with contextlib.suppress(Error):
            dmesg = self._dev.get_new_dmesg()
            # The bug/warning markers we are looking for in 'dmesg'.
            markers = ("bug: ", "error: ", "warning: ")
            for marker in markers:
                variants = (marker, marker.upper(), marker.title())
                for variant in variants:
                    if variant in dmesg:
                        _LOG.warning("found a message prefixed with '%s' in 'dmesg':\n%s",
                                     variant, dmesg)
                        _LOG.warning("consider reporting this to wult developers")
                        break

        if self._stcoll:
            self._stcoll.stop()
            self._stcoll.copy_stats()

    def _get_cmdline(self):
        """Get kernel boot parameters."""

        try:
            with self._proc.open("/proc/cmdline", "r") as fobj:
                return fobj.read().strip()
        except Error as err:
            raise Error(f"failed to read cmdline parameters{self._proc.hostmsg}") from err

    def prepare(self):
        """Prepare for starting the measurements."""

        # The 'irqbalance' service usually causes problems by binding the delayed event to a CPU
        # different form the measured one. Stop the service.
        if self._has_irqbalance:
            _LOG.info("Stopping the 'irqbalance' service")
            self._sysctl.stop("irqbalance")

        self._ep.unload = self.unload
        self._ep.prepare()

        # Validate the delayed event resolution.
        resolution = self._ep.get_resolution()
        _LOG.debug("delayed event resolution %dns", resolution)

        # Save the delayed event device information to the output file.
        self._res.info["devid"] = self._ep.dev.info["devid"]
        self._res.info["devdescr"] = self._ep.dev.info["descr"]
        self._res.info["resolution"] = resolution

        errmsg = None
        if resolution > 1:
            errmsg = f"delayed event device {self._res.info['devid']} has poor resolution of " \
                     f"{resolution}ns"

        if errmsg:
            if resolution > 100:
                if "timer" in self._res.info["devdescr"]:
                    errmsg += "\nMake sure your kernel has high resolution timers enabled " \
                              "(CONFIG_HIGH_RES_TIMERS)"

                    with contextlib.suppress(Error):
                        cmdline = self._get_cmdline()
                        if "highres=off" in cmdline:
                            errmsg += "\nYour system uses the 'highres=off' kernel boot " \
                                      "parameter, try removing it"

                raise Error(errmsg)
            _LOG.warning(errmsg)

        # Initialize statistics collection.
        if self._stconf:
            self._stcoll = WultStatsCollect.WultStatsCollect(self._proc, self._res)
            self._stcoll.apply_stconf(self._stconf)
            _LOG.info("Configured the following statistics: %s", ", ".join(self._stconf["include"]))

    def set_post_trigger(self, path, trange=None):
        """
        Configure the post-trigger - a program that has to be executed after a datapoint is
        collected. The arguments are as follows.
          * path - path to the executable program to run. The program will be executed with the
            '--latency <value>' option, where '<value>' is the observed wake latency value in
            nanoseconds.
          * trange - the post-trigger range. By default, the trigger program is executed on every
            datapoint. But if the trigger range is provided, the trigger program will be executed
            only when wake latency is in trigger range.
        """

        if not FSHelpers.isexe(path, proc=self._proc):
            raise Error(f"post-trigger program '{path}' does not exist{self._proc.hostmsg} or it "
                        f"is not an executable file")

        self._post_trigger = path
        self._post_trigger_range = trange

    def _validate_sut(self):
        """Check the SUT to insure we have everything to measure it."""

        # Make sure a supported idle driver is in use.
        path = Path("/sys/devices/system/cpu/cpuidle/current_driver")
        with self._proc.open(path, "r") as fobj:
            drvname = fobj.read().strip()

        if drvname == "none":
            errmsg = f"no idle driver in use{self._proc.hostmsg}"
            try:
                cmdline = self._get_cmdline()
            except Error as err:
                raise Error(errmsg) from err

            idleoption = [item for item in cmdline.split() if "idle=" in item]
            if idleoption:
                errmsg += f". Your system uses the '{idleoption[0]}' kernel boot parameter, try " \
                          f"removing it."
            raise Error(errmsg)

        supported = ("intel_idle", "acpi_idle")
        if drvname not in supported:
            supported = ", ".join(supported)
            raise Error(f"unsupported idle driver '{drvname}'{self._proc.hostmsg},\n"
                        f"only the following drivers are supported: {supported}")

    def __init__(self, proc, dev, res, ldist=None, csinfo=None, stconf=None):
        """
        The class constructor. The arguments are as follows.
          * proc - the 'Proc' or 'SSH' object that defines the host to run the measurements on.
          * dev - the delayed event device object created by 'Devices.WultDevice()'.
          * res - the 'WORawResult' object to store the results at.
          * ldist - a pair of numbers specifying the launch distance range. The default value is
                    specific to the delayed event driver.
          * csinfo - C-state information for the CPU to measure ('res.cpunum'), generated by
                    'CPUIdle.get_cstates_info_dict()'.
          * stconf - the statistics configuration, a dictionary describing the statistics that
                     should be collected. By default no statistics will be collected.
        """

        self._proc = proc
        self._dev = dev
        self._res = res
        self._ldist = ldist
        self._csinfo = csinfo
        self._stconf = stconf

        # This is a debugging option that allows to disable automatic wult modules unloading on
        # 'close()'.
        self.unload = True

        self._ep = None
        self._ftrace = None
        self._timeout = 10
        self._fields = None
        self._has_cstates = None
        self._cs_colnames = None
        self._us_colnames = None
        self._progress = None
        self._max_latency = 0
        self._sysctl = None
        self._has_irqbalance = None
        self._post_trigger = None
        self._post_trigger_range = []
        self._stcoll = None

        # Not all information from the driver is saved in the CSV file, because it is not very
        # useful and we have it mostly for debugging and purposes. For example, "TAI" (Time After
        # Idle) or "LTime" (Launch Time) are not very interesting for the end user. Here are the
        # columns that we exclude from the CSV file.
        self._exclude_colnames = {"LTime", "TAI", "TBI", "TIntr", "AIOverhead", "IntrOverhead",
                                  "IntrOff", "AICyc1", "AICyc2", "IntrCyc1", "IntrCyc2"}

        self._validate_sut()

        self._progress = _ProgressLine.ProgressLine(period=1)
        self._ep = EventsProvider.EventsProvider(dev, res.cpunum, proc, ldist=self._ldist)
        self._ftrace = _FTrace.FTrace(proc=proc, timeout=self._timeout)

        if self._csinfo is None:
            with CPUIdle.CPUIdle(proc=proc) as cpuidle:
                self._csinfo = cpuidle.get_cstates_info_dict(res.cpunum)

        # Check that there are idle states that we can measure.
        for info in self._csinfo.values():
            if not info["disable"]:
                break
        else:
            raise Error(f"no idle states are enabled on CPU {res.cpunum}{proc.hostmsg}")

        self._sysctl = Systemctl.Systemctl(proc=proc)
        self._has_irqbalance = self._sysctl.is_active("irqbalance")

    def close(self):
        """Stop the measurements."""

        if getattr(self, "_proc", None):
            self._proc = None
        else:
            return

        if getattr(self, "_dev", None):
            self._dev = None

        if getattr(self, "_csinfo", None):
            self._csinfo = None

        if getattr(self, "_stcoll", None):
            self._stcoll.close()

        if getattr(self, "_ep", None):
            self._ep.close()
            self._ep = None

        if getattr(self, "_ftrace", None):
            self._ftrace.close()
            self._ftrace = None

        if getattr(self, "_has_irqbalance") and getattr(self, "_sysctl"):
            _LOG.info("Starting the previously stopped 'irqbalance' service")
            try:
                self._sysctl.start("irqbalance")
            except Error as err:
                # One case when we saw failures here was a system that was running irqbalance, but
                # the user offlined all the CPUs except for CPU0. We were able to stop the service,
                # but could not start it again, probably because there is only one CPU.
                _LOG.warning("failed to start the previously stoopped 'irqbalance' service:\n%s",
                             err)
            self._sysctl = None

    def __enter__(self):
        """Enter the run-time context."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the runtime context."""
        self.close()
