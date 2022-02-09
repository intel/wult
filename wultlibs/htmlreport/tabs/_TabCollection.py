# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""
This module defines what is expected by the JavaScript side when adding a set of tabs to the report.
"""

from dataclasses import dataclass
from typing import Union, List
from wultlibs.htmlreport.tabs.metrictab import _MetricTab


@dataclass
class TabCollection:
    """
    This class defines what is expected by the JavaScript side when adding a set of tabs to the
    report.
    """

    name: str
    tabs: Union["TabCollection", List[_MetricTab.MetricTab]]
