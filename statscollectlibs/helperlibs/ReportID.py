# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2020-2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
Report ID is a string identifying a test report. It usually contains something descriptive and
human-readable. This module contains helper function for dealing with a report IDs.
"""

import re
import time
from pepclibs.helperlibs.Exceptions import Error

MAX_REPORID_LEN = 64
# The special characters allowed in the report ID.
SPECIAL_CHARS = "-.,_~"

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

    if not reportid:
        reportid = time.strftime(strftime)

    result = ""
    if prefix:
        result += prefix.rstrip(separator)
        if not reportid.startswith(separator):
            result += separator

    result += reportid

    if append:
        if not reportid.endswith(separator):
            result += separator
        result += append.lstrip(separator)

    return validate_reportid(result, additional_chars=additional_chars)

def validate_reportid(reportid, additional_chars=None):
    """
    We limit the characters which can be used in report IDs to those which are safe to use in URLs,
    and this function validates a report ID in 'reportid' against the allowed set of characters. The
    characters are ACSII alphanumeric characters, "-", ".", "_", and "~". The 'additional_chars'
    argument is the same as in 'get_charset_descr()'.
    """

    if len(reportid) > MAX_REPORID_LEN:
        raise Error(f"too long run ID ({len(reportid)} characters), the maximum allowed length is "
                    f"{MAX_REPORID_LEN} characters")

    if not additional_chars:
        additional_chars = ""

    chars = SPECIAL_CHARS + additional_chars
    if not re.match(rf"^[A-Za-z0-9{chars}]+$", reportid):
        charset_descr = get_charset_descr() + additional_chars
        raise Error(f"bad run ID '{reportid}'\n"
                    f"Please, use only the following characters: {charset_descr}")

    return reportid
