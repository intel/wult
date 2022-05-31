# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Adam Hawley <adam.james.hawley@intel.com>

"""This module provides the class for pbe metrics definitions (AKA 'defs')."""

from statscollectlibs.defs import DefsBase

class PbeDefs(DefsBase.DefsBase):
    """The class for pbe metrics definitions (AKA 'defs')."""

    def __init__(self, toolname):
        """
        The class constructor. The arguments are as follows.
          * toolname - name of the tool to load the definitions for.
        """

        super().__init__("pbe", toolname, defsdir="defs/wult")
