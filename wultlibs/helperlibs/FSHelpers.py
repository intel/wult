# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2020-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module contains misc. helper functions related to file-system operations.
"""

import os
from pathlib import Path
from collections import namedtuple
from pepclibs.helperlibs import ProcessManager

# pylint: disable=wildcard-import,unused-wildcard-import
from statscollectlibs.helperlibs.FSHelpers import *

# Default debugfs mount point.
DEBUGFS_MOUNT_POINT = Path("/sys/kernel/debug")

def get_mount_points(pman=None):
    """
    This generator parses '/proc/mounts' and for each mount point yields the following named tuples:
      * device - name of the mounted device
      * mntpoint - mount point
      * fstype - file-system type
      * options - list of options

    The 'pman' argument is the process manger object which defines the host to parse '/proc/mounts'
    on. By default, local host's '/proc/mounts' will be parsed.
    """

    mounts_file = "/proc/mounts"
    mntinfo = namedtuple("mntinfo", ["device", "mntpoint", "fstype", "options"])

    with ProcessManager.pman_or_local(pman) as wpman:
        with wpman.open(mounts_file, "r") as fobj:
            try:
                contents = fobj.read()
            except OSError as err:
                msg = Error(err).indent(2)
                raise Error(f"cannot read '{mounts_file}':\n{msg}") from err

    for line in contents.splitlines():
        if not line:
            continue

        device, mntpoint, fstype, options, _ = line.split(maxsplit=4)
        yield mntinfo(device, mntpoint, fstype, options.split(","))

def mount_debugfs(mnt=None, pman=None):
    """
    Mount the debugfs file-system to 'mnt' on the host. By default it is mounted to
    'DEBUGFS_MOUNT_POINT'. The 'pman' argument defines the host to mount debugfs on (default is the
    local host).

    Returns a tuple of the following elements.
      * mount point path.
      * 'True' if debugfs was mounted by this function, 'False' it has already been mounted before.
    """

    if not mnt:
        mnt = DEBUGFS_MOUNT_POINT
    else:
        try:
            mnt = Path(os.path.realpath(mnt)).resolve()
        except OSError as err:
            msg = Error(err).indent(2)
            raise Error(f"cannot resolve path '{mnt}':\n{msg}") from None

    for mntinfo in get_mount_points(pman=pman):
        if mntinfo.fstype == "debugfs" and Path(mntinfo.mntpoint) == mnt:
            # Already mounted.
            return mnt, False

    pman.run_verify(f"mount -t debugfs none '{mnt}'")
    return mnt, True
