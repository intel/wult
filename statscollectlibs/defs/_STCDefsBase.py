# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module provides the base class for metrics definitions (AKA 'defs').

Extends 'statscollectlibs.DefsBase.DefsBase' by specifying the directory for stats-collect
definition files.
"""

from statscollectlibs.defs.DefsBase import DefsBase

class STCDefsBase(DefsBase):
    """The base class for metrics definitions (AKA 'defs')."""

    def __init__(self, toolname):
        """
        The class constructor. The arguments are as follows.
          * toolname - name of the tool to load the definitions for.
        """

        super().__init__("stats-collect", toolname, defsdir="defs/statscollect")
