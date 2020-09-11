# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2020 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module provides API for loading and unloading Linux kernel modules (drivers).
"""

import logging
from wultlibs.helperlibs.Exceptions import Error
from wultlibs.helperlibs import Dmesg

_LOG = logging.getLogger("main")

# The drivers supported by this module.
DRIVERS = {}

class KernelModule:
    """This class represents a Linux kernel module."""

    def _get_usage_count(self):
        """
        Returns 'None' if module is not loaded, otherwise returns the module usage count.
        """

        with self._proc.open("/proc/modules", "r") as fobj:
            for line in fobj:
                line = line.strip()
                if not line:
                    continue
                name, _, usecnt, _ = line.split(maxsplit=3)
                if name == self.name:
                    return int(usecnt)

        return None

    def _get_dmesg_msgs(self):
        """Return new dmesg messages if available."""

        if not self.dmesg:
            return ""
        new_msgs = Dmesg.get_new_messages(self._captured, self._proc, join=True, strip=True)
        if new_msgs:
            return f"\nNew kernel messages{self._proc.hostmsg}:\n{new_msgs}"
        return ""

    def _run_mod_cmd(self, cmd):
        """This helper function runs module load/unload command 'cmd'."""

        if self.dmesg:
            self._captured = Dmesg.capture(self._proc)
            try:
                self._proc.run_verify(cmd)
            except Error as err:
                raise Error(f"{err}{self._get_dmesg_msgs()}")
            if _LOG.getEffectiveLevel() == logging.DEBUG:
                _LOG.debug("the following command finished: %s%s", cmd, self._get_dmesg_msgs())
        else:
            self._proc.run_verify(cmd)

    def is_loaded(self):
        """Check if the module is loaded."""

        return self._get_usage_count() is not None

    def _unload(self):
        """Unload the module if it is loaded."""

        if self.is_loaded():
            self._run_mod_cmd(f"rmmod {self.name}")

    def unload(self):
        """Unload the module if it is loaded."""

        self._unload()

    def load(self, opts=None, unload=False):
        """
        Load the module with 'opts' options to 'modprobe'. If 'unload' is 'True', then unload the
        module first.
        """

        if unload:
            self._unload()
        elif self.is_loaded():
            return

        if opts:
            opts = f"{opts}"
        else:
            opts = ""
        if _LOG.getEffectiveLevel() == logging.DEBUG:
            opts += " dyndbg=+pf"
        self._run_mod_cmd(f"modprobe {self.name} {opts}")

    def __init__(self, proc, name):
        """
        The class constructor. The arguments are as follows.
          * proc - the host to operate on. This object will keep a 'proc' reference and use it in
                   various methods.
          * name - kernel module name.
        """

        self._proc = proc
        self.name = name
        self._captured = None

        # Whether kernel messages should be monitored. They are very useful if something goes wrong.
        self.dmesg = True

    def close(self):
        """Stop the measurements."""
        if getattr(self, "_proc", None):
            self._proc = None

    def __enter__(self):
        """Enter the run-time context."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the run-time context."""
        self.close()
