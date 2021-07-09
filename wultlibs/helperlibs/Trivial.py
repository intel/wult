# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2016-2020 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module contains common trivial helpers.
"""

import os
from itertools import groupby
from wultlibs.helperlibs.Exceptions import Error

# A unique object used as the default value for the 'default' key in some functions.
_RAISE = object()

def is_root():
    """
    Return 'True' if the current process has the superuser (root) privileges and 'False' otherwise.
    """

    try:
        return os.getuid() == 0 or os.geteuid() == 0
    except OSError as err:
        raise Error(f"failed to get process UID: {err}") from None

def get_pid():
    """Return current process ID."""

    try:
        return os.getpid()
    except OSError as err:
        raise Error(f"failed to get own PID: {err}") from None

def get_pgid(pid):
    """Return process group ID of a process with PID 'pid'."""

    try:
        return os.getpgid(pid)
    except OSError as err:
        raise Error(f"failed to get group ID of process with PID {pid}: {err}") from None

def str_to_num(snum, default=_RAISE):
    """
    Convert a string to a numeric value, either 'int' or 'float'. If the conversion is not possible,
    this function raises an exception. However, if the 'default' argumen is provided, this function
    returns 'default' instead of raising the exception.
    """

    try:
        num = int(snum)
    except (ValueError, TypeError):
        try:
            num = float(snum)
        except (ValueError, TypeError):
            if default is _RAISE:
                raise Error(f"failed to convert '{str(snum)}' to a number") from None
            return default

    return num

def is_int(value, base=10):
    """
    Return 'True' if 'value' can be converted to integer using 'int()' and 'False' otherwise.
    """

    try:
        int(str(value), base)
    except (ValueError, TypeError):
        try:
            int(value)
        except (ValueError, TypeError):
            return False
    return True

def is_iterable(value):
    """Return 'True' if 'value' is iterable collection (not string) and 'False' otherwise."""
    try:
        iter(value)
    except TypeError:
        return False
    return not isinstance(value, str)

def is_float(value):
    """
    Return 'True' if 'value' can be converted to a float using 'float()' and 'False' otherwise.
    """

    try:
        float(value)
    except (ValueError, TypeError):
        return False
    return True

def list_dedup(elts):
    """Return list of unique elements in 'elts'."""

    seen = set()
    new_elts = []
    for elt in elts:
        if elt not in seen:
            new_elts.append(elt)
            seen.add(elt)

    return new_elts

def split_csv_line(csv_line, sep=",", dedup=False):
    """
    Split a comma-separated values line and return the list of the comma separated values. The 'sep'
    argument can be used to change the separator from comma to something else. If 'dedup' is 'True',
    this function removes duplicated elements from the returned list.
    """

    result = [val.strip() for val in csv_line.strip(sep).split(sep) if val]
    if dedup:
        return list_dedup(result)
    return result

def rangify(numbers):
    """
    Turn list of numbers in 'numbers' to a string of comma-separated ranges. Numbers can be integers
    or strings. E.g. list of numbers [0,1,2,4] is translated to "0-2,4".
    """

    try:
        numbers = [int(number) for number in numbers]
    except (ValueError, TypeError) as err:
        raise Error(f"failed to translate numbers to ranges, expected list of numbers, got "
                    f"'{numbers}'") from err

    range_strs = []
    for _, pairs in groupby(enumerate(numbers), lambda x:x[0]-x[1]):
        # The 'pairs' is an iterable of tuples (enumerate value, number). E.g. 'numbers'
        # [5,6,7,8,10,11,13] would result in three iterable groups:
        # ((0, 5), (1, 6), (2, 7), (3, 8)) , ((4, 10), (5, 11)) and  (6, 13)

        nums = [val for _, val in pairs]
        if len(nums) > 1:
            range_strs.append(f"{nums[0]}-{nums[-1]}")
        else:
            range_strs.append(str(nums[0]))

    return ",".join(range_strs)
