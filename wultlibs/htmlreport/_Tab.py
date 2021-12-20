# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""
This module defines what is expected by Jinja templates when adding a tab to HTML reports by
defining the 'Tab' dataclass.
"""

from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Tab:
    """
    This class defines what is expected by the Jinja templates when adding a tab to the
    report.

    Jinja templates read from Tab objects to populate tabs in the report. Here is how it is done:
     1. The tab selector (the button you click to open a tab) is created with 'label' as the text in
        the button and 'id' as the HTML element ID.
     2. If 'Tab.tabs' is populated with child tabs, the template recursively adds these tabs.
     3. Depending on the 'category' of tab chosen, the template uses a different macro to populate
        the tab. The macro will be passed the dictionary 'mdata'.
    """

    # HTML tab element ID.
    id: str
    # Label for the tab selector.
    label: str
    # Child tabs (each child tab is of type 'Tab').
    tabs: List['Tab'] = None
    # If a 'category' is defined, it is used to populate the tab using the correct macro.
    # Possible values include 'metric', 'info' or None.
    category: str = None
    # Macros which populate the tab content will be provided the 'mdata' dictionary.
    mdata: Dict = None
