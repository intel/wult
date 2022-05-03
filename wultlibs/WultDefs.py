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

def get_csname(metric, must_get=True):
    """
    If 'metric' is a metric related to a C-state, then returns the C-state name string. Otherwise
    raises an exception, unless the 'must_get' argument is 'False', in which case it returns 'None'
    instead of raising an exception.
    """

    csname = None
    if metric.endswith("Cyc"):
        csname = metric[:-3]
        if csname.endswith("Derived"):
            csname = csname[:-len("Derived")]
    elif metric.endswith("%"):
        csname = metric[:-1]

    if not csname or not (metric.startswith("CC") or metric.startswith("PC")):
        if must_get:
            raise Error(f"cannot get C-state name for metric '{metric}'")
        return None

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

class WultDefs(_DefsBase.DefsBase):
    """This class provides an API to the datapoints CSV file definitions (AKA 'defs')."""

    def __init__(self, hdr):
        """
        The class constructor. The arguments are as follows.
          * hdr - the wult datapoints CSV file header in form of a list. The header is basically a
                  list of "raw" wult metrics.
        """

        super().__init__("wult")

        ccnames = []
        pcnames = []

        for metric in hdr:
            if not metric.endswith("%"):
                continue

            if metric.startswith("CC"):
                # Exclude CC0 and CC1Derived.
                if "Derived" in metric or "CC0" in metric:
                    continue
                ccnames.append(metric[:-1])
            elif metric.startswith("PC") and metric.endswith("%") and len(metric) > 3:
                pcnames.append(metric[:-1])

        placeholders_info = [{ "values" : ccnames, "placeholder" : "CCx"},
                             { "values" : pcnames, "placeholder" : "PCx"}]

        super()._mangle_placeholders(placeholders_info)
