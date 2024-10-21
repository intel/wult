# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023-2024 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Adam Hawley <adam.james.hawley@intel.com>

"""This module provides the class for pbe metrics definitions (AKA 'defs')."""

from wultlibs import _WultDefsBase
from wulttools.pbe import ToolInfo

class PbeDefs(_WultDefsBase.WultDefsBase):
    """The class for pbe metrics definitions (AKA 'defs')."""

    def __init__(self):
        """The class constructor."""

        super().__init__(ToolInfo.TOOLNAME)
        super().mangle()
