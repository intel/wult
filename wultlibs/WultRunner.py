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
from pepclibs import CPUIdle
from pepclibs.helperlibs.Exceptions import Error, ErrorTimeOut
from pepclibs.helperlibs import ClassHelpers, KernelVersion
from statscollectlibs.deploylibs import DeployBase
from wultlibs import _WultRawDataProvider, _ProgressLine, _WultDpProcess
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
                # 6.4+ kernels have a bug where synthetic trace events passed from kernel print out
                # pointer values instead of the value itself. Detect the situation by checking for
                # ridiculously high SMICnt which can never happen, and additionally checking that we
                # have running pointer values in the adjacent data values (in the wult drivers,
                # address of the NMICnt is SMICnt + 8 as the data type is u64.)
                if rawdp['SMICnt'] > 1000000 and rawdp['SMICnt'] + 8 == rawdp['NMICnt']:
                    kver = KernelVersion.get_kver(pman=self._pman)
                    if KernelVersion.kver_ge(kver, "6.4") and KernelVersion.kver_lt(kver, "6.7"):
                        raise Error(f"kernel bug detected with kernel {kver}. Trace subsystem with "
                                    f"6.4-6.6 kernels is known to be bugged, please upgrade your "
                                    f"kernel to latest stable or 6.6-rc2.")

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

    def _stop_run(self):
        """
        This is a helper for 'run()' which takes care of the post-run phase of some data providers.
        """

        self._res.info["duration"] = Human.duration(self._progress.get_duration())
        self._res.write_info()

        self._prov.stop()

        if self._stcoll:
            self._stcoll.stop(sysinfo=True)
            self._stcoll.finalize()

    def run(self, dpcnt=1000000, tlimit=None, keep_rawdp=False):
        """
        Start the measurements. The arguments are as follows.
          * dpcnt - count of datapoints to collect.
          * tlimit - the measurements time limit in seconds.
          * keep_rawdp - by default, many raw datapoint fields are dropped and do not make it to the
                         'datapoints.csv' file. But if 'keep_rawdp' is 'True', all the datapoint raw
                         fields will also be saved in the CSV file.
        """

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

            if isinstance(err, KeyboardInterrupt):
                if self._progress.enabled:
                    # In Linux Ctrl-c prints '^C' on the terminal. Make sure the next output line
                    # does not look messy.
                    print("\r", end="")
                _LOG.notice("interrupted, stopping the measurements")
                with contextlib.suppress(Error):
                    self._stop_run()
                raise

            dmesg = ""
            with contextlib.suppress(Error):
                dmesg = "\n" + self._dev.get_new_dmesg()
            raise Error(f"{err}{dmesg}") from err

        self._progress.update(self._progress.dpcnt, self._progress.maxlat, final=True)
        duration = Human.duration(self._progress.get_duration())
        _LOG.info("Finished measuring CPU %d%s, lasted %s",
                  self._res.cpunum, self._pman.hostmsg, duration)
        self._stop_run()

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
                        _LOG.notice("found a message prefixed with '%s' in 'dmesg'%s:\n%s",
                                    variant, self._pman.hostmsg, dmesg)
                        _LOG.notice("the kernel printed these messages while wult was running.\n"
                                    "They do not necessarily mean that there is a problem with "
                                    "wult,\nbut you may consider reporting this to wult "
                                    "developers.")
                        break

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

    def _validate_sut(self):
        """Check the SUT to insure we have everything to measure it."""

        # Make sure a supported idle driver is in use.
        if not self._cpuidle:
            self._cpuidle = CPUIdle.CPUIdle(self._pman)

        drvname = self._cpuidle.get_idle_driver()
        if not drvname:
            errmsg = f"no idle driver in use{self._pman.hostmsg}"
            try:
                cmdline = self._get_cmdline()
            except Error as err:
                raise Error(errmsg) from err

            for opt in cmdline.split():
                if opt == "cpuidle.off=1" or opt.startswith("idle="):
                    errmsg += f". Your system has '{opt}' kernel boot parameter, try removing it."
                    raise Error(errmsg)

            raise Error(errmsg)

        supported = ("intel_idle", "acpi_idle")
        if drvname not in supported:
            supported = ", ".join(supported)
            raise Error(f"unsupported idle driver '{drvname}'{self._pman.hostmsg},\n"
                        f"only the following drivers are supported: {supported}")

    def __init__(self, pman, dev, res, ldist, tsc_cal_time=10, cpuidle=None, stcoll=None,
                 unload=True):
        """
        The class constructor. The arguments are as follows.
          * pman - the process manager object that defines the host to run the measurements on.
          * dev - the delayed event device object created by 'Devices.GetDevice()'.
          * res - the 'WORawResult' object to store the results at.
          * ldist - a pair of numbers specifying the launch distance range in nanoseconds.
          * tsc_cal_time - amount of seconds to use for calculating TSC rate.
          * cpuidle - the 'CPUIdle.CPUIdle()' object initialized for the measured system.
          * stcoll - the 'StatsCollect' object to use for collecting statistics. No statistics
                     are collected by default.
          * unload - whether or not to unload the kernel driver after finishing measurement.
        """

        self._pman = pman
        self._dev = dev
        self._res = res
        self._ldist = ldist
        self._cpuidle = cpuidle
        self._stcoll = stcoll

        self._close_cpuidle = cpuidle is None

        self._prov = None
        self._dpp = None
        self._timeout = 10
        self._progress = None

        if res.info["toolname"] != "wult":
            raise Error(f"unsupported non-wult test result at {res.dirpath}.\nPlease, provide a "
                        f"wult test result.")

        self._validate_sut()

        self._progress = _ProgressLine.WultProgressLine(period=1)

        if dev.helpername:
            helper_path = DeployBase.get_installed_helper_path("wult", "wult", dev.helpername,
                                                              pman=pman)
        else:
            helper_path = None

        self._prov = _WultRawDataProvider.WultRawDataProvider(dev, pman, res.cpunum, self._ldist,
                                                              helper_path=helper_path,
                                                              timeout=self._timeout,
                                                              unload=unload)

        self._dpp = _WultDpProcess.DatapointProcessor(res.cpunum, pman, self._dev.drvname,
                                                      tsc_cal_time=tsc_cal_time,
                                                      cpuidle=self._cpuidle)

    def close(self):
        """Stop the measurements."""

        close_attrs = ("_dpp", "_prov", "_cpuidle")
        unref_attrs = ("_res", "_dev", "_pman", "_stcoll")
        ClassHelpers.close(self, close_attrs=close_attrs, unref_attrs=unref_attrs)
