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
from pathlib import Path


@dataclass
class DTabDC:
    """
    This dataclass defines what is expected by the JavaScript side when adding a data tab to HTML
    reports. A "data tab" is defined as a tab which contains data such as a summary table and plots.
    """

    # The name is used as the tab label.
    name: str

    # Relative paths to any 'plotly' plots to include in the tab.
    ppaths: List[Path]

    # Relative path to the summary table dump for the metric.
    smrytblpath: Path


@dataclass
class CTabDC:
    """
    This class defines what is expected by the JavaScript side when adding a container tab to HTML
    report. A "container tab" is defined as tab which contains child tabs. Child tabs can either be
    container tabs or data tabs.
    """

    name: str
    tabs: Union["CTabDC", List[DTabDC]]
