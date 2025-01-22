# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""Provide the wult metrics definition base class."""

from pathlib import Path
from statscollectlibs.mdc import MDCBase

class WultMDCBase(MDCBase.MDCBase):
    """The wult metrics definition base class."""

    def __init__(self, toolname):
        """
        The class constructor. The arguments are as follows.
          * toolname - name of the tool to load the definitions for.
        """

        super().__init__("wult", Path(f"defs/wult/{toolname}.yml"))
