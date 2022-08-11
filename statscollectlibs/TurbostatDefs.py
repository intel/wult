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

from statscollectlibs import DefsBase
from wultlibs.parsers import TurbostatParser

def is_reqcs_metric(metric):
    """
    Returns 'True' or 'False' based on whether 'metric' is a metric which represents a requestable
    C-state.
    """

    return metric.startswith("C") and metric[1].isdigit() and metric.endswith("%")

def is_hwcs_metric(metric):
    """
    Returns 'True' or 'False' based on whether 'metric' is a metric which represents a hardware
    C-state.
    """

    return metric.startswith("CPU%")

def is_pkgcs_metric(metric):
    """
    Returns 'True' or 'False' based on whether 'metric' is a metric which represents a hardware
    package C-state.
    """

    return metric.startswith("Pkg%")

class TurbostatDefs(DefsBase.DefsBase):
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

        placeholders_info = [{"placeholder": "Cx", "values": cstates, "casesensitive" : False}]
        self._mangle_placeholders(placeholders_info)
