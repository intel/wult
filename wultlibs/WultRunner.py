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
from wultlibs.helperlibs import Dmesg, FSHelpers, Trivial
from wultlibs.sysconfiglibs import CPUIdle, Systemctl
from wultlibs import _common, EventsProvider, Helpers, Defs, _FTrace, _ProgressLine

_LOG = logging.getLogger("main")

# Maximum count of unexpected lines in the trace buffer we tolerate.
_MAX_FTRACE_BAD_LINES = 10

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

        yield_time = time.time()

        for line in self._ftrace.getlines():
            if time.time() - yield_time > self._timeout:
                raise ErrorTimeOut(f"no wult data in trace buffer for {self._timeout} seconds"
                                   f"{self._proc.hostmsg}. Last seen non-wult line:\n{line.msg}")

            # Wult output format should be: name1=val1 name2=val2, and so on. Parse the line and get
            # the list of (name, val) pairs: [(name1, val1), (name2, val2), ... ].
            try:
                pairs = [pair.split("=") for pair in line.msg.split()]
                names, vals = zip(*pairs)
                if len(names) != len(vals):
                    raise ValueError
            except ValueError:
                _LOG.debug("unexpected line in ftrace buffer%s:\n%s", self._proc.hostmsg, line.msg)
                continue

            yield_time = time.time()
            yield names, vals

    def _process_datapoint(self, rawdp):
        """
        Process a raw datapoint and return it as dictionary. The "raw" part in this contents means
        that the 'rawdp' list contains data provided by the kernel driver. This methods is going to
        amend and extend it.
        """

        dp = dict(zip(self._res.csv.hdr, [int(elt) for elt in rawdp]))

        # Add the C-state percentages.
        for cscyc_colname, csres_colname in self._cs_colnames:
            csres = dp[cscyc_colname] / dp["TotCyc"] * 100.0
            dp[csres_colname] = f"{csres:.2f}"

        # Turn the C-state index into the C-state name.
        try:
            dp["ReqCState"] = self._cstates[dp["ReqCState"]]
        except KeyError:
            # Supposedly an bad C-state index.
            raise Error(f"bad C-state index '{dp['ReqCState']}' coming from the following FTrace "
                        f"line:\n  {self._ftrace.raw_line}")

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

    def _collect(self, dpcnt):
        """Collect datapoints and stop when the CSV file has 'dpcnt' datapoints in total."""

        datapoints = self._get_datapoints()
        rawhdr, rawdp = next(datapoints)

        # Now 'rawhdr' contains information about C-state of the measured platform, save it for
        # later use.
        self._cs_colnames = list(Defs.get_cs_colnames(rawhdr))
        self._rawhdr = list(rawhdr)

        # The raw CSV header (the one that comes from the trace buffer) does not include C-state
        # residency, it only provides the C-state cycle counters. We'll be calculating residencies
        # later and include them too, so extend the raw CSV header.
        rawhdr = list(rawhdr)
        for _, csres_colname in self._cs_colnames:
            rawhdr.append(csres_colname)
        self._res.csv.add_header(rawhdr)

        for rawhdr, rawdp in datapoints:
            self._validate_datapoint(rawhdr, rawdp)
            dp = self._process_datapoint(rawdp)
            # Add the data to the CSV file.
            self._res.csv.add_row([dp[key] for key in self._res.csv.hdr])

            if self._post_trigger:
                self._run_post_trigger(dp["WakeLatency"])

            self._max_latency = max(dp["WakeLatency"], self._max_latency)
            self._progress.update(self._res.csv.rows_cnt, self._max_latency)

            dpcnt -= 1
            if dpcnt <= 0:
                break

    def _get_dmesg_msgs(self, old_dmesg):
        """Return new dmesg messages if available."""

        if not self.dmesg:
            return ""
        new_msgs = Dmesg.get_new_messages(old_dmesg, self._proc, join=True, strip=True)
        if new_msgs:
            return f"\nNew kernel messages{self._proc.hostmsg}:\n{new_msgs}"
        return ""

    def run(self, dpcnt=1000000):
        """
        Start the measurements. The arguments are as follows.
          * dpcnt - count of datapoints to collect.
        """

        dpcnt = Helpers.get_dpcnt(self._res, dpcnt)
        if not dpcnt:
            return

        if self.dmesg:
            old_dmesg = Dmesg.capture(self._proc)
        else:
            old_dmesg = None

        self._res.write_info()

        _LOG.info("Start measuring CPU %d%s, collecting %d datapoints",
                  self._res.cpunum, self._proc.hostmsg, dpcnt)

        self._progress.start()

        try:
            self._ep.start()
            self._collect(dpcnt)
        except Error as err:
            raise Error(f"{err}{self._get_dmesg_msgs(old_dmesg)}")
        finally:
            self._progress.update(self._res.csv.rows_cnt, self._max_latency, final=True)

        _LOG.info("Finished measuring CPU %d%s", self._res.cpunum, self._proc.hostmsg)

    def _get_cmdline(self):
        """Get kernel boot parameters."""

        try:
            with self._proc.open("/proc/cmdline", "r") as fobj:
                return fobj.read().strip()
        except Error:
            raise Error(f"failed to read cmdline parameters{self._proc.hostmsg}")

    def prepare(self):
        """Prepare for starting the measurements."""

        # The 'irqbalance' service usually causes problems by binding the delayed event to a CPU
        # different form the measured one. Stop the service.
        if self._has_irqbalance:
            _LOG.info("Stopping the 'irqbalance' service")
            self._sysctl.stop("irqbalance")

        self._ep.unload = self.unload
        self._ep.dmesg = self.dmesg
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
                    errmsg += f"\nMake sure your kernel has high resolution timers enabled " \
                              f"(CONFIG_HIGH_RES_TIMERS)"

                    with contextlib.suppress(Error):
                        cmdline = self._get_cmdline()
                        if "highres=off" in cmdline:
                            errmsg += f"\nYour system uses the 'highres=off' kernel boot " \
                                      f"parameter, try removing it"

                raise Error(errmsg)
            _LOG.warning(errmsg)

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

        if trange is not None:
            vals = Trivial.split_csv_line(trange)

            for idx, val in enumerate(vals):
                if not Trivial.is_int(val):
                    raise Error(f"bad post-trigger range value '{val}', should be an integer "
                                f"amount of nanoseconds")
                vals[idx] = Trivial.str_to_num(val, default=None)
                if vals[idx] < 0:
                    raise Error(f"bad post trigger range value '{vals[idx]}', should be greater or "
                                f"equal to zero")

            if len(vals) != 2:
                raise Error(f"bad post trigger range '{trange}', it should include 2 numbers")
            if vals[1] - vals[0] < 0:
                raise Error(f"bad post trigger range '{trange}', first number cannot be greater "
                            f"than the second number")

            self._post_trigger_range = vals

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
            except Error:
                raise Error(errmsg)

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

    def __init__(self, proc, devid, res, ldist=None, force=False):
        """
        The class constructor. The arguments are as follows.
          * proc - the 'Proc' or 'SSH' object that defines the host to run the measurements on.
          * devid - the device "ID", which can be a PCI address of a network interface name.
          * res - the 'WORawResult' object to store the results at.
          * ldist - string of single, or comma-separated integers telling how far in future the
                    delayed event should be scheduled. Default is specific to the delayed event
                    driver.
          * force - initialize measurement device, even if it is already in use.
        """

        self._proc = proc
        self._devid = devid
        self._res = res
        self._ldist = ldist

        # This is a debugging option that allows to disable automatic wult modules unloading on
        # 'close()'.
        self.unload = True
        # Whether kernel messages should be monitored. They are very useful if something goes wrong.
        self.dmesg = True

        self._ep = None
        self._ftrace = None
        self._timeout = 10
        self._rawhdr = None
        self._cs_colnames = None
        self._progress = None
        self._cstates = {}
        self._max_latency = 0
        self._sysctl = None
        self._has_irqbalance = None
        self._post_trigger = None
        self._post_trigger_range = []

        _common.validate_cpunum(res.cpunum, proc=proc)
        if self._ldist:
            self._ldist = _common.validate_ldist(self._ldist)
        self._validate_sut()

        self._progress = _ProgressLine.ProgressLine(period=1)
        self._ep = EventsProvider.EventsProvider(devid, res.cpunum, proc, ldist=self._ldist,
                                                 force=force)
        self._ftrace = _FTrace.FTrace(proc=proc, timeout=self._timeout)

        cstates_present = False
        # Build the C-state index -> name mapping. And check for enabled C-states.
        with CPUIdle.CPUIdle(proc=proc) as cpuidle:
            for info in cpuidle.get_cstates_info(res.cpunum):
                self._cstates[info["index"]] = info["name"]
                if info["name"] != "POLL" and info["disable"] == 0:
                    cstates_present = True

        if not cstates_present:
            raise Error(f"no C-states enabled on CPU {res.cpunum}")

        self._sysctl = Systemctl.Systemctl(proc=proc)
        self._has_irqbalance = self._sysctl.is_active("irqbalance")

    def close(self):
        """Stop the measurements."""

        if getattr(self, "_proc", None):
            self._proc = None
        else:
            return

        if getattr(self, "_ep", None):
            self._ep.close()

        if getattr(self, "_ftrace", None):
            self._ftrace.close()

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

    def __enter__(self):
        """Enter the run-time context."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the runtime context."""
        self.close()
