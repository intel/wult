# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module implements the main ndl functionality - runs the measurement experiments and saves the
result.
"""

import time
import logging
import contextlib
from pepclibs.helperlibs import ClassHelpers
from pepclibs.helperlibs.Exceptions import Error
from wultlibs import Deploy, _ProgressLine, _NdlRawDataProvider
from wultlibs.helperlibs import Human

_LOG = logging.getLogger()

class NdlRunner(ClassHelpers.SimpleCloseContext):
    """Run the latency measurements."""

    def _collect(self, dpcnt, tlimit):
        """
        Collect datapoints and stop when the CSV file has 'dpcnt' datapoints in total, or when
        collection time exceeds 'tlimit' (value '0' or 'None' means "no limit").
        """

        datapoints = self._prov.get_datapoints()

        # Populate the CSV header first.
        dp = next(datapoints)
        self._res.csv.add_header(dp.keys())

        collected_cnt = 0
        max_rtd = 0
        start_time = time.time()

        for dp in datapoints:
            if tlimit and time.time() - start_time > tlimit:
                break

            max_rtd = max(dp["RTD"], max_rtd)
            _LOG.debug("launch distance: RTD %.2f (max %.2f), LDist %.2f",
                       dp["RTD"], max_rtd, dp["LDist"])

            if not self._res.add_csv_row(dp):
                continue

            collected_cnt += 1
            self._progress.update(collected_cnt, max_rtd)

            if collected_cnt >= dpcnt:
                break

    def run(self, dpcnt=1000000, tlimit=None):
        """
        Start the measurements. The arguments are as follows.
          * dpcnt - count of datapoints to collect.
          * tlimit - the measurements time limit in seconds.
        """

        msg = f"Start measuring RTD{self._pman.hostmsg}, collecting {dpcnt} datapoints"
        if tlimit:
            msg += f", time limit is {Human.duration(tlimit)}"
        _LOG.info(msg)

        self._prov.start()

        self._progress.start()
        try:
            self._collect(dpcnt, tlimit)
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

            self._res.info["duration"] = Human.duration(self._progress.get_duration())
            self._res.write_info()

            if is_ctrl_c:
                raise

            dmesg = ""
            with contextlib.suppress(Error):
                dmesg = "\n" + self._dev.get_new_dmesg()
            raise Error(f"{err}{dmesg}") from err
        else:
            self._progress.update(self._progress.dpcnt, self._progress.maxlat, final=True)
            duration = Human.duration(self._progress.get_duration())
            _LOG.info("Finished measuring RTD%s, lasted %s", self._pman.hostmsg, duration)
            self._res.info["duration"] = duration
            self._res.write_info()
            self._prov.stop()


    def prepare(self):
        """Prepare to start measurements."""

        self._prov.prepare()

    def __init__(self, pman, dev, res, ldist):
        """
        The class constructor. The arguments are as follows.
          * pman - the process manager object that defines the host to run the measurements on.
          * dev - the network device object to use for measurements (created with
                  'Devices.GetDevice()').
          * res - the 'NdlWORawResult' object to store the results at.
          * ldist - a pair of numbers specifying the launch distance range in nanoseconds (how far
          *         in the future the delayed network packets should be scheduled).
        """

        self._pman = pman
        self._dev = dev
        self._res = res
        self._ldist = ldist

        self._timeout = 10
        self._prov = None
        self._rtd_path = None
        self._progress = None

        self._progress = _ProgressLine.NdlProgressLine(period=1)

        ndlhelper_path = Deploy.get_installed_helper_path(pman, "ndl", dev.helpername)
        self._prov = _NdlRawDataProvider.NdlRawDataProvider(dev, pman, self._ldist, ndlhelper_path,
                                                            timeout=self._timeout)

        drvname = self._prov.drvobjs[0].name
        self._rtd_path = self._prov.debugfs_mntpoint.joinpath(f"{drvname}/rtd")

    def close(self):
        """Stop the measurements."""

        close_attrs = ("_prov",)
        unref_attrs = ("_res", "_dev", "_pman")
        ClassHelpers.close(self, close_attrs=close_attrs, unref_attrs=unref_attrs)
