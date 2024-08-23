# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2024 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module implements the main pbe functionality - runs power break even experiments and saves the
results.
"""

import time
import logging
import contextlib
from pepclibs.helperlibs import ClassHelpers
from pepclibs.helperlibs.Exceptions import Error
from wultlibs import _ProgressLine, _PbeRawDataProvider
from wultlibs.helperlibs import Human
from wulttools.pbe import ToolInfo

_LOG = logging.getLogger()

class PbeRunner(ClassHelpers.SimpleCloseContext):
    """Run power break-even measurement experiments."""

    NSEC_PER_SEC = 1000000000

    def _run_iteration(self, wper):
        """Run a single measurement iteration using wake period 'wper'."""

        _LOG.debug("warm-up for %s", self._hwarmup)
        time.sleep(self._warmup)

        _LOG.debug("collect for %s", self._hspan)
        self._stcoll.add_label("start", metrics={self._wper_metric: wper})
        time.sleep(self._span)
        self._stcoll.add_label("skip")

        self._res.add_csv_row({self._time_metric: time.time(), self._wper_metric: wper})

    def _get_wper(self):
        """Yields all wake period values to measure."""

        def _calc_next_wper(prev_wper):
            """Calculate and return the next wake period from the previous wake period."""

            if self._wper_step_pct:
                return wper + int((wper * self._wper_step_pct) / 100)
            return prev_wper + self._wper_step_ns

        wper = self._wper[0]
        yield wper

        while True:
            wper = _calc_next_wper(wper)
            if wper > self._wper[1]:
                return
            yield wper

    def _finish_run(self):
        """
        This is a helper for 'run()' which takes care of the post-run phase of some data providers.
        """

        self._stcoll.stop()
        self._stcoll.finalize()
        self._res.info["duration"] = Human.duration(self._progress.get_duration())
        self._res.write_info()

    def run(self):
        """Start the measurements."""

        self._res.write_info()

        _LOG.info("Will measure wake period range %s-%s, step %s, warmup %s, span %s",
                  self._hwper[0], self._hwper[1], self._hwper_step,
                  self._hwarmup, self._hspan)

        self._stcoll.add_label("skip")
        self._stcoll.start()
        self._progress.start()

        try:
            self._prov.set_wper(self._wper[0])
            self._prov.start()
            for wper in self._get_wper():
                self._prov.set_wper(wper)
                self._progress.update(wper)
                self._run_iteration(wper)
            self._prov.stop()
        except (KeyboardInterrupt, Error) as err:
            if self._prov.started:
                self._prov.stop()
            if isinstance(err, KeyboardInterrupt):
                # In Linux Ctrl-c prints '^C' on the terminal. Make sure the next output line does
                # not look messy.
                print("\r", end="")
                _LOG.notice("interrupted, stopping the measurements")
                with contextlib.suppress(Error):
                    self._finish_run()
            raise

        duration = Human.duration(self._progress.get_duration())
        _LOG.info("Finished the measurements%s, lasted %s", self._pman.hostmsg, duration)
        self._finish_run()

    def prepare(self):
        """Prepare for starting the measurements."""

        self._prov.prepare()

        self._res.csv.add_header([self._time_metric, self._wper_metric])

        self._res.info["date"] = time.strftime("%d %b %Y")
        self._res.info["devid"] = self._dev.info["devid"]
        self._res.info["devdescr"] = self._dev.info["descr"]
        self._res.info["resolution"] = self._dev.info["resolution"]

    def _validate_wper_step(self):
        """Validate 'self._wper_step_pct' and 'self._wper_step_ns'."""

        if self._wper_step_pct is None and self._wper_step_ns is None:
            raise Error("please provide the wake period step")

        if self._wper_step_pct and self._wper_step_ns:
            raise Error("please provide the wake period step either in percent or in nanoseconds, "
                        "but not both")

        if self._wper_step_pct is not None:
            if self._wper_step_pct < 0 or self._wper_step_pct > 100:
                raise Error(f"bad wake period step percent value '{self._wper_step_pct}', "
                            f"must be in the range of [0, 100%]")

        if self._wper_step_ns is not None:
            if self._wper_step_ns <= 0:
                raise Error(f"bad wake period step value '{self._wper_step_ns}', must be "
                            f"greater than 0")

    def _validate_span(self):
        """Validate 'self._span'."""

        if self._span * self.NSEC_PER_SEC < 100 * self._wper[1]:
            raise Error(f"too short span value '{self._hspan}'. It should be at least 100 times "
                        f"larger than max. wake period distance ({self._hwper[1]}).")

        min_span = 1
        if self._span < min_span:
            raise Error(f"too short span value '{self._hspan}'. It should be greater than "
                        f"{min_span} seconds.")

    def __init__(self, pman, dev, res, wper, span, warmup, stcoll, wper_step_pct=None,
                 wper_step_ns=None, lcpu=0):
        """
        The class constructor. The arguments are as follows.
          * pman - the process manager object that defines the host to run the measurements on.
          * dev - the delayed event device object created by 'Devices.GetDevice()'.
          * res - the 'WORawResult' object to store the results at.
          * wper - a pair of numbers specifying the wake period range in nanoseconds.
          * span - for how long to measure a single wake period in seconds.
          * warmup - the warm-up period in seconds.
          * stcoll - the 'StatsCollect' object to use for collecting statistics.
          * wper_step_pct - the wake period step in percent.
          * wper_step_ns - the wake period step in nanoseconds.
          * lcpu - the lead CPU. This CPU sets timers and triggers interrupts to wake all other
                   CPUs.
        """

        self._pman = pman
        self._dev = dev
        self._res = res
        self._wper = None
        self._span = span
        self._warmup = warmup
        self._stcoll = stcoll
        self._wper_step_pct = wper_step_pct
        self._wper_step_ns = wper_step_ns

        self._timeout = 10
        self._prov = None
        self._progress = None

        # The measurement parameters in human-readable format.
        self._hspan = None
        self._hwarmup = None
        self._hwper = None
        self._hwper_step = None

        self._wper_metric = "LDist"
        self._time_metric = "Time"

        self._prov = _PbeRawDataProvider.PbeRawDataProvider(dev, pman, wper, timeout=self._timeout,
                                                            lcpu=lcpu)

        self._wper = self._prov.ldist
        self._hwper = (Human.duration_ns(self._wper[0]), Human.duration_ns(self._wper[1]))

        self._hspan = Human.duration(self._span)
        self._hwarmup = Human.duration(self._warmup)

        if self._wper_step_pct:
            self._hwper_step = f"{self._wper_step_pct}%"
        else:
            self._hwper_step = Human.duration_ns(self._wper_step_ns)

        if res.info["toolname"] != ToolInfo.TOOLNAME:
            raise Error(f"unsupported non-pbe test result at {res.dirpath}.\nPlease, provide a "
                        f"pbe test result.")

        self._validate_wper_step()
        self._validate_span()

        # Make sure the statistics directory exists.
        try:
            self._res.stats_path.mkdir(parents=True, exist_ok=True)
        except OSError as err:
            msg = Error(err).indent(2)
            raise Error(f"failed to create directory '{self._res.stats_path}':\n{msg}") from None

        self._progress = _ProgressLine.PbeProgressLine()

    def close(self):
        """Stop the measurements."""

        close_attrs = ("_stcoll", "_prov")
        unref_attrs = ("_res", "_dev", "_pman")
        ClassHelpers.close(self, close_attrs=close_attrs, unref_attrs=unref_attrs)
