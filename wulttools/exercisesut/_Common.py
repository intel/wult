# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Antti Laakso <antti.laakso@linux.intel.com>
#         Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""Common code for the 'exercise-sut' tool."""

import sys
import time
from pepclibs.helperlibs import Logging, ClassHelpers, LocalProcessManager

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.wult.{__name__}")

RESET_PROPS = {
    "online": {
        "value": "all",
        "text": "online all CPUs"
    },
    "idle_governors": {
        "value": "menu",
        "text": "set idle governor to 'menu'"
    },
    "cpufreq_governors": {
        "value": "powersave",
        "text": "set CPU frequency governor to 'performance'"
    },
    "cstates": {
        "value": "all",
        "text": "enable all C-states"
    },
    "c1_demotion": {
        "value": "off",
        "text": "disable C1 demotion"
    },
    "c1_undemotion": {
        "value": "off",
        "text": "disable C1 undemotion"
    },
    "c1e_autopromote": {
        "value": "off",
        "text": "disable C1E autopromotion"
    },
    "cstate_prewake": {
        "value": "off",
        "text": "disable C-state prewake"
    },
    "turbo": {
        "value": "on",
        "text": "enable turbo"
    },
    "freqs": {
        "value": "unl",
        "text": "unlock CPU frequency"
    },
    "uncore_freqs": {
        "value": "unl",
        "text": "unlock uncore frequency"
    },
    "epp": {
        "value": "balance_performance",
        "text": "set EPP policy to 'balance_performance'"
    },
    "epb": {
        "value": "balance-performance",
        "text": "set EPB policy to 'balance-performance'"
    },
}

class CmdlineRunner(ClassHelpers.SimpleCloseContext):
    """Helper class for running commandline commands."""

    def _handle_error(self, cmd):
        """Handle error for running command 'cmd'."""

        msg = f"failed to run command:\n'{cmd}'"
        if self._ignore_errors:
            _LOG.error(msg)
        else:
            msg += "\nstop processing more commands and exit"
            _LOG.error_out(msg)

    def _get_completed_procs(self):
        """Yield completed command process objects."""

        for proc in self._procs:
            _, _, exitcode = proc.wait(1)
            if exitcode is None:
                continue

            yield proc

    def _handle_proc(self, proc):
        """Wait for command process 'proc' and handle the output."""

        stdout, stderr, exitcode = proc.wait()

        if stdout:
            _LOG.info(stdout)
        if stderr:
            _LOG.info(stderr)

        if exitcode != 0:
            self._handle_error(proc.cmd)
        else:
            _LOG.notice("command completed:\n'%s'", proc.cmd)

    def _active_proc_count(self):
        """
        Go through list of started processes, handle completed ones, and return number of active
        processes.
        """

        procs_done = set()
        for proc in self._get_completed_procs():
            self._handle_proc(proc)
            procs_done.add(proc)

        self._procs -= procs_done

        for proc in procs_done:
            proc.close()

        return len(self._procs)

    def _run_async(self, cmd):
        """
        Run command 'cmd' asynchronously. If more than 'self._proc_count' processes are already
        running, wait until one of the running processes completes before running the command.
        """

        while self._active_proc_count() >= self._proc_count:
            # Wait until one of the commands are done.
            time.sleep(1)

        _LOG.debug("running command: '%s'", cmd)
        proc = self._lpman.run_async(cmd)
        self._procs.add(proc)

    def _run_command(self, cmd):
        """
        Run command 'cmd' with process manager object 'pman'. If 'dry_run' is 'True', print the
        command instad of running it. If any of the commands failed and 'ignore_errors' is 'False',
        print error and exit.
        """

        _LOG.info("Running the following command:\n%s", cmd)

        if self._dry_run:
            return

        if self._proc_count:
            self._run_async(cmd)
        else:
            res = self._lpman.run(cmd, output_fobjs=(sys.stdout, sys.stderr))
            if res.exitcode != 0:
                self._handle_error(cmd)

    def wait(self):
        """Wait until all commands have completed."""

        while self._active_proc_count() != 0:
            time.sleep(1)
            continue

    def __init__(self, dry_run=False, ignore_errors=False, proc_count=None):
        """
        The class constructor, arguments are as follows.
          * dry_run - if 'True', print the command instead of running it.
          * ignore_errors - if 'True', continue processing commands even if some of them fail.
          * proc_count - number of processes to run in parallel.
        """

        self._dry_run = dry_run
        self._ignore_errors = ignore_errors
        self._proc_count = proc_count

        self._lpman = LocalProcessManager.LocalProcessManager()
        self._procs = set()

        if self._proc_count and not dry_run:
            _LOG.notice("running up to %s commands in parallel", self._proc_count)

    def close(self):
        """Uninitialize the class objetc."""

        for proc in self._procs:
            proc.close()

        ClassHelpers.close(self, close_attrs=("_lpman",))
