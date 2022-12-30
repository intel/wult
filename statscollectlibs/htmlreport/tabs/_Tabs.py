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

from dataclasses import dataclass, field
from typing import Dict, List, Union
from pathlib import Path

@dataclass
class FilePreviewDC:
    """
    This dataclass defines what is expected by the JavaScript side when adding a file preview to an
    HTML report. A "file preview" includes the entire contents of a file in the report in a small
    preview window.
    """

    # The title which will be placed at the top of the file preview.
    title: str

    # A dictionary in the format '{ReportID: FilePath}'.
    paths: Dict[str, Path]

    # Optional path to a diff file to be included in the file preview.
    diff: Path = ""

@dataclass
class DTabDC:
    """
    This dataclass defines what is expected by the JavaScript side when adding a data tab to HTML
    reports. A "data tab" is defined as a tab which contains data such as a summary table and plots.
    """

    # The name is used as the tab label.
    name: str

    # Relative paths to any 'plotly' plots to include in the tab.
    ppaths: List[Path] = field(default_factory=list)

    # Relative path to the summary table dump for the metric.
    smrytblpath: Path = ""

    # File previews to include in the tab.
    fpreviews: List[FilePreviewDC] = field(default_factory=list)

    # Alerts to notify the report viewer of certain elements of the tab.
    alerts: List[str] = field(default_factory=list)

@dataclass
class CTabDC:
    """
    This class defines what is expected by the JavaScript side when adding a container tab to HTML
    report. A "container tab" is defined as tab which contains child tabs. Child tabs can either be
    container tabs or data tabs. In other words, container tabs are non-leaf tabs in the HTML report
    tabs hierarchy.
    """

    name: str
    tabs: Union["CTabDC", List[DTabDC]]
