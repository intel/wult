# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Antti Laakso <antti.laakso@intel.com>

"""
This module provides API for discovering Operating System information.
"""

import contextlib
from pathlib import Path
from powerlablibs.Exceptions import Error
from wultlibs.helperlibs import Procs

_COMMONPKGS = { "phc2sys" : "linuxptp" , "tc" : "iproute2" }
_FEDORAPKGS = { "sch_etf.ko" : "kernel-modules-extra" }
_FEDORAPKGS.update(_COMMONPKGS)
_DEBIANPKGS = { "sch_etf.ko" : "linux-modules" }
_DEBIANPKGS.update(_COMMONPKGS)

_PKGMAP = { "Ubuntu" : _DEBIANPKGS,
            "Debian GNU/Linux" : _DEBIANPKGS,
            "Fedora" : _FEDORAPKGS,
            "CentOS Linux" : _FEDORAPKGS }

def read_os_release(sysroot="/", proc=None):
    """
    Read the 'os-release' file from the host defined by 'proc' and return it as a dictionary.
    """

    if not proc:
        proc = Procs.Proc()

    paths = ("/usr/lib/os-release", "/etc/os-release")
    paths = [Path(sysroot) / path.lstrip("/") for path in paths]
    osinfo = {}

    for path in paths:
        with contextlib.suppress(proc.Error):
            with proc.open(path, "r") as fobj:
                for line in fobj:
                    key, val = line.rstrip().split("=")
                    osinfo[key] = val.strip('"')
        if osinfo:
            break

    if not osinfo:
        files = "\n".join(paths)
        raise Error(f"cannot discover OS version{proc.hostmsg}, these files were checked:\n{files}")

    return osinfo

def tool_to_package_name(tool, proc=None):
    """
    Get OS package name providing 'tool' on host 'proc'. Returns 'None' if package name is not
    found.
    """

    if not proc:
        proc = Procs.Proc()

    osinfo = read_os_release(proc=proc)
    osname = osinfo.get("NAME")

    if osname not in _PKGMAP:
        return None

    return _PKGMAP[osname].get(tool)
