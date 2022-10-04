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
import contextlib
from pepclibs import CStates
from pepclibs.helperlibs.Exceptions import Error, ErrorTimeOut
from pepclibs.helperlibs import ClassHelpers
from wultlibs import _WultRawDataProvider, _ProgressLine, _WultDpProcess, Deploy
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

        # We could actually process this datapoint, but we prefer to drop it and start with the
        # second one.
        self._dpp.prepare(rawdp, keep_rawdp)

        # At least one datapoint should be collected within the 'timeout' seconds interval.
        timeout = self._timeout * 1.5
        start_time = last_rawdp_time = time.time()
        collected_cnt = 0
        max_latency = 0

        for rawdp in datapoints:
            if time.time() - last_rawdp_time > timeout:
                raise ErrorTimeOut(f"no datapoints accepted for {timeout} seconds. While the "
                                   f"driver does produce them, they are being rejected. One "
                                   f"possible reason is that they do not pass filters/selectors.")

            self._dpp.add_raw_datapoint(rawdp)

            for dp in self._dpp.get_processed_datapoints():
                if not self._res.csv.hdr:
                    # Add the first CSV header.
                    self._res.csv.add_header(dp.keys())

                # Add the data to the CSV file.
                if not self._res.add_csv_row(dp):
                    # The data point has not been added (e.g., because it did not pass row filters).
                    continue

                # Interrupt latency and wake latency are measured one after another, and the order
                # depends on C-state interrupt order. Whatever is measured first is more accurate,
                # because of the measurement overhead. Let's use the smaller value for calculating
                # the max. latency that we print, assuming it was measured first and it is more
                # accurate and trustworthy.
                if "IntrLatency" in dp:
                    latency = min(dp["WakeLatency"], dp["IntrLatency"])
                else:
                    latency = dp["WakeLatency"]
                max_latency = max(latency, max_latency)
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
          * keep_rawdp - by default, many raw datapoint fields are dropped and do not make it to the
                         'datapoints.csv' file. But if 'keep_rawdp' is 'True', all the datapoint raw
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

            with contextlib.suppress(Error):
                self._prov.stop()

            if self._stcoll:
                with contextlib.suppress(Error):
                    # We do not consider Ctrl-c as an error, so collect the system information in
                    # that case.
                    self._stcoll.stop(sysinfo=is_ctrl_c)
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
            duration = Human.duration(self._progress.get_duration())
            _LOG.info("Finished measuring CPU %d%s, lasted %s",
                      self._res.cpunum, self._pman.hostmsg, duration)
            self._prov.stop()


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
        self._res.info["early_intr"] = self._early_intr

        if self._stcoll:
            self._stcoll.configure()

    def _validate_sut(self, cpunum):
        """Check the SUT to insure we have everything to measure it."""

        # Make sure a supported idle driver is in use.
        with CStates.CStates(pman=self._pman, rcsobj=self._rcsobj) as csobj:
            drvname = csobj.get_cpu_prop("idle_driver", cpunum)["idle_driver"]["idle_driver"]

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

    def __init__(self, pman, dev, res, ldist, early_intr=None, tsc_cal_time=10, rcsobj=None,
                 stcoll=None):
        """
        The class constructor. The arguments are as follows.
          * pman - the process manager object that defines the host to run the measurements on.
          * dev - the delayed event device object created by 'Devices.GetDevice()'.
          * res - the 'WultWORawResult' object to store the results at.
          * ldist - a pair of numbers specifying the launch distance range in nanoseconds.
          * early_intr - enable interrupts before entering the C-state.
          * tsc_cal_time - amount of seconds to use for calculating TSC rate.
          * rcsobj - the 'Cstates.ReqCStates()' object initialized for the measured system.
          * stcoll - the 'WultStatsCollect' object to use for collecting statistics. No statistics
                     are collected by default.
        """

        self._pman = pman
        self._dev = dev
        self._res = res
        self._ldist = ldist
        self._early_intr = early_intr
        self._stcoll = stcoll
        self._rcsobj = rcsobj

        self._dpp = None
        self._prov = None
        self._timeout = 10
        self._progress = None
        self._stcoll = None

        if res.info["toolname"] != "wult":
            raise Error(f"unsupported non-wult test result at {res.dirpath}.\nPlease, provide a "
                        f"wult test result.")

        self._validate_sut(res.cpunum)

        if self._dev.drvname == "wult_tdt" and self._early_intr:
            raise Error("the 'tdt' driver does not support the early interrupt feature")

        self._progress = _ProgressLine.ProgressLine(period=1)

        if dev.helpername:
            wultrunner_path = Deploy.get_installed_helper_path(pman, "wult", dev.helpername)
        else:
            wultrunner_path = None

        self._prov = _WultRawDataProvider.WultRawDataProvider(dev, pman, res.cpunum, self._ldist,
                                                              wultrunner_path=wultrunner_path,
                                                              timeout=self._timeout,
                                                              early_intr=self._early_intr)

        self._dpp = _WultDpProcess.DatapointProcessor(res.cpunum, pman, self._dev.drvname,
                                                      early_intr=self._early_intr,
                                                      tsc_cal_time=tsc_cal_time, rcsobj=rcsobj)

    def close(self):
        """Stop the measurements."""

        close_attrs = ("_dpp", "_prov", "_stcoll")
        unref_attrs = ("_res", "_dev", "_pman", "_rcsobj")
        ClassHelpers.close(self, close_attrs=close_attrs, unref_attrs=unref_attrs)
