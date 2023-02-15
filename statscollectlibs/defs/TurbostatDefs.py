# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""This module provides the API to turbostat metrics definitions (AKA 'defs')."""

from statscollectlibs.defs import _STCDefsBase
from statscollectlibs.parsers import TurbostatParser

class _CSTypeBase:
    """
    Turbostat collects information about various types of C-state including, but not limited to,
    requestable, package, and module C-states. This base class provides a common interface for all
    of the C-state type classes.
    """
    @staticmethod
    def check_metric(metric):
        """Checks if 'metric' is an instance of this type of C-state."""
        raise NotImplementedError()

    def _get_cs_from_metric(self, metric):
        """Returns the name of the C-state represented in 'metric'."""
        raise NotImplementedError()

    def __init__(self, metric):
        """The class constructor. """
        self.metric = metric
        self.cstate = self._get_cs_from_metric(metric)

class ReqCSDef(_CSTypeBase):
    """This class represents the 'Requestable C-state' type of C-state."""
    @staticmethod
    def check_metric(metric):
        """Checks if 'metric' represents the usage of a requestable C-state."""
        return metric == "POLL%" or (metric.startswith("C") and metric[1].isdigit() and
                                     metric.endswith("%"))

    def _get_cs_from_metric(self, metric):
        """Returns the name of the C-state represented in 'metric'."""
        return metric[:-1]

class CoreCSDef(_CSTypeBase):
    """This class represents the 'Core C-state' type of C-state."""
    @staticmethod
    def check_metric(metric):
        """Checks if 'metric' represents the usage of a core C-state."""
        return metric.startswith("CPU%")

    def _get_cs_from_metric(self, metric):
        """Returns the name of the C-state represented in 'metric'."""
        return metric[4:]

class PackageCSDef(_CSTypeBase):
    """This class represents the 'Package C-state' type of C-state."""
    @staticmethod
    def check_metric(metric):
        """Checks if 'metric' represents the usage of a package C-state."""
        return metric.startswith("Pkg%")

    def _get_cs_from_metric(self, metric):
        """Returns the name of the C-state represented in 'metric'."""
        return metric[4:]

class ModuleCSDef(_CSTypeBase):
    """This class represents the 'Module C-state' type of C-state."""
    @staticmethod
    def check_metric(metric):
        """Checks if 'metric' represents the usage of a module C-state."""
        return metric.startswith("Mod%")

    def _get_cs_from_metric(self, metric):
        """Returns the name of the C-state represented in 'metric'."""
        return metric[4:]

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
