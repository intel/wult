# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module provides API to turbostat metrics definitions (AKA 'defs').
"""

from statscollectlibs.defs import _STCDefsBase
from statscollectlibs.parsers import TurbostatParser

def is_reqcs_metric(metric):
    """
    Returns 'True' or 'False' based on whether 'metric' is a metric which represents a requestable
    C-state.
    """

    return metric == "POLL%" or (metric.startswith("C") and metric[1].isdigit() and
                                 metric.endswith("%"))

def get_reqcs_from_metric(metric):
    """Returns the name of the requested C-state represented by 'metric'."""

    return metric[:-1]

def get_metric_from_reqcs(reqcs):
    """Returns the metric which represents the requestable state 'reqcs'."""

    return f"{reqcs}%"

def is_hwcs_metric(metric):
    """
    Returns 'True' or 'False' based on whether 'metric' is a metric which represents a hardware
    C-state.
    """

    return metric.startswith("CPU%")

def get_hwcs_from_metric(metric):
    """Returns the name of the hardware C-state represented by 'metric'."""

    return metric[4:]

def get_metric_from_hwcs(hwcs):
    """Returns the metric which represents the hardware state 'hwcs'."""

    return f"CPU%{hwcs.lower()}"

def is_pkgcs_metric(metric):
    """
    Returns 'True' or 'False' based on whether 'metric' is a metric which represents a hardware
    package C-state.
    """

    return metric.startswith("Pkg%")

def get_pkgcs_from_metric(metric):
    """Returns the name of the package C-state represented by 'metric'."""

    return metric[5:]

def get_metric_from_pkgcs(pkgcs):
    """Returns the metric which represents the package state 'pkgcs'."""

    return f"Pkg%{pkgcs.lower()}"

class TurbostatDefs(_STCDefsBase.STCDefsBase):
    """This module provides API to turbostat metrics definitions (AKA 'defs')."""

    def mangle_descriptions(self):
        """Mangle turbostat metric descriptions to describe how they are summarised by turbostat."""

        for metric, mdef in self.info.items():
            method = TurbostatParser.get_aggregation_method(metric)
            if method is not None:
                mdef["descr"] = f"{mdef['descr']} Calculated by finding the {method} of " \
                                f"\"{mdef['name']}\" across the system."

    def __init__(self, cstates):
        """
        The class constructor. Arguments are as follows:
         * cstates - a list of C-states parsed from raw turbostat statistic files.
        """

        super().__init__("turbostat")

        # The "POLL" state has its own definition so does not need to be mangled into the template
        # C-state definitions.
        if "POLL" in cstates:
            cstates.remove("POLL")

        placeholders_info = [{"placeholder": "Cx", "values": cstates, "casesensitive" : False}]
        self._mangle_placeholders(placeholders_info)
