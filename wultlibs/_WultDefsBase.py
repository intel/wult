# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module provides the base class for metrics definitions (AKA 'defs').
"""

from statscollectlibs.mdc import MDCBase

class WultDefsBase(MDCBase.MDCBase):
    """The base class for metrics definitions (AKA 'defs')."""

    def __init__(self, toolname):
        """
        The class constructor. The arguments are as follows.
          * toolname - name of the tool to load the definitions for.
        """

        super().__init__("wult", toolname, defsdir="defs/wult")
