# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2014-2020 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module contains misc. helper functions with the common theme of representing something in a
human-readable format, or turning human-oriented data into a machine format.
"""

def duration(seconds, s=True, ms=False):
    """
    Transform duration in seconds to the human-readable format. The 's' and 'ms' arguments control
    whether seconds/milliseconds should be printed or not.
    """

    if not isinstance(seconds, int):
        msecs = int((float(seconds) - int(seconds)) * 1000)
    else:
        msecs = 0

    (mins, secs) = divmod(int(seconds), 60)
    (hours, mins) = divmod(mins, 60)
    (days, hours) = divmod(hours, 24)

    result = ""
    if days:
        result += "%d days " % days
    if hours:
        result += "%dh " % hours
    if mins:
        result += "%dm " % mins
    if s or seconds < 60:
        if ms or seconds < 1 or (msecs and seconds < 10):
            result += "%f" % (secs + float(msecs) / 1000)
            result = result.rstrip("0").rstrip(".")
            result += "s"
        else:
            result += "%ds " % secs

    return result.strip()
