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

from wultlibs import _DefsBase

class TurbostatDefs(_DefsBase.DefsBase):
    """This module provides API to turbostat metrics definitions (AKA 'defs')."""

    def __init__(self):
        """The class constructor."""

        super().__init__("turbostat")
