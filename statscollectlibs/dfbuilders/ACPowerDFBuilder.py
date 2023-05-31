# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""
This module provides the capability of building a 'pandas.DataFrame' out of a raw AC Power
statistics file.
"""

import logging
import numpy
import pandas
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.dfbuilders import _DFBuilderBase

_LOG = logging.getLogger()

class ACPowerDFBuilder(_DFBuilderBase.DFBuilderBase):
    """
    This class provides the capability of building a 'pandas.DataFrame' out of a raw AC Power
    statistics file.
    """

    def _read_stats_file(self, path, labels=None):
        """
        Returns a 'pandas.DataFrame' containing the data stored in the raw AC Power statistics CSV
        file at 'path'.
        """

        sdf = pandas.DataFrame()

        try:
            # 'skipfooter' parameter only available with Python pandas engine.
            sdf = pandas.read_csv(path, skipfooter=1, engine="python", dtype='float64')
        except (pandas.errors.ParserError, ValueError) as err:
            # Failed 'dtype' conversion can cause 'ValueError', otherwise most parsing exceptions
            # are of type 'pandas.errors.ParserError'.
            msg = Error(err).indent(2)
            raise Error(f"unable to parse CSV '{path}':\n{msg}.") from None

        # Confirm that the time metric is in the CSV headers.
        if self._time_metric not in sdf:
            raise Error(f"column '{self._time_metric}' not found in statistics file '{path}'.")

        # Convert Time column from time since epoch to time since the first data point was recorded.
        sdf[self._time_metric] = sdf[self._time_metric] - sdf[self._time_metric][0]

        # Remove any 'infinite' values which can appear in raw ACPower files.
        sdf.replace([numpy.inf, -numpy.inf], numpy.nan, inplace=True)
        if sdf.isnull().values.any():
            _LOG.warning("dropping one or more 'nan' values from statistics file '%s'.", path)
            sdf.dropna(inplace=True)

            # Some 'pandas' operations break on 'pandas.DataFrame' instances without consistent
            # indexing. Reset the index to avoid any of these problems.
            sdf.reset_index(inplace=True)

        return sdf

    def __init__(self):
        """
        The class constructor.

        Note, the constructor does not load the potentially huge test result data into the memory.
        The data are loaded "on-demand" by 'load_df()'.
        """

        self._time_metric = "T"

        super().__init__()
