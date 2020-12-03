# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2014-2020 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module contains misc. handy functions that provide additional functionality on top of 'Proc'
and 'SSH' objects. The idea here is that the helpers provided by this module can run locally via the
'Proc' object or remotely via the 'SSH' object.
"""

import os
import logging
import contextlib
import re
import time
from wultlibs.helperlibs.Exceptions import Error
from wultlibs.helperlibs import Procs, Trivial

_LOG = logging.getLogger()

def _get_pid():
    """Return current process ID."""

    try:
        return os.getpid()
    except OSError as err:
        raise Error("cannot get own PID:\n%s" % err)

def _is_sigterm(sig: str):
    """Return 'True' if sig' is the 'SIGTERM' signal."""
    return sig == "15" or sig.endswith("TERM")

def _is_sigkill(sig: str):
    """Return 'True' if sig' is the 'SIGKILL' signal."""
    return sig == "15" or sig.endswith("KILL")

def kill_pids(pids, sig: str = "SIGTERM", kill_children: bool = False, must_die: bool = False,
              proc=None):
    """
    This function kills or signals processes with PIDs in 'pids' on the host defined by 'procs'. The
    'pids' argument can be a collection of PID numbers ('int' or 'str' types) or a single PID
    number.

    By default the processes are killed (SIGTERM), but you can specify any signal either by name or
    by number.

    The 'children' and 'must_die' arguments must only be used when killing processes (SIGTERM or
    SIGKILL).  The 'children' argument controls whether this function should also try killing the
    children. If the 'must_die' argument is 'True', then this function also verifies that the
    process(es) did actually die, and if any of them did not die, it raises an exception.

    By default this function operates on the local host, but the 'proc' argument can be used to pass
    a connected 'SSH' object in which case this function will operate on the remote host.
    """

    def collect_zombies(proc):
        """In case of a local process we need to 'waitpid()' the children."""

        if not proc.is_remote:
            with contextlib.suppress(OSError):
                os.waitpid(0, os.WNOHANG)

    if not proc:
        proc = Procs.Proc()

    if not pids:
        return

    if not Trivial.is_iterable(pids):
        pids = (pids, )

    pids = [str(int(pid)) for pid in pids]

    if sig is None:
        sig = "SIGTERM"
    else:
        sig = str(sig)

    killing = _is_sigterm(sig) or _is_sigkill(sig)
    if (kill_children or must_die) and not killing:
        raise Error(f"'children' and 'must_die' arguments cannot be used with '{sig}' signal")

    if kill_children:
        # Find all the children of the process.
        for pid in pids:
            children, _, exitcode = proc.run(f"pgrep -P {pid}", join=False)
            if exitcode != 0:
                break
            pids += [child.strip() for child in children]

    pids_spc = " ".join(pids)
    pids_comma = ",".join(pids)
    _LOG.debug("sending '%s' signal to the following process%s: %s",
               sig, proc.hostmsg, pids_comma)

    try:
        proc.run_verify(f"kill -{sig} -- {pids_spc}")
    except Error as err:
        if not killing:
            raise Error(f"failed to send signal '{sig}' to PIDs '{pids_comma}'{proc.hostmsg}:\n"
                        f"{err}")
        # It is fine if one of the processes exited meanwhile.
        if "No such process" not in str(err):
            raise

    if not killing:
        return

    # Give the processes up to 4 seconds to die.
    timeout = 4
    start_time = time.time()
    while time.time() - start_time <= timeout:
        collect_zombies(proc)
        _, _, exitcode = proc.run(f"kill -0 -- {pids_spc}")
        if exitcode != 0:
            return
        time.sleep(0.2)

    if _is_sigterm(sig):
        # Something refused to die, try SIGKILL.
        try:
            proc.run_verify(f"kill -9 -- {pids_spc}")
        except Error as err:
            # It is fine if one of the processes exited meanwhile.
            if "No such process" not in str(err):
                raise
        collect_zombies(proc)
        if not must_die:
            return
        # Give the processes up to 4 seconds to die.
        timeout = 4
        start_time = time.time()
        while time.time() - start_time <= timeout:
            collect_zombies(proc)
            _, _, exitcode = proc.run(f"kill -0 -- {pids_spc}")
            if exitcode != 0:
                return
            time.sleep(0.2)

    # Something refused to die, find out what.
    msg, _, = proc.run_verify(f"ps -f {pids_spc}", join=False)
    if len(msg) < 2:
        msg = pids_comma

    raise Error(f"one of the following processes{proc.hostmsg} did not die after 'SIGKILL': {msg}")

def find_processes(regex: str, proc=None):
    """
    Find all processes which match the 'regex' regular expression on the host defined by 'proc'. The
    regular expression is matched against the process executable name + command-line arguments.

    By default this function operates on the local host, but the 'proc' argument can be used to pass
    a connected 'SSH' object in which case this function will operate on the remote host.

    Returns a list of tuples containing the PID and the command line.
    """

    if not proc:
        proc = Procs.Proc()

    cmd = "ps axo pid,args"
    stdout, stderr = proc.run_verify(cmd, join=False)

    if len(stdout) < 2:
        raise Error(f"no processes found at all{proc.hostmsg}\nExecuted this command:\n{cmd}\n"
                    f"stdout:\n{stdout}\nstderr:{stderr}\n")

    procs = []
    for line in stdout[1:]:
        pid, comm = line.strip().split(" ", 1)
        pid = int(pid)
        if proc.hostname == "localhost" and pid == _get_pid():
            continue
        if re.search(regex, comm):
            procs.append((int(pid), comm))

    return procs

def kill_processes(regex: str, sig: str = "SIGTERM", log: bool = False, name: str = None,
                   proc=None):
    """
    Kill or signal all processes matching the 'regex' regular expression on the host defined by
    'proc'. The regular expression is matched against the process executable name + command-line
    arguments.

    By default the processes are killed (SIGTERM), but you can specify any signal either by name or
    by number.

    If 'log' is 'True', then this function also prints a message which includes the PIDs of the
    processes which are going to be killed.

    The 'name' argument is a human readable name of the processes which are being killed - this name
    will be part of the printed message.

    By default this function operates on the local host, but the 'proc' argument can be used to pass
    a connected 'SSH' object in which case this function will operate on the remote host.

    Returns the list of found and killed processes.
    """

    if not proc:
        proc = Procs.Proc()

    procs = find_processes(regex, proc=proc)
    if not procs:
        return []

    if name:
        name += " "
    else:
        name = "the following process(es) "

    pids = [pid for pid, _ in procs]
    if log:
        pids_str = ", ".join([str(pid) for pid in pids])
        _LOG.info("Sending '%s' signal to %s%s, PID(s): %s",
                  sig, name, proc.hostmsg, pids_str)

    killing = _is_sigterm(sig) or _is_sigkill(sig)
    kill_pids(pids, sig=sig, kill_children=killing, proc=proc)
    return procs
