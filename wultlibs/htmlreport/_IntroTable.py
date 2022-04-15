# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Adam Hawley <adam.james.hawley@intel.com>

"""
This module provides the functionality for generating raw intro table files for HTML reports.
"""

from dataclasses import dataclass
from pepclibs.helperlibs import Trivial


# Text to display if a value is not available for a given set of results.
NA_TEXT = "Not available"

def format_none(val):
    """
    'None' values are represented in the table text format as an empty string. If 'val' is 'None'
    this function returns the empty string, otherwise returns the original value 'val'.
    """

    if val is None:
        return ''
    return val


@dataclass
class _TableCellDC:
    """This dataclass represents a cell within the intro table."""

    # 'value' - the string that is displayed as text in the table cell.
    value: str

    # 'hovertext' - if provided, this text will appear when the user hovers over the cell.
    hovertext: str = ''

    # 'link' - if provided, this string is used as a link so that the user can
    #          click and follow the path.
    link: str = ''


class _TableRow:
    """This class represents a row within the intro table."""

    def add_cell(self, reportid, value, hovertext=None, link=None):
        """
        Add a cell to the row. The cell will be in the 'reportid' column and show 'value' as text.
        If provided, 'hovertext' will be shown when a report viewer hovers over the cell and 'link'
        will make the text clickable. Clicking the text will take the user to 'link'.
        """

        value = value if value else NA_TEXT
        self.res_cells[reportid] = _TableCellDC(value, format_none(hovertext), format_none(link))

    def __init__(self, value, hovertext=None, link=None):
        """
        Class constructor. Arguments will define the first cell in the row which is in the "Title"
        column. The cell will show 'value' as text. If provided, 'hovertext' will be shown when a
        report viewer hovers over the cell and 'link' will make the text clickable. Clicking the
        text will take the user to 'link'.
        """

        self.title_cell = _TableCellDC(value, format_none(hovertext), format_none(link))
        self.res_cells = {}


class IntroTable:
    """
    This module provides the functionality for generating intro table files for HTML reports.

    The HTML format of the intro table has the following layout:

    | Title   | Result Report ID 1 | Result Report ID 2 |
    |---------|--------------------|--------------------|
    | Key 1   | Val 1              | Val 2              |
    | Key 2   | Val 2              | Val 2              |
    |---------|--------------------|--------------------|

    Public methods overview:
    1. Add a row to the intro table.
       * 'create_row()'
    2. Finalise the intro table and generate the intro table file representing it.
       * 'generate()'
    """

    def _dump(self, path, reportids):
        """
        Dump the summary table dictionary to a file. Uses a format specific to this project.
        The format contains 2 types of lines:
        * Header - there is only one per file and should be the first row in the file. Marks
          itself as a header with a leading 'H'. For example:
          H;Title;report_id1;report_id2
        * Table row. For example:
          F;func_name|func_description;func_val|func_hovertext1;func_val2|func_hovertext2
        """

        with open(path, "w", encoding="utf-8") as fobj:
            lines = []
            lines.append(f"H;Title;{';'.join(reportids)}\n")

            for row in self.rows:
                # Generate title cell for 'row'.
                title_cell = row.title_cell
                line = f"R;{title_cell.value}|{title_cell.hovertext}|{title_cell.link}"

                for reportid in reportids:
                    cell = row.res_cells.get(reportid)

                    # If this row has no cell for 'reportid', show an empty cell with '_NA_TEXT'.
                    if cell is None:
                        cell = _TableCellDC(NA_TEXT)

                    line += f";{cell.value}|{cell.hovertext}|{cell.link}"

                lines.append(f"{line}\n")

            fobj.writelines(lines)

    def create_row(self, value, hovertext=None, link=None):
        """
        Returns a new row in the intro table. Arguments will define the first cell in the
        row which is in the "Title" column. The cell will show 'value' as text. If provided,
        'hovertext' will be shown when a report viewer hovers over the cell and 'link' will make the
        text clickable. Clicking the text will take the user to 'link'.

        To populate the row with more cells use 'row.add_cell()'.
        """

        row = _TableRow(value, hovertext, link)
        self.rows.append(row)
        return row

    def generate(self, path):
        """
        Generate the file representing this intro table in text format and save the file at path
        'path'.
        """

        reportids = []
        for row in self.rows:
            reportids += list(row.res_cells.keys())

        reportids = Trivial.list_dedup(reportids)

        self._dump(path, reportids)


    def __init__(self):
        """The class constructor."""

        self.rows = []
