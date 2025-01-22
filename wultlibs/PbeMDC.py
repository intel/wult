# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023-2024 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Adam Hawley <adam.james.hawley@intel.com>

"""Provide the pbe metrics definition class."""

from wultlibs import _WultMDCBase
from wulttools.pbe import ToolInfo

class PbeMDC(_WultMDCBase.WultMDCBase):
    """
    The pbe metrics definition class provides API to ndl metrics definitions, which describe the
    metrics provided by the pbe tool.
    """

    def __init__(self):
        """The class constructor."""

        super().__init__(ToolInfo.TOOLNAME)
