# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""
This module provides the capability of building 'pandas.DataFrames' out of IPMI statistics files.
"""

import numpy
import pandas
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.defs import IPMIDefs
from statscollectlibs.dfbuilders import _DFBuilderBase
from statscollectlibs.parsers import IPMIParser

class IPMIDFBuilder(_DFBuilderBase.DFBuilderBase):
    """
    This class provides the capability of building a 'pandas.DataFrames' out of raw IPMI statistics
    files.
    """

    def _categorise_cols(self, ipmi):
        """
        Associates column names in the IPMIParser dict 'ipmi' to the metrics they represent. For
        example, 'FanSpeed' can be represented by several columns such as 'Fan1', 'Fan Speed' etc.
        This function will add those column names to the 'FanSpeed' metric.
        """

        for colname, val in ipmi.items():
            unit = val[1]
            metric = self._defs.get_metric_from_unit(unit)
            if metric:
                self.metrics[metric].append(colname)

    def _read_stats_file(self, path, labels=None):
        """
        Returns a 'pandas.DataFrame' containing the data stored in the raw IPMI statistics file at
        'path'.
        """

        time_colname = "timestamp"

        def _ipmi_to_df(ipmi):
            """Convert IPMIParser dict to 'pandas.DataFrame'."""

            # Reduce IPMI values from ('value', 'unit') to just 'value'.
            # If "no reading" is parsed in a line of a raw IPMI file, 'None' is returned. In this
            # case, we should exclude that IPMI metric.
            i = {k:[v[0]] for k, v in ipmi.items() if v[0] is not None}
            return pandas.DataFrame.from_dict(i)

        ipmi_gen = IPMIParser.IPMIParser(path).next()

        try:
            # Try to read the first data point from raw statistics file.
            i = next(ipmi_gen)
        except StopIteration:
            raise Error("empty or incorrectly formatted IPMI raw statistics file") from None

        # Populate 'self._metrics' using the columns from the first data point.
        self._categorise_cols(i)
        sdf = _ipmi_to_df(i)

        for i in ipmi_gen:
            df = _ipmi_to_df(i)
            # Append dataset for a single timestamp to the main 'pandas.DataFrame'.
            sdf = pandas.concat([sdf, df], ignore_index=True)

        # Confirm that the time column is in the 'pandas.DataFrame'.
        if time_colname not in sdf:
            raise Error(f"column '{time_colname}' not found in statistics file '{path}'.")

        # Convert time column format to be 'time since epoch in seconds' so it is consistent with
        # other time columns for other statistics and so that labels can be applied using
        # '_apply_labels()'.
        sdf[time_colname] -= numpy.datetime64('1970-01-01T00:00:00Z')
        sdf[time_colname] /= numpy.timedelta64(1, "s")

        if labels:
            self._apply_labels(sdf, labels, time_colname)

        # Convert Time column from time stamp to time since the first data point was recorded.
        sdf[time_colname] = sdf[time_colname] - sdf[time_colname][0]

        sdf = sdf.rename(columns={time_colname: self._time_metric})
        return sdf

    def __init__(self):
        """
        The class constructor.

        Note, the constructor does not load the potentially huge test result data into the memory.
        The data are loaded "on-demand" by 'load_df()'.
        """

        self._time_metric = "Time"
        self._defs = IPMIDefs.IPMIDefs()

        # Metrics in IPMI statistics can be represented by multiple columns. For example the
        # "FanSpeed" of several different fans can be measured and represented in columns "Fan1",
        # "Fan2" etc. This dictionary maps the metrics to the appropriate columns. Initialise it
        # with empty column sets for each metric.
        self.metrics = {metric: [] for metric in self._defs.info}

        super().__init__()
