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

import json
from pepclibs.helperlibs.Exceptions import Error, ErrorNotFound

class DFBuilderBase:
    """
    This base class provides common methods that will help child classes to build a
    'pandas.DataFrame' out of a raw statistics file.
    
    This base class requires child classes to implement the following method:
    1. Read a raw statistics file and convert the statistics data into a 'pandas.DataFrame'.
       * '_read_stats_file()'
    """

    def _read_stats_file(self, path, labels=None):
        """
        Returns a 'pandas.DataFrame' containing the data stored in the raw statistics file at
        'path'.
        """

        raise NotImplementedError()

    def _load_labels(self, labels_path):
        """
        Helper function for 'load_df()'. Parses the labels in the file at 'labels_path'. Returns
        a list of label dictionaries.
        """

        try:
            with open(labels_path, "r", encoding="utf-8") as f:
                labels = [json.loads(line) for line in f.readlines()[1:]]
        except OSError as err:
            raise Error(f"unable to parse labels file at path '{labels_path}''") from err

        if not labels:
            raise Error(f"labels file '{labels_path}' does not contain any labels")

        return labels

    def load_df(self, path, labels_path=None):
        """Read the raw statistics file at 'path' into the 'self.df' 'pandas.DataFrame'."""

        if not path.exists():
            raise ErrorNotFound(f"failed to load raw statistics file at path '{path}': file does "
                                f"not exist.")

        if labels_path:
            labels = self._load_labels(labels_path)
        else:
            labels = None

        try:
            self.df = self._read_stats_file(path, labels)
        except Error as err:
            raise Error(f"unable to load raw statistics file at path '{path}':\n"
                        f"{err.indent(2)}") from None

        return self.df

    def __init__(self):
        """The class constructor."""

        self.df = None
