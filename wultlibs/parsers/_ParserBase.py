# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2015-2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module provides the base class for parsers.
"""

from powerlablibs.Exceptions import Error

class ParserBase:
    """The base class for parsers."""

    def _next(self): # pylint: disable=no-self-use
        """Yield the data-sets - should be implemented by the children of this class."""
        raise Error("_next() is not implemented")

    def next(self):
        """Yield the data-sets."""

        yield from self._next()
        if self._path:
            self._lines.close()

    def __init__(self, path=None, lines=None):
        """
        Initialize a class instance. The 'input_data' parameter can be one of the following:
          o  path to the input file which should be parsed
          o  an iterable object which provides the lines to parse one-by-one. For example, this
             can be a file object or 'iter(list)'.
        """

        self._path = path
        self._lines = lines

        if path and lines:
            raise Error("Please, specify either 'path' or 'lines', but not both")

        if path:
            try:
                with open(path, 'r', encoding="UTF-8") as f:
                    self._lines = iter(f.readlines())
            except OSError as err:
                raise Error(f"cannot open '{path}':\n{err}") from err
