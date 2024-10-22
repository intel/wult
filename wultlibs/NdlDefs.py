# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""This module provides the class for ndl metrics definitions (AKA 'defs')."""

from wultlibs import _WultDefsBase
from wulttools.ndl import ToolInfo

class NdlDefs(_WultDefsBase.WultDefsBase):
    """The class for ndl metrics definitions (AKA 'defs')."""

    def __init__(self):
        """The class constructor."""

        super().__init__(ToolInfo.TOOLNAME)
        super().mangle()
