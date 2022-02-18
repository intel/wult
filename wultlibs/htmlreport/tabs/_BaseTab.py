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
class BaseTabDC:
    """
    This class defines what is expected by the JavaScript side when adding a Metric tab to HTML
    reports.
    """

    # The metric is used as the tab name.
    name: str

    # Relative paths to any 'plotly' plots to include in the tab.
    ppaths: List[Path]

    # Relative path to the summary table dump for the metric.
    smrytblpath: Path


@dataclass
class TabCollectionDC:
    """
    This class defines what is expected by the JavaScript side when adding a set of tabs to the
    report.
    """

    name: str
    tabs: Union["TabCollectionDC", List[BaseTabDC]]
