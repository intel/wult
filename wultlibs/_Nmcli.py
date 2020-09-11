# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2020 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module provides API to NetworkManger's nmcli tool.
"""

import re
from collections import OrderedDict
from wultlibs.helperlibs import Trivial, FSHelpers, Procs
from wultlibs.helperlibs.Exceptions import Error, ErrorNotSupported

class Nmcli:
    """API to the nmcli tool."""

    def _toggle_managed(self, ifname, managed):
        """Change the 'managed' state of network interface 'ifname'."""

        if managed:
            state = "yes"
        else:
            state = "no"

        self._proc.run_verify(f"nmcli dev set '{ifname}' managed {state}")

    def is_managed(self, ifname):
        """
        Returns 'True' if network interface 'ifname' is managed by NetworkManager and 'False'
        otherwise.
        """

        cmd = f"nmcli --fields GENERAL.STATE dev show '{ifname}'"
        stdout, stderr, exitcode = self._proc.run(cmd)
        if exitcode:
            if "not found" in stderr or "not running" in stderr:
                return False
            raise Error(self._proc.cmd_failed_msg(cmd, stdout, stderr, exitcode))

        pattern = r"^GENERAL.STATE:\s+\d+ \((.+)\)$"
        match = re.match(pattern, stdout)
        if not match:
            stdout = "".join(stdout)
            raise Error(f"unexpected stdout from the following command:\n{cmd}\n{stdout}")

        return match.group(1) != "unmanaged"

    def unmanage(self, ifnames):
        """
        Mark network interfaces in 'ifnames' as 'unmanaged'. The managed state can later be restored
        with the 'restore_managed()'.
        """

        if not Trivial.is_iterable(ifnames):
            ifnames = [ifnames]

        for ifname in ifnames:
            managed = self.is_managed(ifname)
            if not managed:
                continue
            self._toggle_managed(ifname, False)
            if ifname not in self._saved_managed:
                self._saved_managed[ifname] = managed

    def restore_managed(self):
        """
        Restore the "managed" state of all the network interfaces that have state previously
        changed.
        """

        for ifname, managed in self._saved_managed.items():
            self._toggle_managed(ifname, managed)

        self._saved_managed = OrderedDict()

    def __init__(self, proc=None):
        """
        Initialize a class instance for the host associated with the 'proc' object. By default it is
        is going to be the local host, but 'proc' can be used to pass a connected 'SSH' object, in
        which case all operation will be done on the remote host. This object will keep a 'proc'
        reference and use it in various methods.
        """

        if not proc:
            proc = Procs.Proc()

        self._proc = proc
        self._saved_managed = OrderedDict()

        if not FSHelpers.which("nmcli", default=None, proc=proc):
            raise ErrorNotSupported(f"the 'nmcli' tool is not installed{proc.hostmsg}")

    def close(self):
        """Stop the measurements."""
        if getattr(self, "_proc", None):
            self._proc = None

    def __enter__(self):
        """Enter the runtime context."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the runtime context."""
        self.close()
