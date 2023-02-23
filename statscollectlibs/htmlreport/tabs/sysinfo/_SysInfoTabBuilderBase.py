# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""
This module provides the capability of populating a "SysInfo" data tab.

"SysInfo" tabs contain various system information about the systems under test (SUTs).
"""

from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.htmlreport.tabs import _DTabBuilder

class SysInfoTabBuilderBase(_DTabBuilder.DTabBuilder):
    """
    This base class provides the capability of populating a "SysInfo" tab.

    Public method overview:
     * get_tab() - returns a '_Tabs.DTabDC' instance which represents system information.
    """

    def get_tab(self):
        """Returns a '_Tabs.DTabDC' instance which represents system information."""

        self.add_fpreviews(self.stats_paths, self.files)

        if self.fpreviews:
            return super().get_tab()

        raise Error(f"unable to build '{self.name}' SysInfo tab, no file previews could be "
                    f"generated.")

    def __init__(self, name, outdir, files, stats_paths):
        """
        Class constructor. Arguments are as follows:
         * name - name to give the tab produced when 'get_tab()' is called.
         * outdir - the directory to store tab files in.
         * files - a dictionary containing the paths of files to include file previews for.
                   Expected to be in the format '{Name: FilePath}' where 'Name' will be the title
                   of the file preview and 'FilePath' is the path of the file to preview.
                   'FilePath' should be relative to the directories in 'stats_paths'
         * stats_paths - a dictionary in the format '{ReportID: StatsDir}' where 'StatsDir' is the
                         path to the directory which contains raw statistics files for 'ReportID'.
        """

        if any(not fp for fp in stats_paths.values()):
            raise Error("Unable to add file previews since not all reports have a statistics dir.")

        # All of the names of 'SysInfo' tabs are file-safe and are also used as the title of the
        # tab.
        mdef = {
            "name": name,
            "fsname": name,
            "title": name
        }

        super().__init__({}, outdir, mdef, outdir)

        self.name = name
        self.files = files
        self.stats_paths = stats_paths
