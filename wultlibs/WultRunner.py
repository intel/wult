# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2021 Intel Corporation
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
from pepclibs.helperlibs.Exceptions import Error, ErrorTimeOut
from pepclibs.helperlibs import Systemctl
from wultlibs import EventsProvider, _FTrace, _ProgressLine, _WultDpProcess, WultStatsCollect
from wultlibs.helperlibs import Human

_LOG = logging.getLogger()

# Maximum count of unexpected lines in the trace buffer we tolerate.
_MAX_FTRACE_BAD_LINES = 10

class WultRunner:
    """Run wake latency measurement experiments."""

    def _validate_datapoint(self, fields, vals):
        """
        This is a helper function for '_get_datapoints()' which checks that every raw datapoint
        from the trace buffer has the same fields in the same order.
        """

        if len(fields) != len(self._fields) or len(vals) != len(self._fields) or \
           not all(f1 == f2 for f1, f2 in zip(fields, self._fields)):
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

    def _collect(self, dpcnt, tlimit, keep_rawdp):
        """
        Collect datapoints and stop when either the CSV file has 'dpcnt' datapoints in total or when
        collection time exceeds 'tlimit' (value '0' or 'None' means "no limit"). Returns count of
        collected datapoints. If the filters were configured, the returned value counts only those
        datapoints that passed the filters.
        """

        datapoints = self._get_datapoints()
        rawdp = next(datapoints)

        _LOG.info("Calculating TSC rate for %s", Human.duration(self._dpp.tsc_cal_time))

        # We could actually process this datapoint, but we prefer to drop it and start with the
        # second one.
        self._dpp.prepare(rawdp, keep_rawdp)

        latkey = "IntrLatency" if self._intr_focus else "WakeLatency"

        # At least one datapoint should be collected within the 'timeout' seconds interval.
        timeout = self._timeout * 1.5
        start_time = last_rawdp_time = time.time()
        collected_cnt = 0
        tsc_rate_printed = False

        for rawdp in datapoints:
            if time.time() - last_rawdp_time > timeout:
                raise ErrorTimeOut(f"no datapoints accepted for {timeout} seconds. While the "
                                   f"driver does produce them, they are being rejected. One "
                                   f"possible reason is that they do not pass filters/selectors.")

            self._dpp.add_raw_datapoint(rawdp)

            if not self._dpp.tsc_mhz:
                # TSC rate has not been calculated yet.
                continue
            if not tsc_rate_printed:
                _LOG.info("TSC rate is %.6f MHz", self._dpp.tsc_mhz)
                tsc_rate_printed = True

            for dp in self._dpp.get_processed_datapoints():
                if not self._res.csv.hdr:
                    # Add the first CSV header.
                    self._res.csv.add_header(dp.keys())

                # Add the data to the CSV file.
                if not self._res.add_csv_row(dp):
                    # The data point has not been added (e.g., because it did not pass row filters).
                    continue

                self._max_latency = max(dp[latkey], self._max_latency)
                self._progress.update(collected_cnt, self._max_latency)
                last_rawdp_time = time.time()

                collected_cnt += 1
                if collected_cnt >= dpcnt:
                    break

            if tlimit and time.time() - start_time > tlimit or collected_cnt >= dpcnt:
                break

        return collected_cnt

    def run(self, dpcnt=1000000, tlimit=None, keep_rawdp=False):
        """
        Start the measurements. The arguments are as follows.
          * dpcnt - count of datapoints to collect.
          * tlimit - the measurements time limit in seconds.
          * keep_rawdp - by default, raw datapoint fields are dropped and do not make it to the
                         'datapoints.csv' file. But if 'keep_rawdp' is 'True', all the raw datapoint
                         fields will also be saved in the CSV file.
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
            collected_cnt = self._collect(dpcnt, tlimit, keep_rawdp)
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

        # The 'irqbalance' service usually causes problems by binding the delayed events (NIC
        # interrupts) to CPUs different form the measured one. Stop the service.
        if self._ep.dev.drvname == "wult_igb":
            self._sysctl = Systemctl.Systemctl(proc=self._proc)
            self._has_irqbalance = self._sysctl.is_active("irqbalance")
            if self._has_irqbalance:
                _LOG.info("Stopping the 'irqbalance' service")
                self._sysctl.stop("irqbalance")

        self._ep.unload = self.unload
        self._ep.prepare()

        # Validate the delayed event resolution.
        resolution = self._ep.get_resolution()
        _LOG.debug("delayed event resolution %dns", resolution)

        # Save the test setup information in the info.yml file.
        self._res.info["devid"] = self._ep.dev.info["devid"]
        self._res.info["devdescr"] = self._ep.dev.info["descr"]
        self._res.info["resolution"] = resolution
        self._res.info["intr_focus"] = self._intr_focus
        self._res.info["early_intr"] = self._early_intr
        if self._dcbuf_size:
            self._res.info["dcbuf_size"] = self._dcbuf_size

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

    def __init__(self, proc, dev, res, ldist=None, intr_focus=None, early_intr=None,
                 tsc_cal_time=10, dcbuf_size=None, rcsobj=None, stconf=None):
        """
        The class constructor. The arguments are as follows.
          * proc - the 'Proc' or 'SSH' object that defines the host to run the measurements on.
          * dev - the delayed event device object created by 'Devices.WultDevice()'.
          * res - the 'WORawResult' object to store the results at.
          * ldist - a pair of numbers specifying the launch distance range. The default value is
                    specific to the delayed event driver.
          * intr_focus - enable inerrupt latency focused measurements ('WakeLatency' is not measured
                         in this case, only 'IntrLatency').
          * early_intr - enable intrrupts before entering the C-state.
          * tsc_cal_time - amount of senconds to use for calculating TSC rate.
          * rcsobj - the 'Cstates.ReqCStates()' object initialized for the measured system.
          * dcbuf_size - size of a memory buffer to write to before requesting C-states in order to
                         "dirty" the CPU cache. By default the CPU cache dirtying fetature is
                         disabled. The size has to be an integer amount of bytes.
          * stconf - the statistics configuration, a dictionary describing the statistics that
                     should be collected. By default no statistics will be collected.
        """

        self._proc = proc
        self._dev = dev
        self._res = res
        self._ldist = ldist
        self._intr_focus = intr_focus
        self._early_intr = early_intr
        self._dcbuf_size = dcbuf_size
        self._stconf = stconf

        # This is a debugging option that allows to disable automatic wult modules unloading on
        # 'close()'.
        self.unload = True

        self._dpp = None
        self._ep = None
        self._ftrace = None
        self._timeout = 10
        self._fields = None
        self._progress = None
        self._max_latency = 0
        self._sysctl = None
        self._has_irqbalance = None
        self._stcoll = None

        if res.info["toolname"] != "wult":
            raise Error(f"unsupported non-wult test result at {res.dirpath}.\nPlease, provide a "
                        f"wult test result.")

        self._validate_sut()

        self._progress = _ProgressLine.ProgressLine(period=1)
        self._ep = EventsProvider.EventsProvider(dev, res.cpunum, proc, ldist=self._ldist,
                                                 intr_focus=self._intr_focus,
                                                 early_intr=self._early_intr,
                                                 dcbuf_size=self._dcbuf_size)
        self._ftrace = _FTrace.FTrace(proc=proc, timeout=self._timeout)

        if self._ep.dev.drvname == "wult_tdt" and self._intr_focus:
            raise Error("the 'tdt' driver does not support the interrupt latency focused "
                        "measurements")

        if self._ep.dev.drvname == "wult_tdt" and self._early_intr:
            raise Error("the 'tdt' driver does not support the early interrupt feature")

        self._dpp = _WultDpProcess.DatapointProcessor(res.cpunum, proc, self._ep.dev.drvname,
                                                      intr_focus=self._intr_focus,
                                                      early_intr=self._early_intr,
                                                      tsc_cal_time=tsc_cal_time, rcsobj=rcsobj)

    def close(self):
        """Stop the measurements."""

        if getattr(self, "_proc", None):
            self._proc = None
        else:
            return

        if getattr(self, "_dev", None):
            self._dev = None

        if getattr(self, "_dpp", None):
            self._dpp.close()
            self._dpp = None

        if getattr(self, "_stcoll", None):
            self._stcoll.close()
            self._stcoll = None

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
                # We saw failures here on a system that was running irqbalance, but the user
                # offlined all the CPUs except for CPU0. We were able to stop the service, but could
                # not start it again, probably because there is only one CPU.
                _LOG.warning("failed to start the previously stoopped 'irqbalance' service:\n%s",
                             err)
            self._sysctl = None

    def __enter__(self):
        """Enter the run-time context."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the runtime context."""
        self.close()
