# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2018-2020 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
Report ID is a string identifying a test report. It usually contains something descriptive and
human-readable. This module contains helper function for dealing with a report IDs.
"""

import re
import time
from wultlibs.helperlibs.Exceptions import Error

MAX_REPORID_LEN = 64
# The special characters allowed in the report ID.
SPECIAL_CHARS = "-.,_~"

# Just a unique object used as default value in few places.
_RAISE = object()

def get_charset_descr(additional_chars=""):
    """
    Returns a string describing the allow report ID characters. The 'additional_chars' argument is a
    string containing the characters allowed in the report ID on top of the default characters
    (alphabetical and those in 'SPECIAL_CHARS'). For example, passing 'additional_chars=":^"' will
    include characters ':' and '^' into the allowed characters set.
    """

    chars_list = [f"'{char}'" for char in SPECIAL_CHARS + additional_chars]
    chars = ", ".join(chars_list[:-1])
    chars += f", and {chars_list[-1]}"
    return f"ACSII alphanumeric, {chars}"

def format_reportid(prefix=None, separator="-", reportid=None, strftime="%Y%m%d-%H%M%S",
                    append=None, additional_chars=""):
    """
    Format a default report ID: 'prefix' + 'separator' + ID, where ID is 'reportid' if it is not
    'None', or current time string formatted with 'time.strftime()' using the 'strftime' pattern.
    The 'additional_chars' argument is the same as in 'get_charset_descr()'.
    """

    result = ""
    if prefix:
        result += prefix + separator
    if reportid:
        result += reportid
    else:
        result += time.strftime(strftime)
    if append:
        result += separator + append

    return validate_reportid(result, additional_chars=additional_chars)

def validate_reportid(reportid, additional_chars="", default=_RAISE):
    """
    We limit the characters which can be used in report IDs to those which are safe to use in URLs,
    and this function validates a report ID in 'reportid' against the allowed set of characters. The
    characters are ACSII alphanumeric characters, "-", ".", "_", and "~". The 'additional_chars'
    argument is the same as in 'get_charset_descr()'.

    By default this function raises an exception if 'reportid' is invalid, but if the 'default'
    argument is provided, the 'default' value is returned instead.
    """

    if len(reportid) > MAX_REPORID_LEN:
        if default is _RAISE:
            raise Error(f"too long run ID ({len(reportid)} characters), the maximum allowed length "
                        f"is {MAX_REPORID_LEN} characters")
        return default

    chars = SPECIAL_CHARS + additional_chars
    if not re.match(rf"^[A-Za-z0-9{chars}]+$", reportid):
        if default is _RAISE:
            charset_descr = get_charset_descr() + additional_chars
            raise Error(f"bad run ID '{reportid}'\n"
                        f"Please, use only the following characters: {charset_descr}")
        return default

    return reportid
