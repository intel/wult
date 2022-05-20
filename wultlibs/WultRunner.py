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
from pepclibs.helperlibs import ClassHelpers
from wultlibs import _WultRawDataProvider, _ProgressLine, _WultDpProcess, WultStatsCollect
from wultlibs.helperlibs import Human

_LOG = logging.getLogger()

# Maximum count of unexpected lines in the trace buffer we tolerate.
_MAX_FTRACE_BAD_LINES = 10

class WultRunner(ClassHelpers.SimpleCloseContext):
    """Run wake latency measurement experiments."""

    def _collect(self, dpcnt, tlimit, keep_rawdp):
        """
        Collect datapoints and stop when either the CSV file has 'dpcnt' datapoints in total or when
        collection time exceeds 'tlimit' (value '0' or 'None' means "no limit").
        """

        datapoints = self._prov.get_datapoints()
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
        max_latency = 0
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

                max_latency = max(dp[latkey], max_latency)
                self._progress.update(collected_cnt, max_latency)
                last_rawdp_time = time.time()

                collected_cnt += 1
                if collected_cnt >= dpcnt:
                    break

            if tlimit and time.time() - start_time > tlimit or collected_cnt >= dpcnt:
                break

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

        msg = f"Start measuring CPU {self._res.cpunum}{self._pman.hostmsg}, collecting {dpcnt} " \
              f"datapoints"
        if tlimit:
            msg += f", time limit is {Human.duration(tlimit)}"
        _LOG.info(msg)

        # Start printing the progress.
        self._progress.start()

        try:
            self._prov.start()
            self._collect(dpcnt, tlimit, keep_rawdp)
        except (KeyboardInterrupt, Error) as err:
            self._progress.update(self._progress.dpcnt, self._progress.maxlat, final=True)

            is_ctrl_c = isinstance(err, KeyboardInterrupt)
            if is_ctrl_c:
                # In Linux Ctrl-c prints '^C' on the terminal. Make sure the next output line does
                # not look messy.
                print("\r", end="")
                _LOG.notice("interrupted, stopping the measurements")

            if self._stcoll:
                with contextlib.suppress(Error):
                    self._stcoll.stop()
                with contextlib.suppress(Error):
                    self._stcoll.copy_stats()

            if is_ctrl_c:
                raise

            dmesg = ""
            with contextlib.suppress(Error):
                dmesg = "\n" + self._dev.get_new_dmesg()
            raise Error(f"{err}{dmesg}") from err
        else:
            self._progress.update(self._progress.dpcnt, self._progress.maxlat, final=True)

        _LOG.info("Finished measuring CPU %d%s", self._res.cpunum, self._pman.hostmsg)

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
            with self._pman.open("/proc/cmdline", "r") as fobj:
                return fobj.read().strip()
        except Error as err:
            raise Error(f"failed to read cmdline parameters{self._pman.hostmsg}") from err

    def prepare(self):
        """Prepare for starting the measurements."""

        self._prov.prepare()

        # Save the test setup information in the info.yml file.
        self._res.info["date"] = time.strftime("%d %b %Y")
        self._res.info["devid"] = self._dev.info["devid"]
        self._res.info["devdescr"] = self._dev.info["descr"]
        self._res.info["resolution"] = self._dev.info["resolution"]
        self._res.info["intr_focus"] = self._intr_focus
        self._res.info["early_intr"] = self._early_intr

        # Initialize statistics collection.
        if self._stconf:
            self._stcoll = WultStatsCollect.WultStatsCollect(self._pman, self._res)
            self._stcoll.apply_stconf(self._stconf)

    def _validate_sut(self):
        """Check the SUT to insure we have everything to measure it."""

        # Make sure a supported idle driver is in use.
        path = Path("/sys/devices/system/cpu/cpuidle/current_driver")
        with self._pman.open(path, "r") as fobj:
            drvname = fobj.read().strip()

        if drvname == "none":
            errmsg = f"no idle driver in use{self._pman.hostmsg}"
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
            raise Error(f"unsupported idle driver '{drvname}'{self._pman.hostmsg},\n"
                        f"only the following drivers are supported: {supported}")

    def __init__(self, pman, dev, res, ldist=None, intr_focus=None, early_intr=None,
                 tsc_cal_time=10, rcsobj=None, stconf=None):
        """
        The class constructor. The arguments are as follows.
          * pman - the process manager object that defines the host to run the measurements on.
          * dev - the delayed event device object created by 'Devices.GetDevice()'.
          * res - the 'WORawResult' object to store the results at.
          * ldist - a pair of numbers specifying the launch distance range. The default value is
                    specific to the delayed event driver.
          * intr_focus - enable inerrupt latency focused measurements ('WakeLatency' is not measured
                         in this case, only 'IntrLatency').
          * early_intr - enable intrrupts before entering the C-state.
          * tsc_cal_time - amount of senconds to use for calculating TSC rate.
          * rcsobj - the 'Cstates.ReqCStates()' object initialized for the measured system.
          * stconf - the statistics configuration, a dictionary describing the statistics that
                     should be collected. By default no statistics will be collected.
        """

        self._pman = pman
        self._dev = dev
        self._res = res
        self._ldist = ldist
        self._intr_focus = intr_focus
        self._early_intr = early_intr
        self._stconf = stconf

        self._dpp = None
        self._prov = None
        self._timeout = 10
        self._progress = None
        self._stcoll = None

        if res.info["toolname"] != "wult":
            raise Error(f"unsupported non-wult test result at {res.dirpath}.\nPlease, provide a "
                        f"wult test result.")

        self._validate_sut()

        if self._dev.drvname == "wult_tdt" and self._intr_focus:
            raise Error("the 'tdt' driver does not support the interrupt latency focused "
                        "measurements")

        if self._dev.drvname == "wult_tdt" and self._early_intr:
            raise Error("the 'tdt' driver does not support the early interrupt feature")

        self._progress = _ProgressLine.ProgressLine(period=1)

        self._prov = _WultRawDataProvider.WultRawDataProvider(dev, res.cpunum, pman,
                                                              timeout=self._timeout,
                                                              ldist=self._ldist,
                                                              intr_focus=self._intr_focus,
                                                              early_intr=self._early_intr)

        self._dpp = _WultDpProcess.DatapointProcessor(res.cpunum, pman, self._dev.drvname,
                                                      intr_focus=self._intr_focus,
                                                      early_intr=self._early_intr,
                                                      tsc_cal_time=tsc_cal_time, rcsobj=rcsobj)

    def close(self):
        """Stop the measurements."""

        close_attrs = ("_dpp", "_prov", "_stcoll")
        unref_attrs = ("_dev", "_pman")
        ClassHelpers.close(self, close_attrs=close_attrs, unref_attrs=unref_attrs)
