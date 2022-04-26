# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module provides API to the datapoints CSV file definitions (AKA 'defs').
"""

from pepclibs.helperlibs.Exceptions import Error
from wultlibs import _DefsBase

# A unique object used as the default value for the 'default' keyword argument in various
# functions.
_RAISE = object()

def is_cscyc_metric(metric):
    """Returns 'True' if 'metric' is a C-state cycles count metric."""

    return (metric.startswith("CC") or metric.startswith("PC")) and \
            metric.endswith("Cyc") and len(metric) > 5

def is_csres_metric(metric):
    """Returns 'True' if 'metric' is a C-state residency metric."""

    return (metric.startswith("CC") or metric.startswith("PC")) and \
            metric.endswith("%") and len(metric) > 3

def is_cs_metric(metric):
    """Returns 'True' if 'metric' is a C-state residency or cycles counter metric."""

    return is_csres_metric(metric) or is_cscyc_metric(metric)

def get_csname(metric, default=_RAISE):
    """
    If 'metric' is a metric related to a C-state, then returns the C-state name string. Otherwise
    raises an exception, unless the 'default' argument is passed, in which case it returns this
    argument instead of raising an exception.
    """

    csname = None
    if metric.endswith("Cyc"):
        csname = metric[:-3]
        if csname.endswith("Derived"):
            csname = csname[:-len("Derived")]
    elif metric.endswith("%"):
        csname = metric[:-1]

    if not csname or not (metric.startswith("CC") or metric.startswith("PC")):
        if default is _RAISE:
            raise Error(f"cannot get C-state name for metric '{metric}'")
        return default

    return csname

def get_cscyc_metric(csname):
    """
    Given 'csname' is a C-state name, this method retruns the corresponding C-state cycles count
    metric.
    """

    return f"{csname}Cyc"

def get_csres_metric(csname):
    """
    Given 'csname' is a C-state name, this method retruns the corresponding C-state residency
    metric.
    """

    return f"{csname}%"

class WultDefs(_DefsBase.CSDefsBase):
    """This class provides API to the datapoints CSV file definitions (AKA 'defs')."""

    def get_csname(self, metric):
        """Returns the name of the C-state represented in 'metric'."""

        return get_csname(metric)

    def get_csmetric(self, metric, csname):
        """Returns a version of 'metric' populated with the C-state name 'csname'."""

        if is_cscyc_metric(metric):
            return get_cscyc_metric(csname)

        return get_csres_metric(csname)

    def is_csmetric(self, metric):
        """Returns 'True' if 'metric' is a C-state residency metric."""

        return is_cs_metric(metric)
