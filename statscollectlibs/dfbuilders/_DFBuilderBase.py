# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Adam Hawley <adam.james.hawley@intel.com>

"""
This module provides a base class that will help child classes to build a 'pandas.DataFrame' out of
a raw statistics file.
"""

from pepclibs.helperlibs.Exceptions import Error, ErrorNotFound

class DFBuilderBase:
    """
    This base class provides common methods that will help child classes to build a
    'pandas.DataFrame' out of a raw statistics file.
    
    This base class requires child classes to implement the following method:
    1. Read a raw statistics file and convert the statistics data into a 'pandas.DataFrame'.
       * '_read_stats_file()'
    """

    def _read_stats_file(self, path):
        """
        Returns a 'pandas.DataFrame' containing the data stored in the raw statistics file at
        'path'.
        """

        raise NotImplementedError()

    def load_df(self, path):
        """Read the raw statistics file at 'path' into the 'self.df' 'pandas.DataFrame'."""

        if not path.exists():
            raise ErrorNotFound(f"failed to load raw statistics file at path '{path}': file does "
                                f"not exist.")

        try:
            self.df = self._read_stats_file(path)
        except Error as err:
            raise Error(f"unable to load raw statistics file at path '{path}':\n"
                        f"{err.indent(2)}") from None

        return self.df

    def __init__(self):
        """The class constructor."""

        self.df = None
