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

from wultlibs.helperlibs import Trivial
from wultlibs.helperlibs.Exceptions import Error

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

# The specifiers that 'parse_duration()' accepts.
DURATION_SPECS = {"d" : "days", "h" : "hours", "m" : "minutes", "s" : "seconds"}
# A short 'parse_duration()' specifiers description string.
DURATION_SPECS_DESCR = ", ".join([f"{spec} - {key}" for spec, key in DURATION_SPECS.items()])

def parse_duration(htime, default_unit="s"):
    """
    This function does the opposite to what 'duration()' does - parses the human time string and
    returns integer number of seconds. This function supports the following specifiers:
      * d - days
      * h - hours
      * m - minutes
      * s - seconds.

    If 'htime' is just a number without a specifier, it is assumed to be in seconds. But the
    'default_unit' argument can be used to specify a different default unit.
    """

    if default_unit not in DURATION_SPECS:
        raise Error(f"bad unit '{default_unit}', supported units are: {DURATION_SPECS_DESCR}")

    htime = htime.strip()
    if htime.isdigit():
        htime += default_unit

    tokens = {}
    rest = htime.lower()
    for spec in DURATION_SPECS:
        split = rest.split(spec, 1)
        if len(split) > 1:
            tokens[spec] = split[0]
            rest = split[1]
        else:
            rest = split[0]

    if rest.strip():
        raise Error(f"failed to parse duration '{htime}'")

    for spec, val in tokens.items():
        if not Trivial.is_int(val):
            raise Error(f"failed to parse duration '{htime}': bad amount of "
                        f"{DURATION_SPECS[spec]}")

    days = int(tokens.get("d", 0))
    hours = int(tokens.get("h", 0))
    mins = int(tokens.get("m", 0))
    secs = int(tokens.get("s", 0))
    return days * 24 * 60 * 60 + hours * 60 * 60 + mins * 60 + secs
