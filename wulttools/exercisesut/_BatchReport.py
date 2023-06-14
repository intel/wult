# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Antti Laakso <antti.laakso@linux.intel.com>
#         Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""A helper module for the 'exercise-sut' tool for generating reports and diffs."""

import os
import logging
from pathlib import Path
from pepclibs.helperlibs import Trivial
from pepclibs.helperlibs.Exceptions import Error
from wulttools.exercisesut import _Common

_LOG = logging.getLogger()

class BatchReport(_Common.CmdlineRunner):
    """Helper class for 'exercise-sut' tool to create reports for series of results."""

    def _search_result_paths(self, searchpaths):
        """Find all result paths in list of paths 'searchpaths'. Returns single list of paths."""

        for searchpath in searchpaths:
            if not searchpath.exists():
                raise Error(f"input path '{searchpath}' does not exist")

            if not searchpath.is_dir():
                raise Error(f"input path '{searchpath}' is not a directory")

            for respath in os.scandir(searchpath):
                if respath.is_dir():
                    yield Path(respath.path)

    def _get_result_paths(self, searchpaths, include, exclude):
        """
        Find results from paths 'searchpaths'. Filter result directories with following arguments.
          * include - List of monikers that must be found from the result path name.
          * exclude - List of monikers that must not be found from the result path name.
        """

        include_monikers = None
        exclude_monikers = None

        if include:
            include_monikers = set(Trivial.split_csv_line(include))

        if exclude:
            exclude_monikers = set(Trivial.split_csv_line(exclude))

        respaths= []
        for respath in self._search_result_paths(searchpaths):
            path_monikers = respath.name.split("-")

            if include_monikers and not include_monikers.issubset(set(path_monikers)):
                continue

            if exclude_monikers and exclude_monikers.intersection(set(path_monikers)):
                continue

            respaths.append(respath)

        return respaths

    def _match_reportid_monikers(self, diff_monikers, reportid_monikers):
        """Find common monikers of moniker lists 'diff_monikers' and 'reportid_monikers'."""

        common_monikers = []
        for diff_moniker in diff_monikers:
            # Diff moniker might include dash ('-'), in which case we need to look for each
            # sub-string.
            sub_strings = diff_moniker.split("-")
            if set(sub_strings).issubset(reportid_monikers):
                for sub_string in sub_strings:
                    common_monikers.append(sub_string)

        return common_monikers

    def _get_grouped_paths(self, respaths, diff_monikers):
        """
        Group results from paths 'respaths'. Group results according to list of monikers in
        'diff_monikers', if any. Returns dictionary with common directory name as key and list
        matching paths as values.
        """

        basepath = Path("-vs-".join([moniker for moniker in diff_monikers if moniker]))

        groups = {}
        for respath in respaths:
            result_monikers = respath.name.split("-")
            common_monikers = self._match_reportid_monikers(diff_monikers, result_monikers)
            if not common_monikers and "" not in diff_monikers:
                continue

            # Remove common monikers from path name.
            for common_moniker in common_monikers:
                if common_moniker in result_monikers:
                    result_monikers.remove(common_moniker)

            outpath = basepath / "-".join(result_monikers)
            if outpath not in groups:
                groups[outpath] = []

            groups[outpath].append(respath)

        return groups

    def _get_diff_paths(self, respaths, diff_monikers):
        """
        Find results matching to list of monikers 'diff_monikers' and yield diff output path with
        list of result paths.
        """

        def _get_path_sortkey(path):
            """
            Method for sorting paths according to order of given diff monikers, or order of input
            paths.
            """

            path_monikers = path.name.split("-")
            for moniker in diff_monikers:
                if moniker in path_monikers:
                    return diff_monikers.index(moniker)

            for respath in respaths:
                if path.parent == respath:
                    return respaths.index(respath)

            return len(diff_monikers)

        grouped_paths = self._get_grouped_paths(respaths, diff_monikers)
        for outpath, paths in grouped_paths.items():
            paths.sort(key=_get_path_sortkey)

            # Yield paths only for diffs where all requested results are found.
            if diff_monikers and len(paths) < len(diff_monikers):
                continue

            yield outpath, paths

    def group_results(self, searchpaths, diffs=None, include=None, exclude=None):
        """
        Find results from paths 'searchpaths'. Group results according to arguments:
          * diffs - List of lists of monikers to group results with.
          * include - Comma-separated list of monikers that must be found from the result path name.
          * exclude - Comma-separated list of monikers that must not be found from the result path
                      name.

        Yields tuple with common directory name as key and list of paths matching to the rules as
        value.
        """

        respaths = self._get_result_paths(searchpaths, include, exclude)

        if diffs:
            for diff_monikers in diffs:
                yield from self._get_diff_paths(respaths, diff_monikers)
        else:
            for respath in respaths:
                outpath = "individual" / Path(respath.name)
                yield outpath, [respath]

    def generate_report(self, respaths, outpath):
        """Generate the report for list of results in 'respaths', store the report to 'outpath'."""

        if outpath.exists():
            _LOG.warning("path '%s' exists", outpath)

        cmd = f"nice -n19 ionice -c3 {self._toolpath} "

        if self._toolpath.name in ("wult", "ndl", "stats-collect"):
            cmd += "report "

        if self._toolopts:
            cmd += f"{self._toolopts} "

        res_str = " ".join([str(path) for path in respaths])
        cmd += f"{res_str} -o {outpath}"

        self._run_command(cmd)

    def __init__(self, toolpath, outpath, toolopts=None, dry_run=False, stop_on_failure=False,
                 proc_count=None):
        """The class constructor."""

        super().__init__(dry_run=dry_run, stop_on_failure=stop_on_failure, proc_count=proc_count)

        self._toolpath = self._lpman.which(toolpath)
        self._outpath = outpath
        self._toolopts = toolopts
