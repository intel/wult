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
from pepclibs import CStates, PStates
from pepclibs.helperlibs import Logging, ClassHelpers, LocalProcessManager
from pepclibs.helperlibs.Exceptions import Error

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.wult.{__name__}")

CSTATES_CONFIG_STRATEGIES = ('measured-only', 'measured-and-poll', 'measured-and-shallower')

PROP_INFOS = {
    "cstates": {
        "name": "Requestable C-state",
        "sname": "CPU",
        "cmd": "pepc cstates config --disable all --enable {} {scope_opts}"
    },
    "pcstates": {
        "name": "Package C-state",
        "sname": "package",
        "cmd": "pepc cstates config --pkg-cstate-limit {} {scope_opts}"
    },
    "freqs": {
        "name": "CPU frequency",
        "sname": "CPU",
        "cmd": "pepc pstates config --min-freq {} --max-freq {} {scope_opts}"
    },
    "uncore_freqs": {
        "name": "Uncore frequency",
        "moniker": "uf",
        "sname": "die",
        "cmd": "pepc pstates config --min-uncore-freq {} --max-uncore-freq {} {scope_opts}"
    },
    "aspm": {
        "name": "ASPM",
        "sname": "global",
        "moniker": "aspm",
        "cmd": "pepc aspm config --policy {}"
    },
    "cpufreq_governors": {
        "name": "CPU frequency governor",
        "moniker": "fgov",
        "pclass": "PStates",
        "pclass_pname": "governor",
        "cmd": "pepc pstates config --governor {} {scope_opts}"
    },
    "idle_governors": {
        "name": "Idle governor",
        "moniker": "igov",
        "pclass": "CStates",
        "pclass_pname": "governor",
        "cmd": "pepc cstates config --governor {} {scope_opts}"
    },
    "c1_demotion": {
        "moniker": "c1d",
        "pclass": "CStates",
        "cmd": "pepc cstates config --c1-demotion {} {scope_opts}"
    },
    "c1_undemotion": {
        "moniker": "c1und",
        "pclass": "CStates",
        "cmd": "pepc cstates config --c1-undemotion {} {scope_opts}"
    },
    "c1e_autopromote": {
        "moniker": "autoc1e",
        "pclass": "CStates",
        "cmd": "pepc cstates config --c1e-autopromote {} {scope_opts}"
    },
    "cstate_prewake": {
        "moniker": "cpw",
        "pclass": "CStates",
        "cmd": "pepc cstates config --cstate-prewake {} {scope_opts}"
    },
    "epp": {
        "moniker": "epp",
        "pclass": "PStates",
        "cmd": "pepc pstates config --epp {} {scope_opts}"
    },
    "epb": {
        "moniker": "epb",
        "pclass": "PStates",
        "cmd": "pepc pstates config --epb {} {scope_opts}"
    },
    "turbo": {
        "moniker": "turbo",
        "pclass": "PStates",
        "cmd": "pepc pstates config --turbo {}"
    },
    "online": {
        "name": "CPU online status",
        "sname": "CPU",
        "cmd": "pepc cpu-hotplug online {scope_opts}"
    },
}

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
        "value": "on",
        "text": "enable C1 undemotion"
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

def list_monikers():
    """Helper to print moniker for each property, if any."""

    min_len = 0
    monikers = {}

    for pname, pinfo in PROP_INFOS.items():
        if "moniker" not in pinfo:
            continue

        name = None
        if pname in PStates.PROPS:
            name = PStates.PROPS[pname].get("name")
        elif pname in CStates.PROPS:
            name = CStates.PROPS[pname].get("name")
        else:
            name = pinfo.get("name")

        if not name:
            raise Error(f"BUG: no name for property '{pname}'")

        min_len = max(min_len, len(name))
        monikers[pinfo["moniker"]] = name

    for moniker, name in monikers.items():
        msg = f"{name:<{min_len}}: {moniker}"
        _LOG.info(msg)

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

    def run_command(self, cmd):
        """
        Run command 'cmd' with process manager object 'self._lpman'. If 'self._proc_count' is
        non-zero, run the command asynchronously.

        Args:
            cmd: The command to run.
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
