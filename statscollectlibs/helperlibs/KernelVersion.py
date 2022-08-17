# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2020-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module contains helper functions for dealing with Linux kernel version numbers.
"""

import re
from collections import namedtuple
from pepclibs.helperlibs.Exceptions import Error

# The resource owner information namedtuple "type".
SplitKver = namedtuple("SplitKver", ["major", "minor", "stable", "rc", "localver"])

def split_kver(kver, numerical=False):
    """
    Split the kernel version string on the components: major, minor, stable, rc, localver. For
    example, '4.18.1-build0' would be ('4', '18', '1', None, '-build0'), and '5.0-rc2' would be
    ('5', '0', 0, '2', ''). By default the numeric parts of the version are returned as strings, but
    if the 'numerical' argument is 'True', they are returned as integers.
    """

    def _fetch_rc(localver):
        """Fetch the release candidate version number from the local version."""

        matchobj = re.match(r"-rc(\d+)(.*)", localver)
        if matchobj:
            return matchobj.group(1, 2)
        return (None, localver)

    matchobj = re.match(r"^(\d+)\.(\d+)(?:(?:\.(\d+)){0,1}(.*)){0,1}", kver)
    if not matchobj:
        raise Error("failed to parse kernel version string '%s'" % kver)

    major, minor, stable, localver = matchobj.group(1, 2, 3, 4)
    if stable is None:
        stable = 0
    rc, localver = _fetch_rc(localver)
    if numerical:
        major = int(major)
        minor = int(minor)
        stable = int(stable)
        if rc is not None:
            rc = int(rc)

    return SplitKver(major, minor, stable, rc, localver)

def kver_lt(kver1, kver2):
    """
    Retrun 'True' if kernel version string 'kver1' is smaller than kernel version string 'kver2'
    (kernel version 'kver1' is older than kernel version 'kver2').
    """

    def _lt(a, b):
        if a is None:
            return False
        if b is None:
            return True
        return a < b

    major1, minor1, stable1, rc1, localver1 = split_kver(kver1, numerical=True)
    major2, minor2, stable2, rc2, localver2 = split_kver(kver2, numerical=True)

    if major1 != major2:
        return major1 < major2
    if minor1 != minor2:
        return minor1 < minor2
    if stable1 != stable2:
        return stable1 < stable2
    if rc1 != rc2:
        return _lt(rc1, rc2)
    return localver1 < localver2

def kver_ge(kver1, kver2):
    """
    Retrun 'True' if kernel version string 'kver1' is greater or equal to kernel version string
    'kver2' (kernel version 'kver1' is newer or equal to kernel version 'kver2').
    """

    return not kver_lt(kver1, kver2)
