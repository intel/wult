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
from wultlibs.pepclibs import CPUIdle, CPUInfo, Systemctl
from wultlibs import EventsProvider, Defs, _FTrace, _ProgressLine, WultStatsCollect

_LOG = logging.getLogger()

# Maximum count of unexpected lines in the trace buffer we tolerate.
_MAX_FTRACE_BAD_LINES = 10

def _dump_dp(dp):
    """Returns a string for datapoint 'dp' suitable for using in error messages."""

    return "\n".join(f"{key}: {val}" for key, val in dp.items())

class WultRunner:
    """Run wake latency measurement experiments."""

    def _run_post_trigger(self, latency):
        """Run the post-trigger program."""

        if self._post_trigger_range and \
           latency < self._post_trigger_range[0] or \
           latency > self._post_trigger_range[1]:
            return

        self._proc.run_verify(f"{self._post_trigger} --latency {latency}")

    def _get_datapoints(self):
        """
        This generators reads the trace buffer and yields datapoints in form of (names, vals)
        tuples, where:
          o names - list of datapoint names (the CSV file header).
          o vals - list of datapoint values.
        """

        last_line = None
        yielded_lines = 0

        try:
            for line in self._ftrace.getlines():
                # Wult output format should be: name1=val1 name2=val2, and so on. Parse the line and
                # get the list of (name, val) pairs: [(name1, val1), (name2, val2), ... ].
                try:
                    if not line.msg:
                        raise ValueError
                    pairs = [pair.split("=") for pair in line.msg.split()]
                    names, vals = zip(*pairs)
                    if len(names) != len(vals):
                        raise ValueError
                except ValueError:
                    _LOG.debug("unexpected line in ftrace buffer%s:\n%s",
                               self._proc.hostmsg, line.msg)
                    continue

                yielded_lines += 1
                last_line = line.msg
                yield names, vals
        except ErrorTimeOut as err:
            msg = f"{err}\nCount of wult ftrace lines read so far: {yielded_lines}"
            if last_line:
                msg = f"{msg}\nLast seen wult ftrace line:\n{last_line}"
            raise ErrorTimeOut(msg) from err

    def _get_datapoint_dict(self, rawdp):
        """Return the raw data provided by the kernel driver as a dictionary."""
        return dict(zip(self._rawhdr, [int(elt) for elt in rawdp]))

    def _is_poll_idle(self, dp): # pylint: disable=no-self-use
        """Returns 'True' if the 'dp' datapoint contains the POLL idle state data."""
        return dp["ReqCState"] == 0

    def _process_datapoint(self, rawdp):
        """
        Process a raw datapoint and return it as dictionary. The "raw" part in this contents means
        that the 'rawdp' list contains data provided by the kernel driver. This methods is going to
        amend and extend it.
        """

        dp = self._get_datapoint_dict(rawdp)

        # The 'wult_tdt' driver does not handle the 'POLL' state correctly.
        if self._ep.dev.drvname == "wult_tdt" and self._is_poll_idle(dp):
            _LOG.debug("dropping the datapoint with 'POLL' idle state as 'wult_tdt' driver does "
                       "not handle it correctly")
            return None

        if dp["TotCyc"] == 0:
            # This should not happen.
            raise Error(f"Zero total cycles ('TotCyc'), this should never happen, unless there is "
                        f"a bug. The datapoint is:\n{_dump_dp(dp)}") from None

        if not self._is_poll_idle(dp):
            # Inject additional C-state information to the datapoint.
            # * CStatesCyc - combined count of CPU cycles in all non-CC0 C-states.
            # * DerivedCC1Cyc - software-calculated CC1 cycles, which is useful to have because not
            #                   every Intel platform has a HW CC1 counter. Calculated as "total
            #                   cycles" - "cycles in C-states other than CC1".
            cyc = sum([dp[name] for name in dp if name.startswith("CC") and name != "CC1Cyc"])
            if self._is_intel:
                dp["DerivedCC1Cyc"] = dp["TotCyc"] - cyc
                dp["CStatesCyc"] = dp["TotCyc"] - dp["CC0Cyc"]
            else:
                dp["CStatesCyc"] = dp["TotCyc"] - cyc
            if dp["DerivedCC1Cyc"] < 0:
                # The C-state counters are not always precise, and we may end up with a negative
                # number.
                dp["DerivedCC1Cyc"] = 0
            if dp["CStatesCyc"] < 0:
                raise Error(f"negative 'CStatesCyc', the datapoint is:\n{_dump_dp(dp)}")
        else:
            dp["DerivedCC1Cyc"] = dp["CStatesCyc"] = 0

        # Inject 'IntrDelay' - the interrupt delay.
        dp["IntrDelay"] = dp["IntrLatency"] - dp["WakeLatency"]

        # Add the C-state percentages.
        for cscyc_colname, csres_colname in self._cs_colnames:
            # In case of POLL state, calculate only CC0%.
            if not self._is_poll_idle(dp) or cscyc_colname == "CC0Cyc":
                dp[csres_colname] = dp[cscyc_colname] / dp["TotCyc"] * 100.0
            else:
                dp[csres_colname] = 0

        # Turn the C-state index into the C-state name.
        try:
            dp["ReqCState"] = self._csinfo[dp["ReqCState"]]["name"]
        except KeyError:
            # Supposedly an bad C-state index.
            indexes_str = ", ".join(f"{idx} ({val['name']})" for idx, val in  self._csinfo.items())
            raise Error(f"bad C-state index '{dp['ReqCState']}' in the following datapoint:\n"
                        f"{_dump_dp(dp)}\nAllowed indexes are:\n{indexes_str}") from None

        # Save time in microseconds.
        times_us = {}
        for colname, val in dp.items():
            if colname in self._us_colnames:
                times_us[colname] = val / 1000
        dp.update(times_us)

        return dp

    def _validate_datapoint(self, rawhdr, rawdp):
        """
        Validate a new datapoint - it should contain the same amount of elements as the previous
        datapoints.
        """

        if len(rawhdr) != len(self._rawhdr) or len(rawdp) != len(self._rawhdr):
            oldhdr = ", ".join(self._rawhdr)
            newhdr = ", ".join(rawhdr)
            newdp = ", ".join(rawdp)
            raise Error(f"the very first datapoint had {len(rawhdr)} elements, but a newer "
                        f"datapoint has {len(self._rawhdr)} elements\n"
                        f"Fist datapoint header: {oldhdr}\n"
                        f"New datapoint header:  {newhdr}\n"
                        f"New datapoint data:    {newdp}\n"
                        f"New datapoint, full ftrace line: {self._ftrace.raw_line}")

    def _collect(self, dpcnt, tlimit):
        """
        Collect datapoints and stop when either the CSV file has 'dpcnt' datapoints in total or when
        collection time exceeds 'tlimit' (value '0' or 'None' means "no limit"). Returns count of
        collected datapoints. If the filters were configured, the returned value counts only those
        datapoints that passed the filters.
        """

        datapoints = self._get_datapoints()
        rawhdr, rawdp = next(datapoints)

        self._rawhdr = list(rawhdr)
        rawhdr = list(rawhdr)
        dp = self._get_datapoint_dict(rawdp)

        # Add the more metrics to the raw header - we'll be injecting the values in
        # '_process_datapoint()'.
        rawhdr.insert(rawhdr.index("IntrLatency") + 1, "IntrDelay")
        if self._is_intel:
            rawhdr.insert(rawhdr.index("CC0Cyc") + 1, "DerivedCC1Cyc")
        rawhdr.append("CStatesCyc")

        # Now 'rawhdr' contains information about C-state of the measured platform, save it for
        # later use.
        self._cs_colnames = list(Defs.get_cs_colnames(rawhdr))

        # Driver sends time data in nanoseconds, build list of columns which we need to convert to
        # microseconds.
        defs = Defs.Defs(self._res.info["toolname"])
        self._us_colnames = [colname for colname, vals in defs.info.items() \
                             if vals.get("unit") == "microsecond"]

        # The raw CSV header (the one that comes from the trace buffer) does not include C-state
        # residency, it only provides the C-state cycle counters. We'll be calculating residencies
        # later and include them too, so extend the raw CSV header.
        for _, csres_colname in self._cs_colnames:
            rawhdr.append(csres_colname)
        self._res.csv.add_header(rawhdr)

        # At least one datapoint should be collected within the 'timeout' seconds interval.
        timeout = self._timeout * 1.5
        start_time = last_collected_time = time.time()
        collected_cnt = 0
        for rawhdr, rawdp in datapoints:
            if tlimit and time.time() - start_time > tlimit:
                break

            if time.time() - last_collected_time > timeout:
                raise ErrorTimeOut(f"no datapoints accepted for {timeout} seconds. While the "
                                   f"driver does produce them, they are being rejected. One "
                                   f"possible reason is that they do not pass filters/selectors.")

            self._validate_datapoint(rawhdr, rawdp)
            dp = self._process_datapoint(rawdp)
            if not dp:
                continue

            # Add the data to the CSV file.
            if not self._res.add_csv_row(dp):
                # the data point has not been added (e.g., because it did not pass raw filters).
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

    def __init__(self, proc, dev, res, ldist=None, csinfo=None, lscpu_info=None, stconf=None):
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
        self._rawhdr = None
        self._cs_colnames = None
        self._us_colnames = None
        self._progress = None
        self._max_latency = 0
        self._sysctl = None
        self._has_irqbalance = None
        self._post_trigger = None
        self._post_trigger_range = []
        self._stcoll = None

        self._validate_sut()

        self._progress = _ProgressLine.ProgressLine(period=1)
        self._ep = EventsProvider.EventsProvider(dev, res.cpunum, proc, ldist=self._ldist)
        self._ftrace = _FTrace.FTrace(proc=proc, timeout=self._timeout)

        if self._csinfo is None:
            with CPUIdle.CPUIdle(proc=proc) as cpuidle:
                self._csinfo = cpuidle.get_cstates_info_dict(res.cpunum)

        # Check that there are idle states that we can measure.
        idle_present = False # An idle state is present, including POLL idle state.
        cstate_present = False # A real C-state is present (POLL idle excluded).
        for info in self._csinfo.values():
            if not info["disable"]:
                idle_present = True
                if info["name"] != "POLL":
                    cstate_present = True

        if not idle_present:
            raise Error(f"no idle states are enabled on CPU {res.cpunum}{proc.hostmsg}")
        if not cstate_present and self._ep.dev.info["devid"] == "tdt":
            msg = ""
            if idle_present:
                msg = "\nNote, the 'tdt' method does not support measuring the POLL idle state, " \
                      "use 'hrtimer' or 'i210' for measuring the POLL idle state."
            raise Error(f"no C-states are enabled on CPU {res.cpunum}{proc.hostmsg}{msg}")

        if not lscpu_info:
            lscpu_info = CPUInfo.get_lscpu_info(proc=proc)
        self._is_intel = lscpu_info["vendor"] == "GenuineIntel"
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
