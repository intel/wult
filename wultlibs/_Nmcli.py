# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module provides API to NetworkManger's nmcli tool.
"""

import re
from pepclibs.helperlibs import Trivial, FSHelpers, LocalProcessManager, ClassHelpers
from pepclibs.helperlibs.Exceptions import Error, ErrorNotSupported

class Nmcli:
    """API to the nmcli tool."""

    def _toggle_managed(self, ifname, managed):
        """Change the 'managed' state of network interface 'ifname'."""

        if managed:
            state = "yes"
        else:
            state = "no"

        self._pman.run_verify(f"nmcli dev set '{ifname}' managed {state}")

    def is_managed(self, ifname):
        """
        Returns 'True' if network interface 'ifname' is managed by NetworkManager and 'False'
        otherwise.
        """

        cmd = f"nmcli --fields GENERAL.STATE dev show '{ifname}'"
        stdout, stderr, exitcode = self._pman.run(cmd)
        if exitcode:
            if "not found" in stderr or "not running" in stderr:
                return False
            raise Error(self._pman.get_cmd_failure_msg(cmd, stdout, stderr, exitcode))

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

        self._saved_managed = {}

    def __init__(self, pman=None):
        """
        Initialize a class instance for the host associated with the 'pman' process manager object
        (local host by default).
        """

        self._pman = pman
        self._saved_managed = {}
        self._close_pman = pman is None

        if not self._pman:
            self._pman = LocalProcessManager.LocalProcessManager()

        if not FSHelpers.which("nmcli", default=None, pman=pman):
            raise ErrorNotSupported(f"the 'nmcli' tool is not installed{pman.hostmsg}")

    def close(self):
        """Uninitialize the object."""
        ClassHelpers.close(self, close_attrs=("_pman",))

    def __enter__(self):
        """Enter the runtime context."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the runtime context."""
        self.close()
