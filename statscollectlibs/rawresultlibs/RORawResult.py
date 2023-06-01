# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""This module provides API for reading raw test results."""

from pepclibs.helperlibs import YAML
from pepclibs.helperlibs.Exceptions import Error, ErrorNotSupported, ErrorNotFound
from statscollectlibs.rawresultlibs import _RawResultBase

class RORawResult(_RawResultBase.RawResultBase):
    """
    This class represents a read-only raw test result. The class API works with the following
    concepts:
     * labels - labels are created during statistics collection and provide extra data about
                datapoints.
     * label definitions - dictionaries defining the metrics which label data measure. For example,
                           if a label contains data about power consumption, the label definition
                           might explain that the data is measured in 'Watts'.

    Public method overview:
     * set_label_defs() - set label definitions for a specific statistic.
     * get_label_defs() - get label definitions for a specific statistic.
     * load_stat() - loads and returns a 'pandas.DataFrame' containing statistics data for this
                     result.
    """

    def set_label_defs(self, stname, defs):
        """Set metric definitions for the 'stname' labels."""

        self._labels_defs[stname] = defs

    def get_label_defs(self, stname):
        """Returns metric definitions for 'stname' data."""

        return self._labels_defs.get(stname, {})

    def _get_stats_path(self, stname, default_name):
        """
        A helper function which returns a path to the raw statistics file for statistic 'stname'.
        Arguments are as follows:
         * stname - the name of the statistic for which statistics paths should be found.
         * default_name - the path that will be used if one is not specified by the result.
        """

        try:
            subpath = self.info["stinfo"][stname]["paths"]["stats"]
        except KeyError:
            subpath = default_name

        path = self.stats_path / subpath
        if path.exists():
            return path

        raise ErrorNotFound(f"raw '{stname}' statistics file not found at path: {path}")

    def _get_labels_path(self, stname):
        """A helper function which returns the path to the labels file for statistic 'stname'."""

        try:
            subpath = self.info["stinfo"][stname]["paths"]["labels"]
        except KeyError:
            return None

        path = self.dirpath / subpath
        if path.exists():
            return path

        raise ErrorNotFound(f"no labels file found for statistic '{stname}' at path: {path} '")

    def load_stat(self, stname, dfbldr, default_name):
        """
        Loads data for statistic 'stname' into 'self.dfs'. Returns a 'pandas.DataFrame' containing
        'stname' data for this result. Arguments are as follows:
         * stname - the name of the statistic for which a 'pandas.DataFrame' should be retrieved.
         * dfbldr - an instance of '_DFBuilderBase.DFBuilderBase' to use to build a
                    'pandas.DataFrame' from the raw statistics file.
         * default_name - the name of the raw statistics file which will be used if one is not
                          defined in 'info.yml'.
        """

        if stname in self.dfs:
            return self.dfs[stname]

        path = self._get_stats_path(stname, default_name)
        labels_path = self._get_labels_path(stname)
        self.dfs[stname] = dfbldr.load_df(path, labels_path)

        return self.dfs[stname]

    def __init__(self, dirpath, reportid=None):
        """
        The class constructor. The arguments are as follows.
          * dirpath - path to the directory containing the raw test result to open.
          * reportid - override the report ID of the raw test result: the 'reportid' string will be
                       used instead of the report ID stored in 'dirpath/info.yml'. Note, the
                       provided report ID is not verified, so the caller has to make sure is a sane
                       string.

        Note, the constructor does not load the potentially huge test result data into the memory.
        It only loads the 'info.yml' file and figures out which metrics have been measured. The data
        are loaded "on-demand" by 'load_df()' and other methods.
        """

        super().__init__(dirpath)

        # Check few special error cases upfront in order to provide a clear error message:
        # the info file should exist and be non-empty.
        for name in ("info_path",):
            attr = getattr(self, name)
            try:
                if not attr.is_file():
                    raise ErrorNotFound(f"'{attr}' does not exist or it is not a regular file")
                if not attr.stat().st_size:
                    raise Error(f"file '{attr}' is empty")
            except OSError as err:
                msg = Error(err).indent(2)
                raise Error(f"failed to access '{attr}':\n{msg}") from err

        self.info = YAML.load(self.info_path)
        if reportid:
            # Note, we do not verify it here, the caller is supposed to verify.
            self.info["reportid"] = reportid
        if "reportid" not in self.info:
            raise ErrorNotSupported(f"no 'reportid' key found in {self.info_path}")
        self.reportid = self.info["reportid"]

        toolname = self.info.get("toolname")
        if not toolname:
            raise Error(f"bad '{self.info_path}' format - the 'toolname' key is missing")

        toolver = self.info.get("toolver")
        if not toolver:
            raise Error(f"bad '{self.info_path}' format - the 'toolver' key is missing")

        if not self.stats_path.is_dir():
            raise Error(f"unable to find statistics directory '{self.stats_path}'")

        # Store each loaded 'pandas.DataFrame' so that it does not need to be re-loaded in future.
        # This dictionary maps statistic names to 'pandas.DataFrames'.
        self.dfs = {}

        # Store label metric definitions provided to 'set_label_defs()'.
        self._labels_defs = {}
