# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Adam Hawley <adam.james.hawley@intel.com>

"""This module provides an API to the IPMI definitions (AKA 'defs')."""

from wultlibs import _DefsBase

class IPMIDefs(_DefsBase.DefsBase):
    """This class provides an API to the IPMI definitions (AKA 'defs')."""

    @staticmethod
    def get_metric_from_unit(unit):
        """
        Get the name of an IPMI metric which is measured using 'unit'. If a metric is not found,
        returns 'None'.
        """

        if unit == "RPM":
            return "FanSpeed"
        if unit == "degrees C":
            return "Temperature"
        if unit == "Watts":
            return "Power"
        return None

    def __init__(self):
        """The class constructor."""

        super().__init__("ipmi")
