# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2024-2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""Provide the ndl metrics definition class."""

from wultlibs import _WultMDCBase
from wulttools.ndl import ToolInfo

class NdlMDC(_WultMDCBase.WultMDCBase):
    """
    The ndl metrics definition class provides API to ndl metrics definitions, which describe the
    metrics provided by the ndl tool.
    """

    def __init__(self):
        """The class constructor."""

        super().__init__(ToolInfo.TOOLNAME)
